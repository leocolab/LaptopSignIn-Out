from flask import Flask, request, jsonify, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import csv
import os
import sys

app = Flask(__name__)


def csvRead(file):
    with open(os.path.join(sys.path[0], file), 'r') as f:
         csv_as_list = list(csv.reader(f))
         csv_as_dict = {}
         for line in csv_as_list:
            if len(line) == 2:
                  csv_as_dict[line[0]] = line[1]
         return csv_as_dict


laptop_dict = csvRead('signout.csv')
lso_dict = csvRead('lastsignedout.csv')  # last signed out dictionary
code_dict = csvRead('codes.csv')


def csvWrite(file, x):  # x is the dictionary that is being written to the csv
    with open(os.path.join(sys.path[0], file), 'w') as f:
        writer = csv.writer(f)
        for i in list(x):
            writer.writerow([i, x[i]])


with open(os.path.join(sys.path[0], "texts.txt"), 'r') as f:
   w = f.read().splitlines()
   m = {
      'disclaimer': w[0],
      'nohdsb': w[1],
      'suc_out': w[2],
      'err_out': w[3],
      'suc_in': w[4],
      'err_in': w[5],
      'adm_blank': w[6],
      'adm_inv_code': w[7]
   }
   sender_address = w[8]
   sender_password = w[9]
   admin_code = w[10]


def queryDict(x, item):
    for i in x:
        if x[i] == item:
            return i


# This is a set because the order of items does not matter, it is only needed to check if an item is in the set


def sendEmail(sa, sp, ra, mmo):  # sender address, sender_password, recipient address, MIMEMultipart Object
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)  # Opens smtp server on port 587
    smtp_server.starttls()
    smtp_server.login(sa, sp)
    email_object = mmo.as_string()  # Convert MIMEMultipart object to string in order to send
    smtp_server.sendmail(sa, ra, email_object)
    smtp_server.quit()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        recipient_address = request.form['nm']
    else:
        recipient_address = request.args.get('nm')

    if recipient_address[-8:] == '@hdsb.ca':  # Checks if last 8 characters if email are "@hdsb.ca"
        v_code = ''.join(random.choices(string.digits, k=4))
        email_subject_line = 'TAB Laptops Verification Code'
        email_body = f'Your Verification Code is {v_code}'

        msg = MIMEMultipart()
        msg['From'] = sender_address
        msg['To'] = recipient_address
        msg['Subject'] = email_subject_line

        # Attach the message to the MIMEMultipart object
        msg.attach(MIMEText(email_body, 'plain'))

        sendEmail(sender_address, sender_password, recipient_address, msg)

        code_dict[recipient_address] = v_code
        csvWrite('codes.csv', code_dict)
        return m['disclaimer']
    else:
        return m['nohdsb']


@app.route("/signOut", methods=['POST', 'GET'])
def signOut():
    if request.method == 'POST':
        laptop_id = request.form['QR']
        user_address = request.form['email']
        uv_code = request.form['code']  # user verification code
    else:
        laptop_id = request.args.get('QRoutput')
        user_address = request.args.get('email')
        uv_code = request.args.get('form')  # user verification code

    if user_address in code_dict:
        # Fetches code associated with email from database to compare to user-given code
        sv_code = code_dict[user_address]
    else:
        return m['err_out']

    if sv_code == uv_code and laptop_id in laptop_dict:
        overwritten_user = laptop_dict[laptop_id]

        # Deletes other users code if somebody overwrites their sign out
        if overwritten_user != 'empty':
            code_dict.pop(overwritten_user)
            csvWrite('codes.csv', code_dict)

        laptop_dict[laptop_id] = user_address
        lso_dict[laptop_id] = user_address
        csvWrite("signout.csv", laptop_dict)
        csvWrite("lastsignedout.csv", lso_dict)
        return m['suc_out']
    else:
        return m['err_out']


@app.route('/return', methods=['POST', 'GET'])
def Return():
    if request.method == 'POST':
        user_address = request.form['email']
        uv_code = request.form['code']
    else:
        user_address = request.args.get('email')
        uv_code = request.args.get('code')

    if user_address in code_dict:
        # Fetches code associated with email from database to compare to user-given code
        sv_code = code_dict[user_address]
    else:
        return m['err_in']

    if sv_code == uv_code:
        code_dict.pop(user_address)
        csvWrite('codes.csv', code_dict)

        laptop_dict[queryDict(laptop_dict, user_address)] = 'empty'
        # Finds laptop number associated with user and sets
        # signout user to 'empty', denoting it is not currently signed out
        csvWrite("signout.csv", laptop_dict)
        return m['suc_in']
    else:
        return m['err_in']


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        ua_code = request.form['code']  # user inputted admin code
    else:
        ua_code = request.args.get['code']

    if ua_code == admin_code:
        cso_string = ""
        lso_string = ""

        for laptop in laptop_dict:
            user = laptop_dict[laptop]
            cso_string += f'<br>{user} signed out: {laptop}'

        for laptop in lso_dict:
            user = lso_dict[laptop]
            lso_string += f'<br>{user} signed out: {laptop}'

        return f'Computers currently signed out: {cso_string}<br><br>Last users to sign out each laptop: {lso_string}'


if __name__ == "__main__":
    app.run(debug=True)
