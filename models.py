from app import db


class BodyParts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body_part = db.Column(db.String, nullable=False, unique=True)
    abbreviation_character = db.Column(db.String(10), nullable=False, unique=True)
    exercises_main_body_part = db.relationship("Exercises", foreign_keys="Exercises.main_body_part_id",
                                               backref="main_body_part", lazy=True)
    exercises_another_body_part = db.relationship("Exercises", foreign_keys="Exercises.another_body_part_id",
                                                  backref="another_body_part", lazy=True)


class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(10), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    name_ang = db.Column(db.String(120), unique=True)
    main_body_part_id = db.Column(db.Integer, db.ForeignKey("body_parts.id"), nullable=False)
    another_body_part_id = db.Column(db.Integer, db.ForeignKey("body_parts.id"))
    description = db.Column(db.Text)
    media = db.Column(db.LargeBinary)
    link = db.Column(db.String)
    exercises_done = db.relationship("ExerciseDone", foreign_keys="ExerciseDone.exercise_id", backref="exercises_done",
                                     lazy=True)


class ExerciseDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set = db.Column(db.Integer, nullable=False, default=1)
    reps_per_set = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)
    exercise_done_id = db.Column(db.Integer, db.ForeignKey("exercise_done.id"), nullable=False)


class ExerciseDone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey("trainings.id"), nullable=False)
    exercise_details = db.relationship("ExerciseDetails", foreign_keys="ExerciseDetails.exercise_done_id",
                                       backref="exercise_details", lazy=True, cascade="all, delete-orphan")


class Trainings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(),
                     server_default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercises_done = db.relationship("ExerciseDone", foreign_keys="ExerciseDone.training_id",
                                     backref="exercises_done", lazy=True, cascade="all, delete-orphan")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    nick = db.Column(db.String(50))
    trainings = db.relationship("Trainings", foreign_keys="Trainings.user_id", backref="trainings", lazy=True,
                                cascade="all, delete-orphan")
