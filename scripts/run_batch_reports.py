from pathlib import Path
import sys

from src.reports.tearsheet import generate_combined_tearsheets, generate_sector_reports

root = Path(__file__).resolve().parents[1]

print('Running combined tearsheet generation...')
res = generate_combined_tearsheets(output_file=str(root / 'reports' / 'tearsheets' / '_tearsheet.pdf'))
print('Combined result:', res)

print('Generating sector reports...')
sectors = generate_sector_reports()
print('Sector reports generated:', len(sectors))

# verify count of files in reports/tearsheets
tearsheet_dir = root / 'reports' / 'tearsheets'
count = len([p for p in tearsheet_dir.iterdir() if p.suffix.lower() == '.pdf'])
print('tearsheet_pdf_count:', count)

# print skipped file if exists
skipped = root / 'output' / 'skipped_tearsheets.csv'
if skipped.exists():
    print('Skipped tickers written to', skipped)

print('Done.')
sys.exit(0)
