from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from copy import deepcopy
# from flask_alembic import Alembic
from flask_migrate import Migrate
# from json import loads, JSONDecodeError

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy()
migrate = Migrate()

from models import BodyParts, Exercises

db.init_app(app)


# with app.app_context():
#     db.create_all()

migrate.init_app(app, db)

# alembic = Alembic()
# alembic.init_app(app)


def get_abbreviation_of_exercise(body_part):
    abbreviation_character = BodyParts.query.filter(BodyParts.body_part == body_part).value(
        BodyParts.abbreviation_character)
    app.logger.info(abbreviation_character)
    count_of_exercises = len(Exercises.query.filter(Exercises.main_body_part == body_part).all())
    if not count_of_exercises:
        count_of_exercises = 0
    if not abbreviation_character:
        abbreviation_character = ""
    return str(count_of_exercises + 1) + abbreviation_character


# def read_csv(path_file):
#     with open(path_file) as file_stream:
#         rows_list = []
#         object_csv_file = csv.reader(file_stream)
#         for row in object_csv_file:
#             rows_list.append(row)
#         app.logger.info(type(object_csv_file))
#         app.logger.info(rows_list)
#         app.logger.info(type(rows_list))
#     pass


@app.route("/", methods=["GET", "POST"])
def index():
    # Pobranie pliku body_parts.csv od użytkownika
    body_parts_file = request.form.get("body_parts_file")
    exercise_database_file = request.form.get("exercise_database_file")
    # read_csv(body_parts_file)

    if body_parts_file:
        flash("Dodano plik z partiami ciała do bazy danych.")

    if exercise_database_file:
        flash("Dodano plik z ćwiczeniami do bazy danych.")

    app.logger.info(body_parts_file)
    app.logger.info(type(body_parts_file))

    app.logger.info(exercise_database_file)
    app.logger.info(type(exercise_database_file))
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

# TODO Utwórz relacje w tabelach w bazie danych !
