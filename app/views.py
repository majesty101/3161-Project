"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app,mysql
from flask import render_template, request, redirect, url_for, flash,session
from app.forms import InfoForm, LoginForm, MealPlanForm, RecipeForm, Register, SearchForm
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb
from flask.helpers import send_from_directory
import os
from time import strptime




###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return redirect(url_for('home'))


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
            return render_template("secure_page.html")  # they should be redirected to a secure-page route instead
    return render_template("login.html", form=form)

@app.route('/viewRecipes',methods=['GET','POST'])
def viewRecipes():
    results = None
    search = SearchForm()
    if request.method== 'POST':
        query = search.search.data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select r.title, r.calories, rd.Desc, r.RecID from recipes as r join recipe_description as rd on r.DescID = rd.DescID where r.title like %s',(['%' + query + '%']))
        results = cursor.fetchall()
        cursor.close()
    return render_template('viewRecipes.html',search=search,results=results)

@app.route('/addRecipe',methods=['GET','POST'])
def addRecipe():
    form = RecipeForm()
    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        desc = form.desc.data
        prep = form.prep.data
        cal = form.cal.data
        date = datetime.today().strftime("%y-%m-%d")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select RecID from recipes order by length(RecID) DESC,RecID Desc Limit 1')
        lastrid = cursor.fetchone()['RecID'].split('-')[1]
        cursor.execute('Select DescID from recipe_description order by length(DescID) DESC,DescID Desc Limit 1')
        lastdid = cursor.fetchone()['DescID'].split('-')[1]


        cursor.execute('Insert into recipe_description values (%s,%s)', ('DESC-' + str(int(lastdid)+1),desc))
        cursor.execute('Insert into recipes values (%s,%s,%s,%s,%s,%s)', ('RE-' + str(int(lastrid)+1),title,cal,'DESC-' + str(int(lastdid)+1),date,prep))
        mysql.connection.commit()
        flash('Recipe Added')
        print(cal,date)
        return redirect(url_for('recipe',id='RE-' + str(int(lastrid)+1)))
    return render_template('addRecipe.html',form=form)

@app.route('/createMealPlan',methods=['GET','POST'])
def createMealPlan():
    form = MealPlanForm()
    if request.method == 'POST':
        requedCal = form.cal.data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if requedCal == None:
            cursor.execute('select c.recID, category, title, calories, prepTime, dateAdded from categories as c join recipes as r on r.RecID = c.RecID where c.category = "Breakfast" order by rand() limit 1')
            breakfast = cursor.fetchone()
            cursor.execute('select c.recID, category, title, calories, prepTime, dateAdded from categories as c join recipes as r on r.RecID = c.RecID where c.category = "Lunch" order by rand() limit 1')
            lunch = cursor.fetchone()
            cursor.execute('select c.recID, category, title, calories, prepTime, dateAdded from categories as c join recipes as r on r.RecID = c.RecID where c.category = "Dinner" order by rand() limit 1')
            dinner = cursor.fetchone()
        else:
            cursor.execute('Call mealswithcalcount(%s,%s)',([requedCal,'Breakfast']))
            breakfast = cursor.fetchone()
            cursor.execute('Call mealswithcalcount(%s,%s)',([requedCal,'Lunch']))
            lunch = cursor.fetchone()
            cursor.execute('Call mealswithcalcount(%s,%s)',([requedCal,'Dinner']))
            dinner = cursor.fetchone()
            
        recepies = [breakfast,lunch,dinner]
        # create meal plan and then assign meal to current user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select planMID from meal_plan order by length(planMID) DESC,planMID Desc Limit 1')
        lastid = cursor.fetchone()
        if lastid == None:
            id = 'MP-1'
        else:
            id = 'MP-' + str(int(lastid.get("planMID").split('-')[1]) +1 )

        cursor.execute('Select mealID from meals order by length(mealID) DESC,mealID Desc Limit 1')
        lastMID = cursor.fetchone()
        if lastMID == None:
            Mid = 1
        else:
            Mid = int(lastMID.get("mealID").split('-')[1]) +1 

        for i in recepies: 
            cursor.execute('Insert into meals (mealID,title,RecID) values(%s,%s,%s)',('ME-' + str(Mid),i['title'],i['recID']))
            Mid +=1
        mysql.connection.commit()



        cursor.execute('Insert into meal_plan values (%s,%s,%s,%s)',(id,'ME-' + str(Mid-3),'ME-' + str(Mid-2),'ME-' + str(Mid-1)))
        cursor.execute('Insert into plan_assignments values (%s,%s)',(session['AccID'],id))
        mysql.connection.commit()
        cursor.close()

        flash('Meal Plan Created')
        return redirect(url_for('userPlans'))
    return render_template('createPlan.html',form = form)

@app.route('/userPlans')
def userPlans():
    meals = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('Select p.planMID, m.Bfast, m.lunch, m.dinner from plan_assignments as p join meal_plan as m on p.planMID = m.planMID where p.AccID = %s order by length(p.planMID) DESC,p.planMID Desc Limit 1;',([session['AccID']]))
    plans = cursor.fetchall()
    if plans is not None:
        for plan in plans:
            cursor.execute('Select r.title,r.RecID, m.mealID, m.servings from recipes as r join meals as m on r.RecID = m.RecID where m.mealID = %s',([plan['Bfast']]))
            Brec = cursor.fetchone()
            print(Brec)
            cursor.execute('Select r.title,r.RecID, m.mealID, m.servings from recipes as r join meals as m on r.RecID = m.RecID where m.mealID = %s',([plan['lunch']]))
            Lrec = cursor.fetchone()
            cursor.execute('Select r.title,r.RecID, m.mealID, m.servings from recipes as r join meals as m on r.RecID = m.RecID where m.mealID = %s',([plan['dinner']]))
            Drec= cursor.fetchone()
            meals.append([plan['planMID'],Brec,Lrec,Drec])
        cursor.close()
        return render_template('userPlan.html',meals = meals)
    cursor.close()
    return render_template('userPlan.html',meals=None)


@app.route('/allMealPlans')
def allMealPlans():
    meals = []
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('call usermeals(%s)',([session['AccID']]))
    plans = cursor.fetchall()
    if plans is not None:
        for plan in plans:
            cursor.execute('Select r.title,r.RecID, m.mealID, m.servings from recipes as r join meals as m on r.RecID = m.RecID where m.mealID = %s',([plan['Bfast']]))
            Brec = cursor.fetchone()
            print(Brec)
            cursor.execute('Select r.title,r.RecID, m.mealID, m.servings from recipes as r join meals as m on r.RecID = m.RecID where m.mealID = %s',([plan['lunch']]))
            Lrec = cursor.fetchone()
            cursor.execute('Select r.title,r.RecID, m.mealID, m.servings from recipes as r join meals as m on r.RecID = m.RecID where m.mealID = %s',([plan['dinner']]))
            Drec= cursor.fetchone()
            meals.append([plan['planMID'],Brec,Lrec,Drec])
        cursor.close()
        return render_template('userPlan.html',meals = meals)
    cursor.close()
    return render_template('allPlans',meals=None)


@app.route('/addInfo/<id>',methods=['GET','POST'])
def addInfo(id):
    print(id)
    form = InfoForm()
    if request.method == 'POST' and form.validate_on_submit():
        servings = form.servings.data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('call setserving(%s,%s) ',(id,servings))
        mysql.connection.commit()
        return redirect(url_for('userPlans'))
    return render_template('addInfo.html',form=form,id=id)
@app.route('/recipe/<id>', methods= ["GET", "POST"])
def recipe(id): 
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('Select * from recipes where RecID=%s',([id]))
    recipe = cursor.fetchone()
    cursor.execute('Select * from recipe_description where DescID =%s',([recipe['DescID']]))
    desc = cursor.fetchone()['Desc']
    filename = 'placeholder.png'

    photo=PhotoForm()
    if request.method == 'POST' and photo.validate_on_submit():
        photo = request.files['photo']

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    return render_template('recipe.html',recipe=recipe,desc=desc, form=photo, filename=filename)
    #When a plan is selected display the plan details

@app.route("/secure-page")
def secure_page():
    return render_template("secure_page.html")
@app.route('/uploads/<filename>')
def get_image(filename):
    root_dir = os.getcwd()
    return send_from_directory(os.path.join(root_dir,app.config['UPLOAD_FOLDER']),filename)

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
        allergies = form.allergies.data
        
          # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select AccID from accounts order by length(AccID) DESC,AccID Desc Limit 1')
        lastid = cursor.fetchone().get("AccID").split('-')[1]
        id =  int(lastid) + 1 
        print(id)
        cursor.execute('INSERT INTO accounts (AccID,first_name,last_name,password) VALUES (%s, %s, %s, %s)', ('AC-' + str(id),fname, lname, password,))
        for key, value in allergies.items():
            if value == True:
                AllID = key.split('_')[1]
                print(AllID)
                cursor.execute('Insert into user_allergies values (%s,%s)',('AC-' + str(id),"AL-" + str(AllID)))
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
