from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from flask import jsonify
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





# @app.route('/')
# def index2():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM Product WHERE Availability = 'available'")
#     if 'logged_in' in session:
#         btn = 'LOGOUT'
#     else:
#         btn = 'LOGIN'
#     fetchdata = cur.fetchall()
#     cur.close()
    
#     return render_template("index.html", data = fetchdata, btn = btn)
@app.route('/')
def index2():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Product WHERE Availability = 'available'")
    fetchdata = cur.fetchall()
    cur.close()

    products = [
        {
            "id": row[0],
            "name": row[1],
            "price": row[8],
            "description": f"{row[4]} / {row[5]}",
            "image": f"static/images/{row[1]}.jpeg"
        }
        for row in fetchdata
    ]

    btn = 'LOGOUT' if 'logged_in' in session else 'LOGIN'

    return jsonify({"products": products, "btn": btn})

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
        # if 'Trigger' not in session:
        #     cur_t = mysql.connection.cursor()
            

        #     p_no = session['phone_number']
        #     trigger_query = """
        #     CREATE TRIGGER clear_cart
        #     AFTER INSERT ON Orders
        #     FOR EACH ROW
        #     BEGIN
        #         DELETE FROM Cart
        #         WHERE Mobile_num = %s;
        #     END;
        #     """

            
        #     cur_t.execute(trigger_query,(p_no,))
        #     mysql.connection.commit()
        #     session['Trigger'] = True
        p_no = session['phone_number']
        cur = mysql.connection.cursor()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT BALANCE FROM Customer WHERE Mobile_num = %s", (p_no,))
        fetchdata2 = cur2.fetchall()
        cur3 = mysql.connection.cursor()
        # cur3.execute("SELECT SUM(PRICE) FROM CART NATURAL JOIN PRODUCT WHERE Mobile_num = %s", (p_no,))
        cur3.execute("""
                        SELECT SUM(cart.Quantity * product.price) AS total_value
                        FROM cart
                        INNER JOIN product ON cart.Product_id = product.Product_id
                        WHERE cart.Mobile_num = %s
                    """, (p_no,))

        fetchdata3 = cur3.fetchall()
        # SELECT SUM(PRICE) FROM CART NATURAL JOIN PRODUCT WHERE Mobile_num = %s", (p_no,))
        cur.execute("SELECT P_Name, Price, Product_id, Quantity FROM Product NATURAL JOIN Cart WHERE Mobile_num = %s",(p_no,))
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
        cur.execute("SELECT Quantity FROM cart WHERE Mobile_num = %s AND Product_id = %s", (p_no, p_id))
        existing_quantity = cur.fetchone()

        if existing_quantity:
            # If the product already exists in the cart, increment the quantity by one
            new_quantity = existing_quantity[0] + 1
            cur.execute("UPDATE cart SET Quantity = %s WHERE Mobile_num = %s AND Product_id = %s", (new_quantity, p_no, p_id))
            mysql.connection.commit()
        else:
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
        cur3.execute("""
                        SELECT SUM(cart.Quantity * product.price) AS total_value
                        FROM cart
                        INNER JOIN product ON cart.Product_id = product.Product_id
                        WHERE cart.Mobile_num = %s
                    """, (p_no,))
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
            cur3.execute("DELETE FROM Cart WHERE Mobile_num = %s",(p_no,))
            mysql.connection.commit()
        #         WHERE Mobile_num = %s;)


            return '''<script>alert("Order Successfully placed."); window.location.replace("/");</script>'''
        else:
            return '''<script>alert("Insufficient Balance."); window.location.replace("/cart");</script>'''
        

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/signup2', methods=['POST'])
def signup2():
    first_name = request.form['first_name']
    # print(first_name)
    # print("aaaaaaaaaaaaaaaa")
    middle_name = request.form['middle_name']
    last_name = request.form['last_name']
    age = request.form['age']
    mobile_num = request.form['mobile_num']
    email = request.form['email']
    house_num = request.form['house_num']
    locality = request.form['locality']
    city = request.form['city']
    state = request.form['state']
    pincode = request.form['pincode']
    landmark = request.form['landmark']
    card_num = request.form['card_num']
    cvv = request.form['cvv']
    expiry = request.form['expiry']
    name_on_card = request.form['name_on_card']
    bank_name = request.form['bank_name']
    account_num = request.form['account_num']
    ifsc = request.form['ifsc']
    password = request.form['password']
    if(first_name == '' or age == '' or name_on_card == '' or mobile_num == ''):
        return '''<script>alert("Enter valid info."); window.location.replace("/signup");</script>'''

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM Customer WHERE Mobile_num = %s", (mobile_num,))
    count = cur.fetchone()[0]
    if count > 0:
        return '''<script>alert("Phone number is already registered with another account."); window.location.replace("/signup");</script>'''
    else:
        cur.execute("INSERT INTO customer (first_name, middle_name, last_name, age, mobile_num, Email_id, house_num, locality, city, state, pincode, landmark, card_num, cvv, expiry, name_on_card, bank_name, account_num, ifsc_code, password_hashed, balance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (first_name.encode('utf-8'), middle_name.encode('utf-8'), last_name.encode('utf-8'), age, mobile_num.encode('utf-8'), email.encode('utf-8'), house_num.encode('utf-8'), locality.encode('utf-8'), city.encode('utf-8'), state.encode('utf-8'), pincode, landmark.encode('utf-8'), card_num.encode('utf-8'), cvv.encode('utf-8'), expiry.encode('utf-8'), name_on_card.encode('utf-8'), bank_name.encode('utf-8'), account_num.encode('utf-8'), ifsc.encode('utf-8'), password.encode('utf-8'), 0))
        # user = cur.fetchone()
        mysql.connection.commit()
        session['phone_number'] = mobile_num
        session['logged_in'] = True
        return redirect(url_for('index2')) 

    # if user:
       
    #     session['phone_number'] = phone_number
    #     session['logged_in'] = True
    #     return redirect(url_for('index2'))  
    # else:
        
    #     # return redirect(url_for('login',invalid = True))
    #     return '''<script>alert("Invalid credentials. Please try again."); window.location.replace("/login");</script>'''
@app.route('/dec_qty/<p_id>')
def dec_qty(p_id):
    p_no = session['phone_number']
        # cur = mysql.connection.cursor()
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT Quantity FROM cart WHERE Mobile_num = %s AND Product_id = %s", (p_no, p_id))
    existing_quantity = cur.fetchone()

    if existing_quantity:
        current_quantity = existing_quantity[0]
        if current_quantity > 1:
            # If the product exists and its quantity is more than 1, decrement the quantity by 1
            new_quantity = current_quantity - 1
            cur.execute("UPDATE cart SET Quantity = %s WHERE Mobile_num = %s AND Product_id = %s", (new_quantity, p_no, p_id))
            mysql.connection.commit()
        else:
            # If the quantity is 1, remove the product from the cart
            cur.execute("DELETE FROM cart WHERE Mobile_num = %s AND Product_id = %s", (p_no, p_id))
            mysql.connection.commit()
    return redirect(url_for('cart'))
@app.route('/inc_qty/<p_id>')
def inc_qty(p_id):
    p_no = session['phone_number']
    cur = mysql.connection.cursor()
    cur.execute("SELECT Quantity FROM cart WHERE Mobile_num = %s AND Product_id = %s", (p_no, p_id))
    existing_quantity = cur.fetchone()

    if existing_quantity:
        current_quantity = existing_quantity[0]
        if current_quantity >= 1:
            # If the product exists and its quantity is more than 1, decrement the quantity by 1
            new_quantity = current_quantity + 1
            cur.execute("UPDATE cart SET Quantity = %s WHERE Mobile_num = %s AND Product_id = %s", (new_quantity, p_no, p_id))
            mysql.connection.commit()
        else:
            # If the quantity is 1, remove the product from the cart
            cur.execute("DELETE FROM cart WHERE Mobile_num = %s AND Product_id = %s", (p_no, p_id))
            mysql.connection.commit()
    return redirect(url_for('cart'))