"""
Advanced logging handlers for ML API operations.

This module provides specialized logging handlers for saving
ML model operations, metadata, and results to databases.
"""

import os
import time
import json
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional

# from ssearch.config import settings
from src.core.config import settings


VALID_LOGGER_HANDLERS = ["elasticsearch", "console"]


class BaseDBLogger(ABC):
    """
    Abstract base class for database loggers.

    This class defines the interface for all database loggers and provides
    common functionality such as context management and log formatting.
    """

    def __init__(
        self,
        name: str,
        tag: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        log_level: Optional[str] = None,
    ) -> None:
        """
        Initialize the base database logger.

        Parameters
        ----------
        name : str
            Logger name
        tag : str, optional
            Version or tag of the model, by default None
        context : Dict[str, Any], optional
            Additional context information for all log entries, by default None
        """
        self.log_level = log_level if log_level else settings.log_level
        self.log_format = settings.logger_format
        self.log_dir = settings.log_dir
        self.name = name
        self.unique_name = f"{name}_{tag}" if tag else name
        self.tag = tag
        self.context = context or {}

        self.connection_error = False
        self.logger = self._setup_logger()

    def with_context(self, **kwargs) -> "BaseDBLogger":
        """
        Add additional context to all log entries.

        Parameters
        ----------
        **kwargs : dict
            Key-value pairs to add to the context

        Returns
        -------
        BaseDBLogger
            Self instance for method chaining
        """
        self.context.update(kwargs)
        return self

    @abstractmethod
    def _setup_logger(self) -> logging.Logger:
        """
        Create and configure the logger instance.

        Returns
        -------
        logging.Logger
            Configured logger instance
        """
        pass

    @abstractmethod
    def log_operation(self, message: str, level: str = "info", **kwargs) -> None:
        """
        Log an operational event.

        Parameters
        ----------
        message : str
            Log message content
        level : str, optional
            Log level (info, warning, error, debug, critical), by default "info"
        **kwargs : dict
            Additional data to include in the log entry
        """
        pass

    @abstractmethod
    def log_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Log model metadata information.

        Parameters
        ----------
        metadata : Dict[str, Any]
            Dictionary of model metadata
        """
        pass

    @abstractmethod
    def log_model_results(self, input_info: Dict[str, Any], results: Dict[str, Any], **kwargs) -> None:
        """
        Log model prediction results.

        Parameters
        ----------
        input_info : Dict[str, Any]
            Information about the input data
        results : Dict[str, Any]
            Model prediction results
        """
        pass

    def format_log_entry(self, base_data: Dict[str, Any], **additional_data) -> Dict[str, Any]:
        """
        Create a standardized log entry format.

        Parameters
        ----------
        base_data : Dict[str, Any]
            Core log data
        **additional_data : dict
            Additional data to include

        Returns
        -------
        Dict[str, Any]
            Formatted log entry
        """
        # Remove sensitive fields if configured
        for field in settings.logger_settings.sensitive_fields:
            if field in base_data:
                base_data[field] = "******"
            if field in additional_data:
                additional_data[field] = "******"

        return {
            "timestamp": str(datetime.now()),
            "logger_name": self.name,
            "tag_name": self.unique_name,
            **self.context,
            **base_data,
            **additional_data,
        }

    def info(self, message: str, **kwargs) -> None:
        """
        Log an informational message.

        Parameters
        ----------
        message : str
            Log message content
        **kwargs : dict
            Additional information to include in the log
        """
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message.

        Parameters
        ----------
        message : str
            Warning message content
        **kwargs : dict
            Additional information to include in the log
        """
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message.

        Parameters
        ----------
        message : str
            Error message content
        **kwargs : dict
            Additional information to include in the log
        """
        self.logger.error(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message.

        Parameters
        ----------
        message : str
            Debug message content
        **kwargs : dict
            Additional information to include in the log
        """
        self.logger.debug(message, **kwargs)


class DefaultLogger(BaseDBLogger):
    """
    Default logger implementation with minimal functionality.

    This logger provides safe implementations of all abstract methods
    but only logs warnings when specialized methods are called.
    It's used as a fallback when other logger types cannot be created.
    """

    def __init__(self, name: str, tag: Optional[str] = None, **kwargs):
        """
        Initialize the default logger.

        Parameters
        ----------
        name : str
            Logger name
        tag : str, optional
            Version or tag of the model, by default None
        **kwargs : dict
            Additional context information
        """
        super().__init__(name, tag, **kwargs)

    def _setup_logger(self) -> logging.Logger:
        """
        Create and configure the logger instance.

        Returns
        -------
        logging.Logger
            Configured logger instance
        """
        logger = logging.getLogger(f"console_{self.unique_name}")
        logger.setLevel(getattr(logging, self.log_level))

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_operation(self, message: str, level: str = "info", **kwargs) -> None:
        """
        Log an operational event.

        Parameters
        ----------
        message : str
            Log message content
        level : str, optional
            Log level (info, warning, error, debug, critical), by default "info"
        **kwargs : dict
            Additional data to include in the log entry
        """
        # Just log the message with standard logger
        getattr(self.logger, level)(message)

    def log_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Log model metadata information.

        Parameters
        ----------
        metadata : Dict[str, Any]
            Dictionary of model metadata
        """
        # Just log a warning that metadata logging is not supported
        self.logger.warning(
            f"Metadata logging not supported in DefaultLogger. " f"Metadata keys: {', '.join(metadata.keys())}"
        )

    def log_model_results(self, input_info: Dict[str, Any], results: Dict[str, Any], *args, **kwargs) -> None:
        """
        Log model prediction results.

        Parameters
        ----------
        input_info : Dict[str, Any]
            Information about the input data
        results : Dict[str, Any]
            Model prediction results
        """
        # Just log a warning that results logging is not supported
        self.logger.warning(
            f"Model results logging not supported in DefaultLogger. " f"Results keys: {', '.join(results.keys())}"
        )

    def flush_all(self) -> None:
        """
        Flush handlers to ensure all logs are written.
        """
        for handler in self.logger.handlers:
            try:
                handler.flush()
            except Exception as e:
                print(f"Handler flush error: {e}")


class ElasticsearchLogger(BaseDBLogger):
    """
    Logger implementation for Elasticsearch.

    This logger sends log entries to Elasticsearch with appropriate
    index templates and batch processing for performance.
    """

    def __init__(
        self,
        name: str,
        tag: Optional[str] = None,
        es_hosts: Optional[List[str]] = None,
        batch_size: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize the Elasticsearch logger.

        Parameters
        ----------
        name : str
            Logger name
        tag : str, optional
            Version or tag of the model, by default None
        es_hosts : List[str], optional
            List of Elasticsearch hosts, by default None
        batch_size : int, optional
            Number of logs to batch before sending, by default None
        **kwargs : dict
            Additional context information
        """
        # Initialize connection error flag before super init
        self.connection_error = False
        self.es = None
        self.batch = {"operations": [], "metadata": [], "results": []}
        self._log_depth = 0  # Simple recursive logging prevention

        # Initialize parent
        super().__init__(name, tag, **kwargs)

        # Setup Elasticsearch connection with error handling
        try:
            from elasticsearch import Elasticsearch

            # Get configuration with defaults
            es_hosts = es_hosts or (
                [settings.elasticsearch_host]
                if isinstance(settings.elasticsearch_host, str)
                else settings.elasticsearch_host
            )
            self.batch_size = batch_size or settings.batch_size

            # Skip if no hosts configured
            if not es_hosts:
                self.connection_error = True
                self.logger.error("No Elasticsearch hosts specified")
                return

            # Setup Elasticsearch client
            # es_config = settings.logger_settings.elasticsearch_settings
            timeout = settings.timeout

            self.es = Elasticsearch(
                es_hosts,
                timeout=timeout,
                # use_ssl=es_config.use_ssl,
                # verify_certs=es_config.verify_certs,
                # Additional auth params if needed
                # basic_auth=(username, password)
            )

            # Test connection
            try:
                if not self.es.ping():
                    raise ConnectionError("Elasticsearch connection test failed")
            except Exception as e:
                self.connection_error = True
                self.logger.error(f"Elasticsearch connection test failed: {e}")
                return

            # Setup index naming
            self.unique_name = f"{name}_{tag}" if tag else name
            self.index_prefix = f"{self.unique_name}".lower().replace(" ", "_")

            # Setup index templates - Template errors won't prevent logging
            try:
                self._create_template()
            except Exception as e:
                self.logger.warning(f"Failed to create Elasticsearch template: {e}")
                # Continue anyway

        except ImportError as e:
            self.connection_error = True
            self.logger.error(f"Elasticsearch package not available: {e}")
        except Exception as e:
            self.connection_error = True
            self.logger.error(f"Error setting up Elasticsearch connection: {e}", exc_info=True)
            print(f"Error setting up Elasticsearch connection: {e}")

    def _setup_logger(self) -> logging.Logger:
        """
        Create and configure the logger instance.

        Returns
        -------
        logging.Logger
            Configured logger instance
        """
        logger = logging.getLogger(f"es_{self.unique_name}")
        logger.setLevel(getattr(logging, self.log_level))

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _create_template(self) -> None:
        """
        Create Elasticsearch index template.
        """
        if self.connection_error or self.es is None:
            return

        template = {
            "index_patterns": [f"{self.index_prefix}*"],
            "template": {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "logger_name": {"type": "keyword"},
                        "tag_name": {"type": "keyword"},
                        "level": {"type": "keyword"},
                        "metadata": {"type": "object", "dynamic": False},
                        "message": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "metrics": {"type": "object", "dynamic": True},
                        "input_info": {"type": "object", "dynamic": False},
                        "results": {"type": "object", "dynamic": False},
                    }
                }
            },
        }

        self.es.indices.put_index_template(name=f"{self.index_prefix}_template", body=template)

    def _flush_batch(self, batch_type: str) -> None:
        """
        Send collected logs to Elasticsearch.

        Parameters
        ----------
        batch_type : str
            Type of batch to flush ("operations", "metadata", or "results")
        """
        if self.connection_error or self.es is None or not self.batch[batch_type]:
            if self.batch[batch_type]:
                self.logger.warning(
                    f"{len(self.batch[batch_type])} {batch_type} logs couldn't be sent to Elasticsearch"
                )
                self.batch[batch_type] = []  # Clear to avoid memory leaks
            return

        try:
            from elasticsearch.helpers import bulk
            import elasticsearch

            max_retries = 3
            retry_delay = 1.0

            # Make a copy and clear the batch to avoid holding items while processing
            actions = list(self.batch[batch_type])
            self.batch[batch_type] = []

            for attempt in range(max_retries):
                try:

                    success, errors = bulk(self.es, actions, request_timeout=30, stats_only=False)
                    break
                except Exception as e:

                    self.logger.error(
                        f"{batch_type} batch flush error (attempt {attempt+1}/{max_retries}): {e}", exc_info=True
                    )

                    # self.logger.error(f"errors :  {errors}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        # Mark as connection error on final retry
                        self.connection_error = True

        except ImportError as e:
            self.logger.error(f"Elasticsearch helpers not available: {e}")
            self.connection_error = True

    def log_operation(self, message: str, level: str = "info", **kwargs) -> None:
        """
        Log an operational event.

        Parameters
        ----------
        message : str
            Log message content
        level : str, optional
            Log level (info, warning, error, debug, critical), by default "info"
        **kwargs : dict
            Additional data to include in the log entry
        """
        try:
            # Prevent recursive logging
            self._log_depth += 1
            if self._log_depth > 3:
                print(f"WARNING: Recursive logging detected: {message}")
                self._log_depth -= 1
                return

            # Ensure message is a string
            if message is None:
                message = "None"
            elif not isinstance(message, str):
                message = str(message)

            # Log to standard logger
            getattr(self.logger, level)(message)

            # Skip Elasticsearch if connection issues
            if self.connection_error or self.es is None:
                return

            # Create and send document
            doc = self.format_log_entry({"message": message, "level": level}, **kwargs)

            action = {"_index": f"{self.index_prefix}_operations", "_source": doc}
            self.batch["operations"].append(action)

            if len(self.batch["operations"]) >= self.batch_size:
                self._flush_batch("operations")
        except Exception as e:
            # Avoid using logger here to prevent potential recursion
            self.logger.error(f"Error logging operation: {e}", exc_info=True)
        finally:
            # Always decrement the counter
            self._log_depth -= 1

    def log_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Log model metadata information.

        Parameters
        ----------
        metadata : Dict[str, Any]
            Dictionary of model metadata
        """
        try:
            # Input validation

            if metadata is None or not isinstance(metadata, dict):

                self.logger.warning("Invalid metadata format. Skipping Elasticsearch logging.")
                metadata = None

            # Log to console safely
            try:
                keys = ", ".join(metadata.keys()) if hasattr(metadata, "keys") else "unknown format"
                if keys == "unknown format":
                    self.log_operation(f"Metadata logged: {keys}, no logging", "warning")
                    return

            except Exception as e:
                self.logger.warning(f"Error extracting metadata keys: {e}")

            # Skip Elasticsearch if connection issues
            if self.connection_error or self.es is None:
                return

            doc = self.format_log_entry({"metadata": metadata})
            action = {"_index": f"{self.index_prefix}_metadata", "_source": doc}
            self.batch["metadata"].append(action)

            if len(self.batch["metadata"]) >= self.batch_size:
                self._flush_batch("metadata")
        except Exception as e:
            self.logger.error(f"Error in log_metadata: {e}", exc_info=True)

    def log_model_results(self, input_info: Dict[str, Any], results: Dict[str, Any], **kwargs) -> None:
        """
        Log model prediction results.

        Parameters
        ----------
        input_info : Dict[str, Any]
            Information about the input data
        results : Dict[str, Any]
            Model prediction results
        """
        try:
            # Input validation
            if input_info is None:
                input_info = {}
            if results is None:
                results = {}

            # # Log to console safely
            # try:
            #     # Only log input keys if configured to do so
            #     if settings.logger_settings.log_model_inputs:
            #         keys = ', '.join(input_info.keys()) if hasattr(input_info, 'keys') else 'unknown format'
            #         self.log_operation(f"Model results logged with input keys: {keys}", "info")
            #     else:
            #         self.log_operation(f"Model results logged with {len(results)} result items", "info")
            # except Exception as e:
            #     self.logger.warning(f"Error extracting results keys: {e}")

            # Skip Elasticsearch if connection issues
            if self.connection_error or self.es is None:
                return

            doc = self.format_log_entry({"input_info": input_info, "results": results, **kwargs})
            action = {"_index": f"{self.index_prefix}_results", "_source": doc}
            self.batch["results"].append(action)

            if len(self.batch["results"]) >= self.batch_size:
                self._flush_batch("results")
        except Exception as e:
            self.logger.error(f"Error in log_model_results: {e}", exc_info=True)

    def flush_all(self) -> None:
        """
        Flush all batches to Elasticsearch.
        """
        try:
            if self.connection_error or self.es is None:
                # Clear batches without sending if connection error
                for batch_type in self.batch:
                    if self.batch[batch_type]:
                        self.logger.warning(
                            f"Cannot flush {len(self.batch[batch_type])} {batch_type} logs: connection error"
                        )
                        self.batch[batch_type] = []
                return

            # Flush each batch type
            for batch_type in self.batch:
                self._flush_batch(batch_type)
        except Exception as e:
            self.logger.error(f"Error in flush_all: {e}", exc_info=True)

    def __del__(self) -> None:
        """
        Flush all batches when object is deleted.
        """
        try:
            self.flush_all()
        except Exception as e:
            # Can't use logger here as it might be destroyed already
            print(f"Error flushing logs during cleanup: {e}")

    def format_log_entry(self, base_data: Dict[str, Any], **additional_data) -> Dict[str, Any]:
        """
        Create a standardized log entry format.

        Parameters
        ----------
        base_data : Dict[str, Any]
            Core log data
        **additional_data : dict
            Additional data to include

        Returns
        -------
        Dict[str, Any]
            Formatted log entry
        """
        # Remove sensitive fields if configured
        for field in settings.sensitive_fields:
            if field in base_data:
                base_data[field] = "******"
            if field in additional_data:
                additional_data[field] = "******"

        return {
            "timestamp": datetime.now().isoformat(),
            "logger_name": self.name,
            "tag_name": self.unique_name,
            **self.context,
            **base_data,
            **additional_data,
        }


def create_logger(logger_type="console", config=settings) -> BaseDBLogger:
    """
    Creates a logger of the specified type (elasticsearch or console).
    
    Parameters
    ----------
    logger_type : str, optional
        Logger type ('elasticsearch' or 'console'), by default "console"
    config : dict, optional
        Additional logger configuration parameters, by default None
    
    Returns
    -------
    BaseDBLogger
        Created logger object
    """
   
    
    # Default values
    name = "ml_api"
    tag = getattr(settings, "project_version", "v1.0")
    log_level = getattr(settings, "log_level", "INFO")
    emergency_logger = None


    try:
        emergency_logger = DefaultLogger(name=f"{name}_emergency", log_level="DEBUG")
    except Exception as e:
        print(f"Emergency logger setup failed: {e}")
        

    try:

        # Process configuration parameters
        
        name = config.logger_name
        log_level = config.log_level
        logger_type = logger_type or config.logger_handler
        
        # Check if logger type is valid
        if logger_type not in VALID_LOGGER_HANDLERS:
            if emergency_logger:
                emergency_logger.warning(f"Logger type '{logger_type}' not supported. Using 'console' instead.")
            logger_type = "console"

        # Create the relevant logger
        if logger_type == "elasticsearch":
            # Safely check Elasticsearch connection settings
            es_user = settings.elasticsearch_user
            es_password = settings.elasticsearch_password
            es_host = settings.elasticsearch_host
            es_port = settings.elasticsearch_port
            batch_size = settings.batch_size

        
         # Test Elasticsearch connection
            try:
                from elasticsearch import Elasticsearch
                es = Elasticsearch([f"{es_host}:{es_port}"], timeout=5)
                if not es.ping():
                    if emergency_logger:
                        emergency_logger.warning("Elasticsearch connection test failed. Falling back to console logger.")
                    return DefaultLogger(name=name, tag=tag, log_level=log_level)
                    
                return ElasticsearchLogger(
                    name=name,
                    tag=tag,
                    es_hosts=[f"{es_host}:{es_port}"],
                    batch_size=batch_size,
                    log_level=log_level)
                
            except (ImportError, Exception) as e:
                if emergency_logger:
                    emergency_logger.error(f"Elasticsearch logger initialization failed: {e}")
                    return DefaultLogger(name=name, tag=tag, log_level=log_level)

        # Default/Console logger (fallback)
        else:
            return DefaultLogger(name=name, tag=tag, log_level=log_level)
        

    except Exception as e:
        # If everything fails
        if emergency_logger:
            emergency_logger.error(f"Logger creation failed: {e}")
            return emergency_logger
        else:
            # Simplest logger as last resort
            fallback_logger = logging.getLogger("fallback")
            fallback_logger.setLevel(logging.INFO)
            if not fallback_logger.handlers:
                handler = logging.StreamHandler()
                fallback_logger.addHandler(handler)
            fallback_logger.error(f"Critical error in logger creation: {e}")
            
            # Try DefaultLogger as last resort
            try:
                return DefaultLogger(name="fallback", log_level="INFO")
            except:
                # At this point, the best we can do is return a working logger
                class MinimalLogger(BaseDBLogger):
                    def __init__(self): 
                        self.logger = fallback_logger
                    def _setup_logger(self): return self.logger
                    def log_operation(self, message, level="info", **kwargs): self.logger.info(message)
                    def log_metadata(self, metadata): pass
                    def log_model_results(self, input_info, results, **kwargs): pass
                    def info(self, message, **kwargs): self.logger.info(message)
                    def warning(self, message, **kwargs): self.logger.warning(message)
                    def error(self, message, **kwargs): self.logger.error(message)
                    def debug(self, message, **kwargs): self.logger.debug(message)
                    def flush_all(self): pass
                
                return MinimalLogger()
            

logger = create_logger(settings.logger_type, settings)

# Create default application logger with fallback
# try:
#     logger = LoggerFactory._create_console_logger(log_level="INFO")
#     logger.info("Default logger initialized")
# except Exception as e:
#     print(f"Default logger creation error: {e}")
#     #  emergency_logger
#     logger = LoggerFactory._get_emergency_logger()

# # Backward compatibility functions
# def create_file_logger(name: str = None, tag: str = None, log_dir: str = None) -> FileLogger:
#     """
#     Backward compatibility function for file logger creation.

#     Parameters
#     ----------
#     name : str, optional
#         Logger name, by default None
#     tag : str, optional
#         Tag or version identifier, by default None
#     log_dir : str, optional
#         Directory for log files, by default None

#     Returns
#     -------
#     FileLogger
#         Configured file logger instance
#     """
#     return LoggerFactory._create_file_logger(name, tag, log_dir)

# def create_db_logger(name: str, tag: str = None, log_type: str = None, **kwargs) -> Union[BaseDBLogger, Dict[str, BaseDBLogger]]:
#     """Backward compatibility function for database logger creation."""
#     return LoggerFactory._create_db_logger(name, tag, log_type, **kwargs)


# if __name__ == "__main__":
#     """
#     Example usage of the logging system.
#     """
#     # from ssearch.logger import logger, create_db_logger

#     # Basic file logger usage
#     logger.info("Application started")
#     logger.warning("A situation that needs attention")
#     logger.error("An error occurred", exc_info=True)

#     # Creating and using MongoDB logger
#     mongo_logger = create_db_logger(
#         name="semantic_search", tag="v1.2", log_type="mongodb"
#     )

#     # Creating and using Elasticsearch logger
#     es_logger = create_db_logger(
#         name="semantic_search", tag="v1.2", log_type="elasticsearch"
#     )

#     # Creating composite logger (both MongoDB and Elasticsearch)
#     loggers = create_db_logger(name="semantic_search", tag="v1.2", log_type="composite")

#     # Adding additional context information
#     mongo_logger.with_context(user_id="123", request_id="abc-456", environment="production")

#     # Operational logs
#     mongo_logger.log_operation(
#         message="Search operation started", level="info", query="machine learning", filter_count=5
#     )

#     # Saving metadata
#     mongo_logger.log_metadata(
#         {
#             "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
#             "model_created_at": "2025-01-15T10:00:00Z",
#             "vector_dimensions": 768,
#             "preprocessing_steps": ["lowercase", "stopword_removal", "stemming"],
#         }
#     )

#     # Saving model results
#     mongo_logger.log_model_results(
#         input_info={"query": "what is machine learning", "filters": {"date": "2024-01-01", "category": "technology"}},
#         results={
#             "top_results": [
#                 {"id": "doc1", "score": 0.89, "title": "Machine Learning Fundamentals"},
#                 {"id": "doc2", "score": 0.78, "title": "AI and ML"},
#             ],
#             "execution_time_ms": 120,
#             "total_matches": 245,
#         },
#     )

#     # Using composite logger
#     mongo_logger = loggers["mongodb"]
#     es_logger = loggers["elasticsearch"]

#     mongo_logger.log_operation("Log saved to MongoDB")
#     es_logger.log_operation("Log saved to Elasticsearch")

#     # Force send all batches
#     mongo_logger.flush_all()
#     es_logger.flush_all()
