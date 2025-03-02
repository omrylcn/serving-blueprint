# src/ml/text_embedding_service.py
import onnxruntime as ort
import numpy as np
import os
from typing import List, Dict, Any, Union, Optional
from transformers import AutoTokenizer
import torch
from src.core.config.main import settings
from src.core.logging import logger


class TextEmbeddingService:
    """
    Text embedding service using ONNX runtime for optimized inference.
    Supports both single and batch text embedding generation.
    """
    
    def __init__(self, model_path: str, model_config: Dict[str, Any]):
        """
        Initialize the text embedding service.
        
        Parameters
        ----------
        model_path : str
            Path to the ONNX model file
        model_config : Dict[str, Any]
            Configuration parameters for the model
        """
        self.model_path = model_path
        self.model_config = model_config
        
        # Extract configuration parameters
        self.max_seq_length = model_config.get("max_seq_length", 128)
        self.batch_size = model_config.get("batch_size", 32)
        self.normalize = model_config.get("normalize", True)
        self.embedding_dim = model_config.get("embedding_dim", 384)
        
        # Initialize session and tokenizer to None (will be loaded on demand)
        self.session = None
        self.tokenizer = None
        
        # Log initialization
        logger.info(f"Initialized TextEmbeddingService with model: {os.path.basename(model_path)}")
        
    def load(self) -> 'TextEmbeddingService':
        """
        Load the ONNX model and tokenizer.
        
        Returns
        -------
        TextEmbeddingService
            Returns self for method chaining
        """
        try:
            # Load ONNX Runtime session with optimizations
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.intra_op_num_threads = 1
            sess_options.inter_op_num_threads = 1
            
            # Create ONNX Runtime session
            self.session = ort.InferenceSession(
                self.model_path,
                sess_options=sess_options,
                providers=['CPUExecutionProvider']
            )
            
            # Get model metadata
            model_metadata = self.session.get_modelmeta()
            
            # Determine the pre-trained model name from config
            tokenizer_name = self.model_config.get("tokenizer_name", None)
            
            # If tokenizer_name is not provided, try to detect from model path
            if tokenizer_name is None:
                base_name = os.path.basename(self.model_path)
                if "MiniLM" in base_name:
                    tokenizer_name = "sentence-transformers/all-MiniLM-L6-v2"
                elif "mpnet" in base_name:
                    tokenizer_name = "sentence-transformers/all-mpnet-base-v2"
                elif "roberta" in base_name:
                    tokenizer_name = "sentence-transformers/all-roberta-large-v1"
                else:
                    # Default fallback
                    tokenizer_name = "sentence-transformers/all-MiniLM-L6-v2"
            
            # Load the tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
            
            logger.info(f"Successfully loaded model and tokenizer: {tokenizer_name}")
            return self
            
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _preprocess(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """
        Preprocess text inputs for the model.
        
        Parameters
        ----------
        texts : List[str]
            List of input texts
            
        Returns
        -------
        Dict[str, np.ndarray]
            Dictionary of preprocessed inputs ready for the model
        """
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not loaded. Call load() method first.")
        
        # Tokenize the input texts
        encoded_inputs = self.tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=self.max_seq_length,
            return_tensors="np"
        )
        
        return {
            "input_ids": encoded_inputs["input_ids"].astype(np.int64),
            "attention_mask": encoded_inputs["attention_mask"].astype(np.int64),
            "token_type_ids": encoded_inputs.get("token_type_ids", np.zeros_like(encoded_inputs["input_ids"])).astype(np.int64)
        }
    
    def _run_inference(self, inputs: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Run inference on preprocessed inputs.
        
        Parameters
        ----------
        inputs : Dict[str, np.ndarray]
            Preprocessed model inputs
            
        Returns
        -------
        np.ndarray
            Raw model outputs
        """
        if self.session is None:
            raise RuntimeError("Model not loaded. Call load() method first.")
        
        # Get input and output names
        input_names = [input.name for input in self.session.get_inputs()]
        output_names = [output.name for output in self.session.get_outputs()]
        
        # Prepare the inputs
        model_inputs = {name: inputs[name] for name in input_names if name in inputs}
        
        # Run inference
        embeddings = self.session.run(output_names, model_inputs)
        
        # Some models return a tuple with one element, others directly the embeddings
        if isinstance(embeddings, list) and len(embeddings) == 1:
            embeddings = embeddings[0]
            
        return embeddings
    
    def _postprocess(self, embeddings: np.ndarray, normalize: bool = None) -> np.ndarray:
        """
        Postprocess model outputs.
        
        Parameters
        ----------
        embeddings : np.ndarray
            Raw embeddings from the model
        normalize : bool, optional
            Whether to normalize embeddings, defaults to value set at initialization
            
        Returns
        -------
        np.ndarray
            Processed embeddings
        """
        if normalize is None:
            normalize = self.normalize
            
        # Some models require special handling to extract sentence embeddings
        # For most sentence transformer models, the first token's embedding (CLS) or mean pooling can be used
        
        # If embeddings have 3 dimensions (batch, seq_len, hidden_size)
        # we take the first token (CLS) or do mean pooling
        if len(embeddings.shape) == 3:
            # Check if we should use CLS token or mean pooling (could be model-dependent)
            if self.model_config.get("use_cls_token", False):
                # Extract CLS token embedding (first token)
                embeddings = embeddings[:, 0, :]
            else:
                # Mean pooling (average all token embeddings)
                embeddings = np.mean(embeddings, axis=1)
        
        # Normalize embeddings if required
        if normalize:
            # L2 normalization
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / np.maximum(norms, 1e-12)
            
        return embeddings
    
    def process_batch(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """
        Process a batch of texts to get embeddings.
        
        Parameters
        ----------
        texts : List[str]
            List of input texts
        batch_size : int, optional
            Batch size to use, defaults to initialization value
            
        Returns
        -------
        np.ndarray
            Matrix of embeddings, shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.zeros((0, self.embedding_dim))
            
        if batch_size is None:
            batch_size = self.batch_size
            
        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Preprocess
            inputs = self._preprocess(batch_texts)
            
            # Run inference
            batch_embeddings = self._run_inference(inputs)
            
            # Postprocess
            batch_embeddings = self._postprocess(batch_embeddings)
            
            all_embeddings.append(batch_embeddings)
            
        # Combine all batch results
        if all_embeddings:
            return np.vstack(all_embeddings)
        else:
            return np.zeros((0, self.embedding_dim))
    
    def process_single(self, text: str) -> np.ndarray:
        """
        Process a single text to get embedding.
        
        Parameters
        ----------
        text : str
            Input text
            
        Returns
        -------
        np.ndarray
            Embedding vector, shape (embedding_dim,)
        """
        result = self.process_batch([text])
        return result[0]