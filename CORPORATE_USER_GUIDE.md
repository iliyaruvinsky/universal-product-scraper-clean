# Universal Product Scraper - Corporate User Guide v1.3

**🎯 Quick Price Comparison Tool - No Technical Knowledge Required**

---

## 🚀 Getting Started (5 Minutes)

### **Step 1: Launch the Application**
1. **Double-click** "Universal Product Scraper" on your desktop
2. **Wait** for the application to start (green window)

### **Step 2: Login**
```
Username: admin
Password: Admin@123
```
> ⚠️ **First time?** You'll be asked to change the password - choose something secure!

### **Step 3: Choose "Quick Scraping Wizard"**
- Select option **1** from the menu
- This is the easiest way to get price comparisons

---

## 📊 Preparing Your Product List

### **Excel File Format:**
- **Column A**: Product names (one per row)
- **Column B**: Current prices (optional)
- **Save as**: .xlsx format

### **Example:**
```
Row 1: Tornado WD INV PRO SQ 45 1PH
Row 2: Electra AI INV 150
Row 3: TADIRAN Wind INV 220
```

### **✅ Good Product Names:**
- Include manufacturer: "Tornado", "Electra", "TADIRAN"
- Include model numbers: "45", "150", "220"
- Include product type: "INV", "Inverter"

### **❌ Avoid:**
- Too short: "AC Unit"
- Missing details: "Air Conditioner"
- Wrong category: "Samsung Phone" (this tool is for HVAC only)

---

## 🎯 Running Price Comparison

### **Quick Process:**
1. **Select your Excel file** when prompted
2. **Choose product range** (e.g., rows 1-5 or "all")
3. **Wait patiently** ☕ (2-3 minutes per product)
4. **Get results** in Excel format

### **What Happens:**
- 🔍 Searches ZAP.co.il for each product
- 🏪 Finds all vendors selling that product
- 💰 Collects current prices
- 📊 Creates Excel report with comparisons

---

## 📄 Understanding Results

Your Excel report contains **2 worksheets**:

### **1. "פירוט" (Details):**
- Complete vendor list
- Individual prices
- Vendor contact info
- Product specifications

### **2. "סיכום" (Summary):**
- Price ranges per product
- Cheapest/most expensive vendors
- Average prices
- Quick comparison table

---

## 💡 Tips for Best Results

### **⏰ Timing:**
- **Best times**: 9 AM - 5 PM (business hours)
- **Avoid**: Late evenings, weekends
- **Allow**: 2-3 minutes per product minimum

### **📶 Internet:**
- Ensure stable internet connection
- Corporate proxy? Contact IT for configuration

### **📋 Product Selection:**
- Start small: Test with 2-3 products first
- Then scale up: Process 10-20 products per batch
- For large lists: Break into smaller chunks

---

## 🆘 Troubleshooting

### **Common Issues & Solutions:**

| Problem | Solution |
|---------|----------|
| "Chrome not found" | Wait - it downloads automatically |
| "No results found" | Check product name spelling |
| "Access denied" | Right-click → "Run as administrator" |
| "Internet error" | Check connection/contact IT |
| "Excel won't open" | Close Excel first, then try again |

### **Still Having Issues?**
1. **Close everything** and restart the application
2. **Check the logs** folder for error details
3. **Contact IT support** with error messages
4. **Try a different product** to test if it's product-specific

---

## 🔒 Security & Privacy

### **Your Data:**
- ✅ **Stays local** - nothing sent to external servers
- ✅ **Encrypted storage** - passwords protected
- ✅ **No tracking** - no personal data collected
- ✅ **Audit logs** - all activities recorded locally

### **What Gets Scraped:**
- ✅ **Public prices** from ZAP.co.il only
- ✅ **Vendor information** (names, contact details)
- ✅ **Product specifications** (publicly available)
- ❌ **No personal data** from vendors

---

## 📞 Support Contacts

### **For Users:**
- **IT Helpdesk**: [Your IT Contact]
- **User Manual**: Check desktop shortcut "Product Scraper - User Guide"

### **For IT Administrators:**
- **Technical Docs**: `/docs` folder
- **Configuration**: `/config/default_config.json`
- **Logs**: `/logs` folder

---

## 🏆 Success Example

**Before:** "I need prices for 10 air conditioners - spent 2 hours calling vendors"

**After:** "Ran scraper during coffee break - got complete price comparison for all 10 products in Excel format. Saved 30% on procurement!"

---

**Ready to save money on your next purchase?** 💰  
**Double-click that desktop icon and get started!** 🚀