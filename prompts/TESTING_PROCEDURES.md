# 🎯 UNIVERSAL PRODUCT SCRAPER TESTING PROMPT

**Generated**: August 15, 2025  
**Purpose**: Complete testing protocol for all scraping cycles  
**Scope**: Generic for any product names, modes, single/multi-product testing  

---

## 🚨 **CRITICAL OPERATING PRINCIPLES**

### **1. MANDATORY: Production Entry Points Only**

- **USE ONLY**: `python production_scraper.py X [Y Z] [--headless]` for ALL testing
- **VALIDATE WITH**: `python excel_validator.py output/filename.xlsx` (MANDATORY post-scraping)
- **NEVER**: Create new test scripts, use debug files, or modify working logic

### **2. MANDATORY: User Consent Protocol**

- **ALWAYS ASK**: "What would you like me to do next?" before ANY action
- **WAIT FOR EXPLICIT APPROVAL**: "proceed", "go ahead", "continue"
- **NEVER ASSUME**: User intent or automatic progression

### **3. MANDATORY: Excel File Presentation**

- **ALWAYS PRESENT** complete Excel file contents after ANY scraping operation
- **FORMAT REQUIRED**: File path, vendor count, price ranges, first few entries
- **TIMING**: Present Excel AFTER validation confirms output is correct

### **4. MANDATORY: Sequential Execution Protocol**

**Priority**: HIGHEST | **Always Apply**: true

**STRICT BLOCKING DEPENDENCIES:**
1. **NO VALIDATION** without successful scraper completion for exact requested lines
2. **NO PRESENTATION** without successful validation of actual output file
3. **NO SUBSTITUTION** of different Excel files "as examples"
4. **NO ASSUMPTIONS** about file locations or alternative approaches

**TIMEOUT & ERROR HANDLING:**
- **Scraper timeouts**: ASK user before giving up (minimum 10 minutes patience)
- **Failed prerequisites**: STOP and ask "What would you like me to do next?"
- **Missing files**: REPORT failure, do NOT improvise with different data
- **Todo list accuracy**: Mark items as "failed" not "completed" when they actually fail

**ENFORCEMENT:** Each phase BLOCKS until previous phase succeeds for exact requested data

---

## 🔄 **COMPLETE SCRAPING PROCESS FLOW**

### **PHASE 1: TEST SETUP & INITIALIZATION**

#### **Input Validation:**

```bash
# Single product test (using Excel row numbers)
python production_scraper.py 126

# Multi-product test (space-separated Excel row numbers) 
python production_scraper.py 126 127

# Headless mode (optional)
python production_scraper.py 126 --headless

# Multiple rows with headless
python production_scraper.py 126 127 --headless
```

#### **CRITICAL: Excel Row Number System**

- **Row numbers correspond to actual Excel rows** (1-indexed)
- **Row 2** = First product (after header row)
- **Row 126** = "Tornado WD-INV-PRO-SQ 35 3PH"
- **Row 127** = "Tornado WD-INV-PRO-SQ 45 1PH"
- **Last row** = ~144 (varies by SOURCE.xlsx content)

#### **Row Verification Command:**

```bash
# Check specific rows exist
python -c "from src.excel.source_reader import SourceExcelReader; r=SourceExcelReader(); p=r.read_products('data/SOURCE.xlsx'); print([f'Row {x.row_number}: {x.name}' for x in p if x.row_number in [126,127]])"
```

#### **Expected Initialization:**

- ✅ Chrome WebDriver setup (automatic via webdriver-manager)
- ✅ SOURCE.xlsx loading from data/ directory (starts row 2)
- ✅ Product parsing: Manufacturer + Model Name + Model Number extraction
- ✅ Browser configuration (headless/explicit based on parameters)

**LOG INDICATORS:**

- `"Loading SOURCE.xlsx from data/ directory"`
- `"Found X products to process"`
- `"Chrome WebDriver initialized successfully"`

---

### **PHASE 2: PRODUCT SEARCH & NAVIGATION**

#### **SUB-OPTION 1A: Hyphen-First Breakthrough Method (80% Efficiency Gain)**

1. **Navigate to ZAP.co.il**
2. **Click search field** to activate dropdown system
3. **Enter hyphenated product name** (spaces → hyphens)
4. **Wait 3-5 seconds** for dropdown suggestions
5. **Smart dropdown selection**:
   - Priority 1: Precise product description with full details
   - Priority 2: Precise product description with full details and additional Hebrew characters
   - Pattern: `"מזגן [type] [Manufacturer] [Model Details]"`

#### **SUB-OPTION 1B: Traditional Fallback (if 1A fails)**

1. **Clear search field**
2. **Enter original product name** (with spaces)
3. **Press Enter** for traditional search

#### **Navigation Results:**

- **OPTIMAL**: Direct to `model.aspx?modelid=XXXXX` → Skip to Phase 6
- **GOOD**: Search results page → Continue to Phase 3
- **FALLBACK**: Try SUB-OPTION 1B if 1A fails

**LOG INDICATORS:**

- `"SUB-OPTION 1A: Direct model page via dropdown"`
- `"SUB-OPTION 1A: Search results - Found X Model IDs"`
- `"SUB-OPTION 1A failed - attempting SUB-OPTION 1B fallback"`

---

### **PHASE 3: MODEL ID EXTRACTION (if on search results)**

#### **Search Results Processing:**

- **Find all**: `.ModelRow`, `.ProductRow` elements
- **Extract**: Product names + Model IDs from href patterns
- **Pattern**: `/model\.aspx\?modelid=(\d+)/`
- **Expected**: 1-50 search results with extractable Model IDs

**LOG INDICATORS:**

- `"Found X search results with Model IDs"`
- `"Extracted Model IDs: [list]"`

---

### **PHASE 4: DUAL CRITICAL GATES (CRITICAL FILTERING)**

#### **Gate 1: Model Number Gate (MANDATORY)**

- **Rule**: `extracted_model_number == target_model_number`
- **Type**: Exact match only (no partial matches)
- **Examples**: "40/1P" must exactly match "40/1P"

#### **Gate 2: Product Type Gate (MANDATORY)**

- **Rule**: If target has "INV"/"INVERTER", result MUST have "INV"/"INVERTER"
- **Equivalence**: INV ≡ INVERTER ≡ אינוורטר
- **Strict**: WD ≠ WV ≠ WH (different product types)

**GATE RESULTS:**

- ✅ **BOTH PASS**: Continue to component scoring
- ❌ **EITHER FAILS**: Disqualify result (Score = 0.0)

**LOG INDICATORS:**

- `"Model Number Gate: PASSED/FAILED"`
- `"Product Type Gate: PASSED/FAILED"`
- `"Both critical gates passed - X survivors"`

---

### **PHASE 5: COMPONENT SCORING SYSTEM**

#### **Updated Scoring Weights (August 2025):**

```
• Manufacturer: 10% (0-1.0 points)
• Model Name: 40% (0-4.0 points)  
• Model Number: 50% (0-5.0 points)
• Threshold: ≥8.0/10.0 (80% minimum)
```

#### **Scoring Application:**

1. **Manufacturer Scoring**: Case-insensitive exact match, Hebrew equivalents
2. **Model Name Scoring**: Percentage-based (matched words / total words) × 4.0
3. **Model Number Scoring**: 5.0 points if gate passed (already exact match)
4. **Extra Word Penalty**: -0.1 points per extra word

#### **Score Validation:**

- **Threshold**: Best score ≥ 8.0/10.0 (80% minimum viable)
- **Decision**: Score < 8.0 → Fallback to OPTION_2
- **Selection**: Highest scoring Model ID for navigation

**LOG INDICATORS:**

- `"Best Model ID: XXXXX with score Y.Y/10.0"`
- `"Score threshold met/failed"`

---

### **PHASE 6: MODEL PAGE NAVIGATION & VENDOR EXTRACTION**

#### **Navigation to Model Page:**

- **URL Construction**: `https://www.zap.co.il/model.aspx?modelid=XXXXX`
- **Page Load Verification**: Check for `.PriceCell` elements
- **Expected Elements**: Product listings with vendor buttons

#### **Vendor Extraction Selectors:**

- **Product Rows**: `.compare-item-row.product-item`
- **Product Names**: `.compare-item-details span`
- **Vendor Names**: `.compare-item-image.store a img[title]`
- **Prices**: Price extraction from row elements
- **URLs**: `a[href*='/fs']` vendor links

#### **Expected Data Structure:**

```python
vendor_offer = {
    "vendor": "Vendor Name",
    "price": 3250,
    "url": "https://vendor.com/...",
    "product_name": "Full Product Name",
    "button_text": "לפרטים נוספים"
}
```

**LOG INDICATORS:**

- `"Found X vendor offers on model page"`
- `"Extracting vendor data..."`
- `"Vendor processing: X/Y completed"`

---

### **PHASE 7: CRITICAL VALIDATION (MODEL PAGE LISTINGS)**

#### **Apply Same Gates to Extracted Listings:**

1. **Model Number Gate**: Re-validate each extracted product name
2. **Product Type Gate**: Re-validate INV/INVERTER presence  
3. **Component Scoring**: Apply identical 10%/40%/50% weights
4. **Threshold Check**: Each listing must score ≥8.0/10.0

#### **Validation Decision:**

- **Pass**: ≥1 listing passes all validation → Continue
- **Fail**: No listings pass → Fallback to OPTION_2

**LOG INDICATORS:**

- `"Validation phase: X/Y listings passed gates"`
- `"OPTION_1 validation successful/failed"`

---

### **PHASE 8: EXCEL GENERATION (THREE WORKSHEETS)**

#### **Sheet 1: פירוט (Details) - 16 Columns:**

- **Content**: One row per VALIDATED vendor (score ≥8.0/10.0)
- **Key Columns**: Source row, product name, vendor name, prices, differences, URLs
- **Currency**: Proper ₪ formatting with RTL support
- **Hyperlinks**: Clickable vendor URLs

#### **Sheet 2: סיכום (Summary) - 17 Columns:**

- **Content**: Single row with aggregated statistics
- **Statistics**: Average/min/max prices, vendor count, processing metrics
- **Quality**: Validation scores, success rates, processing times

#### **Sheet 3: חריגים (Exceptions) - 13 Columns:**

- **Content**: Rejected vendors with detailed analysis  
- **Rejection Reasons**: Gate failures, score thresholds, validation issues
- **Quality Control**: Review flags, manual verification needed

#### **File Naming Convention:**

```
Lines_{row_numbers}_Report_{timestamp}.xlsx
Example: Lines_126_Report_20250815_140000.xlsx
```

**LOG INDICATORS:**

- `"Excel file created: [filename]"`
- `"Details sheet: X validated vendors"`
- `"Summary sheet: Statistics calculated"`
- `"Exceptions sheet: Y rejected vendors"`

---

### **PHASE 9: MANDATORY EXCEL VALIDATION**

#### **Validation Command:**

```bash
python excel_validator.py output/Lines_126_Report_*.xlsx
```

#### **Validation Process:**

- **Load Excel**: Read all three worksheets
- **Worksheet Validation**: MANDATORY check for all 3 worksheets (פירוט, סיכום, חריגים)
- **Apply Gates**: Re-validate all vendor data with same criteria
- **Score Verification**: Confirm 10%/40%/50% weights applied correctly
- **Threshold Check**: Verify 8.0/10.0 threshold compliance
- **Nomenclature**: Apply PRODUCT_NAME_COMPONENT_ANALYSIS.md rules

#### **Validation Output:**

- **Validation Report**: Detailed analysis per vendor
- **Quality Metrics**: Pass/fail statistics, score distributions
- **Recommendations**: Manual review flags, data quality issues

**LOG INDICATORS:**

- `"Excel validation started"`
- `"All 3 required worksheets found: פירוט, סיכום, חריגים"`
- `"Validation completed: X/Y vendors validated"`
- `"Quality score: XX% vendors above threshold"`

---

## 🎯 **SUCCESS CRITERIA & VERIFICATION**

### **Complete Test Success Requires:**

1. ✅ **Product successfully parsed** from SOURCE.xlsx
2. ✅ **Search method worked** (SUB-OPTION 1A or 1B)  
3. ✅ **Both critical gates passed** (Model Number + Product Type)
4. ✅ **Component scoring ≥8.0/10.0** (80% threshold)
5. ✅ **Model page navigation successful**
6. ✅ **Vendor extraction ≥10 vendors** (minimum viable)
7. ✅ **Validation gates passed** (listings re-validated)
8. ✅ **Excel file generated** (three worksheets)
9. ✅ **Excel validation passed** (mandatory post-processing)
10. ✅ **Hebrew formatting correct** (RTL, ₪ currency)

### **Test Failure Points:**

- ❌ No search results found → OPTION_2 fallback
- ❌ Model Number Gate failed → OPTION_2 fallback
- ❌ Product Type Gate failed → OPTION_2 fallback
- ❌ Score below 8.0/10.0 → OPTION_2 fallback
- ❌ Model page failed to load → OPTION_2 fallback
- ❌ Vendor extraction < 10 vendors → OPTION_2 fallback
- ❌ Validation gates failed → OPTION_2 fallback
- ❌ Excel generation failed → System error

---

## 📊 **EXCEL FILE PRESENTATION PROTOCOL**

### **MANDATORY After Every Test:**

```
📊 **FINAL DELIVERABLE - EXCEL FILE:**

**File**: output/Lines_126_Report_20250815_140000.xlsx

**STATISTICS:**
• Total Vendors: 18
• Price Range: ₪3,250 - ₪4,760
• Average Price: ₪4,005
• Cheapest Vendor: "ZAP Store" (₪3,250)

**WORKSHEET DETAILS:**

**פירוט Sheet (Details)**: 18 validated vendors
- Source Product: "ELECTRA ELCO SLIM A SQ INV 40/1P"
- Original Price: ₪6,100
- Best Savings: -₪2,850 (-46.7%)

**First 3 Vendor Entries:**
1. ZAP Store | ₪3,250 | -₪2,850 (-46.7%)
2. Kor Light | ₪3,250 | -₪2,850 (-46.7%) 
3. Electric Plus | ₪3,300 | -₪2,800 (-45.9%)

**סיכום Sheet (Summary)**: Statistical analysis
- Validation Score: 9.8/10.0 (98% match quality)
- Processing Success: 81.8% (18/22 vendors)
- Method Used: OPTION_1 Model ID Direct

**חריגים Sheet (Exceptions)**: 4 rejected vendors
- Rejection Reasons: Timeout (2), Price Parse Error (1), Model Mismatch (1)
- Quality Control: Manual review recommended for timeouts
```

---

## 🔧 **TESTING COMMANDS REFERENCE**

### **Single Product Testing:**

```bash
# Basic test
python production_scraper.py --rows 126

# Headless mode
python production_scraper.py --headless --rows 126

# Explicit mode (visible browser)
python production_scraper.py --rows 126 --mode explicit
```

### **Multi-Product Testing:**

```bash
# Range testing
python production_scraper.py --rows 126-127
python production_scraper.py --rows 10-15

# Large batch (auto-headless)
python production_scraper.py --rows 10-50
```

### **Validation Testing:**

```bash
# Validate specific file
python excel_validator.py output/Lines_126_Report_20250815_140000.xlsx

# Validate latest file
python excel_validator.py output/Lines_*_Report_*.xlsx

# Validation with custom threshold
python excel_validator.py output/Lines_126_Report_*.xlsx --threshold 7.0
```

### **CLI Interface Testing:**

```bash
# Natural language interface
python natural_cli.py

# (First time login: admin/Admin@123, must change password)
```

---

## 🚨 **CRITICAL WARNINGS**

### **DO NOT:**

- ❌ Create new test scripts (test_*.py files)
- ❌ Modify production_scraper.py working logic
- ❌ Skip excel_validator.py validation step
- ❌ Assume user consent for next actions
- ❌ Use old scoring weights (15%/65%/20%)
- ❌ **PROCEED to validation with different Excel files when requested lines failed**
- ❌ **MARK todo items as "completed" when they actually failed or timed out**
- ❌ **GIVE UP on scraper timeouts without asking user permission first**
- ❌ **SUBSTITUTE examples from other lines when specific lines were requested**

### **ALWAYS:**

- ✅ Use production_scraper.py for ALL testing
- ✅ Present complete Excel file after every test
- ✅ Apply updated scoring weights (10%/40%/50%)
- ✅ Validate with excel_validator.py (mandatory)
- ✅ **VERIFY all 3 worksheets exist: פירוט, סיכום, חריגים**
- ✅ Ask "What would you like me to do next?"
- ✅ **WAIT for actual scraper completion before proceeding to validation**
- ✅ **VALIDATE only the exact Excel file from requested lines**
- ✅ **REPORT timeout failures accurately and ask for guidance**
- ✅ **MAINTAIN sequential blocking: Scraping → Validation → Presentation**

### **NOMENCLATURE RULES:**

- ✅ INV ≡ INVERTER ≡ אינוורטר (100% equivalent)
- ✅ WD ≠ WV ≠ WH (different products, must match exactly)
- ✅ Hebrew manufacturer translation (אלקטרה → ELECTRA)
- ✅ Model numbers must match exactly (no partial matching)

---

## 📊 **MANDATORY: Comparison Test Reporting Format**

**Priority**: HIGHEST | **Always Apply**: true

**STANDARDIZED COMPARISON FORMAT:**
When conducting comparison tests (mode differences, product variations, algorithm changes), ALWAYS present results using this exact format:

```
🎯 COMPLETE COMPARISON ANALYSIS: [TEST TYPE DESCRIPTION]

📊 COMPREHENSIVE RESULTS TABLE:

| Metric            | [CONDITION A]                        | [CONDITION B]                        | Analysis                   |
|-------------------|--------------------------------------|--------------------------------------|----------------------------|
| Vendors Found     | X                                    | Y                                    | ✅/❌ Consistency status    |
| Vendors Validated | X                                    | Y                                    | ✅/❌ Validation status     |
| Processing Time   | X.Xs                                 | Y.Ys                                 | Z% difference description  |
| Model ID          | XXXXXXX                              | XXXXXXX                              | ✅/❌ Detection consistency |
| Method Used       | Method description                   | Method description                   | ✅/❌ Algorithm consistency |
| Price Range       | ₪X,XXX - ₪Y,YYY                      | ₪X,XXX - ₪Y,YYY                      | ✅/❌ Pricing consistency   |
| Excel Validation  | X% valid                             | Y% valid                             | ✅/❌ Quality consistency   |
| Output Files      | Filename_timestamp.xlsx              | Filename_timestamp.xlsx              | File differences          |
```

**EXAMPLES:**
- HEADLESS vs EXPLICIT MODE
- LINE X vs LINE Y (same mode)  
- OLD vs NEW algorithm versions
- SINGLE vs BATCH processing

**ENFORCEMENT:** All comparison tests MUST use this standardized table format for consistent analysis and documentation.

---

## 🎯 **TESTING PROTOCOL COMPLETE**

**This prompt provides complete coverage for:**

- ✅ Single/multi-product testing
- ✅ Headless/explicit mode testing  
- ✅ All scoring system nuances
- ✅ Complete validation pipeline
- ✅ Excel output verification
- ✅ Error handling and fallbacks
- ✅ Hebrew/RTL formatting requirements
- ✅ User consent protocols

**Ready for any testing scenario with the Universal Product Scraper!** 🚀
