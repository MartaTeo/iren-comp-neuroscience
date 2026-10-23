#!/usr/bin/env python3
"""
Dataset Validator for AI Networks (IREN 2027 - Prof. Christophe Benavent)
Verifies that a student CSV dataset adheres to all schema rules, exclusion criteria,
and project conventions from conventions.md.
"""

import csv
import sys

EXPECTED_HEADERS = [
    'Company',
    'Founding date',
    'Country',
    'Headquarters city',
    'History',
    'Value proposition',
    'Business model',
    'Market capitalization',
    'Funds raised',
    'Revenue',
    'Profit',
    'Main investors',
    'Main competitors',
    'Main partners'
]

FORBIDDEN_COMPANIES = {
    'microsoft': 'Mega-cap (> B). Excluded from sample.',
    'apple': 'Mega-cap (> B). Excluded from sample.',
    'nvidia': 'Mega-cap (> B). Excluded from sample.',
    'alphabet': 'Mega-cap (> B) & holding. Excluded from sample.',
    'google': 'Mega-cap (> B). Excluded from sample.',
    'amazon': 'Mega-cap (> B). Excluded from sample.',
    'meta': 'Mega-cap (> B). Excluded from sample.',
}

FORBIDDEN_COMPETITOR_MAPPINGS = {
    'alphabet': "Remap to operational entity: 'Google', 'Google Cloud', 'DeepMind', or 'Waymo' (conventions.md §1.3)",
    'facebook': "Remap to corporate entity: 'Meta' (conventions.md §1.4)",
    'instagram': "Remap to corporate entity: 'Meta' (conventions.md §1.4)",
    'whatsapp': "Remap to corporate entity: 'Meta' (conventions.md §1.4)",
    'llama': "Remap to model entity: 'MetaAI' (conventions.md §1.4)",
    'llama2': "Remap to model entity: 'MetaAI' (conventions.md §1.4)",
    'llama3': "Remap to model entity: 'MetaAI' (conventions.md §1.4)",
    'azure': "Remap to corporate entity: 'Microsoft' (conventions.md §1.5)",
    'linkedin': "Remap to corporate entity: 'Microsoft' (conventions.md §1.5)",
    'github': "Remap to corporate entity: 'Microsoft' (conventions.md §1.5)",
    'zhipu ai': "Remap to reference entity: 'Z.AI' (conventions.md §1.6)",
    'zhipu': "Remap to reference entity: 'Z.AI' (conventions.md §1.6)",
}

COMMON_NON_ENGLISH_COUNTRIES = {
    'états-unis': 'United States',
    'etats-unis': 'United States',
    'usa': 'United States',
    'royaume-uni': 'United Kingdom',
    'uk': 'United Kingdom',
    'allemagne': 'Germany',
    'chine': 'China',
    'japon': 'Japan',
    'corée du sud': 'South Korea',
    'south corea': 'South Korea',
    'suisse': 'Switzerland',
    'espagne': 'Spain',
    'italie': 'Italy',
    'pays-bas': 'Netherlands',
}

def validate_csv(filepath):
    errors = []
    warnings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return ['File is completely empty.'], []
            
            # 1. Header validation
            norm_header = [h.strip().lower() for h in header]
            expected_norm = [h.lower() for h in EXPECTED_HEADERS]
            
            if norm_header != expected_norm:
                diff_missing = [h for h in expected_norm if h not in norm_header]
                diff_unexpected = [h for h in norm_header if h not in expected_norm]
                if diff_missing:
                    errors.append(f"Missing required column(s): {', '.join(diff_missing)}")
                if diff_unexpected:
                    warnings.append(f"Unexpected column(s) detected: {', '.join(diff_unexpected)}")
            
            rows = list(reader)
            row_count = len(rows)
            
            # 2. Row count check
            if row_count < 30:
                warnings.append(f"Current row count is {row_count}. The brief requires 30 to 40 companies.")
            elif row_count > 40:
                warnings.append(f"Current row count is {row_count}. The brief specifies 30 to 40 key players.")
                
            # 3. Row by row audit
            for idx, r in enumerate(rows, start=2):
                if not r or not any(field.strip() for field in r):
                    continue
                
                if len(r) != len(header):
                    errors.append(f"Row {idx}: Expected {len(header)} columns, found {len(r)}.")
                    continue
                
                data = dict(zip([h.lower() for h in header], r))
                company = data.get('company', '').strip()
                
                if not company:
                    errors.append(f"Row {idx}: Company name is empty.")
                    continue
                
                # Check forbidden mega-caps
                if company.lower() in FORBIDDEN_COMPANIES:
                    errors.append(f"Row {idx} ('{company}'): {FORBIDDEN_COMPANIES[company.lower()]}")
                
                # Check country in English
                country = data.get('country', '').strip()
                if country.lower() in COMMON_NON_ENGLISH_COUNTRIES:
                    corrected = COMMON_NON_ENGLISH_COUNTRIES[country.lower()]
                    errors.append(f"Row {idx} ('{company}'): Country '{country}' must be normalized to '{corrected}' (conventions.md §4).")
                elif not country:
                    errors.append(f"Row {idx} ('{company}'): Country cannot be empty.")
                
                # Check Value Proposition length (>= 70 chars)
                vp = data.get('value proposition', '').strip()
                if not vp or vp.upper() == 'NA':
                    errors.append(f"Row {idx} ('{company}'): Value proposition is mandatory and cannot be 'NA'.")
                elif len(vp) < 70:
                    errors.append(f"Row {idx} ('{company}'): Value proposition is too short ({len(vp)} chars). Minimum 70 characters required (conventions.md §3.3).")
                
                # Check Competitors mappings
                competitors = data.get('main competitors', '')
                for comp in [c.strip() for c in competitors.split(',') if c.strip()]:
                    if comp.lower() in FORBIDDEN_COMPETITOR_MAPPINGS:
                        errors.append(f"Row {idx} ('{company}'): Competitor '{comp}' violates conventions: {FORBIDDEN_COMPETITOR_MAPPINGS[comp.lower()]}")
                
                # Check Numeric / NA format for financials
                for fin_col in ['market capitalization', 'funds raised', 'revenue', 'profit']:
                    val = data.get(fin_col, '').strip()
                    if not val:
                        errors.append(f"Row {idx} ('{company}'): Financial column '{fin_col}' is empty. Write 'NA' if data is missing or unknown.")
                    elif val.upper() != 'NA':
                        cleaned = val.replace('$', '').replace(',', '').replace('M', '').replace('B', '').strip()
                        try:
                            num = float(cleaned)
                            if fin_col == 'market capitalization' and num > 500000:
                                errors.append(f"Row {idx} ('{company}'): Valuation M exceeds B limit.")
                        except ValueError:
                            errors.append(f"Row {idx} ('{company}'): '{fin_col}' value '{val}' is not a valid number or 'NA'.")
                            
    except Exception as e:
        errors.append(f"Failed to read file: {e}")
        
    return errors, warnings

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else 'companies_ai_neuroscience_psychology.csv'
    print(f"Auditing '{target}' against Benavent AInetworks conventions...")
    errs, warns = validate_csv(target)
    
    if warns:
        print()
        print('--- WARNINGS ---')
        for w in warns:
            print(f'[!] {w}')
            
    if errs:
        print()
        print('--- ERRORS ---')
        for e in errs:
            print(f'[x] {e}')
        print()
        print(f'Result: FAILED ({len(errs)} error(s), {len(warns)} warning(s))')
        sys.exit(1)
    else:
        print()
        print('Result: PASSED! Zero errors found.')
        if warns:
            print(f'Note: {len(warns)} warning(s) to address before final submission (e.g. reaching 30-40 rows).')
        sys.exit(0)
