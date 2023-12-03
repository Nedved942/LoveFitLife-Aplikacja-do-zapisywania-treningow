from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)


class BodyParts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body_parts = db.Column(db.String, nullable=False, unique=True)


class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    main_body_part = db.Column(db.String(120), nullable=False)
    another_body_parts = db.Column(db.Text)
    description = db.Column(db.Text)
    media = db.Column(db.LargeBinary)
    link = db.Column(db.String)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    pass
    return render_template("index.html")


@app.route("/baza-cwiczen", methods=["GET", "POST"])
def exercise_database():
    pass
    return render_template("exercise_database.html")


@app.route("/dodawanie-treningu", methods=["GET", "POST"])
def add_workout():
    pass
    return render_template("add_workout.html")
