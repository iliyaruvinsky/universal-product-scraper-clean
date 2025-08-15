#!/usr/bin/env python3
"""
Universal Product Scoring Engine
===============================
Centralized scoring system for product name matching and validation.
Implements OPTION_1 scoring methodology with enhanced nomenclature intelligence.

Key Features:
- Reduced manufacturer weight (10% instead of 15%)
- Enhanced technical specification importance
- INV ≡ INVERTER equivalence rules
- Year number filtering (2024/2025 treated as extra words)
- Configurable scoring weights and thresholds

Usage:
    from src.validation.scoring_engine import ProductScoringEngine
    
    engine = ProductScoringEngine()
    score, details = engine.calculate_match_score(original_name, scraped_name)

Author: Skywind Universal Scraper Team
Date: August 14, 2025
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """Configurable scoring weights for different components"""
    manufacturer: float = 1.0  # 10% (reduced from 15%)
    series: float = 4.0        # 40% (decreased from 65%)
    model: float = 5.0         # 50% (increased from 20%)
    extra_word_penalty: float = 0.1  # Penalty per extra word


@dataclass 
class ScoringResult:
    """Result of product scoring calculation"""
    total_score: float
    max_score: float
    percentage: float
    components: Dict[str, float]
    gates_passed: Dict[str, bool]
    issues: List[str]
    parsed_original: Dict
    parsed_scraped: Dict


class ProductScoringEngine:
    """
    Universal scoring engine for product name matching.
    Centralizes all scoring logic with configurable weights.
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        """
        Initialize scoring engine with configurable weights.
        
        Args:
            weights: Custom scoring weights (uses defaults if None)
        """
        self.weights = weights or ScoringWeights()
        self.max_score = self.weights.manufacturer + self.weights.series + self.weights.model
        
        # Hebrew manufacturer translations
        self.hebrew_manufacturers = {
            'טורנדו': 'TORNADO',
            'אלקטרה': 'ELECTRA', 
            'תדיראן': 'TADIRAN',
            'טורנאדו': 'TORNADO',  # Alternative spelling
            'גרי': 'GREE',
            'מידאה': 'MIDEA',
            'האייר': 'HAIER'
        }
        
        # Technology equivalence rules
        self.tech_equivalencies = {
            'INV': ['INVERTER', 'אינוורטר'],
            'INVERTER': ['INV', 'אינוורטר'],
            'אינוורטר': ['INV', 'INVERTER']
        }
        
        # Optional technical specifications (less critical for scoring)
        self.optional_specs = {
            '1PH', '3PH', '1PHASE', '3PHASE', 'SINGLE', 'THREE'
        }
    
    def clean_hebrew_text(self, text: str) -> str:
        """
        Remove Hebrew characters and translate known manufacturer names.
        
        Args:
            text: Text potentially containing Hebrew characters
            
        Returns:
            Cleaned text with Hebrew manufacturers translated to English
        """
        if not text:
            return ""
        
        # Translate known Hebrew manufacturer names
        result = text
        for hebrew, english in self.hebrew_manufacturers.items():
            if hebrew in result:
                result = result.replace(hebrew, english)
        
        # Remove remaining Hebrew characters (keep ASCII only)
        cleaned = re.sub(r'[^\x00-\x7F]+', ' ', result)
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def parse_product_components(self, product_name: str, target_model: str = "") -> Dict:
        """
        Parse product into manufacturer, series, and model components.
        Enhanced to prefer target model when multiple numbers exist.
        
        Args:
            product_name: Product name to parse
            target_model: Target model number for preference matching
            
        Returns:
            Dictionary with parsed components
        """
        if not product_name:
            return {'manufacturer': '', 'series': [], 'model': ''}
        
        words = product_name.split()
        if not words:
            return {'manufacturer': '', 'series': [], 'model': ''}
        
        # Extract manufacturer (first word)
        manufacturer = words[0].upper()
        
        # Find all potential model numbers
        all_numbers = re.findall(r'(\d+(?:/\d+[A-Z]*)?)', product_name)
        
        # Enhanced model selection logic
        model_number = ""
        if target_model and target_model in all_numbers:
            # Prefer exact target match
            model_number = target_model
        elif all_numbers:
            # Filter out year numbers (2024, 2025, etc.)
            non_year_numbers = [num for num in all_numbers if not re.match(r'^20\d{2}$', num)]
            
            if non_year_numbers:
                # Use first non-year number
                model_number = non_year_numbers[0]
            elif all_numbers:
                # Fallback to first number if only year numbers exist
                model_number = all_numbers[0]
        
        # Extract series words (exclude manufacturer and model)
        series_words = []
        for word in words[1:]:  # Skip manufacturer
            word_upper = word.upper()
            
            # Skip if it's the model number
            if word == model_number:
                continue
            
            # Skip if it's any number (including years)
            if re.match(r'^\d+(?:/\d+[A-Z]*)?$', word):
                continue
            
            # Skip common non-technical words
            if word_upper not in ['כ''ס', 'שנת', 'דגם', 'מזגן', 'עילי', 'מיני', 'מרכזי']:
                series_words.append(word_upper)
        
        return {
            'manufacturer': manufacturer,
            'series': series_words,
            'model': model_number
        }
    
    def check_technology_equivalence(self, word1: str, word2: str) -> bool:
        """
        Check if two technology terms are equivalent (INV ≡ INVERTER).
        
        Args:
            word1: First technology term
            word2: Second technology term
            
        Returns:
            True if terms are equivalent
        """
        word1_upper = word1.upper()
        word2_upper = word2.upper()
        
        # Direct match
        if word1_upper == word2_upper:
            return True
        
        # Check equivalence rules
        if word1_upper in self.tech_equivalencies:
            return word2_upper in self.tech_equivalencies[word1_upper]
        
        return False
    
    def calculate_match_score(self, original_name: str, scraped_name: str) -> ScoringResult:
        """
        Calculate comprehensive matching score between original and scraped names.
        
        Args:
            original_name: Original product name from source
            scraped_name: Scraped product name from website
            
        Returns:
            ScoringResult with detailed scoring breakdown
        """
        issues = []
        gates_passed = {
            'model_number': False,
            'product_type': False
        }
        
        # Clean scraped name (remove Hebrew)
        scraped_clean = self.clean_hebrew_text(scraped_name)
        
        # Parse both names
        original_components = self.parse_product_components(original_name)
        scraped_components = self.parse_product_components(scraped_clean, original_components['model'])
        
        # CRITICAL GATES - Must pass to continue scoring
        
        # Gate 1: Model Number Gate
        if original_components['model'] != scraped_components['model']:
            issues.append(f"Model mismatch: '{original_components['model']}' ≠ '{scraped_components['model']}'")
            return ScoringResult(
                total_score=0.0,
                max_score=self.max_score,
                percentage=0.0,
                components={'model_gate': 0.0},
                gates_passed=gates_passed,
                issues=issues,
                parsed_original=original_components,
                parsed_scraped=scraped_components
            )
        
        gates_passed['model_number'] = True
        
        # Gate 2: Product Type Gate (INV/INVERTER)
        original_has_inv = any(
            word in ['INV', 'INVERTER'] for word in original_components['series']
        )
        scraped_text_upper = scraped_clean.upper()
        scraped_has_inv = 'INV' in scraped_text_upper or 'INVERTER' in scraped_text_upper
        
        if original_has_inv and not scraped_has_inv:
            issues.append("Missing INV/INVERTER in scraped name")
            return ScoringResult(
                total_score=0.0,
                max_score=self.max_score,
                percentage=0.0,
                components={'product_type_gate': 0.0},
                gates_passed=gates_passed,
                issues=issues,
                parsed_original=original_components,
                parsed_scraped=scraped_components
            )
        
        gates_passed['product_type'] = True
        
        # COMPONENT SCORING - Gates passed, now calculate detailed scores
        
        component_scores = {}
        
        # 1. Manufacturer Scoring (10% - reduced weight)
        if original_components['manufacturer'] in scraped_text_upper:
            manufacturer_score = self.weights.manufacturer
        else:
            manufacturer_score = 0.0
            issues.append(f"Manufacturer '{original_components['manufacturer']}' not found")
        
        component_scores['manufacturer'] = manufacturer_score
        
        # 2. Model Name Scoring (40% - balanced importance for technical specs)
        if original_components['series']:
            series_matches = 0
            missing_series = []
            
            for word in original_components['series']:
                # Check direct presence
                if word in scraped_text_upper:
                    series_matches += 1
                # Check technology equivalence (INV ≡ INVERTER)
                elif any(self.check_technology_equivalence(word, scraped_word) 
                        for scraped_word in scraped_text_upper.split()):
                    series_matches += 1
                # Check for hyphenated compound words (WD-INV-PRO-SQ vs WD INV PRO SQ)
                elif '-' in word:
                    # Split hyphenated word and check if all parts are present
                    word_parts = word.split('-')
                    if all(part in scraped_text_upper for part in word_parts):
                        series_matches += 1
                    else:
                        # Give partial credit based on how many parts match
                        matching_parts = sum(1 for part in word_parts if part in scraped_text_upper)
                        series_matches += matching_parts / len(word_parts)
                        if matching_parts < len(word_parts):
                            missing_parts = [part for part in word_parts if part not in scraped_text_upper]
                            missing_series.append(f"{'-'.join(missing_parts)} (from {word})")
                # Check if it's an optional spec (less critical)
                elif word in self.optional_specs:
                    # Give partial credit for missing optional specs
                    series_matches += 0.7  # 70% credit instead of 0%
                    missing_series.append(f"{word} (optional)")
                else:
                    missing_series.append(word)
            
            series_percentage = series_matches / len(original_components['series'])
            series_score = series_percentage * self.weights.series
            
            if missing_series:
                issues.append(f"Missing series components: {', '.join(missing_series)}")
        else:
            series_score = self.weights.series  # No series words to match
        
        component_scores['series'] = series_score
        
        # 3. Model Number Scoring (50% - increased importance, already passed gate)
        model_score = self.weights.model  # Full points for passing gate
        component_scores['model'] = model_score
        
        # 4. Extra Words Penalty (minor deduction)
        scraped_words = scraped_text_upper.split()
        original_words = (
            [original_components['manufacturer']] + 
            original_components['series'] + 
            [original_components['model']]
        )
        
        # Count unrelated extra words (not partial matches)
        extra_words = []
        for word in scraped_words:
            # Skip if it matches any original component
            if any(orig in word or word in orig for orig in original_words):
                continue
            
            # Skip common website additions
            if word in ['ZAP', 'SHOP', 'LOGO', 'מזגן', 'עילי', 'מיני', 'מרכזי']:
                continue
            
            # Skip year numbers (they're not product-relevant)
            if re.match(r'^20\d{2}$', word):
                continue
                
            extra_words.append(word)
        
        extra_penalty = min(len(extra_words) * self.weights.extra_word_penalty, 1.0)
        
        if extra_penalty > 0:
            issues.append(f"Extra words penalty: {', '.join(extra_words[:5])}")
        
        component_scores['extra_penalty'] = -extra_penalty
        
        # Calculate final score
        total_score = max(0.0, sum(component_scores.values()))
        percentage = (total_score / self.max_score) * 100
        
        return ScoringResult(
            total_score=total_score,
            max_score=self.max_score,
            percentage=percentage,
            components=component_scores,
            gates_passed=gates_passed,
            issues=issues,
            parsed_original=original_components,
            parsed_scraped=scraped_components
        )
    
    def is_valid_match(self, scoring_result: ScoringResult, threshold_percentage: float = 80.0) -> bool:
        """
        Determine if a match is valid based on scoring result and threshold.
        
        Args:
            scoring_result: Result from calculate_match_score
            threshold_percentage: Minimum percentage for valid match
            
        Returns:
            True if match passes validation threshold
        """
        return scoring_result.percentage >= threshold_percentage
    
    def get_scoring_explanation(self, scoring_result: ScoringResult) -> str:
        """
        Generate human-readable explanation of scoring result.
        
        Args:
            scoring_result: Result from calculate_match_score
            
        Returns:
            Formatted explanation string
        """
        lines = []
        
        lines.append(f"SCORING BREAKDOWN ({scoring_result.percentage:.1f}%)")
        lines.append("=" * 50)
        
        # Components breakdown
        if 'manufacturer' in scoring_result.components:
            mfg_score = scoring_result.components['manufacturer']
            lines.append(f"Manufacturer: {mfg_score:.1f}/{self.weights.manufacturer:.1f} points ({self.weights.manufacturer/self.max_score*100:.0f}%)")
        
        if 'series' in scoring_result.components:
            series_score = scoring_result.components['series']
            lines.append(f"Series/Tech:  {series_score:.1f}/{self.weights.series:.1f} points ({self.weights.series/self.max_score*100:.0f}%)")
        
        if 'model' in scoring_result.components:
            model_score = scoring_result.components['model']
            lines.append(f"Model Number: {model_score:.1f}/{self.weights.model:.1f} points ({self.weights.model/self.max_score*100:.0f}%)")
        
        if 'extra_penalty' in scoring_result.components and scoring_result.components['extra_penalty'] < 0:
            penalty = abs(scoring_result.components['extra_penalty'])
            lines.append(f"Extra Words:  -{penalty:.1f} points (penalty)")
        
        lines.append("-" * 50)
        lines.append(f"TOTAL SCORE:  {scoring_result.total_score:.1f}/{scoring_result.max_score:.1f} points ({scoring_result.percentage:.1f}%)")
        
        # Issues
        if scoring_result.issues:
            lines.append("")
            lines.append("ISSUES FOUND:")
            for issue in scoring_result.issues:
                lines.append(f"  • {issue}")
        
        # Component analysis
        lines.append("")
        lines.append("PARSED COMPONENTS:")
        lines.append(f"Original: {scoring_result.parsed_original}")
        lines.append(f"Scraped:  {scoring_result.parsed_scraped}")
        
        return "\n".join(lines)


# Example usage and testing
if __name__ == "__main__":
    # Create scoring engine with reduced manufacturer weight
    engine = ProductScoringEngine()
    
    # Test cases from validation reports
    test_cases = [
        # Valid cases (should score high)
        ("Tornado WD-INV-PRO-SQ 45 1PH", "WD-INV-PRO-SQ-45 1Ph TORNADO 3.5"),
        ("Tornado WD-INV-PRO-SQ 45 1PH", "TORNADO WD INV PRO SQ 45 1PH"),
        
        # Year number cases (should handle correctly now)
        ("Electra MAX INV 170", "ELECTRA MAX INV 170 2024 1.25"),
        ("Electra MAX INV 340", "ELECTRA MAX INV 340 ELECTRA 2025"),
        
        # Hebrew manufacturer translation
        ("Tornado WD-INV-PRO-SQ 45 1PH", "מזגן טורנדו מיני מרכזי 4 כ''ס WD Pro SQ Inv 45"),
    ]
    
    print("🔬 SCORING ENGINE VALIDATION")
    print("=" * 60)
    
    for i, (original, scraped) in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Original: '{original}'")
        print(f"Scraped:  '{scraped}'")
        
        result = engine.calculate_match_score(original, scraped)
        
        print(f"Score: {result.total_score:.1f}/{result.max_score:.1f} ({result.percentage:.1f}%)")
        print(f"Status: {'✅ VALID' if engine.is_valid_match(result) else '⚠️ REVIEW'}")
        
        if result.issues:
            print("Issues:", "; ".join(result.issues))
        
        print("-" * 40)