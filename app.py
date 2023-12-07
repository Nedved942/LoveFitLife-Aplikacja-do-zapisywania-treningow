from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from json import loads, JSONDecodeError

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy()

from models import BodyParts, Exercises

db.init_app(app)


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

    # app.logger.info(body_parts)
    return render_template("exercise_database.html", sorted_exercises=sorted_exercises)


@app.route("/dodawanie-cwiczenia", methods=["GET", "POST"])
def add_exercise():
    body_parts = BodyParts.query.with_entities(BodyParts.body_part).order_by(BodyParts.id).all()

    return render_template("add_exercise.html", body_parts=body_parts)


@app.route("/dodawanie-treningu", methods=["GET", "POST"])
def add_workout():
    pass
    return render_template("add_workout.html")


@app.route("/historia-treningow", methods=["GET", "POST"])
def trainings_history_view():
    pass
    return render_template("trainings_history.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    pass
    return render_template("register.html")
