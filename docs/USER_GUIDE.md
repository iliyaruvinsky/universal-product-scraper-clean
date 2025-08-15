# 📖 Universal Product Scraper - User Guide

**Version**: 1.2 with Enterprise Authentication  
**Target Audience**: End Users  
**Prerequisites**: Windows 10/11, Internet Connection  

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Get Your Login Credentials**
Contact your administrator to get:
- **Username**: Your assigned username
- **Password**: Your secure password

*First-time users will be prompted to change their password.*

### **Step 2: Start the Application**
1. **Navigate** to the scraper folder
2. **Double-click** `natural_cli.py` OR open Command Prompt and run:
   ```cmd
   python natural_cli.py
   ```

### **Step 3: Login**
```
🔐 Universal Product Scraper - Authentication Required
==================================================
Username: [enter your username]
Password: [enter your password]
```

### **Step 4: Use the Menu**
After successful login, you'll see:
```
🚀 UNIVERSAL PRODUCT SCRAPER - Natural Language Interface
==================================================
👤 Logged in as: yourusername
🕐 Session expires in: 8.0 hours

🔧 What would you like to do today?

1. 📊 Configure a custom scraping session
2. ⚡ Quick scraping wizard (guided setup)
3. 📈 View recent scraping results
4. 🔍 Check system status and performance
5. ❓ Help and examples
6. 🔐 Logout
7. 🚪 Exit
```

---

## 🎯 How to Use Each Feature

### **Option 1: Configure Custom Scraping Session**
**Best for**: Experienced users who know exactly what they want

1. **Select Option 1**
2. **Choose your Excel file** with product data
3. **Set row range** (e.g., "4-10" for rows 4 to 10)
4. **Choose browser mode**:
   - **Visible**: See the browser working (slower but good for monitoring)
   - **Headless**: Fast background processing (recommended for large batches)
5. **Review settings** and confirm
6. **Wait for processing** to complete

### **Quick Scraping Wizard** ⭐ **RECOMMENDED FOR BEGINNERS**
**Best for**: New users or quick tests

1. **Select the guided option**
2. **Follow the guided prompts**:
   - File selection with smart recommendations
   - Automatic batch size detection
   - Optimized settings based on your data
3. **Let the wizard handle the technical details**
4. **Get results with minimal setup**

### **Option 3: View Recent Results**
**Purpose**: Check your past scraping sessions

- See all recent output files
- View processing statistics
- Open results directly in Excel
- Check success rates and performance

### **Option 4: System Status**
**Purpose**: Monitor system health and performance

- Current system status
- Recent processing statistics
- Performance metrics
- Troubleshooting information

### **Option 5: Help and Examples**
**Purpose**: Get detailed help and see examples

- Step-by-step tutorials
- Common use cases
- Troubleshooting tips
- Best practices

---

## 📊 Understanding Your Results

### **Excel Output Structure**
Your results will be saved as `.xlsx` files in the `output/` folder with two worksheets:

#### **Worksheet 1: "פירוט" (Details)**
- **Multiple rows per product** (one row per vendor)
- **Columns include**:
  - Source Row Reference
  - Product Name  
  - Official Price
  - Vendor Name
  - ZAP Product Name
  - ZAP Price
  - Price Difference (absolute & percentage)
  - Direct URL to vendor page
  - Processing timestamp

#### **Worksheet 2: "סיכום" (Summary)**
- **One row per product** with statistics
- **Best price found**
- **Number of vendors**
- **Average price**
- **Price savings potential**

### **Result Quality Indicators**
- **86-89% Success Rate**: Typical vendor data collection
- **Green Status**: Successful processing
- **Yellow Status**: Partial success (some vendors failed)
- **Red Status**: Processing failed (check logs)

---

## 🔧 Common Tasks

### **Prepare Your Excel File**
1. **Use the provided template**: `data/SOURCE.xlsx`
2. **Required columns**:
   - **Column A**: Item numbers (optional)
   - **Column B**: Product names (Hebrew or English)
   - **Column C**: Official/reference prices
3. **Data starts at Row 4** (rows 1-3 are headers)
4. **Save in Excel format** (.xlsx)

### **Choose the Right Settings**

#### **For Small Batches** (1-10 products):
- Use **Quick Scraping Wizard**
- Choose **Visible mode** to watch progress
- Processing time: ~5-15 minutes

#### **For Large Batches** (11+ products):
- Use **Custom Configuration**
- Choose **Headless mode** for speed
- Break into smaller chunks if needed
- Processing time: ~2-3 minutes per product

### **Troubleshooting Common Issues**

#### **Login Problems**
```
❌ Invalid username or password
```
**Solution**: Contact your administrator to verify credentials

#### **Account Locked**
```
❌ Account locked. Try again in 15 minutes
```
**Solution**: Wait 15 minutes or contact administrator to unlock

#### **File Not Found**
```
❌ Excel file not found or not accessible
```
**Solution**: 
- Check file path is correct
- Ensure file is not open in Excel
- Verify file permissions

#### **Processing Errors**
```
❌ Scraping failed for some products
```
**Solution**:
- Check internet connection
- Verify product names are clear
- Try smaller batches
- Contact administrator if persistent

---

## 🔐 Security & Session Management

### **Your Session**
- **Duration**: 8 hours from login
- **Auto-logout**: When you close the application
- **Manual logout**: Use Option 6 in main menu

### **Password Requirements**
- **Minimum 8 characters**
- **At least 1 uppercase letter**
- **At least 1 special character** (!@#$%^&*()_+-=[]{}|;:,.<>?)
- **No common passwords** (password123, admin123, etc.)

### **Account Security**
- **5 failed attempts** = 15-minute account lockout
- **Password expires** every 6 months
- **Change password** through administrator

---

## 📞 Getting Help

### **When to Contact Administrator**
- **Login issues**: Forgotten password, account locked
- **User management**: Create new accounts, change passwords
- **Technical problems**: System errors, configuration issues
- **Performance issues**: Slow processing, repeated failures

### **Self-Help Resources**
1. **Built-in Help**: Option 5 in main menu
2. **Log Files**: Check `logs/` folder for error details
3. **Recent Results**: Option 3 shows processing history
4. **System Status**: Option 4 shows current health

### **Best Practices**
- **Test with small batches** before large processing
- **Use clear product names** for better matching
- **Keep Excel files closed** during processing
- **Logout when finished** to free up session
- **Save your work** - results are automatically saved to `output/`

---

**📧 Need additional help? Contact your system administrator.**

*This guide covers the standard user workflow. For advanced configuration and administration tasks, see the Administrator Guide.*
