# Universal Product Scraper v1.2 - Setup Guide

**Development Environment with Enterprise Authentication**  
**Release Date**: August 2, 2025  
**Professional Price Comparison Tool for ZAP.co.il**

---

## 🚀 Quick Setup (Python Environment)

### **Step 1: Verify Requirements**

- ✅ Windows 10 or Windows 11
- ✅ Python 3.11+ installed
- ✅ 2GB RAM minimum
- ✅ 500MB free disk space
- ✅ Internet connection
- ✅ Chrome browser (automatically managed)

### **Step 2: Install Dependencies**

```bash
# Navigate to project directory
cd "path/to/Skywind_Uni_Prod_Scrap_Protected"

# Install required packages
pip install -r requirements.txt
```

### **Step 3: Launch Application**

```bash
# Start the application
python natural_cli.py
```

### **Step 4: First Login (Admin Setup)**

```
🔐 Universal Product Scraper - Authentication Required
Username: admin
Password: Admin@123
⚠️ You MUST change this password on first login!
```

---

## 🎯 First Time Usage

### **Quick Test Run:**

1. Launch `UniversalProductScraper_v1.2.exe`
2. Select option **"2. ⚡ Quick scraping wizard"**
3. Choose **"A. Quick test (2 products)"**
4. When prompted for source file, select `data\SOURCE.xlsx`
5. Watch the scraper process 2 sample products (~10 minutes)

### **Custom Session:**

1. Launch `UniversalProductScraper_v1.2.exe`
2. Select option **"1. 📊 Configure a custom scraping session"**
3. Point to your Excel file with products
4. Configure processing options through guided setup
5. Review and execute your scraping session

---

## 📊 Input File Format

Your Excel file should follow this structure:

**Starting at Row 4:**

```
A          B                    C
Row    Product Name        Reference Price
4      אלקטרה AI INV 150      2080
5      טיטניום INV 140        2340
6      Samsung Galaxy S24     3500
```

**Requirements:**

- Column A: Row number (starting from 4)
- Column B: Product name (Hebrew/English/Mixed)
- Column C: Reference/official price (numeric)
- Data starts at row 2 (row 1 reserved for headers)

---

## 📁 Directory Structure After First Run

```
Universal-Product-Scraper-v1.2/
├── UniversalProductScraper_v1.2.exe        # Main application
├── data/
│   └── SOURCE.xlsx                          # Sample template
├── output/                                  # Your results appear here
│   └── (results created after first run)
├── logs/                                    # Application logs
│   └── (logs created after first run)
├── config/
│   └── default_config.json                 # Settings (advanced users)
└── Documentation files (README.md, etc.)
```

---

## 🔧 Application Features

### **Main Menu Options:**

```
🔧 What would you like to do today?

1. 📊 Configure a custom scraping session
2. ⚡ Quick scraping wizard (guided setup)  
3. 📈 View recent scraping results
4. 🔍 Check system status and performance
5. ❓ Help and examples
6. 🚪 Exit
```

### **Quick Wizard Options:**

```
⚡ Quick Scraping Wizard

A. Quick test (2 products, ~10 minutes, visible browser)
B. Small batch (6-10 products, customizable)  
C. Large batch (11+ products, optimized mode)
D. Single product validation
```

---

## 📈 Expected Results

### **Processing Performance:**

- **Success Rate**: 86-89% vendor data collection
- **Speed**: 30-second timeout per vendor
- **Reliability**: 2-attempt retry system with 3-second delays
- **Browser**: Automatic Chrome WebDriver management

### **Output Files:**

1. **Main Results**: `output/` folder with timestamped results
   - **Worksheet 1** ("פירוט"): Detailed vendor breakdown
   - **Worksheet 2** ("סיכום"): Statistical summary

2. **Log Files**: `logs/vendor_processing_YYYYMMDD_HHMMSS.log`
   - Processing details and performance metrics

---

## 🚀 Deployment Options

### **Single Computer:**

- Copy entire folder to desired location
- Double-click `UniversalProductScraper_v1.2.exe`
- Works from any drive (C:, D:, USB, Network)

### **Multiple Computers:**

- Copy folder to USB drive
- Plug into any Windows 10/11 computer  
- Run immediately - no installation needed
- Copy folder to network share for team access

### **Business Environment:**

- Deploy to shared network location
- All users can access same application
- Individual output folders by user/date
- Centralized configuration management

---

## 🔍 Troubleshooting Quick Guide

### **Application Won't Start:**

- Ensure Windows 10/11 (Windows 7/8 not supported)
- Check available disk space (200MB minimum)
- Run as Administrator if permission issues

### **Chrome Issues:**

- Application manages Chrome WebDriver automatically
- If Chrome browser errors occur, ensure Chrome is updated
- No manual driver installation needed

### **Hebrew Text Problems:**

- Application handles Hebrew/RTL automatically
- Ensure input Excel file is saved in UTF-8 format
- Check that product names contain actual Hebrew characters

### **Performance Issues:**

- Large batches (20+ products) may take 1-2 hours
- Use "Quick test" mode for initial validation
- Check internet connection stability

---

## 📞 Support Resources

- **Common Issues**: See `TROUBLESHOOTING.txt`
- **Complete Documentation**: Review `README.md`
- **Version Information**: Check `VERSION_INFO.json`
- **Technical Context**: Refer to `extract_claude.md`

---

## ✅ Success Checklist

After setup, verify:

- [ ] Application launches without errors
- [ ] Sample data file `data\SOURCE.xlsx` is accessible
- [ ] Quick test completes successfully (2 products)
- [ ] Output files are created in `output/` directory
- [ ] Hebrew text displays correctly in results

---

**🎉 Ready for Production Use!**

*Your standalone professional price comparison tool is ready. No technical maintenance required.*