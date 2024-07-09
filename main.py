from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy

app= Flask (__name__)

proxied =FlaskBehindProxy(app)



@app.route('/register', methods=['GET', 'POST'])
def regiser():
    return render_template('register.html')


# home page login and register 
@app.route('/', methods=['GET','POST'])
def home():
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check():
    if request.request== 'POST':
        username=request.form['username']
        password=request.form['password']
        #find the data in the sql. if match we render the page
        
        #return load page
        

if __name__ == '__main__':
    app.run(debug=True, host ='0.0.0.0')