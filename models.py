from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
import hashlib


db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), primary_key=False,
                         unique=False, nullable=False)

    team = db.relationship('Team', backref='owner', lazy=True)
    message = db.relationship("Message", backref='messagesender', lazy=True)


class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(25), nullable=False)
    team_description = db.Column(db.String(70), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    teammember = db.relationship('TeamMembers', cascade='delete')
    Task = db.relationship('Task', cascade='delete')
    message = db.relationship('Message', cascade='delete')
    activeusers = db.relationship('ActiveUsers', cascade='delete')
    file_db = db.relationship('File', cascade='delete')


class TeamMembers(db.Model):

    __tablename__ = "teammembers"
    is_admin = db.Column(db.Boolean, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team_name = db.Column(db.String(25), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint(
            user_id, team_id
        ),
    )


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(25), nullable=False)
    task_desc = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey(
        'team.id'), nullable=False)  # foregin key from team
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), unique=False, nullable=False)  # foreign key from User
    date_creation = db.Column(db.String(1000), index=True)
    assigned_by = db.Column(db.Integer, nullable=False)
    deadline = db.Column(db.Date, index=True)
    status = db.Column(db.Integer, default=0)
    completed_on = db.Column(db.String(1000), nullable=True, index=True)
    response = db.Column(db.String(100), default="", nullable=True, index=True)


class ActiveUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    __table_args__ = (
        db.UniqueConstraint(
            user_id, team_id
        ),
    )


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    size = db.Column(db.Integer)
    path = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    msgbody = db.Column(db.String(1000), nullable=False)
    time_stamp = db.Column(db.String(1000), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=True)
