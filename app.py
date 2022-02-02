from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
from twilio.rest import Client
import os
from sqlalchemy import true
from werkzeug.utils import secure_filename
import re
import random


app = Flask(__name__)

app.config['UPLOAD_FOLDER']='./static/'
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///store.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Dummy db of all passangers 
class Passengers(db.Model):
    pnr = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(200), nullable=False)

class queue(db.Model):
    pnr = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(200), nullable=False)

class checkedin(db.Model):
    pnr = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String(200), nullable=False)

PNR="8057292953"
otp=123456


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods = ['POST'])
def verify():
    inputpnr = request.form['inputPnr']
    global PNR
    PNR=inputpnr
    print('this is PNR: ', PNR)
    q1=Passengers.query.filter_by(pnr=inputpnr).first()
    if q1:
        getOtpApi(q1.mobile)
        return render_template('verify.html')
    else:
        return render_template('index.html', err="Invalid PNR, Please Try Again!")

@app.route('/validate',methods=['POST'])
def validate():
    global otp
    global PNR
    user_otp=request.form['inputOtp']
    if otp==int(user_otp):
        inQueue = queue.query.filter_by(pnr=PNR).first()
        inCheckedIn = checkedin.query.filter_by(pnr=PNR).first()
        if inQueue:
            return redirect("/status")
        elif inCheckedIn:
            return render_template('checkin.html', msg="checked in")
        else:
            return render_template('checkin.html')            
    return render_template('verify.html', err="Enter valid OTP")

@app.route('/checkin',methods=['POST'])
def checkin():
    global PNR
    checkin = request.form['checkin']
    if checkin == 'Yes':
        query=Passengers.query.filter_by(pnr=PNR).first()
        print(query.pnr, PNR)
        print(PNR)
        q1=queue(pnr=query.pnr, FName=query.FName, LName = query.LName, mobile=query.mobile, Email=query.Email);
        db.session.add(q1)
        db.session.commit()
        return redirect("/status")
    else:
        return redirect("/")

@app.route('/status')
def status():
    global PNR
    allPassengers=queue.query.all()
    idx=0
    for val in allPassengers:
        print(val.pnr, PNR)
        idx+=1
        if(str(val.pnr) == str(PNR)): 
            return render_template('welcome.html', FName=val.FName, LName=val.LName,position=idx, ET=3*idx)
    return render_template('welcome.html')


def generateOtp():
    return random.randrange(100000,999999)

def getOtpApi(number):
    global otp
    # account_sid = 'ACf006b75f5dacb845f0f32f0c533a9d54'
    # auth_token = 'f6711bbd91b72a96438ebe9afff6bacb'
    # client = Client(account_sid,auth_token)
    otp = generateOtp()
    print(otp,number)
    # body = 'Your OTP is '+ str(otp)
    # message = client.messages \
    #             .create(
    #                  body=body,
    #                  from_='+18593405720',
    #                  to='+918057292953'
    #              )
    # # if message.sid:
    # #     return True, otp
    # # else:
    # #     return False, otp
    # return True, otp

if __name__ == "__main__":
    app.run(debug=True, port=8000)
