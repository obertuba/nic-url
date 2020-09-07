#!/usr/bin/env python3
from flask import Flask, render_template, redirect, request
import sqlite3
from os import path


app = Flask(__name__)
DATABASE = 'urls.db'
REDIRECT_PAGE = 'http://nic-url.herokuapp.com/redirect/'


def create_database():
    print('\nCreating new database since no database was found\n')
    with sqlite3.connect(DATABASE) as conn:
        db = conn.cursor()
        db.execute('CREATE TABLE urls (url VARCHAR (512) NOT NULL UNIQUE);')
        conn.commit()

def check_database():
    return path.exists(DATABASE)


def check_url(url: str) -> bool:
    if '.' not in url: return False
    
    # if using both HTTP and HTTPS:
    #   if REDIRECT_PAGE[5:] in url.lower(): return False

    # if using HTTP only or HTTPS only:
    if REDIRECT_PAGE in url.lower(): return False

    
    return True


def generate(url) -> str:
    with sqlite3.connect(DATABASE) as conn:
        try:
            db = conn.cursor()
            db.execute(f"INSERT INTO urls VALUES ('{url}')")
            conn.commit()
            short = db.lastrowid

        except sqlite3.IntegrityError:
            # url is not unique --> get id of url
            db.execute(f"SELECT rowid FROM urls WHERE url='{url}'")
            short = db.fetchone()[0]
        
    return short


@app.route('/redirect/<string:id>')
def redirect_to_url(id):
    with sqlite3.connect(DATABASE) as conn:
        db = conn.cursor()
        db.execute(f"SELECT url FROM urls WHERE rowid='{id}'")

        try:
            url = db.fetchone()[0]
            return redirect(url)

        except TypeError:
            url = REDIRECT_PAGE + str(id)
            return render_template('fail.html', url=url)
    
           
    

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        # generate short url
        original_url = request.form['url']

        if 'http' not in original_url:
            url = 'http://' + original_url
        else:
            url = original_url
            
        if not check_url(url):
            return render_template('index.html', short=original_url, success=False, copy=False)

        short = REDIRECT_PAGE + str(generate(url))

        return render_template('index.html', short=short, success=True, copy=True)
    else:
        # render normal page
        return render_template('index.html', success=True, copy=False)


if __name__ == "__main__":
    
    if not check_database():
        create_database()

    app.run(debug=True)

else:
    # this gets executed when imported as a module
    # (for deployment on pythonanywhere )
    if not check_database():
        create_database()
