from models import Product, session
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
import os

def add_product(name, price, stock):
    product = Product(name=name, price=price, stock=stock)
    session.add(product)
    session.commit()

def list_products():
    return session.query(Product).all()

def create_receipt_pdf(sale):
    if not os.path.exists("receipts"):
        os.makedirs("receipts")

    filename = f"receipts/receipt_{sale.id}.pdf"
    c = canvas.Canvas(filename, pagesize=A5)

    # Letterhead
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 380, "ＭＡＧＮＡＴＥ")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 365, "where freedom meets purpose")
    c.setFont("Helvetica", 8)
    c.drawString(10, 350, "📍 ROVISTA KENYA | 📞 +254 700 000 000 | ✉️ magnate003@email.com")
    c.drawString(10, 340, "🌐 www.magnaterovista.com")

    # Sale details
    c.setFont("Helvetica", 10)
    c.drawString(10, 320, f"Sale ID: {sale.id}")
    c.drawString(10, 310, f"Date: {sale.date}")
    c.drawString(10, 290, f"Items: {sale.items}")
    c.drawString(10, 270, f"Total: KES {sale.total_amount:.2f}")

    c.save()
    return filename
