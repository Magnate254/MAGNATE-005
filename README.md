# MAGNATE POS (Streamlit)

A simple Point of Sale system built with Streamlit + SQLite, branded for **MAGNATE**.

## Features
- Product management (add, view, stock)
- POS checkout with receipts (PDF with MAGNATE letterhead)
- Sales tracking & reports
- SQLite database (persistent)

## Setup
```bash
git clone <your-repo>
cd magnate_pos_streamlit
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
