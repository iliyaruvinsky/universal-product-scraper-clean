# Quick Start Guide - Universal Product Scraper

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Skywind_Uni_Prod_Scrap_Protected.git
   cd Skywind_Uni_Prod_Scrap_Protected
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage

### 1. Prepare Source Excel File

Create an Excel file with products (starting at row 2):
- Column A: Row number
- Column B: Product name
- Column C: Original price

Example:
```
Row | Product Name        | Price
----|-------------------|-------
4   | Electra AI INV 150 | 2080
5   | Titanium INV 140   | 2340
```

### 2. Run the Scraper

**Interactive mode:**
```bash
python examples/run_scraper.py
```

**Command line:**
```bash
python src/main.py --source data/products.xlsx --target output/results.xlsx
```

**With options:**
```bash
# Headless mode (no browser window)
python src/main.py --source data/products.xlsx --target output/results.xlsx --headless

# Limit products
python src/main.py --source data/products.xlsx --target output/results.xlsx --limit 5

# Mock mode (for testing)
python src/main.py --source data/products.xlsx --target output/results.xlsx --mock-mode
```

## Output

The scraper creates an Excel file with 3 worksheets:

### Worksheet 1: "פירוט" (Details)
- All validated vendor offers for each product (score ≥8.0/10.0)
- Price comparisons
- Direct links to vendor pages

### Worksheet 2: "סיכום" (Summary)
- Statistical summary per product
- Average, min, max prices
- Cheapest vendor information

### Worksheet 3: "חריגים" (Exceptions)
- Products that failed validation (score <8.0/10.0)
- Detailed rejection reasons and scoring
- Quality control and review items

## Testing

**Run all tests:**
```bash
pytest
```

**Run specific test types:**
```bash
pytest -m unit      # Fast unit tests
pytest -m mock      # Tests with mock data
pytest -m hebrew    # Hebrew text tests
```

## Configuration

Edit `config/default_config.json` to customize:
- Scraping delays
- Browser settings
- Hebrew text processing
- Logging levels

## Troubleshooting

1. **Chrome driver issues:**
   - The webdriver-manager package handles driver installation automatically
   - If issues persist, download ChromeDriver manually

2. **Hebrew text issues:**
   - Ensure your terminal supports UTF-8
   - Check Excel file encoding

3. **Rate limiting:**
   - Increase delays in config if getting blocked
   - Use headless=false to debug

## Next Steps

- Check `docs/` for detailed documentation
- See `examples/` for more usage examples
- See `docs/` folder for detailed technical documentation