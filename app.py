from flask import Flask,render_template,request,session, redirect
from flask_mysqldb import MySQL
import numpy as np
import pickle
import datetime
from flask_mail import Mail, Message
filename = 'heart-disease-prediction-knn-model.pkl'
model = pickle.load(open(filename, 'rb'))

app=Flask(__name__)
app.secret_key = "heart"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'heart'
mysql = MySQL(app)

app.config['SECRET_KEY'] = 'heart'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gmail id'
app.config['MAIL_PASSWORD'] = 'your-email-password'

mail = Mail(app)
def send_email(name, email, message):
    msg = Message(
        'New Contact Form Submission',
        sender='your-gmail-username@gmail.com',
        recipients=['recipient-email-address'],
        body=f'Name: {name}\nEmail: {email}\nMessage: {message}'
    )

    mail.send(msg)



# Define the feedback form route
@app.route('/feedback', methods=['POST'])
def feedback():
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        email = request.form['email']
        rating = request.form['rating']
        comments = request.form['comments']
        cur = mysql.connection.cursor()
        # Insert the feedback data into the MySQL database
        sql = "INSERT INTO feedback (name, email, rating, comments) VALUES (%s, %s, %s, %s)"
        val = (name, email, rating, comments)
        cur.execute(sql, val)
        mysql.connection.commit()

       
        return render_template('feed.html')


@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        send_email(name, email, message)

        return 'Thank you for contacting us!'

    #return render_template('home.html')


@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM feedback")
    data = cur.fetchall()

    return render_template('home.html',data=data)


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/save', methods=['POST'])
def create_user():
    name = request.form['nam']
    email = request.form['email']
    pwd = request.form['pwd']
    contact = request.form['mob']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, email, pwd, contact) VALUES (%s, %s, %s, %s)", (name, email, pwd, contact))
    mysql.connection.commit()
    cur.close()
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email='"+username+"' and pwd='"+password+"'")
        user = cur.fetchone()

        if user is None:
            return render_template('signup.html', error='Invalid credentials')
        
       
            
        else:
            session['logged_in'] = True
            session["username"]=username
            return render_template('user_panel.html',user=user)



@app.route("/user_home")
def profile():
    if 'logged_in' not in session:
        return redirect('/signup')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email='"+session["username"]+"'")
    user = cur.fetchone()

    # render the age template
    return render_template('user_panel.html',user=user)

@app.route("/hist")
def history():
    if 'logged_in' not in session:
        return redirect('/signup')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM heart_attack_data WHERE user='"+session["username"]+"'")
    user = cur.fetchall()

    # render the age template
    return render_template('history.html',data=user)

@app.route("/pred")
def predect():
    if 'logged_in' not in session:
        return redirect('/signup')
    

    # render the age template
    return render_template('pred.html')

@app.route("/feed")
def feedb():
    if 'logged_in' not in session:
        return redirect('/signup')
    

    # render the age template
    return render_template('feed.html')



@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        cdate=datetime.date.today()
        age = int(request.form['age'])
        sex = request.form.get('sex')
        cp = request.form.get('cp')
        trestbps = int(request.form['trestbps'])
        chol = int(request.form['chol'])
        fbs = request.form.get('fbs')
        restecg = int(request.form['restecg'])
        thalach = int(request.form['thalach'])
        exang = request.form.get('exang')
        oldpeak = float(request.form['oldpeak'])
        slope = request.form.get('slope')
        ca = int(request.form['ca'])
        thal = request.form.get('thal')
        
        data = np.array([[age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal]])
        prediction = model.predict(data)
        if prediction ==0:
            res="Normal"
        else:
            res="Heart Issue"    
        cur = mysql.connection.cursor()    
        sql = "INSERT INTO heart_attack_data (date_created,age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal,user,result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)"
        values = (cdate,age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal,session["username"],res)
        cur.execute(sql, values)
        mysql.connection.commit()
        cur.close()
        # Render prediction results template with prediction string
        return render_template('result.html', prediction=prediction)
        




@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/signin')
def signin():
    return render_template('signup.html')




if __name__=='__main__':
    app.run(debug=True)