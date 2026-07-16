# Project Title

# Nifty 100 Financial Analytics Platform

# Project Overview
This project is a Financial Analytics Platform built using Python, SQLite, Pandas, Plotly, and Streamlit. It provides financial ratio analysis, stock screening, peer comparison, valuation analysis, and an interactive dashboard for Nifty 100 companies.

# Technologies Used
- Python
- SQLite
- Pandas
- NumPy
- Plotly
- Streamlit
- Pytest
- OpenPyXL
- Git & GitHub

# Project Structure
src/
│
├── analytics/
├── dashboard/
├── screener/
├── etl/

output/

tests/

nifty100.db
README.md

# Install Requirements
pip install -r requirements.txt

# Run ETL
python src/db_loader.py

# Run Dashboard
python -m streamlit run src/dashboard/app.py

# Run Tests
python -m pytest

# Dashboard Screen Descriptions

## Dashboard Screens

### Home
Displays overall financial summary, KPI cards, sector distribution, and top-performing companies.

### Company Profile
Shows company details, profitability metrics, historical trends, and business overview.

### Screener
Filters companies using multiple financial criteria and exports results.

### Peer Comparison
Compares companies within the same peer group using KPI tables and radar charts.

### Trend Analysis
Displays historical trends of financial metrics using interactive Plotly charts.

### Sector Analysis
Provides sector-wise comparison using bubble charts and KPI summaries.

### Capital Allocation
Visualizes company capital allocation patterns using treemaps.

### Annual Reports
Displays company-wise annual report links and available reporting years.

## Sprint 4 Retrospective

### UX Decisions
- Used Streamlit sidebar navigation for quick page switching.
- Implemented responsive Plotly charts with automatic width adjustment.
- Added CSV export functionality for screener results.
- Used user-friendly messages for missing data instead of errors.

### Data Edge Cases
- Companies with incomplete historical data display available information without crashing.
- Missing financial values are shown as "N/A".
- Annual reports gracefully handle unavailable documents.
- Sector-specific valuation logic was implemented using sector median P/E.

### Performance Findings
- Dashboard loads successfully within acceptable response times.
- Database queries are cached where appropriate.
- Interactive visualizations remain responsive across supported datasets.