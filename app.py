import os
from flask import Flask, session, redirect, url_for, request, render_template
import datetime
from pymongo import MongoClient
import random
from dotenv import load_dotenv
import bcrypt

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY")
    client = MongoClient(os.environ.get("MONGODB_URI"))
    app.db = client.UselessIcelandic
    db = client.get_database('total_records')
    records = db.register
    entries = []

    @app.route("/")
    def home(message=""):
        data = app.db.entries.find({})
        ordered_data = [( row['content'], row['date'], row['translation'] )
        for row in data]
        quantity = len(ordered_data)
        return render_template("home.html", entries=ordered_data, quantity=quantity, message=message)


    @app.route("/add", methods=["GET", "POST"])
    def add():
        message=""
        if "email" in session:
            if request.method == "POST":
                entry_content = request.form.get("content")
                entry_translation = request.form.get("translation")
                formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
                entries.append((entry_content, formatted_date, entry_translation))
                app.db.entries.insert({"content": entry_content, "date": formatted_date, "translation": entry_translation})
                message = "Successfully added the expression!"
            data = app.db.entries.find({})
            ordered_data = [( row['content'], row['date'], row['translation'] )
            for row in data]
            quantity = len(ordered_data)
            return render_template("add.html", entries=ordered_data, quantity=quantity, message=message)
        else:
            return home(message="you need to be logged in to access the page")

    @app.route("/all")
    def all():
        data = app.db.entries.find({})
        ordered_data = [( row['content'], row['date'], row['translation'] )
        for row in data] 
        return render_template("all.html", entries=ordered_data)

    @app.route("/random_expression")
    def random_expression():
        data = app.db.entries.find({})
        ordered_data = [( row['content'], row['date'], row['translation'] )
        for row in data] 
        random_expression = random.choice(ordered_data)
        return render_template("random.html", random_expression = random_expression)
        
    @app.route("/login", methods=["POST", "GET"])
    def login():
        message = ""
        if "email" in session:
            return home(message="You are now logged in")

        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

        
            email_found = records.find_one({"email": email})
            if email_found:
                email_val = email_found['email']
                passwordcheck = email_found['password']
                
                if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                    session["email"] = email_val
                    return home(message=f"You are logged in as {session['email']}")
                else:
                    if "email" in session:
                        return home(message=f"You are logged in as {session['email']}")
                    message = 'Wrong password'
                    return render_template('login.html', message=message)
            else:
                message = 'Email not found'
                return render_template('login.html', message=message)
        return render_template('login.html', message=message)

    @app.route("/register", methods=['post', 'get'])
    def register():
        message = ''
        if "email" in session:
            session["email"] = email_val
            return home(message=f"You are logged in as {session['email']}")
        if request.method == "POST":
            user = request.form.get("fullname")
            email = request.form.get("email")
            
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")
            
            user_found = records.find_one({"name": user})
            email_found = records.find_one({"email": email})
            if user_found:
                message = 'That name is already registered'
                return render_template('register.html', message=message)
            if email_found:
                message = 'That e-mail is already in use, try a different address'
                return render_template('register.html', message=message)
            if password1 != password2:
                message = 'Passwords do not match! Try again.'
                return render_template('register.html', message=message)
            else:
                hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
                user_input = {'name': user, 'email': email, 'password': hashed}
                records.insert_one(user_input)
                
                user_data = records.find_one({"email": email})
                new_email = user_data['email']
                return home(message=f"successfully registered: {new_email}")    
        return render_template('register.html')

    @app.route('/logged_in')
    def logged_in():
        if "email" in session:
            email = session["email"]
            return home(message=f"You are logged in as {email}")
        else:
            return redirect(url_for("login"))


    @app.route("/logout", methods=["POST", "GET"])
    def logout():
        if "email" in session:
            session.pop("email", None)
            return home(message="You've signed out")
        else:
            return render_template('home.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('500.html'), 500


    return app