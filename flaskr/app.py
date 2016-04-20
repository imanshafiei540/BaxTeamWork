from flask import Flask, render_template, request, url_for, redirect, session, flash

app = Flask(__name__)

app.secret_key = "secret key"

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('you were just logged out!')
    return redirect(url_for('welcome'))


@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('you were just logged in!')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)

