#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, redirect, session, flash
from functools import wraps
import sqlite3


app = Flask(__name__)

app.secret_key = "secret key"
app.database = "database.db"


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('you were just logged out!')
    return redirect(url_for('welcome'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    con = sqlite3.connect('login.db')
    cur = con.execute('select * from logint')
    if request.method == 'POST':
        username = request.form['username']
        new_username = username.lower()
        for row in cur.fetchall():
            if new_username == row[0] and request.form['password'] == row[1]:
                session['logged_in'] = True
                flash('you were just logged in!')
                return redirect(url_for('welcome'))
        else:
            error = '. نام کاربری یا رمز عبور اشتباه است'
            error = error.decode('utf-8')
    return render_template('login2.html', error=error)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    error = None
    con = sqlite3.connect('login.db')
    with con:
        cur = con.cursor()
        data_list = con.execute('select * from logint')
        cnt = 0
        if request.method == 'POST':
            username = request.form['username']
            new_username = username.lower()
            for row in data_list.fetchall():
                if new_username == row[0]:
                    cnt += 1
                    error = '.نام کاربری تکراری است'
                    error = error.decode('utf-8')
                elif request.form['email'] == row[2]:
                    cnt += 1
                    error = '.پست الکترونیک تکراری است'
                    error = error.decode('utf-8')
                elif request.form['username'] == '' or request.form['password'] == '' or request.form['email'] == '' or request.form['password2']=='':
                    error = '.نام کاربری یا رمز عبور نباید خالی باشد'
                    error = error.decode('utf-8')
                    cnt += 1
                    print 3
                elif request.form['password'] < 8:
                    cnt += 1
                    error = '.رمز عبور نباید کمتر از 8 حرف باشد'
                    error = error.decode('utf-8')
                elif request.form['password'] != request.form['password2']:
                    cnt += 1
                    error = '.رمز عبور مانند هم نیستند'
                    error = error.decode('utf-8')
            if cnt == 0:
                flash('you just signed up!')
                cur.execute('insert into  logint (username, password, email) values(?, ?, ?)', [new_username, request.form['password'], request.form['email']])
                return redirect(url_for('login'))

    return render_template('signup.html', error=error)


def connect_db():
    return sqlite3.connect(app.database)


if __name__ == '__main__':
    app.run(debug=True)
