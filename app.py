from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from json import loads

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)


class BodyParts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body_part = db.Column(db.String, nullable=False, unique=True)
    abbreviation_character = db.Column(db.String(10), nullable=False, unique=True)


class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    name_ang = db.Column(db.String(120), unique=True)
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
def exercise_database_view():
    # Pobranie danych z tabel i przypisanie ich posortowanych wg partii mięśniowych do słownika
    sorted_exercises = {}
    body_parts = BodyParts.query.with_entities(BodyParts.body_part).order_by(BodyParts.id).all()
    for body_part in body_parts:
        sorted_exercises[body_part[0]] = (Exercises.query.filter(Exercises.main_body_part == body_part[0]).all())

    # Konwersja another_body_parts w słowniku sorted_exercises z typu string na typ list
    for body_part, exercises in sorted_exercises.items():
        if exercises:
            for exercise in exercises:
                list_of_another_body_parts = loads(exercise.another_body_parts)
                exercise.another_body_parts = list_of_another_body_parts

    app.logger.info(sorted_exercises)
    app.logger.info(body_parts)
    return render_template("exercise_database.html", sorted_exercises=sorted_exercises)


@app.route("/dodawanie-treningu", methods=["GET", "POST"])
def add_workout():
    pass
    return render_template("add_workout.html")
