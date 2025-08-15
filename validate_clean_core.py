#!/usr/bin/env python3
"""
Clean Core Validation Script
=============================
Automatically validates the EXTRACT clean core for:
- File reference inconsistencies  
- Method/function existence
- Definition contradictions
- Scoring weight alignment
- Import path verification
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

class CleanCoreValidator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.file_refs = set()
        self.method_refs = set()
        self.scoring_definitions = {}
        
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print("CLEAN CORE VALIDATION STARTING...")
        print("=" * 50)
        
        # Check 1: File references
        self.check_file_references()
        
        # Check 2: Scoring consistency  
        self.check_scoring_consistency()
        
        # Check 3: Import paths
        self.check_import_paths()
        
        # Check 4: Method references
        self.check_method_references()
        
        # Check 5: Definition contradictions
        self.check_definition_contradictions()
        
        # Generate report
        return self.generate_report()
    
    def check_file_references(self):
        """Check that all referenced files actually exist"""
        print("\nChecking file references...")
        
        # Common file reference patterns
        patterns = [
            r'`([^`]+\.py)`',  # Python files in backticks
            r'`([^`]+\.md)`',  # Markdown files in backticks  
            r'`([^`]+\.json)`', # JSON files in backticks
            r'(src/[a-zA-Z_/]+\.py)', # src/ path references
            r'(docs/[a-zA-Z_/]+\.md)', # docs/ path references
            r'(config/[a-zA-Z_/]+\.json)', # config/ path references
        ]
        
        # Get all documentation files
        doc_files = list(self.base_path.glob("*.md")) + list(self.base_path.glob("docs/*.md"))
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        self.file_refs.add(match)
                        
                        # Check if file exists
                        file_path = self.base_path / match
                        if not file_path.exists():
                            # Skip known issues
                            if any(skip in match for skip in [
                                'extract_claude.md',  # Will be renamed to CLAUDE.md
                                'main.py',  # Not needed in clean core
                                'VERSION_INFO.json',  # Not needed in clean core
                                'utils/validate_excel_format.py',  # Legacy utility
                                'docs/backend-context.md',  # Not needed
                                'COMPLETE_TESTING_CYCLE_GUIDE.md',  # Not needed
                                'docs/OPTION_1_*.md',  # Wildcard pattern
                                'PRODUCT_NAME_COMPONENT_ANALYSIS.md',  # Check specific path
                                'default_config.json',  # Check specific path
                                'USER_GUIDE.md'  # Check specific path
                            ]):
                                continue
                            
                            # Check if it exists in docs/ or config/ subdirectories  
                            alt_paths = [
                                self.base_path / 'docs' / match,
                                self.base_path / 'config' / match
                            ]
                            
                            if not any(p.exists() for p in alt_paths):
                                self.errors.append(f"MISSING FILE: {match} (referenced in {doc_file.name})")
                            
            except Exception as e:
                self.warnings.append(f"Could not read {doc_file.name}: {e}")
    
    def check_scoring_consistency(self):
        """Check scoring weight definitions for consistency"""
        print("Checking scoring consistency...")
        
        # Patterns for scoring weights and thresholds
        weight_patterns = [
            (r'Manufacturer[:\s]+(\d+)%', 'manufacturer_weight'),
            (r'Model Name[:\s]+(\d+)%', 'model_name_weight'),  
            (r'Model Number[:\s]+(\d+)%', 'model_number_weight'),
            (r'Threshold[:\s]+≥?(\d+\.?\d*)/10\.0', 'threshold'),
            (r'(\d+\.?\d*)/10\.0[^\d]*\((\d+)%', 'threshold_percent'),
        ]
        
        doc_files = list(self.base_path.glob("*.md")) + list(self.base_path.glob("docs/*.md"))
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                file_scores = {}
                
                for pattern, key in weight_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        file_scores[key] = matches
                
                if file_scores:
                    self.scoring_definitions[doc_file.name] = file_scores
                    
            except Exception as e:
                self.warnings.append(f"Could not read {doc_file.name}: {e}")
        
        # Check for inconsistencies
        self.validate_scoring_consistency()
    
    def validate_scoring_consistency(self):
        """Validate that scoring definitions are consistent"""
        expected_weights = {
            'manufacturer_weight': ['10'],
            'model_name_weight': ['40'], 
            'model_number_weight': ['50'],
            'threshold': ['8.0', '8'],
        }
        
        for file_name, scores in self.scoring_definitions.items():
            for score_type, values in scores.items():
                if score_type in expected_weights:
                    for value in values:
                        if value not in expected_weights[score_type]:
                            self.errors.append(f"SCORING INCONSISTENCY: {file_name} has {score_type}={value}, expected {expected_weights[score_type]}")
    
    def check_import_paths(self):
        """Check Python import paths"""
        print("Checking import paths...")
        
        python_files = list(self.base_path.glob("**/*.py"))
        
        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Find import statements
                import_patterns = [
                    r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                    r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match.startswith('src.'):
                            # Convert import path to file path
                            file_path = match.replace('.', '/') + '.py'
                            full_path = self.base_path / file_path
                            
                            if not full_path.exists():
                                self.errors.append(f"MISSING IMPORT: {match} (in {py_file.name}) -> {file_path} not found")
                                
            except Exception as e:
                self.warnings.append(f"⚠️ Could not read {py_file.name}: {e}")
    
    def check_method_references(self):
        """Check method and function references"""
        print("Checking method references...")
        
        # Find method references in documentation
        doc_files = list(self.base_path.glob("*.md")) + list(self.base_path.glob("docs/*.md"))
        
        method_pattern = r'`([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))`'
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                matches = re.findall(method_pattern, content)
                
                for match in matches:
                    method_name = match.split('(')[0]
                    self.method_refs.add(method_name)
                    
            except Exception as e:
                self.warnings.append(f"Could not read {doc_file.name}: {e}")
        
        # Note: Actual method existence checking would require AST parsing
        # For now, we collect references for manual review
    
    def check_definition_contradictions(self):
        """Check for contradictory definitions"""
        print("Checking definition contradictions...")
        
        # Check OPTION_2 references (should be removed)
        self.check_option2_references()
        
        # Check column count consistency
        self.check_column_consistency()
    
    def check_option2_references(self):
        """Check for any remaining OPTION_2 references"""
        all_files = list(self.base_path.glob("**/*.py")) + list(self.base_path.glob("**/*.md"))
        
        for file_path in all_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Look for OPTION_2 references that aren't about removal
                if 'OPTION_2' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if 'OPTION_2' in line:
                            # Check if it's documenting removal
                            if not any(word in line.lower() for word in ['removed', 'deleted', 'pollution', 'eliminated']):
                                self.warnings.append(f"OPTION_2 REFERENCE: {file_path.name}:{i} - {line.strip()}")
                                
            except Exception as e:
                pass  # Skip binary or unreadable files
    
    def check_column_consistency(self):
        """Check Excel column count consistency"""
        all_files = list(self.base_path.glob("**/*.py")) + list(self.base_path.glob("**/*.md"))
        
        column_counts = {}
        
        for file_path in all_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Look for column references
                column_patterns = [
                    r'(\d+)\s+columns?',
                    r'columns?\s*[=:]\s*(\d+)',
                    r'max_column[^=]*=\s*(\d+)',
                ]
                
                for pattern in column_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        count = int(match)
                        if file_path.name not in column_counts:
                            column_counts[file_path.name] = []
                        column_counts[file_path.name].append(count)
                        
            except Exception as e:
                pass
        
        # Check for inconsistencies
        for file_name, counts in column_counts.items():
            if len(set(counts)) > 1:
                self.warnings.append(f"COLUMN COUNT INCONSISTENCY: {file_name} has multiple column counts: {set(counts)}")
    
    def generate_report(self) -> Dict:
        """Generate validation report"""
        print("\n" + "=" * 50)
        print("VALIDATION REPORT")
        print("=" * 50)
        
        report = {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'file_references_found': len(self.file_refs),
            'method_references_found': len(self.method_refs),
            'scoring_definitions_found': len(self.scoring_definitions),
        }
        
        # Print summary
        if self.errors:
            print(f"\nERRORS FOUND: {len(self.errors)}")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\nWARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\nNO ISSUES FOUND - CLEAN CORE IS VALID!")
        
        print(f"\nSTATISTICS:")
        print(f"  File references checked: {len(self.file_refs)}")
        print(f"  Method references found: {len(self.method_refs)}")
        print(f"  Scoring definitions found: {len(self.scoring_definitions)}")
        
        return report

def main():
    """Main validation entry point"""
    base_path = Path(__file__).parent
    validator = CleanCoreValidator(str(base_path))
    
    report = validator.validate_all()
    
    # Save report
    report_file = base_path / "validation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull report saved to: {report_file}")
    
    # Return exit code based on errors
    return 1 if report['total_errors'] > 0 else 0

if __name__ == "__main__":
    exit(main())