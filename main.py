from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm
from flask_behind_proxy import FlaskBehindProxy
from flask_bootstrap import Bootstrap4
import secrets

app = Flask(__name__)
bootstrap = Bootstrap4(app)
proxied = FlaskBehindProxy(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Home page with login and register links``
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Register page with form
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
