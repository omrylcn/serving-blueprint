from prometheus_client import Counter, Histogram, Gauge

class StyleTransferMetrics:
    """Centralized metrics collection for style transfer operations"""
    
    def __init__(self):
        # Task processing metrics
        self.task_counter = Counter(
            name="style_transfer_tasks_total",
            documentation="Total number of style transfer tasks initiated",
            labelnames=["model_name", "model_mode"]
        )
        
        self.task_status_counter = Counter(
            name="style_transfer_task_status_total",
            documentation="Total number of style transfer tasks by status",
            labelnames=["model_name", "status"]  # 'completed', 'failed', 'processing'
        )
        
        self.task_processing_time = Histogram(
            name="style_transfer_processing_seconds",
            documentation="Time spent processing style transfer tasks",
            labelnames=["model_name", "model_mode"],
            buckets=(1, 5, 10, 30, 60, 120, 300, 600)
        )
        
        # Error tracking
        self.error_counter = Counter(
            name="style_transfer_errors_total",
            documentation="Total number of errors in style transfer processing",
            labelnames=["model_name", "error_type"]  # 'validation', 'processing', 'system'
        )
        
        # System metrics
        self.active_tasks = Gauge(
            name="style_transfer_active_tasks",
            documentation="Number of currently active style transfer tasks",
            labelnames=["model_name"]
        )

# Create a singleton instance
style_transfer_metrics = StyleTransferMetrics()