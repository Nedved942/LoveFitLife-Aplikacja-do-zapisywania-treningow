from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from copy import deepcopy
from flask_migrate import Migrate
from csv import reader

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy()
migrate = Migrate()

from models import BodyParts, Exercises

db.init_app(app)
migrate.init_app(app, db)


def get_abbreviation_of_exercise(body_part):
    abbreviation_character = BodyParts.query.filter(BodyParts.body_part == body_part).value(
        BodyParts.abbreviation_character)
    app.logger.info(abbreviation_character)
    count_of_exercises = len(Exercises.query.filter(Exercises.main_body_part_id ==
                                                    BodyParts.query.filter(BodyParts.body_part == body_part).value(
                                                        BodyParts.id)).all())
    if not count_of_exercises:
        count_of_exercises = 0
    if not abbreviation_character:
        abbreviation_character = ""
    return str(count_of_exercises + 1) + abbreviation_character


def read_body_parts(path_file):
    with open(path_file) as file_stream:
        list_of_all = []
        dict_of_all = {}
        object_csv_file = reader(file_stream)
        for row in object_csv_file:
            row_list = row[0].split(";")
            list_of_all.append(row_list)
        for ind, body_part in enumerate(list_of_all):
            dict_of_all[ind] = {
                "body_part": body_part[0],
                "abbreviation_character": body_part[1]
            }
    return dict_of_all


def add_body_parts(dict_of_body_parts):
    body_parts = BodyParts.query.all()
    body_parts_list = []
    abbreviation_character_list = []
    record = 0

    for body_part in body_parts:
        body_parts_list.append(body_part.body_part)
        abbreviation_character_list.append(body_part.abbreviation_character)

    for key, value in dict_of_body_parts.items():
        if value["body_part"] in body_parts_list or value["abbreviation_character"] in abbreviation_character_list:
            pass
        else:
            new_body_part = BodyParts(body_part=value["body_part"],
                                      abbreviation_character=value["abbreviation_character"])
            record += 1
            db.session.add(new_body_part)
    db.session.commit()
    flash(f"Liczba dodanych wpisów do bazy: {record}.")


def read_exercises(path_file):
    with open(path_file) as file_stream:
        list_of_all = []
        dict_of_all = {}
        object_csv_file = reader(file_stream)
        for row in object_csv_file:
            row_list = row[0].split(";")
            list_of_all.append(row_list)
        for ind, exercise in enumerate(list_of_all):
            dict_of_all[ind] = {
                "name": exercise[0],
                "name_ang": exercise[1],
                "main_body_part_id": BodyParts.query.filter(BodyParts.body_part == exercise[2]).value(
                    BodyParts.id),
                "another_body_part_id": BodyParts.query.filter(BodyParts.body_part == exercise[3]).value(
                    BodyParts.id),
                "body_part": exercise[2]
            }
    return dict_of_all


def add_exercises(dict_of_exercises):
    exercises = Exercises.query.all()
    name_of_exercises_list = []
    name_ang_of_exercises_list = []
    record = 0

    for exercise in exercises:
        name_of_exercises_list.append(exercise.name)
        name_ang_of_exercises_list.append(exercise.name_ang)

    for key, value in dict_of_exercises.items():
        if value["name"] in name_of_exercises_list or value["name_ang"] in name_ang_of_exercises_list:
            pass
        else:
            new_exercise = Exercises(abbreviation=get_abbreviation_of_exercise(value["body_part"]),
                                     name=value["name"], name_ang=value["name_ang"],
                                     main_body_part_id=value["main_body_part_id"],
                                     another_body_part_id=value["another_body_part_id"])
            db.session.add(new_exercise)
            record += 1
            db.session.commit()
    flash(f"Liczba dodanych wpisów do bazy: {record}.")


@app.route("/", methods=["GET", "POST"])
def index():
    # Pobranie pliku body_parts.csv od użytkownika
    body_parts_file = request.form.get("body_parts_file")
    exercise_database_file = request.form.get("exercise_database_file")

    if body_parts_file:
        add_body_parts(read_body_parts(body_parts_file))
        flash("Wczytano plik z partiami ciała.")

    if exercise_database_file:
        add_exercises(read_exercises(exercise_database_file))
        flash("Wczytano plik z ćwiczeniami.")
    return render_template("index.html")


@app.route("/baza-cwiczen", methods=["GET", "POST"])
def exercise_database_view():
    # Pobranie danych z tabel i przypisanie ich posortowanych wg partii mięśniowych do słownika
    sorted_exercises = {}
    body_parts = BodyParts.query.order_by(BodyParts.id).all()
    for body_part in body_parts:
        exercises_list = Exercises.query.filter(Exercises.main_body_part_id == body_part.id).all()
        sorted_exercises[body_part.body_part] = exercises_list
    return render_template("exercise_database.html", sorted_exercises=sorted_exercises)


@app.route("/dodawanie-cwiczenia", methods=["GET", "POST"])
def add_exercise():
    # Pobranie listy krotek z [0] elementem - dla każdej partii ciała
    body_parts = BodyParts.query.with_entities(BodyParts.body_part).order_by(BodyParts.id).all()

    # Zamiana listy krotek pojedynczych elementów na listę
    for ind, body_part in enumerate(body_parts):
        body_part = body_part[0]
        body_parts[ind] = body_part

    another_body_parts = deepcopy(body_parts)
    another_body_parts.append("")

    # Pobranie danych wprowadzanego ćwiczenia od użytkownika
    exercise_name_from_user = request.form.get("exercise_name")
    exercise_name_ang_from_user = request.form.get("exercise_name_ang")
    main_body_part_from_user = request.form.get("main_body_part")
    another_body_part_from_user = request.form.get("another_body_part")

    list_to_check_entry = [exercise_name_from_user, main_body_part_from_user]
    if all(list_to_check_entry):
        # Dodanie do tabeli Exercises nowego ćwiczenia
        abbreviation_new_exercise = get_abbreviation_of_exercise(main_body_part_from_user)
        new_exercise = Exercises(abbreviation=abbreviation_new_exercise, name=exercise_name_from_user,
                                 name_ang=exercise_name_ang_from_user, main_body_part=main_body_part_from_user,
                                 another_body_part=another_body_part_from_user)
        db.session.add(new_exercise)
        db.session.commit()
        flash("Dodano ćwiczenie do bazy danych!")

    if main_body_part_from_user and not exercise_name_from_user:
        flash("Wymagane podanie nazwy ćwiczenia.")

    return render_template("add_exercise.html", body_parts=body_parts, another_body_parts=another_body_parts)


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
