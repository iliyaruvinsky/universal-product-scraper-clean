"""
Performance Optimizer for Universal Product Scraper
Based on heavy testing insights from July 29, 2025
"""

import psutil
import time
import gc
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger

logger = get_logger(__name__)

class PerformanceOptimizer:
    """Optimize scraper performance based on heavy testing insights."""
    
    def __init__(self):
        self.start_time = None
        self.products_processed = 0
        self.memory_threshold_mb = 2048  # 2GB threshold for restart
        self.vendor_timeout_count = 0
        self.performance_metrics = {
            'avg_time_per_product': 0,
            'memory_usage_mb': 0,
            'vendor_success_rate': 0,
            'timeout_frequency': 0
        }
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = datetime.now()
        logger.info("Performance monitoring started")
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Check current memory usage and recommend actions."""
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        self.performance_metrics['memory_usage_mb'] = memory_mb
        
        status = {
            'memory_mb': round(memory_mb, 1),
            'threshold_mb': self.memory_threshold_mb,
            'needs_restart': memory_mb > self.memory_threshold_mb,
            'recommendation': self._get_memory_recommendation(memory_mb)
        }
        
        if status['needs_restart']:
            logger.warning(f"Memory usage {memory_mb:.1f}MB exceeds threshold {self.memory_threshold_mb}MB")
        
        return status
    
    def _get_memory_recommendation(self, memory_mb: float) -> str:
        """Get memory usage recommendation."""
        if memory_mb > self.memory_threshold_mb:
            return "RESTART_BROWSER"
        elif memory_mb > self.memory_threshold_mb * 0.8:
            return "CHUNK_PROCESSING"
        elif memory_mb > self.memory_threshold_mb * 0.6:
            return "MONITOR_CLOSELY"
        else:
            return "OPTIMAL"
    
    def record_product_completion(self, processing_time_seconds: float, vendor_count: int, timeout_count: int):
        """Record product processing completion."""
        self.products_processed += 1
        self.vendor_timeout_count += timeout_count
        
        # Calculate average time per product
        if self.start_time:
            total_time = (datetime.now() - self.start_time).total_seconds()
            self.performance_metrics['avg_time_per_product'] = total_time / self.products_processed
        
        # Calculate vendor success rate
        total_vendors = vendor_count
        successful_vendors = vendor_count - timeout_count
        if total_vendors > 0:
            success_rate = (successful_vendors / total_vendors) * 100
            # Running average of success rate
            if self.performance_metrics['vendor_success_rate'] == 0:
                self.performance_metrics['vendor_success_rate'] = success_rate
            else:
                self.performance_metrics['vendor_success_rate'] = (
                    self.performance_metrics['vendor_success_rate'] * 0.8 + success_rate * 0.2
                )
        
        logger.info(f"Product {self.products_processed} completed in {processing_time_seconds:.1f}s")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        memory_status = self.check_memory_usage()
        
        summary = {
            'products_processed': self.products_processed,
            'avg_time_per_product_min': round(self.performance_metrics['avg_time_per_product'] / 60, 1),
            'memory_usage_mb': memory_status['memory_mb'],
            'vendor_success_rate': round(self.performance_metrics['vendor_success_rate'], 1),
            'total_timeouts': self.vendor_timeout_count,
            'memory_recommendation': memory_status['recommendation'],
            'needs_restart': memory_status['needs_restart']
        }
        
        return summary
    
    def should_chunk_processing(self, remaining_products: int) -> Dict[str, Any]:
        """Determine if processing should be chunked for optimal performance."""
        memory_status = self.check_memory_usage()
        avg_time_min = self.performance_metrics['avg_time_per_product'] / 60 if self.performance_metrics['avg_time_per_product'] > 0 else 5
        
        estimated_time_hours = (remaining_products * avg_time_min) / 60
        
        recommendation = {
            'should_chunk': False,
            'chunk_size': remaining_products,
            'reason': 'No chunking needed',
            'estimated_time_hours': round(estimated_time_hours, 1)
        }
        
        # Chunking recommendations based on heavy testing insights
        if memory_status['memory_mb'] > 1500:  # High memory usage
            recommendation.update({
                'should_chunk': True,
                'chunk_size': 20,
                'reason': 'High memory usage detected'
            })
        elif remaining_products > 50:  # Large batch
            recommendation.update({
                'should_chunk': True,
                'chunk_size': 30,
                'reason': 'Large batch optimization'
            })
        elif estimated_time_hours > 8:  # Very long processing
            recommendation.update({
                'should_chunk': True,
                'chunk_size': 25,
                'reason': 'Extended processing time'
            })
        elif self.performance_metrics['vendor_success_rate'] < 80:  # Low success rate
            recommendation.update({
                'should_chunk': True,
                'chunk_size': 15,
                'reason': 'Low vendor success rate'
            })
        
        return recommendation
    
    def optimize_browser_settings(self) -> Dict[str, Any]:
        """Get optimized browser settings based on current performance."""
        memory_status = self.check_memory_usage()
        
        # Base optimization settings from heavy testing
        optimizations = {
            'memory_optimization': [
                '--disable-dev-shm-usage',  # Overcome limited resource problems
                '--disable-gpu',             # Disable GPU for headless
                '--no-sandbox',              # Bypass OS security model
                '--disable-web-security',    # Reduce security overhead
                '--disable-features=VizDisplayCompositor'
            ],
            'performance_optimization': [
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--max_old_space_size=2048'  # Limit Node.js memory
            ]
        }
        
        # Additional optimizations based on current state
        if memory_status['memory_mb'] > 1000:
            optimizations['aggressive_memory'] = [
                '--memory-pressure-off',
                '--disable-background-media-suspend'
            ]
        
        return optimizations
    
    def force_cleanup(self):
        """Force cleanup of resources."""
        gc.collect()  # Force garbage collection
        logger.info("Forced resource cleanup completed")


class BatchProcessor:
    """Smart batch processor based on heavy testing insights."""
    
    def __init__(self, optimizer: PerformanceOptimizer):
        self.optimizer = optimizer
        self.chunk_cool_down_seconds = 60  # Cool-down between chunks
    
    def should_restart_browser(self, products_in_chunk: int) -> bool:
        """Determine if browser should be restarted before next chunk."""
        memory_status = self.optimizer.check_memory_usage()
        
        # Restart conditions from heavy testing
        if memory_status['needs_restart']:
            return True
        if products_in_chunk > 30:  # Large chunks need fresh browser
            return True
        if self.optimizer.vendor_timeout_count > 10:  # Too many timeouts
            return True
        
        return False
    
    def get_optimal_chunk_size(self, total_products: int) -> int:
        """Get optimal chunk size based on current performance."""
        recommendation = self.optimizer.should_chunk_processing(total_products)
        return recommendation['chunk_size']
    
    def execute_cool_down(self):
        """Execute cool-down period between chunks."""
        logger.info(f"Cool-down period: {self.chunk_cool_down_seconds} seconds")
        time.sleep(self.chunk_cool_down_seconds)
        self.optimizer.force_cleanup() 