from flask import Flask, render_template, request, send_file, session, redirect, url_for
from flask_session import Session
import io
import qrcode
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Set secret key for session signing
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem-based session storage
Session(app)  # Initialize Session extension with the Flask app

# Ticket history storage
ticket_history = []

# Default profile details
profile_details = {
    'conductor_id': 'A125478963',
    'conductor_name': 'Rajesh',
    'bus_no': 'TSXXTSXXXX',
    'upi_id': '9885060183@ybl'
}

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/index')
def index():
    return render_template('login.html')
database={'22r01a0505':'eshwar','22r01a0507':'shivasri','22r01a0512':'rohit','22r01a0506':'swathi'}
@app.route('/form_login',methods=['POST','GET'])
def login():
    name1=request.form['username']
    pwd=request.form['password']
    if name1 not in database:
        return render_template('login.html',info="Invalid User")
    else:
        if database[name1]!=pwd:
            return render_template('login.html',info="Invalid Password")
        else:
            return render_template('index.html',name=name1)
            
@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/profile')
def profile():
    return render_template('profile.html', profile=profile_details)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    profile_details['conductor_id'] = request.form.get('conductor_id')
    profile_details['conductor_name'] = request.form.get('conductor_name')
    profile_details['bus_no'] = request.form.get('bus_no')
    profile_details['upi_id'] = request.form.get('upi_id')
    return redirect(url_for('index'))

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    current = request.form.get('current')
    destination = request.form.get('destination')
    adults = request.form.get('adults')
    child = request.form.get('child')
    female = request.form.get('female')
    price = request.form.get('price')

    # Store input values in session
    session['current'] = current
    session['destination'] = destination
    session['adults']=adults
    session['child']=child
    session['female']=female
    session['price'] = price

    # Retrieve profile details
    conductor_id = profile_details['conductor_id']
    conductor_name = profile_details['conductor_name']
    bus_no = profile_details['bus_no']
    upi_id = profile_details['upi_id']
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f" TSRTC\nPayment Online\n\nBoarding Point: {current}\nDropping Point: {destination}\nPrice: {price}\n\nDate and Time: {now}\n\nConductor ID: {conductor_id}\nConductor Name: {conductor_name}\n\nBus no: {bus_no}"
    upi_url = f"upi://pay?pa={upi_id}&am={price}&pn=Your+Name&mc={message}"

    qr = qrcode.make(upi_url)

    # Convert QR code image to byte stream
    img_byte_array = io.BytesIO()
    qr.save(img_byte_array)
    img_byte_array.seek(0)

    return send_file(img_byte_array, mimetype='image/png')

@app.route('/generate_ticket', methods=['POST'])
def generate_ticket():
    current = session.get('current')
    destination = session.get('destination')
    adults=session.get('adults')
    child=session.get('child')
    female=session.get('female')
    price = session.get('price')
    
    # Retrieve profile details
    conductor_id = profile_details['conductor_id']
    conductor_name = profile_details['conductor_name']
    bus_no = profile_details['bus_no']
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    ticket_details = f"TSRTC\nPayment Successful\n\nBoarding Point: {current}\nDropping Point: {destination}\n\n Adults: {adults}\nChild: {child}\n Female: {female}\nPrice: {price}\n\nDate and Time: {now}\n\nConductor ID: {conductor_id}\nConductor Name: {conductor_name}\n\nBus no: {bus_no}"
    qr = qrcode.make(ticket_details)

    # Convert QR code image to byte stream
    img_byte_array = io.BytesIO()
    qr.save(img_byte_array)  # Save as JPEG image
    img_byte_array.seek(0)
    # Store ticket details in history
    ticket_history.append({
        'current': current,
        'destination': destination,
        'adults': adults,
        'child': child,
        'female': female,
        'price': price,
        'date_time': now
    })

    return send_file(img_byte_array, mimetype='image/png')

@app.route('/history')
def history():
    return render_template('history.html', ticket_history=ticket_history)
if __name__ == '__main__':
    app.run(debug=True)