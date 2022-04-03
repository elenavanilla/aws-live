from flask import Flask, render_template, request, jsonify
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('registration.html')



# register page - sign up button
@app.route("/registraion", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    emp_name = request.form['emp_name']
    emp_email = request.form['emp_email']
    emp_bod = request.form['emp_bod']
    emp_bio = request.form['emp_bio']
    emp_job = request.form['emp_job']
    emp_interest = request.form['emp_interest']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, emp_name, emp_email, emp_bod, emp_bio, emp_job, emp_interest))
        db_conn.commit()
        # emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('registerSuccess.html', name=emp_name)


# register page - search employee button
@app.route("/searchEmpButton", methods=['POST'])
def search():
    return render_template('searchEmp.html')


# register success page - back button
@app.route("/registerSuccess", methods=['POST'])
def back1():
    return render_template('registration.html')




# search emp page - search emp function to search
@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    searchbox = request.form.get("text")
    cursor = db_conn.cursor()
    query = "select * from employee where emp_id LIKE '%{}%' OR emp_name LIKE '%{}%'  ".format(searchbox, searchbox)#This is just example query , you should replace field names with yours
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)


# search emp page - back button
@app.route("/backButton", methods=['POST'])
def back2():
    return render_template('registration.html')




# employee details page - show employee details
@app.route("/empDetails", methods=['POST'])
def back3():
    return render_template('')

# employee details page - back button
@app.route("/backToRegisterButton", methods=['POST'])
def back():
    return render_template('registration.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
