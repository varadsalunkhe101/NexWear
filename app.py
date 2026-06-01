import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# SECRET KEY
# =========================
app.secret_key = 'supersecretkey'

# =========================
# FILE UPLOAD CONFIGURATION
# =========================
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# =========================
# MYSQL CONFIGURATION
# =========================
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cloth_system'

mysql = MySQL(app)

# =========================
# HELPER FUNCTIONS
# =========================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
# HOME PAGE
# =========================
@app.route('/')
def index():
    return render_template('index.html')


# =========================
# ADMIN BASE
# =========================
@app.route('/adminbase')
def adminbase():

    if 'admin' not in session:
        return redirect('/adminlogin')

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM tbl_category")
    total_categories = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tbl_product")
    total_products = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tbl_userregister")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM tbl_adminregister")
    total_admins = cur.fetchone()[0]

    cur.close()

    return render_template(
        'dashboard.html',
        total_categories=total_categories,
        total_products=total_products,
        total_users=total_users,
        total_admins=total_admins
    )


# =========================
# USER BASE
# =========================
@app.route('/userbase')
def userbase():

    if 'user' not in session:
        return redirect('/userlogin')

    return render_template('userbase.html')

# ==========================================
# USER HOME
# ==========================================
@app.route('/userhome')
def userhome():

    if 'user' not in session:
        return redirect('/userlogin')

    return render_template('userhome.html')

# ==========================================
# MY ACCOUNT
# ==========================================
@app.route('/myaccount')
def myaccount():

    if 'user' not in session:
        return redirect('/userlogin')

    email = session['user']

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM tbl_userregister WHERE email=%s",
        (email,)
    )

    user = cur.fetchone()

    cur.close()

    return render_template('myaccount.html', user=user)


# =====================================================
# ADMIN LOGIN
# =====================================================
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM tbl_adminregister WHERE email=%s",
            (email,)
        )

        data = cur.fetchone()
        cur.close()

        if data:

            db_password = data[5]

            if check_password_hash(db_password, password):

                session['admin'] = email

                return redirect('/add_category')

        return "<script>alert('Invalid Email or Password');</script>" + render_template('adminlogin.html')

    return render_template('adminlogin.html')


# =====================================================
# ADMIN REGISTER
# =====================================================
@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():

    if request.method == 'POST':

        fullname = request.form['fullname']
        address = request.form['address']
        contactnumber = request.form['contactnumber']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO tbl_adminregister(fullname,address,contact,email,password) VALUES(%s,%s,%s,%s,%s)",
            (fullname, address, contactnumber, email, hashed_password)
        )

        mysql.connection.commit()
        cur.close()

        return redirect('/adminlogin')

    return render_template('adminregister.html')


# =====================================================
# ADMIN LIST
# =====================================================
@app.route('/admin_list')
def admin_list():

    if 'admin' not in session:
        return redirect('/adminlogin')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_adminregister")
    data = cur.fetchall()
    cur.close()

    return render_template('admin_list.html', value=data)


# =====================================================
# UPDATE ADMIN
# =====================================================
@app.route('/update_admin', methods=['POST'])
def update_admin():

    admin_id = request.form['cid']
    fullname = request.form['fullname']
    address = request.form['address']
    contactnumber = request.form['contactnumber']
    email = request.form['email']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE tbl_adminregister SET fullname=%s,address=%s,contact=%s,email=%s,password=%s WHERE id=%s",
        (fullname, address, contactnumber, email, hashed_password, admin_id)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/admin_list')


# =====================================================
# DELETE ADMIN
# =====================================================
@app.route('/delete_admin', methods=['POST'])
def delete_admin():

    admin_id = request.form['cid']

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM tbl_adminregister WHERE id=%s",
        (admin_id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/admin_list')


# =====================================================
# USER REGISTER
# =====================================================
@app.route('/userregister', methods=['GET', 'POST'])
def userregister():

    if request.method == 'POST':

        fullname = request.form['fullname']
        address = request.form['address']
        contactnumber = request.form['contactnumber']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO tbl_userregister(fullname,address,contact,email,password) VALUES(%s,%s,%s,%s,%s)",
            (fullname, address, contactnumber, email, hashed_password)
        )

        mysql.connection.commit()
        cur.close()

        return redirect('/userlogin')

    return render_template('userregister.html')


# =====================================================
# USER LOGIN
# =====================================================
@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM tbl_userregister WHERE email=%s",
            (email,)
        )

        data = cur.fetchone()

        cur.close()

        if data:

            db_password = data[5]

            if check_password_hash(db_password, password):
                session['user'] = email
                session['user_id'] = data[0]  # user table id

                return redirect('/view_category')

        return "<script>alert('Invalid Email or Password');</script>" + render_template('userlogin.html')

    return render_template('userlogin.html')


# =====================================================
# CART
# =====================================================
@app.route('/cart')
def cart():

    if 'user_id' not in session:
        return redirect(url_for('userlogin'))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            c.id,
            c.quantity,
            p.product_name,
            p.price
        FROM tbl_cart c
        JOIN tbl_product p
        ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (session['user_id'],))

    rows = cur.fetchall()

    cart_items = []

    for row in rows:

        cart_items.append({
            "cart_id": row[0],
            "quantity": row[1],
            "product_name": row[2],
            "product_price": row[3],
            "total_price": row[1] * row[3]
        })

    cur.close()

    return render_template(
        'cart.html',
        cart_items=cart_items
    )

# =====================================================
# ADD TO CART
# =====================================================
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):

    if 'user_id' not in session:
        return redirect(url_for('userlogin'))

    user_id = session['user_id']

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM tbl_cart WHERE user_id=%s AND product_id=%s",
        (user_id, product_id)
    )

    item = cur.fetchone()

    if item:

        cur.execute(
            """
            UPDATE tbl_cart
            SET quantity = quantity + 1
            WHERE user_id=%s AND product_id=%s
            """,
            (user_id, product_id)
        )

    else:

        cur.execute(
            """
            INSERT INTO tbl_cart(user_id, product_id, quantity)
            VALUES(%s,%s,%s)
            """,
            (user_id, product_id, 1)
        )

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('cart'))

# =====================================================
# PLACE ORDER
# =====================================================
@app.route('/place_order')
def place_order():

    if 'user_id' not in session:
        return redirect(url_for('userlogin'))

    user_id = session['user_id']

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT SUM(p.price * c.quantity)
        FROM tbl_cart c
        JOIN tbl_product p
        ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (user_id,))

    result = cur.fetchone()

    total_amount = result[0] if result[0] else 0

    cur.execute(
        """
        INSERT INTO tbl_orders(user_id, total_amount)
        VALUES(%s,%s)
        """,
        (user_id, total_amount)
    )

    cur.execute(
        "DELETE FROM tbl_cart WHERE user_id=%s",
        (user_id,)
    )

    mysql.connection.commit()
    cur.close()

    return "<script>alert('Order Placed Successfully');window.location='/view_product';</script>"

# =====================================================
# USER LIST
# =====================================================
@app.route('/user_list')
def user_list():

    if 'admin' not in session:
        return redirect('/adminlogin')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_userregister")
    data = cur.fetchall()
    cur.close()

    return render_template('user_list.html', value=data)


# =====================================================
# UPDATE USER
# =====================================================
@app.route('/update_user', methods=['POST'])
def update_user():

    user_id = request.form['cid']
    fullname = request.form['fullname']
    address = request.form['address']
    contactnumber = request.form['contactnumber']
    email = request.form['email']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    cur = mysql.connection.cursor()

    cur.execute(
        "UPDATE tbl_userregister SET fullname=%s,address=%s,contact=%s,email=%s,password=%s WHERE id=%s",
        (fullname, address, contactnumber, email, hashed_password, user_id)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/user_list')


# =====================================================
# DELETE USER
# =====================================================
@app.route('/delete_user', methods=['POST'])
def delete_user():

    user_id = request.form['cid']

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM tbl_userregister WHERE id=%s",
        (user_id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/user_list')


# =====================================================
# ADD CATEGORY
# =====================================================
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():

    if 'admin' not in session:
        return redirect('/adminlogin')

    if request.method == 'POST':

        category_name = request.form['category_name']
        category_description = request.form['category_description']

        category_image = request.files['category_image']

        if category_image and allowed_file(category_image.filename):

            filename = secure_filename(category_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            category_image.save(filepath)

            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO tbl_category(category_name,category_image,category_description) VALUES(%s,%s,%s)",
                (category_name, filepath, category_description)
            )

            mysql.connection.commit()
            cur.close()

            return redirect('/category_list')

    return render_template('add_category.html')


# =====================================================
# CATEGORY LIST
# =====================================================
@app.route('/category_list')
def category_list():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_category")
    data = cur.fetchall()
    cur.close()

    return render_template('category_list.html', value=data)


# =====================================================
# DELETE CATEGORY
# =====================================================
@app.route('/delete_category', methods=['POST'])
def delete_category():

    category_id = request.form['cid']

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM tbl_category WHERE id=%s",
        (category_id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/category_list')


# =====================================================
# UPDATE CATEGORY
# =====================================================
@app.route('/update_category', methods=['POST'])
def update_category():

    category_id = request.form['cid']
    category_name = request.form['category_name']
    category_description = request.form['category_description']

    category_image = request.files.get('category_image')

    cur = mysql.connection.cursor()

    if category_image and category_image.filename != '':

        filename = secure_filename(category_image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        category_image.save(filepath)

        cur.execute(
            "UPDATE tbl_category SET category_name=%s,category_image=%s,category_description=%s WHERE id=%s",
            (category_name, filepath, category_description, category_id)
        )

    else:

        cur.execute(
            "UPDATE tbl_category SET category_name=%s,category_description=%s WHERE id=%s",
            (category_name, category_description, category_id)
        )

    mysql.connection.commit()
    cur.close()

    return redirect('/category_list')


# =====================================================
# ADD PRODUCT
# =====================================================
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    if 'admin' not in session:
        return redirect('/adminlogin')

    if request.method == 'POST':

        product_name = request.form['product_name']
        price = request.form['price']
        size = request.form['size']
        brand = request.form['brand']
        category = request.form['category']
        color = request.form['color']
        discount = request.form['discount']

        product_image = request.files['product_image']

        if product_image and allowed_file(product_image.filename):

            filename = secure_filename(product_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            product_image.save(filepath)

            cur = mysql.connection.cursor()

            cur.execute(
                "INSERT INTO tbl_product(product_name,price,size,product_image,brand,category,color,discount) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                (product_name, price, size, filepath, brand, category, color, discount)
            )

            mysql.connection.commit()
            cur.close()

            return redirect('/product_list')

    return render_template('add_product.html')


# =====================================================
# PRODUCT LIST
# =====================================================
@app.route('/product_list')
def product_list():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_product")
    data = cur.fetchall()
    cur.close()

    return render_template('product_list.html', value=data)


# =====================================================
# DELETE PRODUCT
# =====================================================
@app.route('/delete_product', methods=['POST'])
def delete_product():

    product_id = request.form['cid']

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM tbl_product WHERE id=%s",
        (product_id,)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/product_list')


# =====================================================
# UPDATE PRODUCT
# =====================================================
@app.route('/update_product', methods=['POST'])
def update_product():

    product_id = request.form['cid']

    product_name = request.form['product_name']
    price = request.form['price']
    size = request.form['size']
    brand = request.form['brand']
    category = request.form['category']
    color = request.form['color']
    discount = request.form['discount']

    product_image = request.files.get('product_image')

    cur = mysql.connection.cursor()

    if product_image and product_image.filename != '':

        filename = secure_filename(product_image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        product_image.save(filepath)

        cur.execute(
            "UPDATE tbl_product SET product_name=%s,price=%s,size=%s,product_image=%s,brand=%s,category=%s,color=%s,discount=%s WHERE id=%s",
            (product_name, price, size, filepath, brand, category, color, discount, product_id)
        )

    else:

        cur.execute(
            "UPDATE tbl_product SET product_name=%s,price=%s,size=%s,brand=%s,category=%s,color=%s,discount=%s WHERE id=%s",
            (product_name, price, size, brand, category, color, discount, product_id)
        )

    mysql.connection.commit()
    cur.close()

    return redirect('/product_list')


# =====================================================
# VIEW CATEGORY
# =====================================================
@app.route('/view_category')
def view_category():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_category")
    data = cur.fetchall()
    cur.close()

    return render_template('view_category.html', value=data)

# =====================================================
# VIEW PRODUCT
# =====================================================
@app.route('/view_product')
def view_product():

    category = request.args.get('category')

    cur = mysql.connection.cursor()

    if category:

        cur.execute(
            "SELECT * FROM tbl_product WHERE category=%s",
            (category,)
        )

    else:

        cur.execute(
            "SELECT * FROM tbl_product"
        )

    data = cur.fetchall()

    cur.close()

    return render_template(
        'view_product.html',
        value=data
    )

# =====================================================
# MY ORDERS
# =====================================================
@app.route('/my_orders')
def my_orders():

    if 'user_id' not in session:
        return redirect(url_for('userlogin'))

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM tbl_orders WHERE user_id=%s ORDER BY id DESC",
        (session['user_id'],)
    )

    orders = cur.fetchall()

    cur.close()

    return render_template(
        'my_orders.html',
        orders=orders
    )

# =====================================================
# LOGOUT
# =====================================================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


# =====================================================
# MAIN
# =====================================================
if __name__ == '__main__':
    app.run(debug=True)