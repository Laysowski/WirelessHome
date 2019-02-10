from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import PyScripts.validate_device_form as fctns
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307  # an integer is required
app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/configuration')
def configuration():
    # create cursor
    cur = mysql.connection.cursor()
    # get devices
    result = cur.execute("SELECT * FROM devices")

    devices = cur.fetchall()  # catch in dictionary form

    if result > 0:
        return render_template('devices.html', devices=devices)
    else:
        msg = 'No Devices Found'
        return render_template('devices.html', msg=msg)
    # close the connection
    cur.close()


@app.route('/devices/<string:id>/')
def device(id):
    # create cursor
    cur = mysql.connection.cursor()

    # get devices
    result = cur.execute("SELECT * FROM devices WHERE id = %s", [id])

    device = cur.fetchone()  # catch in dictionary form
    return render_template('device.html', device=device)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [
        validators.Length(min=6, max=50),
        validators.Email()  # check for e-mail syntax
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match!')
    ])
    confirm = PasswordField('Confirm password')


# Register form class
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))  # ???

        # create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # commit to db
        mysql.connection.commit()

        # close connection
        cur.close()

        flash('You are now registered! Just login..', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor
        cur = mysql.connection.cursor()

        # get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            # Get stored hash
            data = cur.fetchone() # takes data from the query result
            password = data['password']
            # Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')


# check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login!', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    # create cursor
    cur = mysql.connection.cursor()

    # get devices
    result = cur.execute("SELECT * FROM devices")

    devices = cur.fetchall() # catch in dictionary form

    if result > 0:
        return render_template('dashboard.html', devices=devices)
    else:
        msg = 'No Devices Found'
        return render_template('dashboard.html', msg=msg)
    # close the connection
    cur.close()

# Device form class
class DeviceForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=200)])
    device_type = StringField('Device type [relay/other]', [validators.Length(min=1, max=200)])
    ip_address = StringField('IP Address', [validators.Length(min=1, max=200)])
    # body = TextAreaField('Body', [validators.Length(min=30)])


# Add Device
@app.route('/add_device', methods=['GET', 'POST'])
@is_logged_in
def add_device():
    form = DeviceForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        device_type = form.device_type.data
        ip_address = form.ip_address.data
        if (fctns.validateIP(ip_address)):
            # create cursor
            cur = mysql.connection.cursor()

            # execute
            cur.execute("INSERT INTO devices(name, device_type, ip_address) VALUES(%s, %s, %s)", (name, device_type, ip_address))

            # commit to DB
            mysql.connection.commit()

            # close connection
            cur.close()

            flash('Device created', 'success')
        else:
            flash('Wrong IP Address!', 'danger')
        redirect(url_for('dashboard'))

    return render_template('add_device.html', form=form)


# Edit Device
@app.route('/edit_device/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_device(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get device by id
    result = cur.execute("SELECT * FROM device WHERE id = %s", [id])

    device = cur.fetchone()

    # Get form
    form = DeviceForm(request.form)

    # Populate device form fields
    form.name.data = device['name']
    form.device_type.data = device['device_type']
    form.ip_address.data = device['ip_address']

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        device_type = request.form['device_type']
        ip_address = request.form['ip_address']

        # create cursor
        cur = mysql.connection.cursor()

        # execute
        cur.execute("UPDATE devices SET name=%s, device_type=%s, ip_address=%s WHERE id=%s", (name,device_type, ip_address, id))

        # commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        flash('Device created', 'success')
        redirect(url_for('dashboard'))

    return render_template('add_device.html', form=form)


# Delete device
@app.route('/delete_device/<string:id>', methods=['POST'])
@is_logged_in
def delete_device(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM devices WHERE id = %s", [id])

    # commit to DB
    mysql.connection.commit()

    # close connection
    cur.close()

    flash('Device deleted', 'success')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True) # no refreshing needed anymore