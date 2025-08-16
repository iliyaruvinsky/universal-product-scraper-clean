# 🔄 GIT RESTORATION GUIDE - Universal Product Scraper

**Generated**: August 16, 2025  
**Purpose**: Guide Claude to help restore application to specific commit points  
**Usage**: Ask Claude to "read prompts/GIT_RESTORATION_GUIDE.md" when restoration needed  

---

## 🚨 **USER RESTORATION REQUEST PROTOCOL**

When you want to restore the application to a previous state, simply ask Claude:

### **Basic Restoration Request:**

```
"Read prompts/GIT_RESTORATION_GUIDE.md and help me restore to [COMMIT_TYPE]"
```

### **Request Types:**

#### **Option A: Restore to Specific Functionality**

```
"Restore to the last working state before CLI changes"
"Restore to clean core without authentication"  
"Restore to basic scraper without Excel enhancements"
```

#### **Option B: Restore to Specific Commit Hash**

```
"Restore to commit 5cc192d"
"Restore to commit 72949f8"
```

#### **Option C: Show Available Restore Points**

```
"Show me available restore points with descriptions"
"What are the major checkpoint commits I can restore to?"
```

---

## 🤖 **CLAUDE RESPONSE PROTOCOL**

When this guide is read, Claude MUST follow this exact protocol:

### **STEP 1: SAFETY CHECK**

```bash
# Always check current status first
git status
git log --oneline -10
```

**⚠️ CRITICAL**: If there are uncommitted changes, STOP and ask:

```
"You have uncommitted changes. Do you want to:
1. Save current work as a new commit before restoring
2. Discard current changes and restore  
3. Cancel restoration"
```

### **STEP 2: SHOW AVAILABLE RESTORE POINTS**

Present this table with ACTUAL commit data:

```
🎯 AVAILABLE RESTORE POINTS:

| Commit | Date | Description | What You Get Back |
|--------|------|-------------|------------------|
| [HASH] | [DATE] | [DESCRIPTION] | [FUNCTIONALITY] |
| [HASH] | [DATE] | [DESCRIPTION] | [FUNCTIONALITY] |
```

**Key Restore Points to ALWAYS Show:**

- **LATEST CHECKPOINT**: Most recent stable state
- **PRE-CLI ARCHITECTURE**: Before CLI modifications
- **CLEAN CORE COMPLETION**: Core functionality complete  
- **SCORING ENHANCEMENT**: Updated scoring system
- **AUTHENTICATION ADDITION**: Before auth system

### **STEP 3: RESTORATION RECOMMENDATION**

Based on user request, recommend:

```
🎯 RECOMMENDED RESTORE POINT:

Commit: [HASH] - [DESCRIPTION]
Date: [DATE]
Why: [EXPLANATION]

This will restore:
✅ [FEATURE 1]
✅ [FEATURE 2] 
✅ [FEATURE 3]

You will lose:
❌ [FEATURE 1]
❌ [FEATURE 2]
```

### **STEP 4: EXECUTE RESTORATION** (Only after user confirmation)

**Safe Restoration Commands:**

```bash
# Method 1: Hard reset (DESTRUCTIVE - use only if confirmed)
git reset --hard [COMMIT_HASH]

# Method 2: Create new branch from restore point (SAFE)
git checkout -b restored-[DATE] [COMMIT_HASH]

# Method 3: Merge restore point (SAFEST)
git checkout -b merge-restore [COMMIT_HASH]
git checkout main
git merge merge-restore
```

**Always use Method 2 (new branch) unless user specifically requests destructive reset**

### **STEP 5: VERIFY RESTORATION**

After restoration, ALWAYS verify:

```bash
# Check restoration was successful
git log --oneline -5
git status

# Test critical functionality
python production_scraper.py --rows 126
```

**Report to user:**

```
✅ RESTORATION COMPLETE

Current state: [COMMIT_HASH] - [DESCRIPTION]
Branch: [BRANCH_NAME]
Functionality verified: [TEST_RESULTS]

Next steps:
1. Test your key workflows
2. If satisfied, continue development
3. If not satisfied, we can restore to different point
```

---

## 🎯 **MAJOR CHECKPOINT REFERENCE**

### **Expected Checkpoint Categories:**

#### **🚀 CORE FUNCTIONALITY MILESTONES**

- Clean Core Implementation (48 files)
- Scraping Engine Completion
- Excel Generation System
- Validation Pipeline

#### **🔧 ENHANCEMENT MILESTONES**  

- Scoring System Updates
- Authentication System
- CLI Architecture
- Performance Optimizations

#### **📊 TESTING MILESTONES**

- Algorithm Validation Complete
- Multi-product Testing Success  
- Mode Comparison Validation
- State Verification Systems

#### **🏗️ ARCHITECTURE MILESTONES**

- Module Separation
- API Layer Implementation
- Interface Enhancements
- Integration Completions

---

## 🚨 **CRITICAL SAFETY RULES**

### **BEFORE ANY RESTORATION:**

1. **ALWAYS** check for uncommitted changes
2. **ALWAYS** show available restore points with descriptions
3. **ALWAYS** recommend safest restoration method
4. **NEVER** perform destructive operations without explicit confirmation
5. **ALWAYS** create backup branch before destructive operations

### **CONFIRMATION REQUIRED FOR:**

- `git reset --hard` (destructive)
- Discarding uncommitted changes
- Overwriting current work

### **NO CONFIRMATION NEEDED FOR:**

- Showing commit history
- Creating new branches
- Read-only operations

---

## 📝 **USER EXAMPLES**

### **Example 1: Basic Restoration Request**

**User**: "Read prompts/GIT_RESTORATION_GUIDE.md and restore to clean core"

**Claude Response**:

1. Check current status
2. Show restore point table
3. Recommend specific clean core commit
4. Wait for user confirmation
5. Execute safe restoration (new branch)
6. Verify and report

### **Example 2: Emergency Rollback**

**User**: "Something is broken, restore to last working state"

**Claude Response**:

1. Identify last checkpoint commit
2. Show what will be lost/gained
3. Recommend restoration method
4. Execute after confirmation
5. Test critical functionality

### **Example 3: Exploration Restoration**

**User**: "Show me what commits I can restore to"

**Claude Response**:

1. Generate comprehensive restore point table
2. Explain each checkpoint's significance
3. Recommend based on current development phase
4. Wait for specific restoration request

---

## 🎯 **RESTORATION GUIDE COMPLETE**

**This guide ensures:**

- ✅ Safe restoration procedures
- ✅ Clear communication with user
- ✅ No accidental data loss
- ✅ Comprehensive restore point information
- ✅ Verification of restoration success

**Ready to help restore Universal Product Scraper to any checkpoint!** 🚀

---

**⚠️ IMPORTANT**: This guide should be read by Claude whenever restoration is needed. It provides complete protocol for safe application state management.
