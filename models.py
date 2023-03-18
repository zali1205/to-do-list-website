from __main__ import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)

    # Relationships
    lists = relationship("List", back_populates="author")

class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="lists")

    list_items = relationship("ListItem", back_populates="parent_list")

class ListItem(db.Model):
    __tablename__ = "list_items"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    parent_list_id = db.Column(db.Integer, db.ForeignKey("lists.id"))
    parent_list = relationship("List", back_populates="list_items")