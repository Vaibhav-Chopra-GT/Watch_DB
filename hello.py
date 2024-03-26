from flask import Flask, render_template
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vaibhav@1'
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

@app.route('/')
def index():
    list1 = ["abc","def"]

    return render_template("index.html", list = list1)


@app.route('/user')
def user():
    name = "User"
    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM Product")
    # fetchdata = cur.fetchall()
    # cur.close()
    return render_template("user.html", user_name = name)

@app.errorhandler(404)
def pnf(err):return render_template("404.html"), 404

@app.route('/home')
def startup():
    return render_template("startup.html")

@app.route('/products')
def prod():
    # name = "User"
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template("all_products.html", data = fetchdata)