import email
from unicodedata import name
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
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT ='465',
    MAIL_USE_SSL = True, 
    MAIL_USERNAME='*******@gmail.com',
    MAIL_PASSWORD='*******'
)   
app.config['UPLOAD_FOLDER']='./static/'
mail=Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///store.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Dummy db of all passangers 
class Passengers(db.Model):
    pnr = db.Column(db.String, primary_key=True)
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String, nullable=False)
    Email = db.Column(db.String(200), nullable=False)

class queue(db.Model):
    sno = db.Column(db.String, primary_key=True)
    pnr = db.Column(db.String, nullable=False)
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String, nullable=False)
    Email = db.Column(db.String(200), nullable=False)

class checkedin(db.Model):
    pnr = db.Column(db.String, primary_key=True)
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String, nullable=False)
    Email = db.Column(db.String(200), nullable=False)

class staff(db.Model):
    FName = db.Column(db.String(200), nullable=False)
    LName = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String, nullable=False)
    Email = db.Column(db.String(200), primary_key=True)

PNR="329"
otp=123456
Email="hash8647@gmail.com"

#######################
#######################
### ADMIN Interface ###
#######################
#######################

@app.route('/admin/login')
def admin():
    return render_template('index.html',role='admin')


@app.route('/admin/verify', methods = ['POST'])
def admin_verify():
    inputEmail = request.form['inputEmail']
    global Email
    Email=inputEmail

    q1=staff.query.filter_by(Email=inputEmail).first()
    if q1:
        getOtpApiOnEmail(q1.mobile)
        return render_template('verify.html', role='admin')
    else:
        return render_template('index.html', err="Invalid Email, Please Try Again!", role='admin')

@app.route('/admin/validate',methods=['POST'])
def admin_validate():
    global otp
    global Email

    user_otp=request.form['inputOtp']
    if otp==int(user_otp):
        return redirect('/admin/queue')
    return render_template('verify.html', err="Entered OTP does not matches! Please Try Again.")

@app.route('/admin/queue')
def admin_queue():
    global Email
    allUsers = queue.query.all()
    staff_person = staff.query.filter_by(Email=Email).first()
    return render_template('admin.html', allUsers=allUsers, FName=staff_person.FName, LName=staff_person.LName)

@app.route('/admin/checked/<string:pnr>')
def admin_checked_in(pnr):
    del1 = queue.query.filter_by(pnr=pnr).first()
    add1 = checkedin(pnr=del1.pnr, FName=del1.FName, LName = del1.LName, mobile=del1.mobile, Email=del1.Email)
    db.session.add(add1)
    db.session.delete(del1)
    db.session.commit()
    return  redirect('/admin/queue')

@app.route('/admin/notify/<string:pnr>')
def admin_notify(pnr):
    q1 = queue.query.filter_by(pnr=pnr).first()
    notifyUser(q1.mobile)
    return  redirect('/admin/queue')


######################
######################
### USER Interface ###
######################
######################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods = ['POST'])
def verify():
    inputpnr = request.form['inputPnr']
    global PNR
    PNR=inputpnr
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
    return render_template('verify.html', err="Entered OTP does not matches! Please Try Again.")

@app.route('/checkin',methods=['POST'])
def checkin():
    global PNR
    checkin = request.form['checkin']
    if checkin == 'Yes':
        query=Passengers.query.filter_by(pnr=PNR).first()
        q = queue.query.all()
        sz=len(q)+1
        print(sz)
        q1=queue(sno = sz, pnr=query.pnr, FName=query.FName, LName = query.LName, mobile=query.mobile, Email=query.Email);
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
        idx+=1
        if(str(val.pnr) == str(PNR)): 
            return render_template('welcome.html', FName=val.FName, LName=val.LName,position=idx, ET=3*idx)
    return render_template('welcome.html')

########################
########################
### Helper functions ###
########################
########################

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

def notifyUser(number):
    account_sid = 'ACf006b75f5dacb845f0f32f0c533a9d54'
    auth_token = 'f6711bbd91b72a96438ebe9afff6bacb'
    client = Client(account_sid,auth_token)
    body = 'Be ready with your luggage, You are next in the queue! '
    print('notified', number)
    # message = client.messages \
    #             .create(
    #                  body=body,
    #                  from_='+18593405720',
    #                  to='+918057292953'
    #              )
    # if message.sid:
    #     return True, otp
    # else:
    #     return False, otp

def getOtpApiOnEmail(email):
    global otp
    # account_sid = 'ACf006b75f5dacb845f0f32f0c533a9d54'
    # auth_token = 'f6711bbd91b72a96438ebe9afff6bacb'
    # client = Client(account_sid,auth_token)
    otp = generateOtp()
    print(otp,email)
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


    # passenger1 = Passengers(pnr=789, FName="Yash", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger2 = Passengers(pnr=989, FName="Hash", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger3 = Passengers(pnr=889, FName="Jash", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger4 = Passengers(pnr=459, FName="Tash", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger5 = Passengers(pnr=765, FName="Abc", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger6 = Passengers(pnr=754, FName="XYz", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger7 = Passengers(pnr=129, FName="test", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # passenger8 = Passengers(pnr=329, FName="test2", LName = "Mittal", mobile= '+918057292953', Email="qwerty@gmail.com")
    # db.session.add(passenger1)
    # db.session.add(passenger2)
    # db.session.add(passenger3)
    # db.session.add(passenger4)
    # db.session.add(passenger5)
    # db.session.add(passenger6)
    # db.session.add(passenger7)
    # db.session.add(passenger8)
    # db.session.commit()


    # staff1 = staff(FName="test", LName="user1", mobile="+918057292953", Email="hash8647@gmail.com")
    # staff2 = staff(FName="test", LName="user2", mobile="+918057292953", Email="yashmittal8017@gmail.com")
    # staff3 = staff(FName="test", LName="user3", mobile="+918057292953", Email="yash.mittal7417@gmail.com")
    # db.session.add(staff1)
    # db.session.add(staff2)
    # db.session.add(staff3)
    # db.session.commit()
    






if __name__ == "__main__":
    app.run(debug=True, port=8000)
