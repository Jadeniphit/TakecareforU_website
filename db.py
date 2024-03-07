import mysql.connector
mydb = mysql.connector.connect(
host="localhost",
user="root",
password="",
database="takecareforu"
# mysql_query("SET character_set_results=utf8");
# mysql_query("SET character_set_client=utf8");
# mysql_query("SET character_set_connection=utf8");
)
mycursor = mydb.cursor()


#mycursor.execute("CREATE DATABASE takecareforu")

#mycursor.execute("CREATE TABLE accounts(id INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL, fullname VARCHAR(200) NOT NULL, username  VARCHAR(50)  NOT NULL, password  VARCHAR(255)  NOT NULL, email VARCHAR(100) NOT NULL)")

#mycursor.execute("CREATE TABLE service_userinfo(id INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL, firstname VARCHAR(200) NOT NULL, lastname  VARCHAR(50)  NOT NULL, age VARCHAR(200) NOT NULL, gender  VARCHAR(10)  NOT NULL, weight VARCHAR(5) NOT NULL,height VARCHAR(5) NOT NULL,phone VARCHAR(20) NOT NULL,sick VARCHAR(200) NOT NULL,starts VARCHAR(200) NOT NULL,Ends VARCHAR(200) NOT NULL,valuedistance VARCHAR(200) NOT NULL,valueprice VARCHAR(200) NOT NULL)")

#mycursor.execute("CREATE TABLE service_charge(service_id INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,id INT,FOREIGN KEY(id) REFERENCES service_userinfo(id), service_type VARCHAR(200) NOT NULL)")
#mycursor.execute("ALTER TABLE service_charge ADD service_equipment VARCHAR(30)")
#mycursor.execute("ALTER TABLE service_userinfo DROP valueprice")
#mycursor.execute("CREATE TABLE payment(payment_id INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL,id INT,FOREIGN KEY(id) REFERENCES service_userinfo(id), Cardholder VARCHAR(200) NOT NULL,CardNumber VARCHAR(20) NOT NULL,exdate VARCHAR(20) NOT NULL,cvv VARCHAR(20) NOT NULL,totalprice VARCHAR(200) NOT NULL)")
#mycursor.execute("ALTER TABLE payment ADD equipment_price VARCHAR(30)")
#mycursor.execute("ALTER TABLE payment DROP equipment_price")
#mycursor.execute("ALTER TABLE payment DROP service_price")

#mycursor.execute("CREATE TABLE report(report_id INT(11) PRIMARY KEY AUTO_INCREMENT NOT NULL, fullname VARCHAR(200) NOT NULL,email VARCHAR(200) NOT NULL,subjects VARCHAR(200) NOT NULL,messages VARCHAR(200) NOT NULL)")
#mycursor.execute("CREATE TABLE locations(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,latitude FLOAT(10,6) NOT NULL,longitude FLOAT(10,6) NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")mycursor.execute("CREATE TABLE locations(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, latitude FLOAT(10,6) NOT NULL, longitude FLOAT(10,6) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
#mycursor.execute("CREATE TABLE locations(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, latitude FLOAT(10,6) NOT NULL, longitude FLOAT(10,6) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")


#mycursor.execute("CREATE TABLE drivers(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,username  VARCHAR(50)  NOT NULL, password  VARCHAR(255)  NOT NULL,name VARCHAR(30) NOT NULL,email VARCHAR(50) NOT NULL,phone VARCHAR(20) NOT NULL,car_type VARCHAR(20) NOT NULL,license VARCHAR(20) NOT NULL,status INT DEFAULT 0)")
#mycursor.execute("ALTER TABLE drivers ADD COLUMN status VARCHAR(10) DEFAULT 'active'")
#mycursor.execute("ALTER TABLE drivers ADD COLUMN image_data LONGBLOB")
#mycursor.execute("ALTER TABLE drivers ADD COLUMN vehicle_plate VARCHAR(20)")
#mycursor.execute("ALTER TABLE service_userinfo ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'waiting'")

#mycursor.execute("CREATE TABLE received_jobs (id INT PRIMARY KEY AUTO_INCREMENT, driver_name VARCHAR(50), phone_number VARCHAR(20), car_type VARCHAR(20), vehicle_plate VARCHAR(20), profile_image LONGBLOB, customer_id INT)")
#mycursor.execute("ALTER TABLE received_jobs ADD COLUMN customer_id INT;")
mycursor.execute("ALTER TABLE received_jobs ADD COLUMN driver_id INT;")

#mycursor.execute("CREATE TABLE drivers_Cams (id INT AUTO_INCREMENT PRIMARY KEY, driver_id INT(6) UNSIGNED, filename VARCHAR(255), timestamp DATETIME, FOREIGN KEY (driver_id) REFERENCES drivers(id))");








