import streamlit as st
import sqlite3
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Register Unicode font (so receipts support all characters)
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

DB_FILE = "pos.db"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 price REAL NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_id INTEGER,
                 quantity INTEGER,
                 total REAL,
                 date TEXT,
                 FOREIGN KEY(product_id) REFERENCES products(id))''')
    conn.commit()
    conn.close()

# ---------- Product Management ----------
def add_product(name, price):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return products

# ---------- Sales Management ----------
def record_sale(product_id, quantity, total):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
              (product_id, quantity, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_sales():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT s.id, p.name, s.quantity, s.total, s.date FROM sales s JOIN products p ON s.product_id = p.id")
    sales = c.fetchall()
    conn.close()
    return sales

# ---------- Receipt Generator ----------
def generate_receipt(sale_items, total_amount, discount=0, vat=0.16):
    filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>POS RECEIPT</b>", styles['Title']))
    story.append(Paragraph("Customer Receipt", styles['Heading2']))
    story.append(Spacer(1, 12))

    for item in sale_items:
        story.append(Paragraph(f"{item[1]} x {item[2]} = {item[3]:.2f}", styles['Normal']))

    story.append(Spacer(1, 12))

    discounted_total = total_amount - discount
    vat_amount = discounted_total * vat
    final_total = discounted_total + vat_amount

    story.append(Paragraph(f"Subtotal: {total_amount:.2f}", styles['Normal']))
    story.append(Paragraph(f"Discount: {discount:.2f}", styles['Normal']))
    story.append(Paragraph(f"VAT (16%): {vat_amount:.2f}", styles['Normal']))
    story.append(Paragraph(f"<b>Total: {final_total:.2f}</b>", styles['Heading2']))

    doc.build(story)
    return filename

# ---------- Streamlit App ----------
def main():
    st.title("💰 SIMPLE POS SYSTEM")

    menu = ["Products", "Sales", "Reports"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Products":
        st.subheader("Manage Products")
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            price = st.number_input("Price", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Product")
            if submitted and name:
                add_product(name, price)
                st.success(f"Added {name} at {price}")

        products = get_products()
        st.write("### Product List")
        st.table(products)

    elif choice == "Sales":
        st.subheader("Record Sale")
        products = get_products()
        if not products:
            st.warning("⚠️ No products available. Please add products first.")
            return

        product_dict = {p[1]: (p[0], p[2]) for p in products}
        product_name = st.selectbox("Select Product", list(product_dict.keys()))
        quantity = st.number_input("Quantity", min_value=1, step=1)
        if st.button("Record Sale"):
            product_id, price = product_dict[product_name]
            total = price * quantity
            record_sale(product_id, quantity, total)
            st.success(f"Sale recorded: {product_name} x {quantity} = {total:.2f}")

            sale_items = [(product_id, product_name, quantity, total)]
            receipt = generate_receipt(sale_items, total)
            with open(receipt, "rb") as f:
                st.download_button("Download Receipt", f, file_name=receipt)

    elif choice == "Reports":
        st.subheader("Sales Report")
        sales = get_sales()
        st.table(sales)

if __name__ == "__main__":
    init_db()
    main()
