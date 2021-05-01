from flask import Flask, render_template, request
import datetime
from pymongo import MongoClient
import random

def create_app():
    app = Flask(__name__)
    client = MongoClient("mongodb+srv://kzcepielik:GvhVAQ3pbvSqFnN@uslessicelandic.1cxkr.mongodb.net/test")
    app.db = client.UselessIcelandic
    entries = []

    @app.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            entry_content = request.form.get("content")
            entry_translation = request.form.get("translation")
            formatted_date = datetime.datetime.today().strftime("%Y-%m-%d")
            entries.append((entry_content, formatted_date, entry_translation))
            app.db.entries.insert({"content": entry_content, "date": formatted_date, "translation": entry_translation})
        data = app.db.entries.find({})
        ordered_data = [( row['content'], row['date'], row['translation'] )
        for row in data]
        quantity = len(ordered_data)
        return render_template("home.html", entries=ordered_data, quantity=quantity)

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
    return app