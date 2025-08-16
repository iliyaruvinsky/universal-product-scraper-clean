---
alwaysApply: true
priority: HIGHEST
---

# Universal Product Scraper - Clean Core Claude Instructions

**Project**: Fully purified clean core (48 essential files, 99% reduction + pollution removal)  
**Status**: Ready for production testing - scoring fixed, OPTION_2 pollution removed  
**Context**: Minimal focused context - pure implemented functionality only  
**Updated**: August 16, 2025 - Testing procedures protocol imperative added, TESTING_PROCEDURES.md alignment enforced  

---

## 🚨 CRITICAL OPERATING PRINCIPLES

### **1. MANDATORY: Product Nomenclature Intelligence**

**Priority**: HIGHEST | **Always Apply**: true

**ALWAYS CONSULT** `docs/PRODUCT_NAME_COMPONENT_ANALYSIS.md` for:
- **WD ≠ WV ≠ WH**: DIFFERENT products, not equivalent variations
- **INV ≡ INVERTER**: Technology term equivalence (100% equal)
- **Model Number Priority**: 50% weight in scoring (highest priority)
- **Smart Matching**: Apply equivalence rules before rigid comparison

**NEW SCORING WEIGHTS (August 2025):**
```
• Manufacturer: 10% (0-1.0 points) - REDUCED
• Model Name: 40% (0-4.0 points) - DECREASED  
• Model Number: 50% (0-5.0 points) - INCREASED
• Threshold: ≥8.0/10.0 (80% minimum) - INCREASED
```

**❌ VIOLATIONS:**
- Treating WD/WV/WH as equivalent
- Penalizing INV vs INVERTER differences
- Using old scoring weights (15%/65%/20%)

**THIS NOMENCLATURE INTELLIGENCE OVERRIDES RIGID MATCHING** ⚠️

---

### **2. MANDATORY: No Task Progression Without Explicit User Consent**

**Priority**: HIGHEST | **Always Apply**: true

**STRICT REQUIREMENTS:**
1. **ALWAYS ASK:** "What would you like me to do next?"
2. **WAIT FOR EXPLICIT APPROVAL** before:
   - Running any tests
   - Moving to next steps
   - Implementing changes
   - ANY other activity

3. **EXPLICIT CONSENT MEANS:**
   - User says "proceed", "go ahead", "continue"
   - Specific instructions to move forward
   - NOT assumptions about user intent

**❌ VIOLATIONS:**
- Starting tests without permission
- Continuing workflows automatically
- Making assumptions about next steps

**THIS RULE OVERRIDES ALL OTHER CONSIDERATIONS** ⚠️

---

### **2.1. MANDATORY: Testing Procedures Protocol Adherence**

**Priority**: HIGHEST | **Always Apply**: true

**ABSOLUTE REQUIREMENTS:**
1. **ALWAYS FOLLOW** `prompts/TESTING_PROCEDURES.md` protocol during ANY testing cycle
2. **NEVER DEVIATE** from established testing procedures without explicit user permission
3. **STRICT PROTOCOL COMPLIANCE:**
   - Use exact command syntax specified in TESTING_PROCEDURES.md
   - Follow sequential execution protocol (no skipping phases)
   - Mandatory Excel validation and presentation
   - Proper timeout handling (minimum 10 minutes patience)

**INHERITANCE RULE:**
- **CONTINUOUSLY UPDATE** `prompts/TESTING_PROCEDURES.md` to maintain alignment with current processes
- **ELIMINATE REDUNDANCIES** and keep procedures clean and contemporary
- **ENSURE 100% ALIGNMENT** between documented procedures and actual implementation

**❌ VIOLATIONS:**
- Using ad-hoc testing approaches
- Skipping mandatory validation steps
- Deviating from established command syntax
- Operating without documented procedures

**TESTING_PROCEDURES.md IS THE AUTHORITATIVE TESTING GUIDE** ⚠️

---

### **3. MANDATORY: Excel File Presentation After Test Cycles**

**Priority**: HIGHEST | **Always Apply**: true

**STRICT REQUIREMENTS:**
1. **ALWAYS PRESENT EXCEL FILE** after ANY complete scraping operation
2. **EXCEL IS THE DELIVERABLE** - not validation commentary
3. **MANDATORY FORMAT:**
   - File location and name
   - Vendor count and price ranges
   - Key data from both worksheets (פירוט + סיכום)
   - First few vendor entries as evidence

**TIMING:** Present Excel AFTER validation confirms output is correct

**ENFORCEMENT:** Every test cycle MUST end with:
```
📊 **FINAL DELIVERABLE - EXCEL FILE:**
[Excel file path and contents presentation]
```

**THE EXCEL FILE IS THE TEST RESULT - ALWAYS PRESENT IT** ⚠️

---

### **4. MANDATORY: Sequential Execution Blocking**

**Priority**: HIGHEST | **Always Apply**: true

**STRICT BLOCKING DEPENDENCIES:**
1. **NO VALIDATION** without successful scraper completion for exact requested lines
2. **NO PRESENTATION** without successful validation of actual output file  
3. **NO SUBSTITUTION** of different Excel files or data sources
4. **NO ASSUMPTIONS** about file locations or alternative approaches

**ERROR HANDLING PROTOCOL:**
- **Scraper timeouts**: Ask user before giving up (minimum 10 minutes patience)
- **Failed prerequisites**: STOP and ask "What would you like me to do next?"
- **Missing files**: Report failure, do NOT improvise with different data
- **Todo accuracy**: Mark items as "failed" not "completed" when they fail

**THIS BLOCKING PROTOCOL OVERRIDES ALL CONVENIENCE SHORTCUTS** ⚠️

---

### **5. MANDATORY: Use Production Entry Points Only**

**Priority**: HIGHEST | **Always Apply**: true

**CLEAN CORE TESTING RULES:**
1. **USE:** `production_scraper.py --rows X` for all testing
2. **USE:** `excel_validator.py` for post-validation  
3. **NEVER:** Create new test scripts or debug files
4. **PRESERVE:** Existing working patterns exactly

**TESTING COMMANDS:**
```bash
# Single product test
python production_scraper.py --rows 126

# Range test  
python production_scraper.py --rows 126-127

# Validate Excel output
python excel_validator.py output/Lines_126_Report_*.xlsx
```

**❌ FORBIDDEN:**
- Creating test_*.py files
- Modifying working scraper logic
- Reinventing existing patterns

**REUSE WORKING PATTERNS - NEVER REINVENT** ⚠️

---

### **6. MANDATORY: Efficient Session Startup**

**Priority**: HIGHEST | **Always Apply**: true

**❌ NEVER start sessions with:**
- Directory access verification
- "Let me check what directories I have access to"
- Setup verification routines
- Access capability explanations

**✅ ALWAYS start with:**
- Direct engagement with user's request
- Immediate productive work
- "What would you like me to work on?"

**EXCEPTIONS:** Only mention access issues when operations actually fail

**PREVENT TOKEN WASTE ON SETUP VERIFICATION** ⚠️

---

## 📁 **CLEAN CORE STRUCTURE REFERENCE**

### **PRIMARY ENTRY POINTS:**
- `production_scraper.py` - Main scraper (USE FOR ALL TESTING)
- `excel_validator.py` - Validation pipeline (MANDATORY after scraping)
- `natural_cli.py` - User interface

### **CORE MODULES:**
- `src/scraper/zap_scraper.py` - ZAP scraping engine
- `src/excel/source_reader.py` - SOURCE.xlsx reading (starts row 2)
- `src/excel/target_writer.py` - Excel generation
- `src/validation/scoring_engine.py` - Updated scoring system

### **CRITICAL DOCUMENTATION:**
- `docs/OPTION_1_DETAILED_FLOW.md` - 12-phase methodology
- `docs/PRODUCT_NAME_COMPONENT_ANALYSIS.md` - Nomenclature rules
- `LLM_HANDOVER.md` - Complete context understanding

---

## 🎯 **CLEAN CORE OPERATING GUIDELINES**

### **SOURCE DATA RULES:**
- SOURCE.xlsx starts at **row 2** (row 1 is headers)
- Read-only - never modify SOURCE files
- Use SourceExcelReader for all source operations

### **EXCEL PROCESSING:**
- TARGET files: Hebrew headers, dual worksheets (פירוט + סיכום) 
- Validation: MANDATORY excel_validator.py post-processing
- Format: Proper ₪ currency and RTL formatting

### **12-PHASE OPTION_1 WORKFLOW:**
1. Initial Search (hyphen-first SUB-OPTION 1A/1B)
2. Model ID Extraction
3. **Dual Critical Gates** (Model Number + Product Type)
4. **Component Scoring** (8.0/10.0 threshold)
5. Select Best & Navigate
6. Extract Product Listings
7. Critical Validation
8. Vendor Button Discovery
9. Vendor Processing (≥70% success rate)
10. Statistics & Excel Generation
11. Final Success
12. **Excel Validation** (MANDATORY)

**Key Decision Points:** Gates passed (Phase 3) → Score ≥8.0 (Phase 4) → Success

---

## ⚠️ **CRITICAL WARNINGS**

### **DO NOT:**
- ❌ Change scoring weights without updating ALL references
- ❌ Create new test scripts when production_scraper.py exists
- ❌ Skip excel_validator.py validation
- ❌ Use old scoring weights (15%/65%/20%)
- ❌ Progress to next tasks without user consent
- ❌ **VALIDATE different Excel files when specific lines were requested**
- ❌ **MARK todo items as "completed" when they actually failed**
- ❌ **PROCEED without blocking dependencies being satisfied**

### **ALWAYS:**
- ✅ Use production_scraper.py for testing
- ✅ Present Excel file contents after test cycles
- ✅ Consult PRODUCT_NAME_COMPONENT_ANALYSIS.md for matching
- ✅ Ask "What would you like me to do next?"
- ✅ Apply new scoring weights (10%/40%/50%)
- ✅ **WAIT for actual scraper completion before validation**
- ✅ **VALIDATE only exact files from requested lines**
- ✅ **MAINTAIN strict sequential blocking: Scraping → Validation → Presentation**

---

## 🚀 **SUCCESS CRITERIA**

The clean core succeeds when:
- ✅ Uses production entry points for all operations
- ✅ Applies updated scoring weights correctly
- ✅ Presents Excel deliverables after test cycles
- ✅ Waits for user consent before task progression
- ✅ Maintains nomenclature intelligence rules

---

**CLEAN CORE CLAUDE INSTRUCTIONS COMPLETE** - Focused for maximum efficiency 🎯

**Remember**: This is a MINIMAL FOCUSED CONTEXT (99% reduction). Every rule here is essential for proper clean core operation.