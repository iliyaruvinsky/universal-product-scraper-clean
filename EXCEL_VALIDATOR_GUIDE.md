# Excel Validator Module - Usage Guide

## Overview

The **Excel Validator** is a standalone quality control tool that analyzes scraped Excel outputs to validate product name accuracy. It compares original product names (Column B) with scraped product names (Column E) in the "פירוט" (Details) worksheet.

## Key Features

✅ **Smart Validation Using OPTION_1 Logic**
- Uses the same scoring system from the main scraper
- Applies Model Number Gate and Product Type Gate checks
- Recognizes INV ≡ INVERTER equivalence
- Scores on 0-10 scale with 8.0 default threshold (80%)

✅ **Hebrew-Aware Processing**
- Automatically removes Hebrew marketing text
- Translates common Hebrew manufacturer names (טורנדו → TORNADO)
- Focuses on English/numeric components for validation

✅ **Production-Ready Reporting**
- Clear summary with pass/fail percentages
- Detailed findings for products requiring review
- File output option for audit trails
- Exit codes for CI/CD integration

## Installation

The validator uses only standard Python libraries plus openpyxl (already installed):

```bash
# No additional installation needed if openpyxl is already installed
pip install openpyxl  # Only if not already installed
```

## Basic Usage

### Validate a Single Excel File

```bash
python excel_validator.py output/Lines_127_Report_20250814.xlsx
```

### With Custom Threshold

```bash
# Use 70% threshold instead of default 80%
python excel_validator.py --threshold 7.0 output/report.xlsx
```

### Save Report to File

```bash
python excel_validator.py --output validation_report.txt output/report.xlsx
```

### Verbose Mode

```bash
python excel_validator.py --verbose output/report.xlsx
```

## Understanding the Output

### Summary Section

```
SUMMARY
------------------------------
Total Products Validated: 100
✅ Valid: 94 products (94.0%)
⚠️  Review Needed: 6 products (6.0%)
```

### Products Requiring Review

Shows products that failed validation with detailed reasons:

```
⚠️  Row 234 - REVIEW NEEDED (Score: 6.5/10.0)
   Original: "ELECTRA ELCO SLIM A SQ INV 40/1P"
   Scraped:  "ELECTRA ELCO SLIM 40/1P מזגן עילי חסכוני"
   Cleaned:  "ELECTRA ELCO SLIM 40/1P"
   Issues:
     • Missing series components: INV
   Gates: Type Gate FAILED
```

## Validation Logic

### 1. Critical Gates (Pass/Fail)

**Model Number Gate**: Exact match required
- "45" ≠ "4" → FAIL
- "40/1P" = "40/1P" → PASS

**Product Type Gate**: INV/INVERTER consistency
- If original has INV, scraped must have INV or INVERTER
- Missing critical type indicator → FAIL

### 2. Component Scoring (0-10 scale)

- **Manufacturer**: 10% (0-1 points)
- **Model Name**: 40% (0-4 points)
- **Model Number**: 50% (0-5 points)
- **Extra Words**: Minor penalty (-0.1 per word)

### 3. Threshold Check

- Default: 8.0/10.0 (80%)
- Products below threshold marked for review
- Threshold adjustable via `--threshold` flag

## Common Issues Detected

### ✅ Correctly Validated

1. **INV vs INVERTER** - Recognized as equivalent
2. **Hebrew marketing text** - Ignored appropriately
3. **Word order variations** - Handled correctly
4. **Hyphenation differences** - Normalized properly

### ⚠️ Flagged for Review

1. **Model number mismatches** - Critical failure
2. **Missing INV/INVERTER** - Type gate failure
3. **Wrong manufacturer** - Major scoring penalty
4. **Corrupted model numbers** - "4 כ''ס" parsed as "4" instead of "45"

## Integration Examples

### Batch Processing Script

```python
import subprocess
from pathlib import Path

# Validate all Excel files in output directory
for excel_file in Path("output").glob("*.xlsx"):
    result = subprocess.run(
        ["python", "excel_validator.py", str(excel_file)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ {excel_file.name}: All products valid")
    elif result.returncode == 1:
        print(f"⚠️ {excel_file.name}: Some products need review")
    else:
        print(f"❌ {excel_file.name}: Validation error")
```

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Validate Excel Output
  run: |
    python excel_validator.py output/latest_report.xlsx --threshold 8.0
  continue-on-error: false  # Fail pipeline if validation fails
```

### Post-Scraping Hook

```python
# In main scraper
def post_scraping_validation(excel_path):
    """Run validation after Excel generation"""
    from excel_validator import ExcelValidator
    
    validator = ExcelValidator(threshold=8.0)
    if validator.validate_excel_file(excel_path):
        report = validator.generate_report()
        
        # Log validation results
        if validator.summary_stats['review'] > 0:
            logger.warning(f"Validation: {validator.summary_stats['review']} products need review")
        else:
            logger.info("Validation: All products passed")
```

## Exit Codes

- **0**: All products valid
- **1**: Some products need review
- **2**: Validation error (file not found, wrong format, etc.)

## Troubleshooting

### Unicode Errors on Windows

The script includes automatic Unicode handling for Windows:
```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### Missing פירוט Sheet

Ensure Excel file has the standard structure:
- Must contain "פירוט" (Details) worksheet
- Column B: Original product names
- Column E: Scraped product names

### Performance with Large Files

- Validates ~1000 products per second
- Uses read-only mode for memory efficiency
- Suitable for files with thousands of products

## Future Enhancements (Not Yet Implemented)

1. **Batch mode**: Process multiple Excel files at once
2. **Configuration file**: Store thresholds and settings
3. **CSV export**: Export validation results to CSV
4. **Auto-correction suggestions**: Propose fixes for common issues
5. **Integration with main scraper**: Automatic post-scraping validation

## Support

For issues or questions:
- Check validation_report.txt for detailed findings
- Adjust threshold if too strict/lenient
- Add manufacturer translations to hebrew_to_english dict
- Contact development team for systematic issues

---

**Version**: 1.0.0  
**Date**: August 14, 2025  
**Author**: Skywind Universal Scraper Team