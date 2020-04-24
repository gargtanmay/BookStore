import csv
import os


from flask import Flask,render_template,request,redirect,url_for,flash,session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
import requests
from flask_debug import Debug

engine=create_engine("postgres://postgres:tanmay@localhost:5432/book")

db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author,year in reader:
        db.execute("insert into book_data (isbn,title,author,year) values (:isbn,:title,:author,:year)",{"isbn":isbn,"title":title,"author":author,"year":year})
        db.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
