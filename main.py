from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy

app= Flask (__name__)

proxied =FlaskBehindProxy(app)


@app.route('/', methods=['GET','POST'])
@app.route('/home')

def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host ='0.0.0.0')