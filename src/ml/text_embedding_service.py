# src/ml/text_embedding_service.py
from typing import Dict, List, Union, Optional, Any
from kombu import log
import numpy as np
import os
from src.core.config  import settings,ModelConfig
from src.core.logger import logger
from light_embed import TextEmbedding



# from typing import Dict, List, Union, Optional
# import numpy as np
# from src.config import ModelCon
# from light_embed import TextEmbedding


class TextEmbeddingService:
    """
    A wrapper class for text embedding operations using the light_embed library.

    This class manages the lifecycle of a text embedding model, handling its initialization
    and prediction operations with proper type safety.

    Parameters
    ----------
    model_config : Dict[str, Union[str, int]]
        Configuration dictionary containing model parameters.
        Must include 'model_name' key with the path to the model.

    Attributes
    ----------
    config : Dict[str, Union[str, int]]
        Stored configuration dictionary containing model parameters
    model : Optional[TextEmbedding]
        The underlying text embedding model instance, None before loading

    Examples
    --------
    >>> config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
    >>> embedder = Embedder(config)
    >>> embedder.load()
    >>> sentences = ["Hello world", "Another sentence"]
    >>> embeddings = embedder.predict(sentences)
    """
    
    def __init__(self, model_config:ModelConfig) -> None:
        """
        Initialize the Embedder with model configuration.

        Parameters
        ----------
        model_config : Dict[str, Union[str, int]]
            Configuration dictionary containing model parameters.
            Must include 'model_name' key.
        """
        self.config = model_config
        self.model: Optional[TextEmbedding] = None
        self.model_config = {
            "onnx_file": self.config.params['onnx_file'],
            "normalize": self.config.params['normalize'],
        }

        logger.info(f"Initialized TextEmbeddingService with name {self.config.name}")
        logger.info(f"Model config: {self.model_config}")
    def load(self)-> "TextEmbeddingService":
        """
        Load the text embedding model into memory.

        Returns
        -------
        Embedder
            Returns self for method chaining.

        Raises
        ------
        KeyError
            If model_name is not found in config
        ValueError
            If model loading fails
        """
        
       
        try:
            
            self.model = TextEmbedding(
                model_name_or_path=self.config.path,
                model_config=self.model_config
            )
            logger.info(f"Loaded model: {self.config.name}")
            return self
        except Exception as e:
            raise ValueError(f"Failed to load model: {str(e)}")

    def predict(self, sentences: List[str]) -> np.ndarray:
        """
        Generate embeddings for the input sentences.

        Parameters
        ----------
        sentences : List[str]
            List of input strings to generate embeddings for.
            Each string should be a valid text sequence.

        Returns
        -------
        np.ndarray
            Matrix of embeddings, shape (n_sentences, embedding_dim)
            where n_sentences is the number of input sentences and
            embedding_dim is the dimensionality of the embedding space.

        Raises
        ------
        RuntimeError
            If model is not loaded
        ValueError
            If sentences list is empty
        """
        if self.model is None:
            raise RuntimeError("Model must be loaded before prediction. Call load() first.")
            
        if not sentences:
            raise ValueError("Input sentences list cannot be empty")
        
        return self.model.encode(sentences)