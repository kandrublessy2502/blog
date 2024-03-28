from flask import Flask,render_template,url_for,request,redirect,flash,session 
import mysql.connector
from cmail import sendmail
from otp import genotp
app=Flask(__name__)
#secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
mydb=mysql.connector.connect(host='localhost',user='root',password='system',db='blogss')     
with mysql.connector.connect(host='localhost',user='root',password='system',db='blogss'):  
    cursor=mydb.cursor(buffered=True) 
    cursor.execute("create table if not exists registration(username varchar(30) primary key,mobile varchar(30)unique,email varchar(50) unique,address varchar(50),password varchar(20))")
mycursor=mydb.cursor()
@app.route('/registration',methods=['GET','POST'])
def kbs():
    if request.method=="POST":
        username=request.form.get('username')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        address=request.form.get('address')
        password=request.form.get('password')
        otp=genotp()
        sendmail(to=email,subject="Thanks for registration",body=f'otp is :{otp}')
        return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)
    return render_template('registration.html')
@app.route('/otp/<username>/<mobile>/<email>/<address>/<password>/<otp>',methods=['GET','POST'])
def otp(username,mobile,email,address,password,otp):
    if request.method=="POST":
        uotp=request.form['uotp']
        if otp==uotp:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('insert into registration values(%s,%s,%s,%s,%s)',[username,mobile,email,address,password])
            mydb.commit()
            cursor.close()
            return redirect(url_for('login'))
    return render_template('verification.html',username=username,mobile=mobile,email=email,address=address,password=password,otp=otp)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select count(*) from registration where username=%s && password=%s',[username,password])
        data=cursor.fetchone()[0]
        print(data)
        if data==1:
            session['username']=username
            if not session.get(session['username']):
                session[session['username']]={}
            return redirect(url_for('homepage'))
        else:
            return'Invalid Username and Password'
    return render_template('login.html')
@app.route('/logout',methods=['GET','POST'])
def logout():
    if session.get('username'):
        session.pop('username')
    return redirect(url_for('login'))
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/addpost',methods=['GET','POST'])
def add_post():
    if request.method=="POST":
        title=request.form.get('title')
        content=request.form.get('content')
        slug=request.form.get('slug')
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('insert into posts(title, content, slug) values (%s,%s,%s)',[title,content,slug])
        mydb.commit()
        cursor.close()
    return render_template('add_post.html')


#create admin page

@app.route('/admin')
def admin():
    return render_template('admin.html')

#view posts
@app.route('/view_posts')
def view_posts():
    cursor = mydb.cursor(buffered=True)
    cursor.execute("SELECT * FROM posts")
    posts=cursor.fetchall()
    print(posts)
    cursor.close()
    return render_template('view_posts.html',posts=posts)
#delete post route
@app.route('/delete_post/<int:id>',methods=['POST'])
def delete_post(id):
    cursor=mydb.cursor(buffered=True)
    cursor.execute('select * from posts where id=%s',(id,))
    post=cursor.fetchone() 
    cursor.execute('DELETE FROM posts WHERE id=%s',(id,))
    mydb.commit()
    cursor.close()
    return redirect(url_for('view_posts'))

#update posts route

@app.route('/update_post/<int:id>',methods=['GET','POST'])
def update_post(id):
    if request.method=="POST":
        title=request.form.get('title')
        content=request.form.get('content')
        slug=request.form.get('slug')
        print(title)
        print(content)
        print(slug)
        cursor=mydb.cursor(buffered=True)
        cursor.execute('UPDATE posts SET title=%s,content=%s,slug=%s WHERE id=%s',(title,content,slug,id)) 
        mydb.commit()
        cursor.close()
        return redirect(url_for('view_posts')) 
    else:
        cursor=mydb.cursor(buffered=True)
        cursor.execute('select * from posts where id=%s',(id,))
        post=cursor.fetchone()
        cursor.close()
        return render_template('update.html',post=post)

app.run(debug=True,use_reloader=True)