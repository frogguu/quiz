from flask import Flask, render_template, session, request, redirect, url_for, g
from database import get_db, close_db
from flask_session import Session
from forms import RegistrationForm, LoginForm, SuggestionForm, DeleteForm
from random import shuffle
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Admin user name and password is
# Username: admin
# Password: password
# Registrating makes up a regular user
# Login and register function are adapted from the lectures
# shuffle and deck code comes from W3Schools (https://www.w3schools.com/python/ref_random_shuffle.asp)

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id",None)
    g.admin = session.get("admin")

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user_check = db.execute(''' SELECT * FROM users
                                    WHERE user_id = ?;''',(user_id,)).fetchone()
        if user_id == "admin" and user_check is None:
            db.execute('''INSERT INTO users (user_id, password, games_played, quests_ans, high_score, admin_value)
                           VALUES (?, ?, 0, 0, 0, 1);''',(user_id,generate_password_hash(password)))
            db.commit()
            return redirect(url_for("login"))
        elif user_check is None:
            db.execute('''INSERT INTO users (user_id, password, games_played, quests_ans, high_score, admin_value)
                           VALUES (?, ?, 0, 0, 0, 0);''',(user_id,generate_password_hash(password)))
            db.commit()
            return redirect(url_for("login"))
        else:
            form.user_id.errors.append("Someone already uses that name, please pick another")
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user = db.execute(''' SELECT * FROM users
                                WHERE user_id = ?;''',(user_id,)).fetchone()
        if user is None:
            form.user_id.errors.append("Unknown user id")
        elif not check_password_hash(user["password"],password):
            form.password.errors.append("Incorrect password!")
        else:
            session.clear()
            session["user_id"] = user_id
            session["high_score"] = user["high_score"]
            session["admin"] = user["admin_value"]
            session["high_score"] = user["high_score"]
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page)
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Links to the user's own profile
@app.route("/profile")
@login_required
def self_profile():
    user = g.user
    return redirect(url_for("profile", user=user))

# Links to the profile of the user specified
@app.route("/profile/<user>")
@login_required
def profile(user):
    db = get_db()
    user_info = db.execute(''' SELECT * FROM users
                        WHERE user_id = ?;''',(user,)).fetchone()
    user = user_info["user_id"]
    games = user_info["games_played"]
    quests = user_info["quests_ans"]
    high_score = user_info["high_score"]
    return render_template("profile.html", user=user, games=games, quests=quests, high_score=high_score)

# Quiz operates by going through a set of questions from the table that are deemed valid
# (Valid referring to questions that are not just suggestions and verified by the admin)   
@app.route("/quiz")
def quiz():
    # Initialising game, number of questions cleared and the deck
    if "game" not in session:
        session["game"] = {}
    if "quest_num" not in session["game"]:
        session["game"]["quest_num"] = 1
    if "quiz" not in session["game"]:
        session["game"]["quiz"] = {}
    if "quest_deck" not in session["game"]:
        session["game"]["quest_deck"] = []
    db = get_db()
    # Refilling the question deck if it's empty
    if session["game"]["quest_deck"] == []:
        count = db.execute(''' SELECT quest_id
                            FROM quizTable
                            WHERE valid = 1''').fetchall()
        quest_deck = []
        # Deck is full of quest IDs that correspond to valid questions
        for row in count:
            for num in row:
                num = str(num)
                quest_deck.append(num)
        shuffle(quest_deck)
        session["game"]["quest_deck"] = quest_deck
    # Popping a question ID to use from deck
    quest_id = str(session["game"]["quest_deck"].pop())
    answers_list = []
    answers = db.execute(''' SELECT question, trueA, falseA, falseB, falseC
                            FROM quizTable
                          WHERE quest_id = ?;''', (quest_id,)).fetchone()
    question = answers['question'] # Question is question
    ans_id = 0
    deck = list(range(0, 5)) 
    shuffle(deck) # Shuffles to ensure answer order is random
    while deck != []: 
        # Repeats until the answer deck is empty
        # Loop goes through the random answers, assigns it a number that will be its position,
        # checks if its true or false, records the truth value and adds the answers to a list
        random = deck.pop()
        if answers[random] == question: # Does not append question to answer list
            pass
        elif answers[random] == answers['trueA']:
            ans_id += 1
            session["game"]["quiz"][ans_id] = True 
            answers_list.append(answers[random])
        else:
            ans_id += 1
            session["game"]["quiz"][ans_id] = False
            answers_list.append(answers[random])
    quest_num = session["game"]["quest_num"]
    return render_template("quiz.html", ans=session["game"]["quiz"], 
            answers_list=answers_list, quest_num=quest_num, question=question)

@app.route("/quiz/<int:ans_id>")
def answered(ans_id):
    # If answer is correct, continues game
    if session["game"]["quiz"][ans_id] == True:
        session["game"]["quiz"].clear()
        session["game"]["quest_num"] = session["game"]["quest_num"] + 1
        return redirect(url_for("quiz"))
    # If answer is false, ends game
    else:
        quest_clear = session["game"]["quest_num"] - 1
        # Just ends game if not logged in
        if g.user is None:
            session["game"].clear()
            return render_template("results.html", quest_clear=quest_clear)
        # Updates profile if logged in
        else:
            db = get_db()
            db.execute('''UPDATE users SET games_played = games_played + 1
                        WHERE user_id = ?;''',(session["user_id"],))
            db.execute('''UPDATE users SET quests_ans = quests_ans + ?
                        WHERE user_id = ?;''',(quest_clear, session["user_id"]))
            # Updates high score if higher
            if session["high_score"] < quest_clear and g.user is not None:
                session["high_score"] = quest_clear
                db.execute('''UPDATE users SET high_score = ?
                        WHERE user_id = ?;''',(quest_clear, session["user_id"]))
            db.commit()
            session["game"].clear()
            return render_template("results.html", quest_clear=quest_clear)

# Leaderboard of all the user's stats, sorted by high score
@app.route("/leaderboard")
def leaderboard():
    db = get_db()
    info = db.execute(''' SELECT user_id, games_played, quests_ans, high_score FROM users
                        ORDER BY high_score DESC''').fetchall()
    user_data = []
    for row in info:
        user_list = []
        for data in row:
            if type(data) == str:
                if len(data) > 20:
                    pass
                else:
                    user_list.append(data)
            else:
                user_list.append(data)
        user_data.append(user_list)
    return render_template("leaderboard.html", user_data=user_data)

# Users can suggest questions here through a form
@app.route("/suggest", methods=["GET","POST"])
@login_required
def suggest():
    form = SuggestionForm()
    outcome = ""
    if form.validate_on_submit():
        quest = form.suggest.data
        trueA = form.true.data
        falseA = form.falseA.data
        falseB = form.falseB.data
        falseC = form.falseC.data
        db = get_db()
        db.execute('''INSERT INTO quizTable (question, trueA, falseA, falseB, falseC, valid)
                           VALUES (?, ?, ?, ?, ?, 0);''',(quest, trueA, falseA, falseB, falseC))
        db.commit()
        outcome = "Your suggestion has been submitted!"
    return render_template("suggest.html", form=form, outcome=outcome)

# Admin goes through questions and can switch them from being active in the quiz or not
# Can verify suggested questions and delete questions
@app.route("/review", methods=["GET","POST"])
@login_required
def review():
    if g.admin == 0:
        return redirect(url_for("index"))
    else:
        form = DeleteForm()
        db = get_db()
        if form.validate_on_submit:
            if "game" in session:
                if "quest_deck" in session["game"]:
                    session["game"]["quest_deck"].clear()
            quest_id = form.quest_id.data
            db.execute('''DELETE FROM quizTable 
                        WHERE quest_id = ?;''',(quest_id,))
            db.commit()
        quest_table = db.execute(''' SELECT *
                                FROM quizTable''').fetchall()
        question_list = []
        for row in quest_table:
            single = []
            for data in row:
                single.append(data)
            question_list.append(single)
    return render_template("review.html", question_list=question_list, form=form)

@app.route("/review/<int:quest_id>")
@login_required
def change_valid(quest_id):
    if "game" in session:
        if "quest_deck" in session["game"]:
            session["game"]["quest_deck"].clear()
    db = get_db()
    valid = db.execute('''SELECT valid FROM quizTable
                    WHERE quest_id = ?;''',(quest_id,)).fetchone()
    for value in valid:
        valid = value
    count = db.execute('''SELECT COUNT(quest_id) FROM quizTable
                    WHERE valid = ?;''',(valid,)).fetchone()
    for value in count:
        count = value
    if count == 1 and valid == 1:
        return redirect( url_for("review") )
    if valid == 0:
        db.execute('''UPDATE quizTable SET valid = '1'
                        WHERE quest_id = ?;''',(quest_id,))
        db.commit()
    else:
        db.execute('''UPDATE quizTable SET valid = '0'
                        WHERE quest_id = ?;''',(quest_id,))
        db.commit()
    return redirect( url_for("review") )