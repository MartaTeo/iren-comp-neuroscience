#!/usr/bin/env python3
"""
Relational Network Analysis - AI in Neuroscience & Psychology
Extracts directed adjacency matrices, Clout vs. Vulnerability metrics,
investor syndicates, and partner networks from companies_ai_neuroscience_psychology.csv.
Pure Python standard library (no external pip dependencies required).
"""

import csv
import os
from collections import defaultdict

def run_analysis(csv_path='companies_ai_neuroscience_psychology.csv', export_dir='exports'):
    os.makedirs(export_dir, exist_ok=True)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    companies = [r['Company'].strip() for r in rows]
    comp_set = set(companies)
    
    # 1. Adjacency Matrix & Degree Metrics
    matrix = {c: {c2: 0 for c2 in companies} for c in companies}
    in_degree = defaultdict(int)
    out_degree = defaultdict(int)
    investors_map = defaultdict(list)
    partners_map = defaultdict(list)
    
    for r in rows:
        c = r['Company'].strip()
        comps = [x.strip() for x in r['Main competitors'].split(',') if x.strip()]
        invs = [x.strip() for x in r['Main investors'].split(',') if x.strip() and x.strip().upper() != 'NA']
        parts = [x.strip() for x in r['Main partners'].split(',') if x.strip() and x.strip().upper() != 'NA']
        
        for target in comps:
            if target in comp_set:
                matrix[c][target] = 1
                out_degree[c] += 1
                in_degree[target] += 1
                
        for inv in invs:
            investors_map[inv].append(c)
            
        for part in parts:
            partners_map[part].append(c)
            
    # Export Adjacency Matrix
    matrix_csv = os.path.join(export_dir, 'neuro_adjacency_matrix.csv')
    with open(matrix_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company'] + companies)
        for c in companies:
            writer.writerow([c] + [matrix[c][c2] for c2 in companies])
            
    # Export Clout vs Vulnerability
    clout_csv = os.path.join(export_dir, 'neuro_clout_vulnerability.csv')
    clout_ranked = sorted(companies, key=lambda x: (in_degree[x], out_degree[x]), reverse=True)
    with open(clout_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Company', 'Clout (In-Degree / On Other Radars)', 'Vulnerability (Out-Degree / Pressure Felt)'])
        for rank, c in enumerate(clout_ranked, start=1):
            writer.writerow([rank, c, in_degree[c], out_degree[c]])
            
    # Export Investors Summary
    investors_csv = os.path.join(export_dir, 'neuro_investors_summary.csv')
    with open(investors_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Investor', 'Portfolio Count in Vertical', 'Funded Companies'])
        for inv, co_list in sorted(investors_map.items(), key=lambda x: len(x[1]), reverse=True):
            writer.writerow([inv, len(co_list), ', '.join(co_list)])
            
    # Export Partners Summary
    partners_csv = os.path.join(export_dir, 'neuro_partners_summary.csv')
    with open(partners_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Partner Organization', 'Partnership Count in Vertical', 'Partner Companies'])
        for part, co_list in sorted(partners_map.items(), key=lambda x: len(x[1]), reverse=True):
            writer.writerow([part, len(co_list), ', '.join(co_list)])
            
    print(f'==============================================================')
    print(f'RELATIONAL ANALYSIS COMPLETE FOR: {csv_path}')
    print(f'==============================================================')
    print(f'Total Companies Analyzed: {len(companies)}')
    print(f'Adjacency Matrix saved to:   {matrix_csv}')
    print(f'Clout / Vulnerability saved: {clout_csv}')
    print(f'Investor Syndicates saved:  {investors_csv}')
    print(f'Partnership Networks saved: {partners_csv}')
    print()
    print('TOP 10 LEADERS BY COMPETITIVE CLOUT (IN-DEGREE):')
    for rank, c in enumerate(clout_ranked[:10], start=1):
        print(f'  {rank:2d}. {c:<26} | Clout (In): {in_degree[c]:2d} | Vulnerability (Out): {out_degree[c]:2d}')
    print()
    print('TOP 5 MOST ACTIVE VENTURE INVESTORS:')
    for inv, co_list in sorted(investors_map.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f'  - {inv:<28} : {len(co_list)} companies ({', '.join(co_list[:3])}...)')
    print()
    print('TOP 5 STRATEGIC PARTNERS (Hospitals / Big Pharma / Tech):')
    for part, co_list in sorted(partners_map.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f'  - {part:<28} : {len(co_list)} partnerships ({', '.join(co_list[:3])}...)')
    print('==============================================================')

if __name__ == '__main__':
    run_analysis()
