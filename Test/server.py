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
    user=session['user']

    if request.method == 'POST':
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        cap = 'No Caption'
        cap = request.form['caption']
        file = request.files['image']
        path = 'uploads/image.png'
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

    return render_template('hello.html',DATA = dic ,user = user)
DB = "./login.db"

def get_all_users( json_str = False ):
    conn = sqlite3.connect( DB )
    conn.row_factory = sqlite3.Row
    db = conn.cursor()

    rows = db.execute('''
    SELECT * from logint
    ''').fetchall()

    conn.commit()
    conn.close()
    dic = {}
    if json_str:
        return ( [dict(ix) for ix in rows] )


    return rows
@app.route('/mypanel', methods=['GET', 'POST'])
@login_required
def panel():
    user=session['user']
    con=sqlite3.connect('login.db')
    cur = con.execute('select * from logint WHERE id=%s' % get_user_id(user))
    data = cur.fetchall()

    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        status = request.form['status']
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        file = request.files['image']
        path = data[0][4]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            path = UPLOAD_FOLDER + filename

        if status:
            cur.execute("UPDATE logint SET status=? WHERE id=?",(status,data[0][3]))
            con.commit()




        if path:
            cur.execute("UPDATE logint SET  user_image=? WHERE id=?",(path,data[0][3]))
            con.commit()

        if lastname:
            cur.execute("UPDATE logint SET  lastname=? WHERE id=?",(lastname,data[0][3]))
            con.commit()

        if firstname:
            cur.execute("UPDATE logint SET  firstname=? WHERE id=?",(firstname,data[0][3]))
            con.commit()




        if data[0][1].encode('utf-8') == oldpassword:
            cur.execute("UPDATE logint SET  password=? WHERE id=?",(newpassword,data[0][3]))
            con.commit()



    return render_template('panel.html',data=data)

def get_user_id(user):
    con=sqlite3.connect('login.db')
    cur = con.execute('select * from logint')
    data = cur.fetchall()
    user=session['user']
    for item in data:
        if user == item[0]:
            return item[3]




@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/post/uploads/<filename>')
def send_file2(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/post/<number>/comment/uploads/<filename>')
def send_file3(filename,number):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/edit/<number>',methods=['GET','POST'])
@login_required
def edit(number):
    conn=sqlite3.connect('test.db')
    user=session['user']
    cursor=conn.execute("SELECT id ,caption,image,creator,time from POST WHERE id="+number)
    post=cursor.fetchall()
    if request.method == 'POST':

        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        cap = request.form['caption']
        file = request.files['image']
        id=request.form['id']
        path = 'uploads/image.png'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            path = UPLOAD_FOLDER + filename



        cursor.execute("UPDATE POST SET  CAPTION= ? ,IMAGE = ?,CREATOR = ?,TIME = ? WHERE id= ? ",(cap,path,user,time,id))
        conn.commit()
        cursor=conn.execute("SELECT id ,caption,image,creator,time from POST WHERE id="+number)
        post=cursor.fetchall()
        conn.close()

    conn.close()
    if post==[]:
        abort(403)
    elif post[0][3]!=user:
        abort (403)

    else:

        return render_template('edit.html',DATA=post)

@app.route('/myposts' , methods=["GET","POST"])
def myposts():
    conn =sqlite3.connect('test.db')
    curr_user=session['user']

    cursor=conn.execute("SELECT id,caption,image,creator,time from POST")
    dic = cursor.fetchall()
    if request.method == 'POST':

        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        cap = request.form['caption']
        file = request.files['image']
        id=request.form['id']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        path = UPLOAD_FOLDER + filename
        cursor.execute("UPDATE POST SET  CAPTION= ? ,IMAGE = ?,CREATOR = ?,TIME = ? WHERE id= ? ",(cap,path,user,time,id))
        conn.commit()
        conn.close()

    for i in range(len(dic)):
            dic[i] =  (dic[i][0],dic[i][1].encode('utf-8'),dic[i][2].encode('utf-8'), dic[i][3].encode('utf-8'), dic[i][4].encode('utf-8'))

    mine=[]
    for i in dic:
        if i[3]==curr_user:
            mine.append(i)

    conn.close()



    return render_template('myposts.html',DATA=mine,user=curr_user)

@app.route('/post/<number>',  methods=['GET', 'POST'])
@login_required
def post(number):
    conn = sqlite3.connect('test.db')
    user=session['user']

    if request.method == 'POST':
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        COMMENT = request.form['comment']


        conn.execute("insert into COMMENT (comment, F_KEY,creator,time,user_image) values (?, ?,?,?,?);",(COMMENT, number, user, time, getUserImage(user)))
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
            comment_time = row[4]
            break

    cursor2 = conn.execute("SELECT ID, comment, F_KEY, creator, time, user_image from COMMENT")
    com_dic = {}

    for row in cursor2:
        if str(row[2]) == number.encode('utf-8'):
            user_img = row[5]
            COM_ID = row[0]
            COM = row[1]
            cre = row[3]
            time = row[4]

            com_dic[str(COM_ID)] = (COM.encode('utf-8'), cre.encode('utf-8'), time.encode('utf-8'),user_img.encode('utf-8'))
    cursor3 = conn.execute("SELECT ID, reply, F_KEY_POST,F_KEY_COMMENT, creator, time, user_image from REPLY")
    rep_dic = {}
    for row in cursor3:
        if str(row[2]) == number.encode('utf-8') :
            REP = row[1]
            com_num = row[3]
            cre_rep = row[4]
            time = row[5]
            rep_image = row[6]
            rep_dic[com_num] = (REP, cre_rep,time,rep_image)

    return render_template('post.html', ID = id, CAP = caption, IMG = image,post_creator = creator ,COMMENT = com_dic, rep_dic = rep_dic, user = user, ct = comment_time)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user',None)
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
                user_img = row[4]
                session['logged_in'] = True
                session['user']=username
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


def getUserImage(user):
    con = sqlite3.connect('login.db')
    cur = con.execute('select * from logint')
    for row in cur.fetchall():
        if user == row[0] :
            return row[4]



@app.route('/post/<number>/comment/<number2>', methods=['GET', 'POST'])
@login_required

def reply(number,number2):

    user=session['user']
    conn = sqlite3.connect('test.db')
    if request.method == 'POST':
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        reply = request.form['reply']
        number = number.encode('utf-8')
        number2 = number2.encode('utf-8')
        conn.execute("insert into REPLY (reply, F_KEY_POST, F_KEY_COMMENT, CREATOR,USER_IMAGE,TIME) values (?, ?,?,?,?,?);",(reply, number, number2, user, getUserImage(user),time))
        conn.commit()
        conn.close()

    conn = sqlite3.connect('test.db')
    cursor = conn.execute("SELECT id, caption, image, creator, user_image,time  from POST")
    for row in cursor:
        if str(row[0]) == number.encode('utf-8'):

            id = row[0]
            caption = row[1]
            image = row[2]
            post_creator = row[3]
            post_user_image = row[4]
            post_time = row[5]


            break

    cursor2 = conn.execute("SELECT ID, comment, F_KEY, creator, user_image,time  from COMMENT")
    for row in cursor2:
        comment_content = []
        if str(row[0]) == number2.encode('utf-8'):
            COM = row[1]
            creator = row[3]
            user_image = row[4]
            time = row[5]
            comment_content+=[COM , creator ,user_image,time ]
            break



    cursor3 = conn.execute("SELECT ID, reply, F_KEY_POST,F_KEY_COMMENT,creator, user_image,time from REPLY")
    rep_dic = {}
    for row in cursor3:

        if str(row[2]) == number.encode('utf-8') and str(row[3]) == number2.encode('utf-8'):
            REP = row[1]
            com_num = row[3]
            reply_cre = row[4]
            reply_user_img = row[5]
            time_reply = row[6]
            rep_dic[com_num] = (REP,reply_cre, reply_user_img,time_reply)



    return render_template('reply.html',number2 = number2, number = number, rep_dic = rep_dic, ID = id, CAP = caption, IMG = image, comment_content = comment_content,pc = post_creator,pu = post_user_image, pt = post_time)

@app.route('/people', methods=['GET', 'POST'])
@login_required

def people():
    data = get_all_users()

    return render_template('people.html', data = data)


if __name__ == '__main__':
    app.run(debug=True)
