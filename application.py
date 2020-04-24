import os

from flask import Flask,render_template,request,redirect,url_for,flash,session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from flask_debug import Debug

engine=create_engine("postgres://postgres:tanmay@localhost:5432/book")

db = scoped_session(sessionmaker(bind=engine))

app=Flask(__name__)
Debug(app)
app.run(debug=True)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        user = db.execute(" Select * from user_database where username=:username", {"username":username} ).fetchone()
        if user.username==username and user.password==password:
            session["logged_in"] = True
            session["user_id"] = user.id
            session["user_name"] = username
            return redirect(url_for('search'))
        else:
            return render_template("error.html",error="User not found")
    else:
        return render_template("login.html")



@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        password1=request.form.get('password1')
        user=db.execute("select username from user_database where username=:username",{"username":username}).fetchone()
        if user:
            return render_template("error.html",error="Username exists")
        elif password!=password1:
            return render_template("error.html",error="Password Incorrect")
        else:
            db.execute(" insert into user_database (username,password) Values(:username,:password)", {"username":username,"password":password} )
            db.commit()
            flash("Succesfully registered")
            return render_template("home.html")
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    if session.get("logged_in"):
        session["logged_in"] = False
        session["user_id"] = None
        return redirect("/")
    else:
        return render_template("login.html")
@app.route('/search',methods=["GET","POST"])
def search():
    if session.get("logged_in"):
        if request.method=='GET':
            return render_template("search.html")
        else:
            x=request.form.get("search")
            books=db.execute("select * from book_data where isbn like :isbn OR title like :title OR author like :author",{"isbn":x,"title":x,"author":x}).fetchall()
            if books:
                return render_template("search.html",books=books)
            else:
                return render_template("error.html",error="No matches found")
    else:
        return render_template("login.html")

@app.route('/search/<int:book_id>',methods=["GET","POST"])
def searchbook(book_id):
    books=db.execute("select * from book_data where id=:id",{"id":book_id}).fetchone()
    res=requests.get("https://www.goodreads.com/book/review_counts.json?isbns="+books.isbn+"&key=7QmCSNBbbmnVYWsONvNnQ")
    res=res.json()
    ratings=res["books"][0]["average_rating"]
    return render_template("searchbook.html",books=books,ratings=ratings)
