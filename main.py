from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm, CreateNewListForm, CreateNewListItemForm, EditListItemForm
import os
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY")
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../to-do.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from models import User, List, ListItem

with app.app_context():
    db.create_all()

def check_list_item_bounds(list_item):
    if list_item == None:
        return abort(404)
    current_user_lists = List.query.filter_by(author_id=current_user.id).all()
    for current_list in current_user_lists:
        if list_item.parent_list_id == current_list.id:
            return
    return abort(404)

def check_list_bounds(lists, list_id):
    list_to_find = None
    for current_list in lists:
        if current_list.id == list_id:
            list_to_find = current_list
    if list_to_find == None:
        return abort(404)
    return list_to_find

def check_list_complete(current_list):
    for list_item in current_list.list_items:
        if not list_item.complete:
            return False
    return True

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@app.route("/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('lists'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        check_user = User.query.filter_by(email=email).first()
        if check_user == None:
            flash("This email does not exists! Please try registering!")
            return redirect(url_for('register'))
        if not check_password_hash(check_user.password, password):
            flash("Invalid password. Please try again!")
            return redirect(url_for('login'))
        login_user(check_user)
        return redirect(url_for('lists'))
    return render_template('login.html', form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('lists'))
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data    
        check_user = User.query.filter_by(email=email).first()
        if check_user != None:
            flash("This email already exists, please try logging in instead!")
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('lists'))
    return render_template('register.html', form=form)

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/lists', methods=["GET"])
@login_required
def lists():
    lists = List.query.filter_by(author_id=current_user.id).all()
    return render_template("lists.html", lists=lists, current_user = current_user)

@app.route("/list-detail/<int:list_id>", methods=["GET"])
@login_required
def list_details(list_id):
    lists = List.query.filter_by(author_id=current_user.id).all()
    list_to_find = check_list_bounds(lists, list_id)
    return render_template('list-details.html', list=list_to_find)

@app.route("/create-new-list", methods=["GET", "POST"])
@login_required
def create_new_list():
    form = CreateNewListForm()
    if form.validate_on_submit():
        name = form.name.data
        date = datetime.datetime.now()
        author_id = current_user.id
        new_list = List(name=name, date=date, author_id=author_id)
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('lists', current_user=current_user))
    return render_template("create-list.html", form=form)

@app.route("/create-new-list-item/<int:list_id>", methods=["GET", "POST"])
@login_required
def create_new_list_item(list_id):
    form = CreateNewListItemForm()
    if form.validate_on_submit():
        body = form.body.data
        parent_list_id = list_id
        new_list_item = ListItem(body=body, parent_list_id=parent_list_id)
        db.session.add(new_list_item)
        db.session.commit()
        return redirect(url_for('list_details', list_id=parent_list_id))

    return render_template("create-new-list-item.html", form=form)

@app.route("/edit-list-item/<int:list_item_id>", methods=["GET", "POST"])
@login_required
def edit_list_item(list_item_id):
    list_item_to_edit = ListItem.query.filter_by(id=list_item_id).first()
    check_list_item_bounds(list_item_to_edit)
    form = EditListItemForm()
    if request.method == "GET":
        form.body.data = list_item_to_edit.body
    if form.validate_on_submit():
        new_body = form.body.data
        list_item_to_edit.body = new_body
        db.session.commit()
        return redirect(url_for("list_details", list_id=list_item_to_edit.parent_list_id))
    return render_template('edit-list-item.html', form=form)

@app.route("/list-item-complete/<int:list_item_id>", methods=["GET"])
@login_required
def mark_list_item_complete(list_item_id):
    list_item = ListItem.query.filter_by(id=list_item_id).first()
    current_list = List.query.filter_by(id=list_item.parent_list_id).first()
    check_list_item_bounds(list_item)
    list_item.complete = True
    if check_list_complete(current_list):
        current_list.complete = True
    db.session.commit()
    return redirect(url_for('list_details', list_id=list_item.parent_list_id))

@app.route("/list-item-incomplete/<int:list_item_id>", methods=["GET"])
@login_required
def mark_list_item_incomplete(list_item_id):
    list_item = ListItem.query.filter_by(id=list_item_id).first()
    current_list = List.query.filter_by(id=list_item.parent_list_id).first()
    check_list_item_bounds(list_item)
    current_list.complete = False
    list_item.complete = False
    db.session.commit()
    return redirect(url_for('list_details', list_id=list_item.parent_list_id))

@app.route("/list-item-delete/<int:list_item_id>", methods=["GET"])
@login_required
def delete_list_item(list_item_id):
    list_item_delete = ListItem.query.filter_by(id=list_item_id).first()
    check_list_item_bounds(list_item_delete)
    db.session.delete(list_item_delete)
    db.session.commit()
    return redirect(url_for('list_details', list_id=list_item_delete.parent_list_id))

@app.route("/list-delete/<int:list_id>", methods=["GET"])
@login_required
def delete_list(list_id):
    list_to_delete = List.query.filter_by(id=list_id).first()
    current_user_lists = List.query.filter_by(author_id=current_user.id).all()
    check_list_bounds(current_user_lists, list_id)
    for list_item in list_to_delete.list_items:
        db.session.delete(list_item)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('lists', current_user=current_user))

if __name__ == "__main__":
    app.run(port=8000, debug=True)