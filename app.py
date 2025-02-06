from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from fpdf import FPDF
import razorpay
import uuid
import os
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key
db = SQLAlchemy(app)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'achhutanandjha1@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'awur ojsz gshw ztjq'  # Replace with your app password

mail = Mail(app)

# Replace with your Razorpay API keys
RAZORPAY_API_KEY = os.environ.get('RAZORPAY_API_KEY', 'rzp_test_UASg8QDyHDXQkz')
RAZORPAY_API_SECRET = os.environ.get('RAZORPAY_API_SECRET', 'im3zYBK6PuIoZ6dS1LhlMQDj')

class Item(db.Model):
    barcode = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Item {self.name}>'

# PDF Generation Function
def generate_pdf_receipt(items, total_price, email):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="Receipt", ln=1, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(200, 10, txt="Your Purchase", ln=1, align="C")
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(60, 10, "Barcode", border=1, align="C")
    pdf.cell(80, 10, "Name", border=1, align="C")
    pdf.cell(50, 10, "Price", border=1, align="C")
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", size=12)
    for item in items:
        pdf.cell(60, 10, item['barcode'], border=1, align="C")
        pdf.cell(80, 10, item['name'], border=1, align="C")
        pdf.cell(50, 10, f"${item['price']:.2f}", border=1, align="C")
        pdf.ln()

    pdf.ln(10)
    pdf.set_font("Arial", size=12, style='B')
    pdf.cell(0, 10, txt=f"Total Price: ${total_price:.2f}", ln=1, align="R")

    now = datetime.datetime.now()
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Date and Time: {date_time_str}", ln=1, align="R")

    # Save PDF temporarily (using email as part of filename for uniqueness)
    pdf_filename = f"receipt_{email.replace('@','_').replace('.','_')}.pdf"  # Unique filename
    pdf_path = os.path.join(app.root_path, pdf_filename)  # Save in app's directory
    pdf.output(pdf_path)
    return pdf_path  # Return the path to the PDF

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'search' in request.form:
            barcode = request.form['barcode']
            item = Item.query.filter_by(barcode=barcode).first()
            if item:
                session.setdefault('items', [])
                if not any(i['barcode'] == item.barcode for i in session['items']):
                    session['items'].append({'barcode': item.barcode, 'name': item.name, 'price': item.price})
                    flash('Item added to cart!')
                else:
                    flash('Item already in cart.')
            else:
                flash('Item not found.')
        elif 'add' in request.form:
            try:
                new_item = Item(
                    barcode=request.form['new_barcode'],
                    name=request.form['new_name'],
                    price=float(request.form['new_price'])  # Ensure price is a float
                )
                db.session.add(new_item)
                db.session.commit()
                flash('Item added successfully!')
            except ValueError:
                flash('Invalid price entered. Please enter a valid number.')
            except Exception as e:
                flash(f'Error adding item: {str(e)}')

    items = session.get('items', [])
    total_price = sum(item['price'] for item in items)

    return render_template('index.html', items=items, total_price=total_price)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/proceed_to_payment', methods=['POST'])
def proceed_to_payment():
    if 'items' not in session or not session['items']:
        flash('No items in cart.')
        return redirect(url_for('index'))

    email = request.form.get('email')
    if not email:
        flash('Please provide an email address.')
        return redirect(url_for('index'))

    # Store email in session for later use
    session['email'] = email

    # Generate and send receipt email
    items = session['items']
    total_price = sum(item['price'] for item in items)
    pdf_path = generate_pdf_receipt(items, total_price, email)

    try:
        msg = Message("Your Purchase Receipt", sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = "Thank you for your purchase! Please find your receipt attached."
        with open(pdf_path, "rb") as f:
            msg.attach("receipt.pdf", "application/pdf", f.read())
        mail.send(msg)
        flash('Receipt sent successfully!')
    except Exception as e:
        flash(f'Error sending receipt: {str(e)}')

    # Clean up the PDF file after sending
    os.remove(pdf_path)

    # Proceed to payment
    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))

    # Generate a receipt ID that is exactly 40 characters long
    receipt_id = str(uuid.uuid4()).replace('-', '')[:40]  # Remove dashes and slice to 40 characters

    order_data = {
        'amount': int(total_price * 100),  # Amount in paise
        'currency': 'INR',
        'receipt': receipt_id,  # Use the generated receipt ID
        'payment_capture': 1
    }

    try:
        response = client.order.create(order_data)
        order_id = response['id']
        order_options = {
            'key': RAZORPAY_API_KEY,
            'amount': response['amount'],
            'currency': response['currency'],
            'name': 'Your Company',
            'description': 'Order for items in your cart',
            'order_id': order_id,
            'handler': url_for('verify', _external=True),
            'theme': {
                'color': '#F37254'
            }
        }
        return render_template('payment.html', order_options=order_options)
    except Exception as e:
        flash(f'Error creating payment: {str(e)}')
        return redirect(url_for('index'))

@app.route('/verify', methods=['POST'])
def verify():
    response = request.form
    payment_id = response.get('razorpay_payment_id')
    order_id = response.get('razorpay_order_id')
    signature = response.get('razorpay_signature')

    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        flash('Payment successful! Your order will be processed shortly.')
    except Exception as e:
        flash('Payment verification failed. Please try again.')

    return redirect(url_for('index'))

@app.route('/print_receipt', methods=['GET'])
def print_receipt():
    if 'items' not in session or not session['items']:
        flash('No items in cart to print receipt.')
        return redirect(url_for('index'))

    items = session['items']
    total_price = sum(item['price'] for item in items)

    return render_template('receipt.html', items=items, total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)