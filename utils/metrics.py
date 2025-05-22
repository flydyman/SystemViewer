import time
import psutil
import logging
import os
from collections import deque
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects system metrics including CPU, RAM, and disk usage.
    Maintains historical data for graphing.
    """
    # Maximum history size (approximately 5 minutes at 5-second intervals)
    MAX_HISTORY_SIZE = 60
    
    def __init__(self):
        """Initialize the metrics collector with empty history containers."""
        # CPU metrics history
        self.cpu_percent_history = deque(maxlen=self.MAX_HISTORY_SIZE)
        self.cpu_load_history = deque(maxlen=self.MAX_HISTORY_SIZE)
        
        # Memory metrics history
        self.memory_history = deque(maxlen=self.MAX_HISTORY_SIZE)
        
        # Disk metrics history - dictionary of mount points to histories
        self.disk_history = {}
        
        # Timestamps for metrics
        self.timestamps = deque(maxlen=self.MAX_HISTORY_SIZE)
        
        # Initial scan of disk partitions to set up history queues
        self._init_disk_history()
        
        logger.info("MetricsCollector initialized")
    
    def _init_disk_history(self) -> None:
        """Initialize disk history containers for all partitions."""
        try:
            partitions = psutil.disk_partitions(all=False)
            for partition in partitions:
                self.disk_history[partition.mountpoint] = deque(maxlen=self.MAX_HISTORY_SIZE)
        except Exception as e:
            logger.error(f"Error initializing disk history: {str(e)}")
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect all current system metrics and update history.
        Returns a dictionary with current metrics.
        """
        current_time = datetime.now()
        self.timestamps.append(current_time.strftime("%H:%M:%S"))
        
        metrics = {
            "timestamp": current_time.isoformat(),
            "cpu": self._collect_cpu_metrics(),
            "memory": self._collect_memory_metrics(),
            "disk": self._collect_disk_metrics()
        }
        
        return metrics
    
    def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect CPU usage percentage and load averages."""
        cpu_metrics = {}
        
        try:
            # CPU percentage (across all cores)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_percent_history.append(cpu_percent)
            cpu_metrics["percent"] = cpu_percent
            
            # CPU load averages (1, 5, 15 minutes)
            load_avg = os.getloadavg()
            self.cpu_load_history.append(load_avg)
            cpu_metrics["load_avg"] = {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2]
            }
            
            # Per-core CPU usage
            cpu_metrics["per_cpu_percent"] = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # CPU count
            cpu_metrics["count"] = {
                "physical": psutil.cpu_count(logical=False) or 1,
                "logical": psutil.cpu_count(logical=True) or 1
            }
            
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {str(e)}")
            cpu_metrics["error"] = str(e)
        
        return cpu_metrics
    
    def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect RAM usage statistics."""
        memory_metrics = {}
        
        try:
            # Virtual memory
            virtual_memory = psutil.virtual_memory()
            memory_data = {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "free": virtual_memory.free,
                "percent": virtual_memory.percent
            }
            self.memory_history.append(memory_data)
            memory_metrics["virtual"] = memory_data
            
            # Swap memory
            swap = psutil.swap_memory()
            memory_metrics["swap"] = {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent
            }
            
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {str(e)}")
            memory_metrics["error"] = str(e)
        
        return memory_metrics
    
    def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect disk usage for all mounted partitions."""
        disk_metrics = {"partitions": {}}
        
        try:
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    partition_data = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                    
                    # Initialize history for this partition if doesn't exist
                    if partition.mountpoint not in self.disk_history:
                        self.disk_history[partition.mountpoint] = deque(maxlen=self.MAX_HISTORY_SIZE)
                    
                    # Add to history
                    self.disk_history[partition.mountpoint].append(partition_data)
                    
                    # Add to current metrics
                    disk_metrics["partitions"][partition.mountpoint] = partition_data
                    
                except PermissionError:
                    logger.warning(f"Permission denied when accessing {partition.mountpoint}")
                except Exception as e:
                    logger.error(f"Error collecting metrics for partition {partition.mountpoint}: {str(e)}")
            
            # IO counters
            io_counters = psutil.disk_io_counters(perdisk=True)
            disk_metrics["io_counters"] = io_counters
            
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {str(e)}")
            disk_metrics["error"] = str(e)
        
        return disk_metrics
    
    def get_history(self) -> Dict[str, Any]:
        """Get all historical metrics for graphing."""
        return {
            "timestamps": list(self.timestamps),
            "cpu": {
                "percent": list(self.cpu_percent_history),
                "load_avg": list(self.cpu_load_history)
            },
            "memory": list(self.memory_history),
            "disk": {mountpoint: list(history) for mountpoint, history in self.disk_history.items()}
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the most recent metrics.
        Returns a simplified view of current system state.
        """
        if not self.cpu_percent_history or not self.memory_history:
            # No data collected yet
            return {"status": "No data collected yet"}
        
        try:
            # Get the most recent values
            cpu_percent = self.cpu_percent_history[-1] if self.cpu_percent_history else None
            memory = self.memory_history[-1] if self.memory_history else None
            
            # Simplify disk data - just get usage percentages
            disk_usage = {}
            for mountpoint, history in self.disk_history.items():
                if history:
                    disk_usage[mountpoint] = history[-1]["percent"]
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory["percent"] if memory else None,
                "disk_usage": disk_usage
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {str(e)}")
            return {"status": f"Error: {str(e)}"}

