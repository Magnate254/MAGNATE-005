import streamlit as st
from db import init_db
from utils import add_product, list_products, create_receipt_pdf
from models import Product, Sale, session
import datetime

st.set_page_config(page_title="MAGNATE POS", page_icon="💳", layout="wide")

# Company branding
st.image("assets/logo.png", width=100)
st.markdown("## ＭＡＧＮＡＴＥ")
st.caption("where freedom meets purpose")
st.write("📍 ROVISTA KENYA | 📞 +254 700 000 000 | ✉️ magnate003@email.com | 🌐 www.magnaterovista.com")

# Sidebar navigation
menu = st.sidebar.radio("Menu", ["Dashboard", "Products", "POS / Sell", "Reports"])

init_db()

if menu == "Dashboard":
    st.subheader("📊 Dashboard")
    sales = session.query(Sale).all()
    total_sales = sum([s.total_amount for s in sales])
    st.metric("Total Sales", f"KES {total_sales:.2f}")
    st.metric("Number of Sales", len(sales))

elif menu == "Products":
    st.subheader("📦 Products")
    with st.form("add_product"):
        name = st.text_input("Product Name")
        price = st.number_input("Price (KES)", min_value=0.0, step=0.01)
        stock = st.number_input("Stock", min_value=0, step=1)
        submitted = st.form_submit_button("Add Product")
        if submitted:
            add_product(name, price, stock)
            st.success(f"{name} added successfully!")

    st.write("### Product List")
    products = list_products()
    st.table([{"Name": p.name, "Price": p.price, "Stock": p.stock} for p in products])

elif menu == "POS / Sell":
    st.subheader("💳 Point of Sale")
    products = list_products()
    cart = []
    for p in products:
        qty = st.number_input(f"{p.name} (Stock: {p.stock})", min_value=0, max_value=p.stock, step=1, key=f"cart_{p.id}")
        if qty > 0:
            cart.append((p, qty))

    if st.button("Checkout"):
        if not cart:
            st.warning("No items in cart")
        else:
            total = sum([p.price * qty for p, qty in cart])
            sale = Sale(
                date=datetime.datetime.now(),
                items=",".join([f"{p.name}x{qty}" for p, qty in cart]),
                total_amount=total
            )
            session.add(sale)
            for p, qty in cart:
                p.stock -= qty
            session.commit()
            create_receipt_pdf(sale)
            st.success(f"Sale recorded. Total: KES {total:.2f}. Receipt saved.")

elif menu == "Reports":
    st.subheader("📑 Sales Reports")
    sales = session.query(Sale).all()
    st.table([{"Date": s.date, "Items": s.items, "Total": s.total_amount} for s in sales])
