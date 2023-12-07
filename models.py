from app import db


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
    another_body_part = db.Column(db.String(120))
    description = db.Column(db.Text)
    media = db.Column(db.LargeBinary)
    link = db.Column(db.String)
