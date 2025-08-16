"""
Validation Service - API interface for Excel validation operations

This service provides a clean API interface to the validation functionality,
enabling CLI to validate Excel outputs without direct imports.
"""

import sys
import os
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import glob


class ValidationService:
    """Service class for validation operations."""
    
    def __init__(self):
        """Initialize validation service."""
        self.project_root = Path(__file__).parent.parent.parent
        self.validator_path = self.project_root / "excel_validator.py"
        self.output_dir = self.project_root / "output"
    
    def find_latest_excel_file(self, pattern: str = "Lines_*_Report_*.xlsx") -> Optional[str]:
        """
        Find the latest Excel file matching pattern.
        
        Args:
            pattern: Glob pattern to match files
            
        Returns:
            Path to latest Excel file or None
        """
        try:
            search_pattern = str(self.output_dir / pattern)
            files = glob.glob(search_pattern)
            
            if not files:
                return None
            
            # Sort by modification time, newest first
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            return files[0]
            
        except Exception as e:
            raise Exception(f"Failed to find Excel files: {e}")
    
    def find_excel_files_for_rows(self, row_numbers: List[int]) -> List[str]:
        """
        Find Excel files for specific row numbers.
        
        Args:
            row_numbers: List of row numbers to find files for
            
        Returns:
            List of matching Excel file paths
        """
        try:
            files = []
            
            for row in row_numbers:
                # Look for files containing this row number
                pattern = f"Lines_{row}_Report_*.xlsx"
                search_pattern = str(self.output_dir / pattern)
                matching_files = glob.glob(search_pattern)
                files.extend(matching_files)
            
            # Also look for range files
            if len(row_numbers) > 1:
                min_row = min(row_numbers)
                max_row = max(row_numbers)
                range_pattern = f"Lines_{min_row}-{max_row}_Report_*.xlsx"
                search_pattern = str(self.output_dir / range_pattern)
                range_files = glob.glob(search_pattern)
                files.extend(range_files)
            
            # Remove duplicates and sort by modification time
            unique_files = list(set(files))
            unique_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return unique_files
            
        except Exception as e:
            raise Exception(f"Failed to find Excel files for rows: {e}")
    
    def validate_excel_file(self, excel_file: str, threshold: float = 8.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate Excel file using excel_validator.py.
        
        Args:
            excel_file: Path to Excel file to validate
            threshold: Validation threshold (default 8.0)
            
        Returns:
            Tuple of (success, validation_results)
        """
        try:
            # Ensure file exists
            if not os.path.exists(excel_file):
                return False, {"error": f"Excel file not found: {excel_file}"}
            
            # Build validation command
            cmd = [sys.executable, str(self.validator_path), excel_file]
            
            if threshold != 8.0:
                cmd.extend(["--threshold", str(threshold)])
            
            # Run validation
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                # Parse validation output
                validation_results = self._parse_validation_output(result.stdout)
                return True, validation_results
            else:
                error_msg = result.stderr or result.stdout
                return False, {"error": f"Validation failed: {error_msg}"}
                
        except Exception as e:
            return False, {"error": f"Validation service error: {e}"}
    
    def _parse_validation_output(self, output: str) -> Dict[str, Any]:
        """Parse validation output into structured data."""
        results = {
            "validation_summary": "",
            "total_vendors": 0,
            "validated_vendors": 0,
            "validation_percentage": 0.0,
            "quality_metrics": {},
            "recommendations": [],
            "raw_output": output
        }
        
        lines = output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract key metrics
            if "Total vendors found:" in line:
                try:
                    results["total_vendors"] = int(line.split(":")[-1].strip())
                except:
                    pass
            
            elif "Vendors passing validation:" in line:
                try:
                    results["validated_vendors"] = int(line.split(":")[-1].strip())
                except:
                    pass
            
            elif "Validation percentage:" in line:
                try:
                    percentage_str = line.split(":")[-1].strip().replace("%", "")
                    results["validation_percentage"] = float(percentage_str)
                except:
                    pass
            
            elif "RECOMMENDATION:" in line:
                results["recommendations"].append(line.replace("RECOMMENDATION:", "").strip())
            
            # Store first meaningful line as summary
            if not results["validation_summary"] and ("validation" in line.lower() or "quality" in line.lower()):
                results["validation_summary"] = line
        
        return results
    
    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get history of recent validations.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of validation history records
        """
        try:
            # Find all Excel files in output directory
            pattern = str(self.output_dir / "Lines_*_Report_*.xlsx")
            files = glob.glob(pattern)
            
            # Sort by modification time, newest first
            files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            history = []
            for file_path in files[:limit]:
                file_info = {
                    "file_path": file_path,
                    "filename": os.path.basename(file_path),
                    "created_time": os.path.getctime(file_path),
                    "modified_time": os.path.getmtime(file_path),
                    "file_size": os.path.getsize(file_path),
                    "rows_processed": self._extract_rows_from_filename(os.path.basename(file_path))
                }
                history.append(file_info)
            
            return history
            
        except Exception as e:
            raise Exception(f"Failed to get validation history: {e}")
    
    def _extract_rows_from_filename(self, filename: str) -> str:
        """Extract row information from Excel filename."""
        import re
        # Pattern: Lines_126_Report_... or Lines_126-127_Report_...
        match = re.search(r'Lines_([0-9-]+)_Report_', filename)
        if match:
            return match.group(1)
        return "unknown"
    
    def check_validation_requirements(self) -> Dict[str, Any]:
        """
        Check if validation requirements are met.
        
        Returns:
            Dictionary with validation system status
        """
        try:
            status = {
                "validator_exists": os.path.exists(self.validator_path),
                "output_dir_exists": os.path.exists(self.output_dir),
                "output_dir_writable": os.access(self.output_dir, os.W_OK) if os.path.exists(self.output_dir) else False,
                "recent_files_count": 0,
                "validation_ready": False
            }
            
            # Count recent Excel files
            if status["output_dir_exists"]:
                pattern = str(self.output_dir / "Lines_*_Report_*.xlsx")
                files = glob.glob(pattern)
                status["recent_files_count"] = len(files)
            
            # Overall readiness
            status["validation_ready"] = (
                status["validator_exists"] and 
                status["output_dir_exists"] and 
                status["output_dir_writable"]
            )
            
            return status
            
        except Exception as e:
            return {
                "error": f"Failed to check validation requirements: {e}",
                "validation_ready": False
            }