1# 🔄 GitHub Workflow Guide

## 📁 **Available Scripts**

- `pull_latest.bat` - Get latest changes from GitHub
- `smart_commit.bat` - Commit with proper categorization  
- `switch_version.bat` - Switch between versions/branches
- `setup_on_new_computer.bat` - Instructions for new computers

## 🖥️ **Setting Up on New Computer**

1. **Clone Repository**:

   ```bash
   git clone https://github.com/iliyaruvinsky/universal-product-scraper-clean.git
   cd universal-product-scraper-clean
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Add Your Data**:
   - Copy `SOURCE.xlsx` to `data/` folder
   - Test with: `python production_scraper.py 126`

## 🔄 **Daily Workflow**

### **Before Starting Work** (Pull Latest Changes)

```bash
# Option 1: Use script
double-click pull_latest.bat

# Option 2: Manual
git pull origin main
```

### **After Making Changes** (Commit & Push)

```bash
# Use smart commit script (recommended)
double-click smart_commit.bat

# Choose commit type:
# 🐛 Bug Fix - Fixed validation threshold
# ✨ New Feature - Added vendor sorting
# 🔧 Improvement - Enhanced error handling  
# 📚 Documentation - Updated README
# 🧪 Testing - Added unit tests
# 🚀 Release - Major version (creates tag)
```

### **Working with Versions**

```bash
# View all versions
double-click switch_version.bat → Option 1

# Switch to specific version  
double-click switch_version.bat → Option 2

# Return to latest
double-click switch_version.bat → Option 3
```

## 🏷️ **Version Tagging Strategy**

### **Version Format**: `vX.Y-description`

- `v1.0-working-vendor-extraction` - Current working version
- `v1.1-enhanced-validation` - Next improvement
- `v1.2-performance-optimized` - Performance update
- `v2.0-major-rewrite` - Major changes

### **When to Create Versions**

- ✅ Working scraper with new feature
- ✅ Important bug fixes
- ✅ Before major changes (backup point)
- ✅ Before deploying to production

## 🌿 **Branching Strategy**

### **Main Branch**: `main`

- Always working, tested code
- Never commit broken code here

### **Feature Branches**

```bash
# Create feature branch
git checkout -b feature-excel-improvements
# Make changes, commit
git push origin feature-excel-improvements
# Merge when ready
```

### **Hotfix Branches**

```bash
# Quick fixes
git checkout -b hotfix-price-parsing
# Fix, test, merge
```

## 🚨 **Emergency Procedures**

### **Revert to Last Working Version**

```bash
# If current code is broken
git checkout v1.0-working-vendor-extraction
git checkout -b emergency-fix
# Fix the issue, then merge back
```

### **Recover Deleted Files**

```bash
# Show deleted files
git log --diff-filter=D --summary

# Recover specific file
git checkout HEAD~1 -- filename.py
```

## 👥 **Multi-Computer Sync**

### **Computer A** (Make changes)

```bash
# Make changes
double-click smart_commit.bat
```

### **Computer B** (Get changes)

```bash
# Get latest
double-click pull_latest.bat
# Continue working
```

## 📊 **Monitoring & History**

### **View History**

```bash
# Recent commits
git log --oneline -10

# Specific file history
git log --oneline production_scraper.py

# See what changed
git diff HEAD~1
```

### **Compare Versions**

```bash
# Compare two versions
git diff v1.0-working-vendor-extraction v1.1-enhanced-validation

# Compare specific file
git diff v1.0..v1.1 production_scraper.py
```

## 🎯 **Best Practices**

1. **Always pull before starting work**
2. **Commit frequently with clear messages**
3. **Test before committing**
4. **Create version tags for working states**
5. **Use branches for experimental features**
6. **Keep main branch always working**

## 🚀 **Quick Reference**

| Task | Script | Manual Command |
|------|--------|----------------|
| Get latest | `pull_latest.bat` | `git pull origin main` |
| Commit changes | `smart_commit.bat` | `git add . && git commit -m "message"` |
| Switch version | `switch_version.bat` | `git checkout v1.0` |
| Create version | Smart commit → Release | `git tag -a v1.1 -m "msg"` |
| New computer | `setup_on_new_computer.bat` | `git clone ...` |

🎯 **Repository**: <https://github.com/iliyaruvinsky/universal-product-scraper-clean>
