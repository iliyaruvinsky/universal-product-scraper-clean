# Universal Product Scraper - Corporate Distribution v1.3

**Enterprise Price Comparison Tool for ZAP.co.il**  
**Release Date**: August 16, 2025  
**Build**: Production-Ready Corporate Distribution

---

## 🏢 Corporate Deployment Package

This is a ready-to-deploy corporate package for the Universal Product Scraper. Designed for easy installation and use across corporate environments.

### ✅ What's Included:
- Complete application source code
- Automated installation script
- Pre-configured Chrome WebDriver
- Sample data files and templates
- User documentation and guides
- Enterprise authentication system
- Excel validation and reporting tools

---

## 🚀 Quick Installation (IT Administrators)

### **Option A: Automated Installation (Recommended)**
```cmd
1. Extract the ZIP file to desired location (e.g., C:\ProductScraper\)
2. Right-click "INSTALL.bat" → "Run as Administrator"
3. Follow the prompts
4. Installation complete!
```

### **Option B: Manual Installation**
```cmd
1. Ensure Python 3.11+ is installed
2. Extract to desired location
3. Run: pip install -r requirements.txt
4. Run: python natural_cli.py
```

---

## 👥 End User Quick Start

### **For Users (No Technical Knowledge Required):**

1. **Double-click "START_SCRAPER.bat"** on desktop
2. **Login** with provided credentials
3. **Choose "Quick scraping wizard"**
4. **Select your Excel file** with product list
5. **Wait for results** (coffee break time! ☕)
6. **Get Excel report** with price comparisons

**That's it!** 🎉

---

## 📋 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Internet**: Required for web scraping
- **Software**: Python 3.11+ (auto-installed if missing)
- **Browser**: Chrome (auto-managed)

---

## 🔧 Configuration for Corporate Networks

### **Proxy Settings** (if needed):
Edit `config/default_config.json`:
```json
{
  "proxy": {
    "http": "http://proxy.company.com:8080",
    "https": "https://proxy.company.com:8080"
  }
}
```

### **Firewall Whitelist**:
- *.zap.co.il (primary scraping target)
- *.github.com (for updates)
- *.googleapis.com (Chrome WebDriver)

---

## 📊 Sample Workflow

1. **Prepare Excel File**: List products in column A
2. **Launch App**: Double-click START_SCRAPER.bat
3. **Quick Scraping**: Choose from menu
4. **Select Products**: Pick range or all
5. **Wait**: ~2-3 minutes per product
6. **Results**: Excel file with vendor prices
7. **Analysis**: Compare prices, find best deals

---

## 🆘 Support & Troubleshooting

### **Common Issues:**
- **"Chrome not found"** → Chrome will auto-install
- **"No internet"** → Check proxy settings
- **"Access denied"** → Run as Administrator
- **"Python error"** → Use automated installer

### **For IT Support:**
- Logs: `logs/` directory
- Config: `config/default_config.json`
- Data: `data/` directory
- Output: `output/` directory

---

## 📄 Included Documentation

- `USER_GUIDE.md` - Complete user manual
- `SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `EXCEL_VALIDATOR_GUIDE.md` - Excel formatting help
- `QUICKSTART.md` - 5-minute getting started

---

## 🔐 Security Features

- **User Authentication**: Multi-user support
- **Password Protection**: Encrypted storage
- **Session Management**: Automatic logout
- **Data Privacy**: No data sent externally
- **Audit Logs**: Complete operation tracking

---

**Ready to save money on product procurement?** 💰  
**Contact IT for installation assistance.**