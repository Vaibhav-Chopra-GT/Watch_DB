from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vaibhav@1'
app.config['MYSQL_DB'] = 'mydb'
app.secret_key = 'VIPA'
mysql = MySQL(app)

# @app.route('/')
# def index():
#     list1 = ["abc","def"]

#     return render_template("index.html", list = list1)


# @app.route('/user')
# def user():
#     name = "User"
#     # cur = mysql.connection.cursor()
#     # cur.execute("SELECT * FROM Product")
#     # fetchdata = cur.fetchall()
#     # cur.close()
#     return render_template("user.html", user_name = name)

@app.errorhandler(404)
def pnf(err):return render_template("404.html"), 404

# @app.route('/home')
# def startup():
#     return render_template("startup.html")

# @app.route('/products')
# def prod():
#     # name = "User"
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM Product")
#     fetchdata = cur.fetchall()
#     cur.close()
#     return render_template("all_products.html", data = fetchdata)





@app.route('/')
def index2():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product WHERE Availability = 'available'")
    if 'logged_in' in session:
        btn = 'LOGOUT'
    else:
        btn = 'LOGIN'
    fetchdata = cur.fetchall()
    cur.close()
    
    return render_template("index.html", data = fetchdata, btn = btn)

@app.route('/login')
def login():
    return render_template("login2.html")

@app.route('/dashboard')
def dashboard():
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT Product.P_name,SUM(Sells.Quantity)FROM Product,Sells WHERE Product.Product_id = Sells.Product_id Group By Product.Product_id")
    fetchdata = cur.fetchall()
    cur.close()

    return render_template("dashboard.html",data = fetchdata)

@app.route('/cart')
def cart():
    if 'logged_in' in session:
        if 'Trigger' not in session:
            cur_t = mysql.connection.cursor()
            

            p_no = session['phone_number']
            trigger_query = """
            CREATE TRIGGER clear_cart
            AFTER INSERT ON Orders
            FOR EACH ROW
            BEGIN
                DELETE FROM Cart
                WHERE Mobile_num = %s;
            END;
            """

            
            cur_t.execute(trigger_query,(p_no,))
            mysql.connection.commit()
            session['Trigger'] = True
        p_no = session['phone_number']
        cur = mysql.connection.cursor()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT BALANCE FROM Customer WHERE Mobile_num = %s", (p_no,))
        fetchdata2 = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT SUM(PRICE) FROM CART NATURAL JOIN PRODUCT WHERE Mobile_num = %s", (p_no,))
        fetchdata3 = cur3.fetchall()
        # SELECT SUM(PRICE) FROM CART NATURAL JOIN PRODUCT WHERE Mobile_num = %s", (p_no,))
        cur.execute("SELECT P_Name, Price, Product_id FROM Product NATURAL JOIN Cart WHERE Mobile_num = %s",(p_no,))
        fetchdata = cur.fetchall()
        cur.close()

        return render_template("cart.html", data=fetchdata, data2 = fetchdata2, data3 = fetchdata3)
    else:
        return redirect(url_for('login'))

    # return render_template("cart.html")

@app.route('/product/<p_id>')
def product(p_id):
    id = p_id
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM Product WHERE Product_id = %s", (id,))
    fetchdata = cur.fetchall()
    cur.close()
    return render_template("product.html", data = fetchdata)

@app.route('/search', methods=['GET'])
def search_products():
    search_query = request.args.get('search_query')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product WHERE P_Name LIKE %s", ("%" + search_query + "%",))
    fetchdata = cur.fetchall()

    return render_template('search.html', data=fetchdata)

@app.route('/login2', methods=['POST'])
def login2():
    phone_number = request.form['phone_number']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Customer WHERE Mobile_num = %s AND Password_hashed = %s", (phone_number, password))
    user = cur.fetchone()

    if user:
       
        session['phone_number'] = phone_number
        session['logged_in'] = True
        return redirect(url_for('index2'))  
    else:
        
        # return redirect(url_for('login',invalid = True))
        return '''<script>alert("Invalid credentials. Please try again."); window.location.replace("/login");</script>'''
    
@app.route('/logout')
def logout():
    
    session.pop('phone_number', None)
    session.pop('logged_in', None)
    session.pop('Trigger',None)
    session.pop('Trigger2',None)
    return redirect(url_for('index2'))

@app.route('/remove_cart/<p_id>')
def remove_cart(p_id):
    p_no = session['phone_number']
    # print("abc")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM Cart WHERE Mobile_num = %s AND Product_id = %s",(p_no,p_id))
    mysql.connection.commit()
    # fetchdata = cur.fetchall()
    return redirect(url_for('cart'))

@app.route('/add_cart/<p_id>')
def add_cart(p_id):
    if 'logged_in' in session:
        p_no = session['phone_number']
        # print("abc")
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Cart (Mobile_num, Product_id, Quantity) VALUES (%s, %s, %s)",(p_no,p_id,1))
        mysql.connection.commit()
        # fetchdata = cur.fetchall()
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('login'))

@app.route('/buy_now')
def buy_now():
        p_no = session['phone_number']
        # cur = mysql.connection.cursor()
        
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT BALANCE FROM Customer WHERE Mobile_num = %s", (p_no,))
        fetchdata2 = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        cur3.execute("SELECT SUM(PRICE) FROM CART NATURAL JOIN PRODUCT WHERE Mobile_num = %s", (p_no,))
        fetchdata3 = cur3.fetchall()
        bal = fetchdata2[0][0]
        tot = fetchdata3[0][0]
        if(int(fetchdata2[0][0]) > int(fetchdata3[0][0])):
            cur3 = mysql.connection.cursor()
            cur3.execute("SELECT Prod_var FROM Admin")
            fetchdata3 = cur3.fetchall()
            new_oid = fetchdata3
            # print(new_oid)
            cur3.execute("INSERT INTO Orders VALUES(%s,NULL,NULL,NULL,NULL,NULL,NULL,0)",(new_oid[0][0],))

            # if 'Trigger2' not in session:
            #     cur_t = mysql.connection.cursor()
                

            #     p_no = session['phone_number']
            #     trigger_query = """
            #     CREATE TRIGGER create_placement_record
            #     AFTER INSERT ON Orders 
            #     FOR EACH ROW 
            #     BEGIN
            #         INSERT INTO Places
            #             VALUES(%s, %s,NULL);
            #         UPDATE Places SET Placement_date = '2017-02-10' WHERE Order_id =%s AND Mobile_num =%s;
            #     END

                
            #     """

                
            #     cur_t.execute(trigger_query,(new_oid[0][0],p_no,new_oid[0][0],p_no))
            #     mysql.connection.commit()
            #     session['Trigger2'] = True

            mysql.connection.commit()
            # cur3.execute("")
            cur3.execute("UPDATE Orders SET Total_value = (SELECT SUM(PRICE) FROM CART NATURAL JOIN PRODUCT WHERE Mobile_num = %s) WHERE Order_id = %s",(p_no,int(new_oid[0][0])))
            mysql.connection.commit()
            a = int(new_oid[0][0])
            b = str(a+1)
            cur3.execute("UPDATE Admin SET Prod_var = %s WHERE Prod_var = %s",(b,a))
            mysql.connection.commit()
            newb = int(bal) - int(tot)
            cur3.execute("UPDATE Customer SET Balance = %s WHERE Mobile_num = %s",(newb,p_no))
            mysql.connection.commit()


            return '''<script>alert("Order Successfully placed."); window.location.replace("/");</script>'''
        else:
            return '''<script>alert("Insufficient Balance."); window.location.replace("/cart");</script>'''
        

