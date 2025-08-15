# Universal Product Scraper

[![Version](https://img.shields.io/badge/version-1.2-blue.svg)](.)
[![Status](https://img.shields.io/badge/status-Production%20Ready-green.svg)](.)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](.)
[![Authentication](https://img.shields.io/badge/security-Enterprise%20Auth-red.svg)](.)

**Professional-grade scraper for product price comparison from ZAP.co.il with enterprise authentication.** Automatically extracts and compares prices across multiple vendors with comprehensive Excel output.

## 🔐 NEW: Enterprise Authentication System

Secure user authentication with enterprise-grade features:
- **Password Requirements**: 8+ chars, uppercase, special characters
- **Account Security**: 5-attempt lockout, session management
- **Admin Commands**: User creation, password reset, user management
- **Session Control**: 8-hour sessions, secure logout

## 🆕 Natural Language Interface

The easiest way to use the scraper! Run the new conversational interface:

```bash
python natural_cli.py
# First time: Login with admin/Admin@123 (must change password)
# Admin commands: --create-user, --list-users, --reset-password
```

Features user-friendly menus with:
- 🧪 **Quick test scraping** (2 products, ~10 minutes, visible browser)
- 📊 **Guided batch setup** with smart recommendations  
- 🚀 **Large batch processing** (auto-optimized for 11+ products)
- 📈 **Recent results viewer** and system status checks
- ❓ **Built-in help** and examples

Perfect for users who prefer guided, conversational interaction over command-line parameters!

---

## Features

- **Multi-vendor Price Aggregation**: Scrapes all vendor offers for each product using 3-artifact validation
- **Hebrew Language Support**: Full Unicode support with RTL text handling
- **Excel Integration**: Reads from source Excel files and outputs to target Excel with dual worksheets (פירוט/סיכום)
- **Automatic Model ID Discovery**: Intelligent algorithm that finds correct Model IDs for any product
- **Anti-bot Protection**: Configurable delays and user agent rotation
- **Mock Mode**: Development mode with simulated data
- **Comprehensive Logging**: Structured logging with configurable levels
- **System Preservation**: Automated monitoring and health checks to maintain system integrity
- **Recovery Procedures**: Built-in recovery mechanisms for system failures

## Project Structure

```
Skywind_Uni_Prod_Scrap_Protected/
├── src/                    # Source code
│   ├── scraper/           # Scraper implementations
│   │   ├── zap_scraper.py # ZAP.co.il scraper
│   │   └── mock_scraper.py # Mock scraper for testing
│   ├── excel/             # Excel processing
│   │   ├── source_reader.py
│   │   └── target_writer.py
│   ├── hebrew/            # Hebrew text processing
│   │   └── text_processor.py
│   ├── models/            # Data models
│   │   └── data_models.py
│   ├── parsers/           # Product parsing
│   │   └── product_parser.py
│   ├── utils/             # Utilities
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── logger.py
│   └── main.py           # CLI entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test data
├── config/               # Configuration files
│   └── default_config.json
├── docs/                 # Documentation
├── examples/             # Example scripts
├── data/                 # Sample data files
├── logs/                 # Log files
└── output/               # Output files
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Skywind_Uni_Prod_Scrap_Protected.git
cd Skywind_Uni_Prod_Scrap_Protected
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Chrome WebDriver (automatically handled by webdriver-manager)

## 🎯 Business Use Cases

**Professional Applications:**
- **Market Research**: Comprehensive price comparison and competitive analysis
- **Procurement Analysis**: Supplier comparison and cost optimization
- **Business Intelligence**: Market trend analysis and pricing strategies
- **Cost Management**: Identify savings opportunities and track price changes

**Performance Metrics:**
- 🎯 **86-89% vendor data collection success rate**
- ⚡ **30-second timeouts with intelligent retry logic**
- 🔒 **Enterprise-grade authentication and security**
- 📊 **Comprehensive dual-worksheet Excel reports**

## Usage

### 🎯 Natural Language Interface (Recommended)

**Easiest way to use the scraper!** Interactive, conversational interface:

```bash
python natural_cli.py
```

The Natural Language CLI provides:

🧪 **Quick Test Scraping** - Perfect for first-time users
- Tests 2 products in ~10 minutes with visible browser
- Immediate results and validation
- Great for learning the system

⚡ **Quick Scraping Wizard** - Guided setup with smart defaults
- A. Quick test (2 products, ~10 minutes, visible browser)  
- B. Small batch (6-10 products, your choice of mode)
- C. Large batch (11+ products, auto-headless mode)
- D. Single product validation

📊 **Custom Configuration** - Step-by-step setup
- Choose source file from available options
- Analyze products and select range to process
- Smart mode recommendations based on batch size
- Review configuration before execution

📈 **Recent Results** - View and manage outputs
- Browse recent scraping results
- File information and timestamps
- Easy access to past work

🔍 **System Status** - Health checks and diagnostics
- Verify all components are working
- Check recent activity and logs
- System performance overview

### Advanced: Command Line Interface

For power users and automation:

```bash
python src/main.py --source data/products.xlsx --target output/results.xlsx
```

### Command Line Options

- `--source`: Path to source Excel file (required)
- `--target`: Path to target Excel file (required)
- `--headless`: Run browser in headless mode
- `--mock-mode`: Use mock data instead of real scraping
- `--limit`: Limit number of products to process
- `--config`: Path to configuration file
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Example Scripts

Run the interactive scraper:
```bash
python examples/run_scraper.py
```

### Excel File Format

**Source File (Column Structure):**
- Column A: Row number
- Column B: Product name
- Column C: Original/Official price
- Data starts at row 4

**Target File (2 Worksheets):**

**Worksheet 1 - "פירוט" (Details):**
- Multiple rows per product (one per vendor)
- Contains vendor names, prices, URLs, and price comparisons

**Worksheet 2 - "סיכום" (Summary):**
- One row per product
- Contains average, minimum, maximum prices and vendor statistics

## Configuration

Edit `config/default_config.json` to customize:
- Scraper settings (delays, timeouts, user agent)
- Excel processing options
- Hebrew text normalization
- Logging configuration
- Performance settings

## Testing

Run all tests:
```bash
pytest
```

Run specific test categories:
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m hebrew       # Hebrew processing tests
```

### Excel Format Validation
```bash
# Validate specific Excel file
python src/utils/validate_excel_format.py output/your_file.xlsx

# Validate most recent Excel file (auto-detection)
python src/utils/validate_excel_format.py

# Quick validation test
python tests/quick_excel_validation.py
```

### Complete Testing Cycle
```bash
# Comprehensive validation suite (all phases)
python tests/run_validation_suite.py

# Quick critical tests only
python tests/run_validation_suite.py --quick

# Validate specific Excel file
python tests/run_validation_suite.py --excel-file output/results.xlsx

# Access detailed testing guide
# See: docs/COMPLETE_TESTING_CYCLE_GUIDE.md
```

### Working Test Examples

The system includes comprehensive testing capabilities:
- Unit tests in `tests/unit/` - Component-level validation
- Integration tests in `tests/integration/` - End-to-end system tests  
- CLI tests in `tests/` - Command-line interface validation

### Post-Test Cleanup (MANDATORY)

**Execute after EVERY test to maintain project cleanliness:**

```powershell
# Automatic cleanup - run after every test cycle
Remove-Item logs/line_*_test_*.log, logs/error_*.png, logs/*_diagnosis.png, logs/*_analysis.png -Force -ErrorAction SilentlyContinue
Remove-Item output/test_*.xlsx, output/quick_*.xlsx, output/debug_*.xlsx, output/~$*.xlsx -Force -ErrorAction SilentlyContinue  
Remove-Item test_*.py, quick_*.py, debug_*.py, examine_*.py -Force -ErrorAction SilentlyContinue
```

**Purpose**: Removes temporary test files, debug screenshots, and test logs (saves 10+ MB).  
**Frequency**: After individual tests, batch tests, and development sessions.  
**Target**: Keep logs/ <5MB, remove temp files from output/ and root directory.

## System Preservation & Monitoring

The system includes automated preservation and monitoring features:

### Daily Health Checks
```bash
python test_daily_validation.py
# or
run_daily_check.bat  # Windows
```

### System Monitoring
```bash
python system_monitor.py
```

### Key Documents
- `docs/ZAP-SCRAPING-GUIDE.md` - Complete URL Construction Method workflow
- `docs/backend-context.md` - Technical implementation details
- `LLM_HANDOVER.md` - Current development context and status

## Development

### Adding a New Scraper

1. Create a new scraper class in `src/scraper/`
2. Inherit from the base scraper interface
3. Implement required methods:
   - `initialize()`
   - `scrape_product()`
   - `scrape_batch()`
   - `close()`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all functions
- Run code formatters:
  ```bash
  black src/
  isort src/
  flake8 src/
  ```

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `/docs`
- Review example scripts in `/examples`