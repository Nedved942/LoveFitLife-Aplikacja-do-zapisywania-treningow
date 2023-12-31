from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from copy import deepcopy
from csv import reader
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

from models import BodyParts, Exercises, ExerciseDetails, ExerciseDone, Trainings, User

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
        elif not value["main_body_part_id"]:
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


# Wymagana data w formacie DD-MM-YYYY, w przeciwnym wypadku zwraca False. Jeżeli date_string=None zwraca None
def date_from_string_to_datetime(date_string):
    date_format = "%Y-%m-%d"
    date_object = None
    try:
        date_object = datetime.strptime(date_string, date_format)
    except (ValueError, TypeError):
        pass
    return date_object


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
@login_required
def exercise_database_view():
    # Pobranie danych z tabel i przypisanie ich posortowanych wg partii mięśniowych do słownika
    sorted_exercises = {}
    body_parts = BodyParts.query.order_by(BodyParts.id).all()
    for body_part in body_parts:
        exercises_list = Exercises.query.filter(Exercises.main_body_part_id == body_part.id).all()
        sorted_exercises[body_part.body_part] = exercises_list
    return render_template("exercise_database.html", sorted_exercises=sorted_exercises)


@app.route("/dodawanie-cwiczenia", methods=["GET", "POST"])
@login_required
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
        main_body_part_id_from_user = BodyParts.query.filter(main_body_part_from_user == BodyParts.body_part).first().id
        try:
            another_body_part_id_from_user = BodyParts.query.filter(another_body_part_from_user ==
                                                                    BodyParts.body_part).first().id
        except AttributeError:
            another_body_part_id_from_user = ""

        if exercise_name_ang_from_user == "":
            exercise_name_ang_from_user = None

        check_name_exercises_repeat = Exercises.query.filter_by(name=exercise_name_from_user).first()
        if check_name_exercises_repeat:
            flash("Ćwiczenie o podanej nazwie istnieje już w bazie!")
        else:
            # Dodanie do tabeli Exercises nowego ćwiczenia
            abbreviation_new_exercise = get_abbreviation_of_exercise(main_body_part_from_user)
            new_exercise = Exercises(abbreviation=abbreviation_new_exercise, name=exercise_name_from_user,
                                     name_ang=exercise_name_ang_from_user,
                                     main_body_part_id=main_body_part_id_from_user,
                                     another_body_part_id=another_body_part_id_from_user)
            db.session.add(new_exercise)
            db.session.commit()
            flash("Dodano ćwiczenie do bazy danych!")

    if main_body_part_from_user and not exercise_name_from_user:
        flash("Wymagane podanie nazwy ćwiczenia.")

    return render_template("add_exercise.html", body_parts=body_parts, another_body_parts=another_body_parts)


@app.route("/dodawanie-treningu", methods=["GET", "POST"])
@login_required
def add_workout():
    if request.method == "POST":
        date_from_user = request.form.get("training_date")
        training_id = request.form.get("training_id")
        if date_from_user:
            date = date_from_string_to_datetime(date_from_user)
            new_training = Trainings(date=date, user_id=current_user.id)
            db.session.add(new_training)
            db.session.commit()
            return redirect(url_for('edit_workout', edit_training_id=new_training.id))
        elif date_from_user == "":
            flash("Podaj datę treningu.")
        if training_id:
            check_current_user_training = Trainings.query.filter_by(id=training_id, user_id=current_user.id).first()
            if check_current_user_training:
                return redirect(url_for('edit_workout', edit_training_id=training_id))
            else:
                flash("Trening o podanym ID nie istnieje w bazie.")
        elif training_id == "":
            flash("Wprowadź ID treningu.")
    return render_template("add_workout.html")


@app.route("/dodawanie-treningu/edytuj", methods=["GET", "POST"])
@login_required
def edit_workout():
    exercises = Exercises.query.order_by(Exercises.main_body_part_id).all()
    edit_training_id = request.args.get('edit_training_id')
    edit_training = Trainings.query.get(edit_training_id)
    if request.method == "POST":
        exercise_id = request.form.get("exercise_id")
        exercise = Exercises.query.get(exercise_id)
        edit_training_id = request.form.get("edit_training_id")
        edit_training = Trainings.query.get(edit_training_id)
        weight = request.form.get("weight")
        sets = request.form.get("sets")
        reps_per_set = request.form.get("reps_per_set")
        if weight == "":
            weight = 0
        if sets and reps_per_set:
            new_exercise_done = ExerciseDone(exercise_id=exercise.id, training_id=edit_training_id)
            db.session.add(new_exercise_done)
            db.session.commit()
            new_exercise_details = ExerciseDetails(weight=weight, set=sets, reps_per_set=reps_per_set,
                                                   exercise_done_id=new_exercise_done.id)
            db.session.add(new_exercise_details)
            db.session.commit()
        elif not sets or not reps_per_set:
            flash("Uzupełnij ilość wykonanych serii i powtórzeń na serię.")
    return render_template("edit_workout.html", exercises=exercises, edit_training_id=edit_training_id,
                           edit_training=edit_training)


@app.route("/historia-treningow", methods=["GET", "POST"])
@login_required
def trainings_history_view():
    current_user_trainings = Trainings.query.filter_by(user_id=current_user.id).all()
    return render_template("trainings_history.html", current_user_trainings=current_user_trainings)


@app.route("/rejestracja", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nick = request.form.get("nick")
        email = request.form.get("email")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")

        list_to_check_entry = [nick, email, password, password_repeat]
        if not all(list_to_check_entry):
            flash("Wymagane wypełnienie wszystkich pól formularza.")
        elif password_repeat != password:
            flash("Powtórzone hasło jest inne niż pierwotne.")
        else:
            existing_user_email = User.query.filter_by(email=email).first()
            existing_user_nick = User.query.filter_by(nick=nick).first()
            if existing_user_email:
                flash("Użytkownik o podanym emailu już istnieje.")
            elif existing_user_nick:
                flash("Użytkownik o podanej nazwie już istnieje. Wpisz inną nazwę.")
            else:
                password_hash = generate_password_hash(password)
                new_user = User(email=email, password=password_hash, nick=nick)
                db.session.add(new_user)
                db.session.commit()
                flash("Pomyślnie zarejestrowano użytkownika!")
                return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/logowanie", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        list_to_check_entry = [email, password]
        if not all(list_to_check_entry):
            flash("W celu zalogowania wypełnij formularz.")
        elif user and check_password_hash(user.password, password):
            login_user(user)
            flash("Zalogowano pomyślnie!")
            return redirect(url_for('index'))
        elif not user:
            flash("Nie ma takiego użytkownika!")
        elif user and not check_password_hash(user.password, password):
            flash("Podano błędne hasło! Spróbuj ponownie.")
        else:
            flash("Błędne dane logowania.")
    return render_template("login.html")


@app.route("/wyloguj", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Wylogowano pomyślnie!")
    return redirect(url_for('login'))
