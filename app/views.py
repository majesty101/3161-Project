"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app,mysql
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, Register
from flask_mysqldb import MySQL

from werkzeug.security import check_password_hash
import MySQLdb




###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    if session.get('loggedin') == True:
        user = session['AccID']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE AccID = %s', ([user]))
        account = cursor.fetchone()
        print(account)
        return render_template('about.html', account=account)
    else:
        flash('Please Login')
        return redirect(url_for('login'))
    

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():

        if form.username.data:

            username=form.username.data
            password=form.password.data
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE AccID = %s AND password = %s', (username, password,))
            user = cursor.fetchone()


            if user is not None:
                session['loggedin'] = True
                session['AccID'] = user['AccID']
            else:
                flash('Username or Password Incorrect')
                return redirect(url_for('login'))
            cursor.close()
            flash('Logged In.')
            return redirect(url_for("secure_page"))  # they should be redirected to a secure-page route instead
    return render_template("login.html", form=form)



@app.route('/createMealPlan')
def createMealPlan():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('select c.recID, category, title, calories, prepTime, dateAdded from categories as c join recipes as r on r.RecID = c.RecID where c.category = "Breakfast" order by rand() limit 1')
    breakfast = cursor.fetchone()
    cursor.execute('select c.recID, category, title, calories, prepTime, dateAdded from categories as c join recipes as r on r.RecID = c.RecID where c.category = "Lunch" order by rand() limit 1')
    lunch = cursor.fetchone()
    cursor.execute('select c.recID, category, title, calories, prepTime, dateAdded from categories as c join recipes as r on r.RecID = c.RecID where c.category = "Dinner" order by rand() limit 1')
    dinner = cursor.fetchone()

    # create meal plan and then assign meal to current user
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('Select planMID from meal_plan order by length(planMID) DESC,planMID Desc Limit 1')
    lastid = cursor.fetchone()
    if lastid == None:
        id = 'MP-1'
    else:
        id = 'MP-' + str(int(lastid.get("planMID").split('-')[1]) +1 )

    cursor.execute('Insert into meal_plan values (%s,%s,%s,%s)',(id,breakfast['recID'],lunch['recID'],dinner['recID']))
    cursor.execute('Insert into plan_assignments values (%s,%s)',(session['AccID'],id))
    mysql.connection.commit()
    cursor.close()

    flash('Meal Plan Created')
    return redirect(url_for('userPlans'))


@app.route('/userPlans')
def userPlans():
    meals = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('Select p.planMID, m.Bfast, m.lunch, m.dinner from plan_assignments as p join meal_plan as m on p.planMID = m.planMID where p.AccID = %s',([session['AccID']]))
    plans = cursor.fetchall()
    if plans is not None:
        for plan in plans:
            cursor.execute('Select title,RecID from recipes where RecID = %s',([plan['Bfast']]))
            Brec = cursor.fetchone()
            cursor.execute('Select title,RecID from recipes where RecID = %s',([plan['lunch']]))
            Lrec = cursor.fetchone()
            cursor.execute('Select title,RecID from recipes where RecID = %s',([plan['dinner']]))
            Drec= cursor.fetchone()
            meals.append([plan['planMID'],Brec,Lrec,Drec])
        return render_template('userPlan.html',meals = meals)
    return render_template('userPlan.html',meals=None)

@app.route('/recipe/<ID>')
def meals(ID):
    return None
    #When a plan is selected display the plan details

@app.route("/secure-page")
def secure_page():
    return render_template("secure_page.html")


@app.route("/logout")
def logout():

    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/register",methods=['GET', 'POST'])
def register():
    form = Register()
    if request.method == 'POST' and form.validate_on_submit():
        fname = request.form['fname']
        lname = request.form['lname']
        password = request.form['password']
          # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select AccID from accounts order by length(AccID) DESC,AccID Desc Limit 1')
        lastid = cursor.fetchone().get("AccID").split('-')[1]
        id =  int(lastid) + 1 
        print(id)
        cursor.execute('INSERT INTO accounts (AccID,first_name,last_name,password) VALUES (%s, %s, %s, %s)', ('AC-' + str(id),fname, lname, password,))
        mysql.connection.commit()
        cursor.close()
        flash('Registration Complete ID is: AC-' + str(id))
        return redirect(url_for('login'))

    return render_template('register.html',form=form)

###
# The functions below should be applicable to all Flask apps.
###


# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
