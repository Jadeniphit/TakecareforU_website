#app.py
from turtle import distance
from flask import Flask, request, session, redirect, url_for, render_template,jsonify, Response,make_response
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
import pymysql 
import re
import json
import sqlite3
import requests
import cv2
from geopy.geocoders import GoogleV3
import mysql.connector
import base64
import time
import uuid

import torch

import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import plotly.express as px
import pandas as pd

from django.http import HttpResponse
from django.template import loader
 
app = Flask(__name__)
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'Takecareforu'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/takecareforu'  # ปรับให้เข้ากับฐานข้อมูลของคุณ
db = SQLAlchemy(app)

 
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'takecareforu'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



# Function to capture frames from the driver's camera
def capture_frame():
    camera = cv2.VideoCapture(0)  # 0 indicates the default camera (usually the built-in webcam)
    
    while True:
        # Read a frame from the camera
        ret, frame = camera.read()
        
        if ret:
            # Encode the frame as JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            
            if ret:
                # Convert the JPEG data to bytes
                frame_bytes = jpeg.tobytes()
                
                # Yield the frame bytes as a response to the client
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
        else:
            break
    
    # Release the camera
    camera.release()

@app.route('/cameratest')
def cameratest():
    return render_template('cameratest.html')

@app.route('/video_feed')
def video_feed():
    return Response(capture_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')




 
# http://localhost:5000/pythonlogin/ - this will be the login page
@app.route('/user_login/', methods=['GET', 'POST'])
def login():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
   
    # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            #return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    
    return render_template('index.html', msg=msg)

@app.route('/Rider_login/', methods=['GET', 'POST'])
def Riderlogin():
    # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM drivers WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
   
        # If account exists in accounts table in out database and status is active
        if account and account['status'] == 'active':
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            #return 'Logged in successfully!'
            return redirect(url_for('riderhome'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password or account is inactive!'
    
    return render_template('Riderlogin.html', msg=msg)
 
# http://localhost:5000/register - this will be the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
   
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s)', (fullname, username, password, email)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/registerdriver', methods=['GET', 'POST'])
def registerdriver():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        cartype = request.form['cartype']
        license = request.form['license']
        profile_image = request.files['profile_image']
        vehicle_plate = request.form['vehicle_plate']
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM drivers WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO drivers VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, NOT NULL, %s, %s)', (username, password, email, name, phone, cartype, license,profile_image,vehicle_plate)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registerdriver.html', msg=msg)
  
# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
   
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/riderhome')
def riderhome():
    # Check if user is loggedin
    if 'loggedin' in session:
   
        # User is loggedin show them the home page
        return render_template('riderhome.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
  
# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/gps')
def gps():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('automatic.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/Service charge')
def svcost():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('svcost.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
@app.route('/Aboutus')
def aboutus():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('aboutus.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/Rider')
def Rider():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('wRider.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/Rider_com')
def Rider_com():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('CompanyRider.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/User_Waiting_Room2')
def User_Waiting_Room2():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('user_waiting_room.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/User_Waiting_Room3')
def User_Waiting_Room3():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # Check if user is logged in
    if 'loggedin' in session:
        # User is logged in
        # Query the service_userinfo table to check the status based on the latest id
        query = f"SELECT status FROM service_userinfo WHERE id = (SELECT MAX(id) FROM service_userinfo)"
        cursor.execute(query)
        status = cursor.fetchone()

        if status and status['status'] == 'waiting':
            # User is waiting, show the waiting room page
            return render_template('user_waiting_room.html', username=session['username'])
        elif status and status['status'] == 'accepted':
            # Status changed to accepted, redirect to another page
            return redirect(url_for('driver_info'))
    
    # User is not logged in or status is not waiting or accepted, redirect to login page
    return redirect(url_for('login'))

@app.route('/User_Waiting_Room')
def User_Waiting_Room():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # Check if user is logged in
    if 'loggedin' in session:
        # User is logged in
        # Query the service_userinfo table to check the status based on the latest id
        query = f"SELECT status FROM service_userinfo WHERE id = (SELECT MAX(id) FROM service_userinfo)"
        cursor.execute(query)
        status = cursor.fetchone()

        if status and status['status'] == 'waiting':
            # User is waiting, show the waiting room page
            return render_template('user_waiting_room.html', username=session['username'])
        elif status and status['status'] == 'accepted':
            # Status changed to accepted, redirect to received_jobs_details page with job_id parameter
            query = f"SELECT MAX(id) FROM received_jobs"
            cursor.execute(query)
            job_id = cursor.fetchone()['MAX(id)']
            return redirect(url_for('received_jobs_details', job_id=job_id))

    # User is not logged in or status is not waiting or accepted, redirect to login page
    return redirect(url_for('login'))


# ...
@app.route('/received_jobs/<int:job_id>')
def received_jobs_details(job_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Query the received_jobs table
    query = f"SELECT * FROM received_jobs WHERE id = {job_id}"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        # Separate the job details from the result
        job = {key: result[key] for key in result if not key.startswith('customer_')}

        # Get the customer ID from the job details
        customer_id = result['customer_id']

        # Query the service_userinfo table to get customer details based on the customer_id
        query = f"SELECT * FROM service_userinfo WHERE id = {customer_id}"
        cursor.execute(query)
        customer = cursor.fetchone()

        # Query the drivers_cams table to get driver video based on the driver_id
        driver_id = result['driver_id']
        query = f"SELECT * FROM drivers_cams WHERE driver_id = {driver_id} ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        driver = cursor.fetchone()

        # Render the job details, customer details, and driver details
        return render_template('received_jobs_details.html', job=job, customer=customer, driver=driver)

    # Job not found, redirect to another page or display an error message
    return redirect(url_for('other_page'))



@app.route('/Savelocation')
def savelocation():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('save_location.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/Contactus', methods=['GET', 'POST'])
def contactus():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST':
            fullname = request.form['name']
            email = request.form['email']
            subjects = request.form['subject']
            messages = request.form['message']
            cursor.execute("INSERT INTO report VALUES (NULL,%s,%s,%s,%s)", (fullname,email,subjects,messages))
            conn.commit()
            msg = 'Successfully!'
            return redirect(url_for('contactus'))
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('contact.html', msg=msg)
    return redirect(url_for('login'))

 
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT valuedistance FROM service_userinfo ORDER BY id DESC ')
    data1 = cursor.fetchmany()
    cursor.execute('SELECT service_type,service_equipment FROM service_charge ORDER BY service_id DESC ')
    data = cursor.fetchmany()
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST':
            Cardholder = request.form['Cardholder']
            CardNumber = request.form['Cardnumber']
            exdate = request.form['exdate']
            cvv = request.form['cvv']
            #service_price = request.form['tot_amount']
            #equipment_price = request.form['tot_amount2']
            totalprice = request.form['total1']
            cursor.execute("INSERT INTO payment VALUES (NULL,NULL,%s,%s,%s,%s,%s)", (Cardholder,CardNumber,exdate,cvv,totalprice))
            conn.commit()
            msg = 'Successfully!'
            time.sleep(2)
            return redirect(url_for('home'))
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('payment.html', msg=msg,service_charge=data,service_userinfo=data1)
    return redirect(url_for('login'))

@app.route('/contact', methods=['GET', 'POST'])
def contact(): 
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'age' in request.form and 'phone' in request.form and 'height' in request.form :
            # Create variables for easy access
            firstname = request.form['first_name']
            lastname = request.form['last_name']
            age = request.form['age']
            gender = request.form['gender']
            weight = request.form['weight']
            height = request.form['height']
            phone = request.form['phone']
            sick = request.form['sick']
    
            #Check if account exists using MySQL
            cursor.execute('SELECT * FROM service_userinfo WHERE phone = %s', (phone))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Phone already exists!'
            elif not phone or not height or not weight:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute("INSERT INTO service_userinfo VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)", (firstname,lastname,age,gender,weight,height,phone,sick))
                conn.commit()
                msg = 'Successfully!'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('test.html', msg=msg)
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile(): 
 # Check if account exists using MySQL
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/getstart', methods=['GET', 'POST'])
def getstart(): 
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST':
            firstname = request.form['first_name']
            lastname = request.form['last_name']
            age = request.form['age']
            gender = request.form['gender']
            weight = request.form['weight']
            height = request.form['height']
            phone = request.form['phone']
            sick = request.form['sick']
            starts = request.form['starts']
            Ends = request.form['Ends']
            service_type = request.form['sv_type']
            service_equipment = request.form['sv_eqm']
            valuedistance = request.form['realdis']
            #valueprice = request.form['realprice']
            cursor.execute("INSERT INTO service_userinfo VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'waiting')", (firstname,lastname,age,gender,weight,height,phone,sick,starts,Ends,valuedistance))#valuedistance,#valueprice))
            cursor.execute("INSERT INTO service_charge VALUES (NULL,NOT NULL,%s,%s)", (service_type,service_equipment))
            conn.commit()
            msg = 'Successfully!'
            return redirect(url_for('payment'))
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('backup.html', msg=msg)
    return redirect(url_for('login'))
  
  
  
@app.route('/teststart', methods=['GET', 'POST'])
def teststart(): 
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        # Output message if something goes wrong...
        msg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'age' in request.form and 'phone' in request.form and 'height' in request.form :
            # Create variables for easy access
            firstname = request.form['first_name']
            lastname = request.form['last_name']
            age = request.form['age']
            gender = request.form['gender']
            weight = request.form['weight']
            height = request.form['height']
            phone = request.form['phone']
            sick = request.form['sick']
            starts = request.form['starts']
            Ends = request.form['Ends']
            valuedistance = request.form['valuedistance']
            valueprice = request.form['valueprice']
    
            #Check if account exists using MySQL
            cursor.execute('SELECT * FROM service_userinfo WHERE phone = %s', (phone))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Phone already exists!'
            elif not phone or not height or not weight:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute("INSERT INTO service_userinfo VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (firstname,lastname,age,gender,weight,height,phone,sick,starts,Ends,valuedistance,valueprice))
                conn.commit()
                msg = 'Successfully!'
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('getstart3.html', msg=msg)
    return redirect(url_for('login'))

@app.route('/showmap', methods=['GET', 'POST'])  
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/add_location', methods=['POST'])
def add_location():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # รับค่าละติจูดและลองจิจูดจากการ POST
    name = request.form.get("name")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    # เตรียมข้อมูล SQL สำหรับเพิ่มข้อมูลในฐานข้อมูล
    cursor = conn.cursor()
    sql = "INSERT INTO locations (name, latitude, longitude) VALUES (%s, %s, %s)"
    val = (name, latitude, longitude)

    # ส่งคำสั่ง SQL ไปยังฐานข้อมูล
    cursor.execute(sql, val)
    conn.commit()

    return "Location saved successfully"

@app.route('/customer/<int:id>', methods=['GET'])
def get_customer_location(id):
    # connect to MySQL
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # get the customer location from the database
    cursor.execute("SELECT * FROM service_userinfo WHERE id=%s", id)
    service_userinfo = cursor.fetchone()
    
    # close the database connection
    cursor.close()
    conn.close()

    # return the customer location as a JSON object
    return jsonify(service_userinfo)

# API endpoint for retrieving customer locations
@app.route('/api/customers')
def get_customers():
    # Connect to the MySQL database
    conn = mysql.connect()
    # Query the customer locations
    cursor = conn.cursor()
    query = ("SELECT name, latitude, longitude FROM locations")
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Create a list of dictionaries representing the customer locations
    customers = []
    for row in rows:
        customer = {'name': row[0], 'lat': row[1], 'lng': row[2]}
        customers.append(customer)
    
    # Close the database connection
    cursor.close()
    conn.close()
    
    # Return the customer locations as JSON
    return jsonify(customers)

@app.route('/map')
def map():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('map.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


API_KEY = "AIzaSyBRaJ0a97IIUUJLv00Cqbaxcg9ndlLQvyE"
@app.route('/api/customers2')
def get_customers2():
    # Connect to the MySQL database
    conn = mysql.connect()
    # Query the customer locations
    cursor = conn.cursor()
    query = ("SELECT id,firstname, starts, status FROM service_userinfo")
    cursor.execute(query)
    rows = cursor.fetchall()

    # Create a list of dictionaries representing the customer locations
    customers = []
    for row in rows:
        # Geocode the address to get latitude and longitude
        address = row[2]
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}'
        response = requests.get(geocode_url)
        data = response.json()
        if data['status'] == 'OK':
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            customer = {'id': row[0], 'name': row[1],'address': row[2], 'lat': lat, 'lng': lng, 'status': row[3]}
            customers.append(customer)
    
    # Close the database connection
    cursor.close()
    conn.close()

    # Return the customer locations as JSON
    return jsonify(customers)



@app.route('/map2')
def map2():
    job_id = request.args.get('job_id')
    return '''<!DOCTYPE html>
<html>
<head>
<title>Take Care for U</title>
<style>
/* Set the size of the map */
#map {
  height: 600px;
  width: 80%;
  background-color: green; /* เพิ่มสีพื้นหลังเป็นสีเขียว */
}
body {
      background-color: #CFFF8D;
    }
h2 {
      color: #425F57;
      font-weight: bold;
    }
</style>
</head>
<body background="static\img\BG001.png">
<center><h2>Customer Location</h2></center>
<center><div id="map"></div></center>
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBRaJ0a97IIUUJLv00Cqbaxcg9ndlLQvyE"></script>
<script>
  // Make an AJAX request to the API endpoint to get the customer locations
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/api/customers2', true);
  xhr.onload = function() {
    // Parse the JSON response and extract the customer locations
    var customers = JSON.parse(xhr.responseText);
    
    // Initialize and display the map
    initMap(customers);
  };
  xhr.send();

  // Initialize and display the map using the customer locations
  function initMap(customers) {
    // Set the coordinates of the customer location
    var customerLoc = { lat: 13.286123168758246, lng: 100.92591672517473 };
    
    // Create a new map centered at the customer location
    var map = new google.maps.Map(document.getElementById("map"),{
      center: customerLoc,
      zoom: 14,
    });
    
    // Loop through the customers array and add a marker for each customer
    for (let i = 0; i < customers.length; i++) {
      const customer = customers[i];
      const latLng = new google.maps.LatLng(customer.lat, customer.lng);
      const marker = new google.maps.Marker({
        position: latLng,
        map: map,
      });
      
      // Add a click event listener to the marker
      marker.addListener("click", function () {
        // Show the customer name in an info window
        const infowindow = new google.maps.InfoWindow({
         content: `<h3>${customer.name}</h3><p>${customer.address}</p><p>Status: ${customer.status}</p>
            <form id="accept-job-form" method="POST" action="/api/update_customer_status">
                <input type="hidden" name="id" value="${customer.id}">
                <input type="hidden" name="status" value="accepted">
                <button type="submit">Accept Job</button>
            </form>`,
        });

        infowindow.open(map, marker);
        
        // Add a click event listener to the submit button in the info window
        document.getElementById("accept-job-form").addEventListener("submit", function(event) {
          event.preventDefault();
          acceptJob(customer.id, infowindow);
        });
      });
    }
  }
  
  function acceptJob(customerId, infowindow) {
  // Send a POST request to your API endpoint to accept the job with the given customer ID
  fetch('/api/accept_job', {
    method: 'POST',
    body: new FormData(document.getElementById('accept-job-form')),
  })
  .then(response => {
    if (response.ok) {
      // Update the info window to show that the job has been accepted
      infowindow.setContent(`<h3>${customer.name}</h3><p>${customer.address}</p><p>Status: accepted</p>`);
      // Update the status of the customer in the service_userinfo table
      fetch(`/api/update_customer_status?id=${customerId}&status=accepted`)
        .then(response => {
          if (!response.ok) {
            console.log('Error updating customer status:', response.statusText);
          }
        })
        .catch(error => {
          console.log('Network error:', error);
        });
    } else {
      // Handle the error response
      console.log('Error accepting job:', response.statusText);
    }
  })
  .catch(error => {
    // Handle the network error
    console.log('Network error:', error);
  });
}


</script>
</body>
</html> '''

@app.route('/api/accept_job', methods=['POST'])
def accept_job():
    job_id = request.form['job_id']
    
    # Update the status of the customer in the service_userinfo table
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "UPDATE service_userinfo SET status = 'accepted' WHERE id = %s"
    cursor.execute(query, (job_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/accept_job2', methods=['POST'])
def accept_job2():
    job_id = request.form['job_id']
    
    # Update the status of the customer in the service_userinfo table
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "UPDATE service_userinfo SET status = 'accepted' WHERE id = %s"
    cursor.execute(query, (job_id,))
    conn.commit()

    # Get the driver's information based on the user who accepted the job
    query = "SELECT * FROM drivers WHERE username = %s"
    cursor.execute(query, (session['username'],))
    driver_data = cursor.fetchone()

    if driver_data:
        # Insert data into the received_jobs table using the driver's information
        query = "INSERT INTO received_jobs (driver_name, phone_number, car_type) VALUES (%s, %s, %s)"
        cursor.execute(query, (driver_data['name'], driver_data['phone'], driver_data['car_type']))
        conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'success': True})


@app.route('/api/update_customer_status2', methods=['POST'])
def update_customer_status2():
    # Get the customer ID and status from the request
    customer_id = request.form.get('id')
    status = request.form.get('status')

    # Update the customer status in the database
    conn = mysql.connect()
    cursor = conn.cursor()
    query = f"UPDATE service_userinfo SET status='{status}' WHERE id='{customer_id}'"
    cursor.execute(query)
    conn.commit()

    # Retrieve the updated customer information
    query = f"SELECT * FROM service_userinfo WHERE id='{customer_id}'"
    cursor.execute(query)
    customer = cursor.fetchone()

    # Get the driver's information based on the user who accepted the job
    query = "SELECT * FROM drivers WHERE username = %s"
    cursor.execute(query, (session['username'],))
    driver_data = cursor.fetchone()

    if driver_data:
        # Insert data into the received_jobs table using the driver's information
        query = "INSERT INTO received_jobs (driver_name, phone_number, car_type, vehicle_plate, profile_image) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (driver_data[4], driver_data[5], driver_data[6], driver_data[10], driver_data[9]))
        conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Create the customer info dictionary
    customer_info = {
        'customer': customer,
        'driver_data': driver_data
    }
    print(customer_info)
    # Return JSON response
    response = jsonify({'success': True})

    # Render the customer information in a new template
    return render_template('customer_info.html', customer=customer, response=response)


@app.route('/api/update_customer_status', methods=['POST'])
def update_customer_status():
    # Get the customer ID and status from the request
    customer_id = request.form.get('id')
    status = request.form.get('status')

    # Update the customer status in the database
    conn = mysql.connect()
    cursor = conn.cursor()
    query = f"UPDATE service_userinfo SET status='{status}' WHERE id='{customer_id}'"
    cursor.execute(query)
    conn.commit()

    # Retrieve the updated customer information
    query = f"SELECT * FROM service_userinfo WHERE id='{customer_id}'"
    cursor.execute(query)
    customer = cursor.fetchone()

    # Get the driver's information based on the user who accepted the job
    query = "SELECT * FROM drivers WHERE username = %s"
    cursor.execute(query, (session['username'],))
    driver_data = cursor.fetchone()

    if driver_data:
        # Check if the received job for the customer already exists in the received_jobs table
        query = "SELECT * FROM received_jobs WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        existing_job = cursor.fetchone()

        if not existing_job:
            # Insert data into the received_jobs table using the driver's information and customer ID
            query = "INSERT INTO received_jobs (driver_name, phone_number, car_type, vehicle_plate, profile_image, customer_id,driver_id) VALUES (%s, %s, %s, %s, %s, %s,%s)"
            cursor.execute(query, (driver_data[4], driver_data[5], driver_data[6], driver_data[10], driver_data[9], customer_id,driver_data[0]))
            conn.commit()


    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Create the customer info dictionary
    customer_info = {
        'customer': customer,
        'driver_data': driver_data
    }

    # Return JSON response
    response = jsonify({'success': True})

    # Render the customer information in a new template
    return render_template('customer_info.html', customer=customer, customer_info=customer_info, response=response)



@app.route('/finish_job', methods=['POST'])
def finish_job():
    customer_id = request.form.get('customer_id')
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    # Delete the customer data from the database
    delete_query = "DELETE FROM service_userinfo WHERE id = %s"
    cursor.execute(delete_query, (customer_id,))
    conn.commit()

    cursor.close()
    conn.close()
    
    return jsonify({"status": "success"})

def generate_unique_filename():
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4().hex)
    filename = f"{timestamp}_{unique_id}.png"  # แก้ไขนามสกุลไฟล์ตามที่คุณต้องการ
    return filename




@app.route('/save_image', methods=['POST'])
def save_image_to_db():
    # Get the image data from the request
    image_data = request.form['imageData']

    # Get the username from session
    username = session.get('username')

    # Retrieve the driver's information based on the username
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT id FROM drivers WHERE username = %s"
    cursor.execute(query, (username,))
    driver_data = cursor.fetchone()

    if driver_data:
        driver_id = driver_data[0]

        # Convert the image data from base64 to binary
        image_binary = base64.b64decode(image_data.split(',')[1])

        # Generate a unique filename (e.g., using timestamp or unique identifier)
        filename = generate_unique_filename()

        # Save the image to the database
        sql = "INSERT INTO drivers_cams (driver_id, filename, timestamp) VALUES (%s, %s, NOW())"
        val = (driver_id, filename)
        cursor.execute(sql, val)
        conn.commit()

        return 'Success'
    else:
        return 'Driver not found'



# API endpoint to get nearest customer from database
@app.route('/api/get_nearest_customer')
def get_nearest_customer():
    # Retrieve all customers from database
    conn = mysql.connect()
    mycursor = conn.cursor()
    mycursor.execute("SELECT * FROM customers")
    customers = mycursor.fetchall()
    
    # Find the nearest customer
    geolocator = GoogleV3(api_key='your_api_key')
    my_location = (13.736717, 100.523186)  # example location, you can change to your location
    nearest_customer = None
    min_distance = float('inf')
    for customer in customers:
        address = f"{customer[1]}, {customer[2]}, {customer[3]} {customer[4]}"
        location = geolocator.geocode(address)
        if location is not None:
            distance = geolocator.distance(my_location, (location.latitude, location.longitude)).km
            if distance < min_distance:
                nearest_customer = customer
                min_distance = distance
    
    # Return the nearest customer's information as JSON response
    if nearest_customer is not None:
        return jsonify({
            "name": nearest_customer[0],
            "age": nearest_customer[5],
            "gender": nearest_customer[6],
            "phone": nearest_customer[7],
            "latitude": location.latitude,
            "longitude": location.longitude
        })
    else:
        return jsonify({"message": "No customer found in the database."})



def create_figure():
    us_cities = pd.read_csv("us-cities-top-1k.csv")
    fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", hover_name="City", hover_data=["State", "Population"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=800)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
    return fig
if __name__ == "__main__":
    app.run(port=3000, debug=True)