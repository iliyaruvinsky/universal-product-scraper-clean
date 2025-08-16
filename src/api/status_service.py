"""
Status Service - API interface for system status and health monitoring

This service provides a clean API interface to system status information,
enabling CLI to monitor system health and performance.
"""

import sys
import os
import subprocess
import psutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import glob


class StatusService:
    """Service class for system status operations."""
    
    def __init__(self):
        """Initialize status service."""
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "output"
        self.logs_dir = self.project_root / "logs"
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            System status information
        """
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "system_health": self._get_system_health(),
                "scraper_status": self._get_scraper_status(),
                "file_system_status": self._get_file_system_status(),
                "recent_activity": self._get_recent_activity(),
                "performance_metrics": self._get_performance_metrics()
            }
            
            return status
            
        except Exception as e:
            return {"error": f"Failed to get system status: {e}"}
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get basic system health metrics."""
        try:
            health = {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage(str(self.project_root)).percent,
                "python_version": sys.version,
                "platform": sys.platform
            }
            
            # Health assessment
            if health["cpu_usage"] > 80:
                health["cpu_status"] = "HIGH"
            elif health["cpu_usage"] > 60:
                health["cpu_status"] = "MEDIUM"
            else:
                health["cpu_status"] = "NORMAL"
            
            if health["memory_usage"] > 85:
                health["memory_status"] = "HIGH"
            elif health["memory_usage"] > 70:
                health["memory_status"] = "MEDIUM"
            else:
                health["memory_status"] = "NORMAL"
            
            return health
            
        except Exception as e:
            return {"error": f"Failed to get system health: {e}"}
    
    def _get_scraper_status(self) -> Dict[str, Any]:
        """Get scraper-specific status information."""
        try:
            status = {
                "production_scraper_exists": os.path.exists(self.project_root / "production_scraper.py"),
                "excel_validator_exists": os.path.exists(self.project_root / "excel_validator.py"),
                "source_file_exists": os.path.exists(self.project_root / "data" / "SOURCE.xlsx"),
                "chrome_available": self._check_chrome_availability(),
                "dependencies_status": self._check_dependencies()
            }
            
            # Overall scraper readiness
            status["scraper_ready"] = all([
                status["production_scraper_exists"],
                status["excel_validator_exists"],
                status["source_file_exists"],
                status["chrome_available"]
            ])
            
            return status
            
        except Exception as e:
            return {"error": f"Failed to get scraper status: {e}"}
    
    def _check_chrome_availability(self) -> bool:
        """Check if Chrome/Chromium is available."""
        try:
            # Try to import webdriver manager
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Check if Chrome executable can be found
            import subprocess
            result = subprocess.run(
                ["where", "chrome"] if sys.platform == "win32" else ["which", "google-chrome"],
                capture_output=True, text=True
            )
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check if required Python dependencies are available."""
        dependencies = {
            "selenium": False,
            "openpyxl": False,
            "webdriver_manager": False,
            "psutil": False
        }
        
        for dep in dependencies:
            try:
                __import__(dep)
                dependencies[dep] = True
            except ImportError:
                dependencies[dep] = False
        
        return dependencies
    
    def _get_file_system_status(self) -> Dict[str, Any]:
        """Get file system status."""
        try:
            status = {
                "project_root_exists": os.path.exists(self.project_root),
                "output_dir_exists": os.path.exists(self.output_dir),
                "output_dir_writable": os.access(self.output_dir, os.W_OK) if os.path.exists(self.output_dir) else False,
                "logs_dir_exists": os.path.exists(self.logs_dir),
                "recent_output_files": 0,
                "total_output_size": 0
            }
            
            # Count output files
            if status["output_dir_exists"]:
                pattern = str(self.output_dir / "*.xlsx")
                files = glob.glob(pattern)
                status["recent_output_files"] = len(files)
                
                # Calculate total size
                total_size = 0
                for file_path in files:
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
                status["total_output_size"] = total_size
            
            return status
            
        except Exception as e:
            return {"error": f"Failed to get file system status: {e}"}
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Get recent activity information."""
        try:
            activity = {
                "last_24_hours": 0,
                "last_week": 0,
                "last_month": 0,
                "latest_file": None,
                "latest_file_time": None
            }
            
            if not os.path.exists(self.output_dir):
                return activity
            
            now = datetime.now()
            pattern = str(self.output_dir / "Lines_*_Report_*.xlsx")
            files = glob.glob(pattern)
            
            latest_time = 0
            latest_file = None
            
            for file_path in files:
                try:
                    file_time = os.path.getctime(file_path)
                    file_datetime = datetime.fromtimestamp(file_time)
                    
                    # Track latest file
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = os.path.basename(file_path)
                    
                    # Count by time periods
                    if now - file_datetime <= timedelta(hours=24):
                        activity["last_24_hours"] += 1
                    if now - file_datetime <= timedelta(days=7):
                        activity["last_week"] += 1
                    if now - file_datetime <= timedelta(days=30):
                        activity["last_month"] += 1
                        
                except:
                    continue
            
            if latest_file:
                activity["latest_file"] = latest_file
                activity["latest_file_time"] = datetime.fromtimestamp(latest_time).isoformat()
            
            return activity
            
        except Exception as e:
            return {"error": f"Failed to get recent activity: {e}"}
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from recent operations."""
        try:
            metrics = {
                "average_processing_time": 0,
                "average_vendors_per_product": 0,
                "success_rate": 0,
                "performance_trend": "unknown"
            }
            
            # This would ideally read from log files or a performance database
            # For now, return placeholder metrics
            metrics["note"] = "Performance metrics would be implemented with logging system"
            
            return metrics
            
        except Exception as e:
            return {"error": f"Failed to get performance metrics: {e}"}
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive health check.
        
        Returns:
            Health check results with recommendations
        """
        try:
            health_check = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "UNKNOWN",
                "checks": {},
                "recommendations": [],
                "critical_issues": []
            }
            
            # Run individual checks
            checks = {
                "system_resources": self._check_system_resources(),
                "scraper_dependencies": self._check_scraper_dependencies(),
                "file_permissions": self._check_file_permissions(),
                "recent_operations": self._check_recent_operations()
            }
            
            health_check["checks"] = checks
            
            # Determine overall status
            critical_failures = sum(1 for check in checks.values() if check.get("status") == "CRITICAL")
            warnings = sum(1 for check in checks.values() if check.get("status") == "WARNING")
            
            if critical_failures > 0:
                health_check["overall_status"] = "CRITICAL"
            elif warnings > 0:
                health_check["overall_status"] = "WARNING"
            else:
                health_check["overall_status"] = "HEALTHY"
            
            # Collect recommendations
            for check_name, check_result in checks.items():
                if "recommendations" in check_result:
                    health_check["recommendations"].extend(check_result["recommendations"])
                if "critical_issues" in check_result:
                    health_check["critical_issues"].extend(check_result["critical_issues"])
            
            return health_check
            
        except Exception as e:
            return {"error": f"Failed to run health check: {e}"}
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability."""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage(str(self.project_root)).percent
            
            check = {"status": "OK", "recommendations": [], "critical_issues": []}
            
            if cpu_usage > 90:
                check["status"] = "CRITICAL"
                check["critical_issues"].append(f"CPU usage very high: {cpu_usage}%")
            elif cpu_usage > 75:
                check["status"] = "WARNING"
                check["recommendations"].append(f"CPU usage elevated: {cpu_usage}%")
            
            if memory_usage > 90:
                check["status"] = "CRITICAL"
                check["critical_issues"].append(f"Memory usage very high: {memory_usage}%")
            elif memory_usage > 80:
                check["status"] = "WARNING"
                check["recommendations"].append(f"Memory usage elevated: {memory_usage}%")
            
            if disk_usage > 95:
                check["status"] = "CRITICAL"
                check["critical_issues"].append(f"Disk usage very high: {disk_usage}%")
            elif disk_usage > 85:
                check["status"] = "WARNING"
                check["recommendations"].append(f"Disk usage elevated: {disk_usage}%")
            
            check["metrics"] = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "disk_usage": disk_usage
            }
            
            return check
            
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
    
    def _check_scraper_dependencies(self) -> Dict[str, Any]:
        """Check scraper dependencies."""
        dependencies = self._check_dependencies()
        chrome_available = self._check_chrome_availability()
        
        check = {"status": "OK", "recommendations": [], "critical_issues": []}
        
        missing_deps = [dep for dep, available in dependencies.items() if not available]
        if missing_deps:
            check["status"] = "CRITICAL"
            check["critical_issues"].append(f"Missing dependencies: {', '.join(missing_deps)}")
        
        if not chrome_available:
            check["status"] = "CRITICAL"
            check["critical_issues"].append("Chrome/Chromium not available")
        
        check["dependencies"] = dependencies
        check["chrome_available"] = chrome_available
        
        return check
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions."""
        check = {"status": "OK", "recommendations": [], "critical_issues": []}
        
        if not os.access(self.project_root, os.R_OK):
            check["status"] = "CRITICAL"
            check["critical_issues"].append("Cannot read project root directory")
        
        if not os.access(self.output_dir, os.W_OK):
            check["status"] = "CRITICAL"
            check["critical_issues"].append("Cannot write to output directory")
        
        return check
    
    def _check_recent_operations(self) -> Dict[str, Any]:
        """Check recent operations for issues."""
        check = {"status": "OK", "recommendations": [], "critical_issues": []}
        
        activity = self._get_recent_activity()
        
        if activity["last_24_hours"] == 0 and activity["last_week"] > 0:
            check["recommendations"].append("No recent activity in last 24 hours")
        
        return check