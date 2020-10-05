from time import localtime, strftime
from flask import Flask, render_template, redirect, request, send_file, session, flash, url_for, jsonify
from werkzeug.utils import secure_filename
from forms import *
from models import *
from flask_sqlalchemy import *
from werkzeug.security import generate_password_hash
import shutil
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
import os
import json
from datetime import date
from momentjs import *
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)

app.secret_key = os.urandom(24)

app.jinja_env.globals['momentjs'] = momentjs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'Uploads/'

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

app.config['JWT_COOKIE_CSRF_PROTECT'] = True


db.init_app(app)
with app.app_context():
    db.create_all()
login = LoginManager(app)
login.init_app(app)

socketio = SocketIO(app)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/", methods=['GET', 'POST'])
def main():

    if session.get("logged_in") is not None:
        print("yes")
        if session["logged_in"] == False:
            flash("You have logged out successfully!", "info")
    session.pop("logged_in", None)

    if session.get("accountexists") is not None:
        print("yes")
        if session["accountexists"] == True:
            flash("An account with the email already exists. Please create an account with different email.", "info")
    session.pop("accountexists", None)

    return render_template("main.html")


@app.route("/features", methods=['GET', 'POST'])
def feat():

    return render_template("viewteams.html")


@app.route("/editprofile", methods=['GET', 'POST'])
def editpr():
    if request.method == "POST":
        current_user.name = request.form['fullname']
        db.session.commit()
        return redirect("/editprofile")

    return render_template("editprofile.html", profile=True)


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    signup = SignUp()
    if signup.validate_on_submit():
        name = signup.name.data
        email = signup.email.data
        password = signup.password.data

        userOb = User.query.filter_by(email=email).first()
        if userOb:
            session["accountexists"] = True
            return redirect('/')
        else:
            user = User(name=name,
                        email=email,
                        password=generate_password_hash(password, method='sha256'))
            db.session.add(user)
            db.session.commit()
            session["accountcreated"] = True
            return redirect('login')

    return render_template("signup.html", form=signup)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if session.get("accountcreated") is not None:
        if session["accountcreated"] == True:
            flash("Account created successfully! You can now login", "info")

    session.pop("accountcreated", None)

    loginForm = Login()
    if loginForm.validate_on_submit():
        userOb = User.query.filter_by(email=loginForm.email.data).first()
        login_user(userOb)
        session["logged_in"] = True
        return redirect('profile')

    return render_template("login.html", form=loginForm)


@app.route("/profile", methods=['GET', 'POST'])
def profile():

    if not current_user.is_authenticated:
        return redirect('login')

    if session.get("logged_in") is not None:
        if session["logged_in"] == True:
            flash("You have logged in successfully!", "info")

    session.pop("logged_in", None)

    if session.get("team_created") is not None:
        print("yes")
        if session["team_created"] == False:
            flash("Team deleted succesfully", "info")

    if session.get("errort") is not None:
        print("yes")
        if session["errort"] == True:
            flash("Team does not exist, please create a new team", "info")
    session.pop("errort", None)

    if session.get("errorteamname") is not None:
        print("yes")
        if session["errorteamname"] == True:
            flash("Team name already exists", "info")
    session.pop("errorteamname", None)

    createteam = CreateTeam()

    teams = TeamMembers.query.filter_by(user_id=current_user.id)

    return render_template("profile.html", teams=teams)


@app.route("/createteam", methods=['GET', 'POST'])
def createTeams():

    if not current_user.is_authenticated:
        return redirect('login')

    createteam = CreateTeam()

    if createteam.validate_on_submit():
        name = createteam.team_name.data
        description = createteam.team_description.data

        u_id = current_user.id
        teamOb = Team.query.filter_by(team_name=name).first()
        if teamOb:
            session["errorteamname"] = True
            return redirect('/profile')
        else:
            team = Team(team_name=name,
                        team_description=description, owner=current_user)
            db.session.add(team)
            db.session.commit()
            print(str(team.id) + team.team_name + "\n")

            nt = TeamMembers(is_admin=True, user_id=current_user.id,
                             team_id=team.id, team_name=team.team_name)
            db.session.add(nt)
            db.session.commit()
            session['team_created'] = True
            return redirect(url_for('team_chat', team_id=team.id))

    return render_template('createteam.html', form=createteam)


@app.route("/team/<int:team_id>/chat", methods=['GET', 'POST'])
def team_chat(team_id):

    if not current_user.is_authenticated:
        return redirect('/login')

    unauth = TeamMembers.query.filter(
        TeamMembers.user_id == current_user.id, TeamMembers.team_id == team_id).first()
    if unauth is None:
        return redirect('/profile')

    if session.get("team_created") is not None:

        if session["team_created"] == True:
            flash("Team created succesfully.", "info")
    session.pop("team_created", None)

    if session.get("member_added") is not None:

        if session["member_added"] == True:
            flash("Member added succesfully.", "info")
        else:
            flash("Member deleted succesfully.", "info")
    session.pop("member_added", None)

    if session.get("error") is not None:

        if session["error"] == True:
            flash("User does not exist, please try changing the user email.", "info")
    session.pop("error", None)

    if session.get("errort") is not None:

        if session["errort"] == True:
            flash("Team does not exist, please try changing the team name.", "info")
    session.pop("errort", None)

    if session.get("file-error") is not None:

        if session["file-error"] == True:
            flash(
                "File not yet available to download. Please try after some time. ", "info")
    session.pop("file-error", None)

    if session.get("admin") is not None:

        if session["admin"] == True:
            flash(
                "You cannot remove yourself. If you wish you to remove team, select Delete Team", "info")
    session.pop("admin", None)

    messages = Message.query.filter_by(team_id=team_id)
    all_teams = TeamMembers.query.filter_by(user_id=current_user.id)
    team = Team.query.get(team_id)
    team_details = TeamMembers.query.filter(
        TeamMembers.user_id == current_user.id, TeamMembers.team_id == team.id).first()
    a = TeamMembers.query.filter(
        TeamMembers.is_admin == True, TeamMembers.team_id == team.id).first()
    if a is None:
        session['errort'] = True
        return redirect('/profile')

    ad = User.query.filter_by(id=a.user_id).first()

    memcnt = TeamMembers.query.filter(TeamMembers.team_id == team.id).count()

    mess = Message.query.filter(team_id == team.id)
    active_members = ActiveUsers.query.filter_by(team_id=team_id)
    active_members_list = []
    for user in active_members:
        active_members_list.append(user.user_id)
    members = db.session.query(User).join(TeamMembers).filter(
        TeamMembers.user_id == User.id).filter_by(team_id=team_id)

    print(active_members)
    return render_template('profile.html', curr_team=team, teams=all_teams, is_admin=team_details.is_admin, admin=ad, cnt=memcnt, active_members=active_members_list, members=members, messages=messages)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    session["logged_in"] = False
    return redirect('/')


@app.route("/team/<int:team_id>/add_member", methods=['GET', 'POST'])
@login_required
def add_member(team_id):
    if not current_user.is_authenticated:
        return redirect('login')

    print(team_id)
    email = request.form['email']
    print(email)

    user = User.query.filter_by(email=email).first()

    if user is None:
        session['error'] = True
        return redirect(url_for('team_chat', team_id=team_id))

    t = Team.query.filter_by(id=team_id).first()
    newMem = TeamMembers(is_admin=False, user_id=user.id,
                         team_id=team_id, team_name=t.team_name)
    db.session.add(newMem)
    db.session.commit()
    session["member_added"] = True
    return redirect(url_for('team_chat', team_id=team_id))


@app.route("/team/<int:team_id>/remove_member", methods=['GET', 'POST'])
@login_required
def remove_member(team_id):
    if not current_user.is_authenticated:
        return redirect('login')

    email = request.form['email']

    user = User.query.filter_by(email=email).first()

    if user is None:
        session['error'] = True
        return redirect(url_for('team_chat', team_id=team_id))

    if email == current_user.email:
        session["admin"] = True
        return redirect(url_for('team_chat', team_id=team_id))

    t = Team.query.filter_by(id=team_id).first()
    TeamMembers.query.filter_by(user_id=user.id, team_id=team_id).delete()
    db.session.commit()
    session["member_added"] = False
    return redirect(url_for('team_chat', team_id=team_id))


@app.route("/team/<int:team_id>/delete_team", methods=['GET', 'POST'])
@login_required
def delete_team(team_id):
    if not current_user.is_authenticated:
        return redirect('login')

    team_name = request.form['team']

    t = Team.query.filter_by(team_name=team_name).first()
    if t is None:
        session['errort'] = True
        return redirect(url_for('team_chat', team_id=team_id))

    team = Team.query.filter_by(id=team_id).first()
    db.session.delete(team)
    db.session.commit()
    session["team_created"] = False
    path = os.path.join(app.config['UPLOAD_FOLDER'], str(team_id))
    if os.path.isdir(path):
        shutil.rmtree(path)
    return redirect('/profile')


# Tasks

@app.route("/taskentry", methods=["POST", "GET"])
def add_task():
    if not current_user.is_authenticated:
        return redirect('login')

    if session.get("task-error") is not None:
        if session["task-error"] == True:
            flash("Please select team name", "info")
    session.pop("task-error", None)

    task = NewTask()
    all_teams = TeamMembers.query.filter_by(user_id=current_user.id)
    task.user_team.choices = [(c.team_name) for c in TeamMembers.query.filter_by(
        user_id=current_user.id, is_admin=True).all()]
    task.user_team.choices.insert(0, ("Select a team"))
    task.user_email.choices = []
    task.user_email.choices.insert(0, ("Select a member"))
    if request.method == 'POST':
        name = task.task_name.data
        desc = task.task_desc.data
        team_name = task.user_team.data

        deadline_str = str(task.deadline_date.data)
        deadline_obj = datetime.strptime(deadline_str, "%Y-%m-%d")

        team_name = task.user_team.data

        if team_name == "Select a team":
            session["task-error"] = True
            return redirect('/taskentry')
        else:
            t = Team.query.filter_by(team_name=team_name).first()
            email = task.user_email.data
            user = User.query.filter_by(email=email).first()
        # fetch user id from User table given email
            task_current = Task(task_name=name, task_desc=desc, team_id=t.id,
                                user_id=user.id, assigned_by=current_user.id, deadline=deadline_obj)
            db.session.add(task_current)
            db.session.commit()
            session["task_created"] = True
            return redirect('taskmanager')

    return render_template('createtasks.html', form=task, teams=all_teams, check=True)


@app.route("/mem/<team>", methods=["POST", "GET"])
def mem(team):
    members = TeamMembers.query.filter_by(team_name=team).all()
    memberArray = []
    for mem in members:
        z = User.query.filter_by(id=mem.user_id).first()
        memobj = {}
        memobj['team'] = mem.team_name
        memobj["member"] = z.email

        memberArray.append(memobj)
    return jsonify({'members': memberArray})


@app.route('/viewtasks')
@login_required
def viewtasks():

    if session.get("task_created") is not None:

        if session["task_created"] == True:
            flash("Task added succesfully.", "info")
        else:
            flash("Task deleted succesfully.", "info")
    session.pop("task_created", None)

    if session.get("response") is not None:

        if session["response"] == True:
            flash("Response submitted succesfully.", "info")
    session.pop("response", None)
    all_teams = TeamMembers.query.filter_by(user_id=current_user.id)
    passed = Task.query.filter(
        Task.status == 0, Task.user_id == current_user.id, Task.deadline < date.today())
    for task in passed.all():
        task.status = 2
        db.session.commit()
    incompleted = db.session.query(Task, Team).filter(Task.team_id == Team.id).filter(
        Task.status == 0, Task.user_id == current_user.id).all()
    completed = db.session.query(Task, Team).filter(Task.team_id == Team.id).filter(
        Task.status == 1, Task.user_id == current_user.id).all()
    expired = db.session.query(Task, Team).filter(Task.team_id == Team.id).filter(
        Task.status == 2, Task.user_id == current_user.id).all()
    return render_template('viewtasks.html', incompleted=incompleted, completed=completed, expired=expired, teams=all_teams, check=True)


@app.route('/taskmanager')
@login_required
def taskmanager():
    if session.get("task_created") is not None:
        if session["task_created"] == True:
            flash("Task added succesfully.", "info")
        else:
            flash("Task deleted succesfully.", "info")
    session.pop("task_created", None)

    all_teams = TeamMembers.query.filter_by(user_id=current_user.id)
    passed = Task.query.filter(
        Task.status == 0, Task.assigned_by == current_user.id, Task.deadline < date.today())
    for task in passed.all():
        task.status = 2
        db.session.commit()
    incompleted = db.session.query(Task, Team, User).filter(Task.team_id == Team.id, User.id == Task.user_id).filter(
        Task.status == 0, Task.assigned_by == current_user.id).all()
    completed = db.session.query(Task, Team, User).filter(Task.team_id == Team.id, User.id == Task.user_id).filter(
        Task.status == 1, Task.assigned_by == current_user.id).all()
    expired = db.session.query(Task, Team, User).filter(Task.team_id == Team.id, User.id == Task.user_id).filter(
        Task.status == 2, Task.assigned_by == current_user.id).all()
    return render_template('taskmanager.html', incompleted=incompleted, completed=completed, expired=expired, teams=all_teams, check=True, tsk=True)


@app.route('/completetask/<int:task_id>')
def complete(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.status = 1
    task.completed_on = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S Z')
    db.session.commit()
    return redirect('/viewtasks')


@app.route('/undocompletetask/<int:task_id>')
def undo_complete(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.status = 0
    task.completed_on = None
    db.session.commit()
    return redirect('/viewtasks')


@app.route('/undocompletetask2/<int:task_id>')
def undo_complete2(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.status = 0
    task.completed_on = None
    db.session.commit()
    return redirect('/taskmanager')


@app.route('/taskmanager/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    db.session.delete(task)
    db.session.commit()
    session["task_created"] = False
    return redirect('/taskmanager')


@app.route('/taskmanager/update/<int:task_id>', methods=["POST", "GET"])
@login_required
def update_task(task_id):
    print("update task entry")
    task_form = NewTask()
    task = Task.query.filter_by(id=task_id).first()
    team = Team.query.filter_by(id=task.team_id).first()
    user = User.query.filter_by(id=task.user_id).first()
    task_form.user_team.choices = [(c.team_name) for c in TeamMembers.query.filter_by(
        user_id=current_user.id, is_admin=True).all()]
    task_form.user_email.choices = [(User.query.filter(User.id == c.user_id).first(
    ).email) for c in TeamMembers.query.filter_by(team_id=task.team_id)]
    task_form.user_team.choices.remove(team.team_name)
    task_form.user_email.choices.remove(user.email)
    task_form.user_team.choices.insert(0, team.team_name)
    task_form.user_email.choices.insert(0, user.email)
    all_teams = TeamMembers.query.filter_by(user_id=current_user.id)
    if request.method == "POST":
        deadline_str = str(task_form.deadline_date.data)
        deadline_obj = datetime.strptime(deadline_str, "%Y-%m-%d")
        task = Task.query.filter_by(id=task_id).first()
        task.task_name = task_form.task_name.data
        task.task_desc = task_form.task_desc.data
        email = task_form.user_email.data
        user = User.query.filter_by(email=email).first()
        task.user_id = user.id  # fetch from db from email task_form.email
        task.deadline = deadline_obj
        task.status = 0
        db.session.commit()
        return redirect('/taskmanager')
    task_form.task_name.data = task.task_name
    task_form.task_desc.data = task.task_desc
    task_form.deadline_date.data = task.deadline
    return render_template("updatetasks.html", form=task_form, taskid=task_id, teams=all_teams, check=True)


@app.route('/submitrespone/<int:task_id>', methods=["POST", "GET"])
def submit_response(task_id):
    if request.method == "POST":
        task = Task.query.filter_by(id=task_id).first()
        task.response = request.form['response']
        db.session.commit()
        session["response"] = True
        return redirect('/viewtasks')


def newfilepath(filename):
    counter = 1
    file_part, ext_part = os.path.splitext(filename)
    filename = file_part+"({})"+ext_part
    while os.path.isfile(filename.format(counter)):
        counter = counter+1
    filename = filename.format(counter)
    print(filename)
    return filename


@app.route('/uploads/<int:team_id>', methods=["POST"])
def uploads(team_id):
    if request.method == 'POST':
        print("Team id ", team_id)
        if not os.path.isdir(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        path = os.path.join(app.config['UPLOAD_FOLDER'], str(team_id))
        if not os.path.isdir(path):
            os.mkdir(path)
        file = request.files['file']
        filename = file.filename
        file_path = os.path.join(path, filename)
        if os.path.exists(file_path):
            file_path = newfilepath(file_path)
        # delay
        file.save(file_path)
    return redirect(url_for('team_chat', team_id=team_id))


@app.route('/download/<int:team_id>/<filename>', methods=['GET'])
def download(team_id, filename):
    if current_user.is_authenticated:
        teams_of_current_user = TeamMembers.query.filter_by(
            user_id=current_user.id).all()
        for team in teams_of_current_user:
            if team_id == team.team_id:
                file_path = os.path.join(os.path.join(
                    app.config['UPLOAD_FOLDER'], str(team_id)), filename)
                if os.path.exists(file_path) == False:
                    session["file-error"] = True
                    return redirect(url_for('team_chat', team_id=team_id))
                else:
                    session["file-error"] = False
                    # Add a Flash Message Saying that file is not present is in the server, the link will be available if file uploaded succesfully
                return send_file(file_path, as_attachment=True, attachment_filename="")
        return redirect(url_for('profile'))
    else:
        return redirect(url_for('main'))

# Calendar


@app.route("/calendar", methods=['GET', 'POST'])
@login_required
def cal():
    all_teams = TeamMembers.query.filter_by(user_id=current_user.id)
    return render_template("calendar.html", teams=all_teams, check=True)


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    tasks = Task.query.filter_by(user_id=current_user.id, status=0).all()
    json_array = []
    for task in tasks:
        json_file = {
            "title": task.task_name,
            "start": str(task.deadline),
            "end": str(task.deadline)
        }
        json_array.append(json_file)
    with open('tasks.json', 'w') as outfile:
        json.dump(json_array, outfile)
    with open("tasks.json", "r") as input_data:
        return input_data.read()

# Sockets


@socketio.on('message')
def on_message(data):

    print("Message received at the server")

    t = User.query.filter_by(id=data["id"]).first()

    if(data['type'] == 1):
        m = Message(sender=data["id"], team_id=data["room"], msgbody=data["msg"],
                    time_stamp=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S Z'))
        db.session.add(m)
        db.session.commit()
        emit('receive', {'type': 1, 'msg': data["msg"], 'username': t.name,
                         'time_stamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S Z')}, room=data["room"], broadcast=True)
    else:
        file_path = os.path.join(os.path.join(
            app.config['UPLOAD_FOLDER'], data["room"]), data["filename"])
        if os.path.exists(file_path) == False:
            pass
        else:
            file_path = newfilepath(file_path)
            data["filename"] = os.path.basename(file_path)
        emit('receive', {'type': 2, 'filename': data["filename"], 'username': t.name,
                         'time_stamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S Z'), "room": data["room"]}, room=data["room"], broadcast=True)
        file_db = File(name=data["filename"], size=data["size"],
                       path=file_path, team_id=data["room"])
        db.session.add(file_db)
        db.session.commit()
        file_db = File.query.filter_by(path=file_path).first()
        m = Message(sender=data["id"], team_id=data["room"], msgbody=file_db.name, time_stamp=datetime.utcnow(
        ).strftime('%Y-%m-%dT%H:%M:%S Z'), file_id=file_db.id)
        db.session.add(m)
        db.session.commit()


@socketio.on('join')
def join(data):
    join_room(data["room"])
    emit('system', {'type': 3, 'state': "active",
                    'user_id': data["user_id"]}, room=data["room"], broadcast=True)
    active = ActiveUsers.query.filter_by(
        user_id=data["user_id"], team_id=data["room"])
    active = ActiveUsers(user_id=data["user_id"], team_id=data["room"])
    db.session.add(active)
    db.session.commit()


@socketio.on('leave')
def leave(data):
    leave_room(data["room"])
    emit('system', {'type': 3, 'state': "not active",
                    'user_id': data["user_id"]}, room=data["room"], broadcast=True)
    active = ActiveUsers.query.filter_by(
        user_id=data["user_id"], team_id=data["room"])
    if active is not None:
        active.delete()
    db.session.commit()


if __name__ == "__main__":
    socketio.run(app, debug=True)
