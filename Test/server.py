#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from werkzeug import secure_filename
from functools import wraps
import sqlite3, os
from flask import *
from flask_login import *



app = Flask(__name__)


UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.secret_key = "secret key"
app.database = "database.db"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print session
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/welcome', methods=['GET', 'POST'])
@login_required
def welcome():
    conn = sqlite3.connect('test.db')
    flag = 0
    for x in session:
        flag += 1
        if flag == 2:
            user = x
            break
    print user
    if request.method == 'POST':
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        cap = request.form['caption']
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        path = UPLOAD_FOLDER + filename
        conn.execute("insert into POST (CAPTION, IMAGE, CREATOR,TIME) values (?, ?, ?,?);",(cap, path, user,time ))
        conn.commit()
        conn.close()
    conn = sqlite3.connect('test.db')
    cursor = conn.execute("SELECT id, caption, image, creator, time  from POST")
    dic = cursor.fetchall()
    for i in range(len(dic)):
            dic[i] =  (dic[i][0],dic[i][1].encode('utf-8'),dic[i][2].encode('utf-8'), dic[i][3].encode('utf-8'), dic[i][4].encode('utf-8'))
    print dic
    return render_template('hello.html',DATA = dic ,user = user)


@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/post/uploads/<filename>')
def send_file2(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/post/<number>/comment/uploads/<filename>')
def send_file3(filename,number):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/post/<number>',  methods=['GET', 'POST'])
@login_required
def post(number):
    conn = sqlite3.connect('test.db')
    flag = 0
    print session
    for x in session:
        flag += 1
        if flag == 2:
            print 1
            user = x
            break

    if request.method == 'POST':
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        COMMENT = request.form['comment']
        print COMMENT, number

        conn.execute("insert into COMMENT (comment, F_KEY,creator,time) values (?, ?,?,?);",(COMMENT, number, user, time))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('test.db')
    cursor = conn.execute("SELECT id, caption, image , creator, time from POST")
    for row in cursor:
        if str(row[0]) == number.encode('utf-8'):

            id = row[0]
            caption = row[1]
            image = row[2]
            creator = row[3]
            break

    cursor2 = conn.execute("SELECT ID, comment, F_KEY, creator, time from COMMENT")
    com_dic = {}

    for row in cursor2:
        if str(row[2]) == number.encode('utf-8'):
            COM_ID = row[0]
            COM = row[1]
            cre = row[3]
            time = row[4]
            com_dic[str(COM_ID)] = (COM.encode('utf-8'), cre.encode('utf-8'), time.encode('utf-8'))
    cursor3 = conn.execute("SELECT ID, reply, F_KEY_POST,F_KEY_COMMENT, creator, time from REPLY")
    rep_dic = {}
    for row in cursor3:
        if str(row[2]) == number.encode('utf-8') :
            REP = row[1]
            com_num = row[3]
            cre_rep = row[4]
            time = row[5]
            rep_dic[com_num] = (REP, cre_rep,time)
    return render_template('post.html', ID = id, CAP = caption, IMG = image,post_creator = creator ,COMMENT = com_dic, rep_dic = rep_dic, user = user)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    print session
    flash('you were just logged out!')
    return redirect(url_for('welcome'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:

        return redirect(url_for('welcome'))

    error = None
    con = sqlite3.connect('login.db')
    cur = con.execute('select * from logint')
    if request.method == 'POST':
        username = request.form['username']
        new_username = username.lower()
        for row in cur.fetchall():
            if new_username == row[0] and request.form['password'] == row[1]:
                session['logged_in'] = True
                session[username] = True
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
            print new_username
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




@app.route('/post/<number>/comment/<number2>', methods=['GET', 'POST'])
@login_required

def reply(number,number2):
    conn = sqlite3.connect('test.db')
    if request.method == 'POST':
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        reply = request.form['reply']
        number = number.encode('utf-8')
        number2 = number2.encode('utf-8')
        conn.execute("insert into REPLY (reply, F_KEY_POST, F_KEY_COMMENT) values (?, ?,?);",(reply, number, number2))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('test.db')
    cursor = conn.execute("SELECT id, caption, image  from POST")
    for row in cursor:
        if str(row[0]) == number.encode('utf-8'):

            id = row[0]
            caption = row[1]
            image = row[2]


            break

    cursor2 = conn.execute("SELECT ID, comment, F_KEY from COMMENT")
    for row in cursor2:
        print 111111111111111111111111
        print str(row[0])
        print number2.encode('utf-8')

        if str(row[0]) == number2.encode('utf-8'):
            COM = row[1]
            print COM
            break



    cursor3 = conn.execute("SELECT ID, reply, F_KEY_POST,F_KEY_COMMENT from REPLY")
    rep_dic = []
    for row in cursor3:

        if str(row[2]) == number.encode('utf-8') and str(row[3]) == number2.encode('utf-8'):

            REP = row[1]
            print REP
            com_num = row[3]
            print com_num
            rep_dic.append(REP.encode('utf-8'))

    print rep_dic
    return render_template('reply.html',number2 = number2, number = number, rep_dic = rep_dic, ID = id, CAP = caption, IMG = image, com_text = COM)



if __name__ == '__main__':
    app.run(debug=True)
