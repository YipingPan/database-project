
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response \
  , url_for, session
import random
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'HTML')
app = Flask(__name__, template_folder=tmpl_dir)

# server, database, webpage

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.231.103.173/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.231.103.173/proj1part2"
#
DATABASEURI = "postgresql://yp2524:0118@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names, myprint = 'this is my print')

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  
  #return render_template("index.html", **context)
  return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/post')
def post():
  try:
    cursor = g.conn.execute("SELECT post_id, post_comment, post_time, price, state FROM post")
    posts = []
    posts = cursor.fetchall()
    cursor.close()
    
    context = dict(posts=posts)
    return render_template("post.html", **context)

  except Exception as e:
    print(e) # see error in the prompt
    return render_template("post.html", msg='server error !')  

@app.route('/view', methods=['POST'])
def view():
    cursor = g.conn.execute("SELECT post_id, post_comment, post_time, price, state FROM post")
    posts = []
    posts = cursor.fetchall()
    cursor.close()
  
    post_id_details = request.form['post_id']
    query2 = """
      SELECT item_id
      FROM containsitem
      WHERE post_id = %s
    """
    cursor2 = g.conn.execute(query2, post_id_details)
    get_item_id = cursor2.fetchone()
    cursor2.close()

    query3 = """
      SELECT item_id, name, picture_url, brand, description, category
      FROM item
      WHERE item_id = %s
    """
    cursor3 = g.conn.execute(query3, get_item_id)
    item_info = []
    item_info = cursor3.fetchone()
    cursor3.close()

    query4 = """
      SELECT price
      FROM post
      WHERE post_id = %s
    """
    cursor4 = g.conn.execute(query4, post_id_details)
    price = cursor4.fetchone()
    #print(item_info)
    #print(post_info)
    
    
    context = dict(posts=posts,item_info=item_info, price=price)
    
    return render_template("post.html", **context)
 
@app.route('/pay')
def pay():
  try:
    return render_template("payment.html")
  except Exception as e:
    print(e)
    return render_template("payment.html", msg='server error !')

@app.route('/sell', methods=['GET','POST'])
def sell():
  try:
# =============================================================================
#     if 'loggedin' not in session:
#       return render_template('login.html',msg='Please log in !')
# =============================================================================
    
    if request.method=='POST':
      
      name = request.form['name'] 
      picture_url = "default"
      original_price = request.form['original_price']
      brand = request.form['brand']
      description = request.form['description']
      year_bought = request.form['year_bought']
      category = request.form['category']
      
      currentDT = datetime.datetime.now()
      post_time = currentDT.strftime("%Y-%m-%d %H:%M:%S")
      price = request.form['price']

        # generate post_id item_id
      ids_exists = True
      while ids_exists:
        new_post_id = str(random.randrange(10**11,10**12-1))
        new_item_id = str(random.randrange(10**11,10**12-1))
        query = """
          SELECT *
          FROM containsitem
          WHERE post_id = %s 
          AND item_id = %s
        """
        cursor = g.conn.execute(query, (new_post_id,new_item_id))
        if not cursor.fetchone():
          ids_exists = False
      cursor.close()
      post_id = new_post_id
      item_id = new_item_id
      
      query = """
        INSERT INTO post
        VALUES (%s,NULL,NULL,%s,%s,%s)
      """
      g.conn.execute(query, (post_id,post_time,price,'for sale'))
      
      query = """
        INSERT INTO item
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
      """
      
      g.conn.execute(query, (item_id,name,picture_url, original_price,\
                             brand,description, year_bought,category)) 
        
      query = """
        INSERT INTO containsitem
        VALUES (%s,%s)
      """
      g.conn.execute(query,(post_id,item_id))
      
      sellsarray = session['sellsarray']
      sellsarray.append({'itemname':name, 'id':post_id})
      session['sellsarray'] = sellsarray
      
      
      context = {'postid':post_id, 'itemid':item_id,\
                 'msg':"Successfully posted."}
      return render_template("sell.html",**context)
    return render_template("sell.html")
  except Exception as e:
    print(e)
    return render_template("sell.html", msg='server error !') 

# These should be placed in post.html or postinfo.html somewhere:
#   <form method="POST" action="/add">
#   <input type="text" name="item_id">
#   <input type="submit" value="Add"></p>
@app.route('/add', methods=['POST'])
def add_to_cart():
  try:
    if 'loggedin' not in session:
      return render_template('login.html',msg='Please log in !')
    item_id = request.form['item_id']
    query = """
      SELECT item_id, name, picture_url, brand, description, category
      FROM item
      WHERE item_id = %s
    """
    cursor = g.conn.execute(query,item_id)
    newitem_info1 = cursor.fetchone() #from item
    
    query = """
      SELECT post_id, post_comment, post_time, price, state
      FROM post
      WHERE post_id in (SELECT post_id FROM containsitem WHERE item_id = %s) 
    """
    cursor = g.conn.execute(query,item_id)
    newitem_info2 = cursor.fetchone() #from post
    print(newitem_info2['state'])
    if newitem_info2['state'] != "for sale" :
      cursor = g.conn.execute("SELECT post_id, post_comment, post_time, price, state FROM post")
      posts = []
      posts = cursor.fetchall()
      cursor.close()
      context = dict(posts=posts)
      return render_template('post.html', **context, msg="Please select items 'for sale'")    

    #####  following steps are extremely important/strict to revise 'session';
    ##### to use session['itemsarray'], must write like this instead of 'context = dict(items=session['itemsarray'])'
    ##### tuples = [tuple(x.values()) for x in session['itemsarray']]
    ##### context = dict(items=tuples)
    newitem = {**dict(newitem_info1),**dict(newitem_info2)}
    itemsarray = session['itemsarray']
    itemsarray.append(newitem)
    cursor.close()
    session['itemsarray'] = itemsarray
    #####
    
    print(newitem)
    print(itemsarray)
    print(session['itemsarray'])
    print(session)
    return redirect('/post')
  except Exception as e:
    print(e)
    return redirect('/post')

# These are placed in cart.html:
#   <form method="POST" action="/clear">
#   <input type="submit" value="Clear cart"></p>
@app.route('/clear', methods=['POST'])
def clear_cart():
  try:
    # if 'clear cart' button is submitted
    if request.method == 'POST':
      session['itemsarray'] = []
      return render_template('cart.html')   
  except Exception as e:
    print(e)
    return redirect('/cart')   

@app.route('/cart')
def cart():
  try:
    if 'loggedin' not in session:
      return render_template('login.html',msg='Please log in !')
    print(session['itemsarray'])
    if session['itemsarray'] == []:
      return render_template("cart.html", msg='Your cart is empty')
    else:
      tuples = [tuple(x.values()) for x in session['itemsarray']]
      context = dict(items=tuples)
      print(session['itemsarray'])
      return render_template("cart.html", **context)
  except Exception as e:
    print(e)
    return render_template("cart.html", msg='server error !') 

@app.route('/profile', methods=['GET','POST'])
def profile():
  try:
    # Check if user is loggedin
    if 'loggedin' in session:
      query0 = """
        SELECT *
        FROM users
        WHERE user_id = %s
      """
      cursor = g.conn.execute(query0, (session['id']))
      account = cursor.fetchone()
      cursor.close()
      
      if request.method == 'POST':
        msg1 = ""
        msg2 = ""
        if 'attribute' in request.form and 'data' in request.form\
          and request.form['attribute'] != "" and request.form['data'] != "":
            attribute = request.form['attribute']
            data = request.form['data']
            if attribute == 'phone':
              if len(data) != 10 : msg1 = "Phone number should be 10 digits!"
            elif attribute == 'address1':
              if len(data) > 50 : msg1 = "Address should be shorter than 50!"
            elif attribute == 'address2':
              if len(data) > 50 : msg1 = "Address should be shorter than 50!"
            elif attribute == 'city':
              if len(data) > 50 : msg1 = "City should be shorter than 50!"
            elif attribute == 'state':
              if len(data) > 20 : msg1 = "State should be shorter than 20!"
            elif attribute == 'zipcode':
              if len(data) != 5 : msg1 = "Zipcode should be 5 digits!"
            if msg1 == "":
              query = "UPDATE users SET " + attribute + " = %s WHERE user_id = %s"
              print('Executing query: \n', query)
              g.conn.execute(query,(data,session['id']))
              msg1 = 'Attribute successfully updated !'
              
        if 'oldpassword' in request.form and 'newpassword' in request.form \
          and request.form['oldpassword']!='' and request.form['newpassword']!='':
          oldpassword = request.form['oldpassword']
          newpassword = request.form['newpassword']
          query = """
            SELECT password
            FROM login
            WHERE username = %s
          """
          cursor = g.conn.execute(query, session['username'])
          password = cursor.fetchone()['password']
          cursor.close()
          if password != oldpassword or len(newpassword)>50:
            msg2 = 'Wrong oldpassword OR newpassword too long'
          else:
            query = """
              UPDATE login
              SET password=%s
              WHERE username=%s
            """
            g.conn.execute(query, (newpassword, session['username']))
            msg2 = 'Password successfully updated'
        # refetch the new account infomation
        cursor = g.conn.execute(query0, (session['id']))
        account = cursor.fetchone()
        cursor.close()
        return render_template('profile.html', account=account,msg1=msg1,msg2=msg2)
          
        
      # Show the profile page with account info
      return render_template('profile.html', account=account)
      # User is not loggedin redirect to login page
    return redirect('/login')
  except Exception as e:
    print(e)
    return render_template("profile.html", msg='server error !')

@app.route('/login',methods=['GET','POST'])
def login():
  try:
    if 'loggedin' in session:
      context = dict(msg = "You have already logged in.")
    else:
      context = dict(msg = "You haven't logged in.")
    if request.method == 'POST':
      entered_username = request.form['username']
      entered_password = request.form['password']
      query = """
        SELECT l.username as username, u.user_id as user_id
        FROM login as l, haslogin as h, users as u
        WHERE l.username = %s
        and l.password = %s
        and l.username = h.username
        and h.user_id = u.user_id
      """
      cursor = g.conn.execute(query,\
                              (entered_username,entered_password))
      account = cursor.fetchone()
      cursor.close()
      if account:
        session['loggedin'] = True
        session['id'] = account['user_id']
        session['username'] = account['username']
        session['itemsarray'] = []
        session.modified = True
        print(session)
        #return 'Logged in successfully!'
        context['msg'] = 'Logged in successfully!'
      else:
        context['msg'] = 'Incorrect username/password!'
    return render_template("login.html",**context)
  except Exception as e:
    print(e)
    return render_template("login.html", msg='server error !')

@app.route('/logout')
def logout():
  try:
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect('/login')
  except Exception as e:
    print(e)
    return render_template("login.html", msg='server error !')

@app.route('/register', methods = ['GET','POST'])
def register():
  try:
    msg = ''
    if request.method == 'POST' :
            # check username exists or not:
            username = request.form['username']
  
            query = """
              SELECT *
              FROM login
              WHERE username = %s
            """
            cursor = g.conn.execute(query, (username))
            account = cursor.fetchone()
            cursor.close()
            
            if account:
              msg = 'Username already exists !'
            else:
              # prepared for inserting the new account
                # for login table
              password   = request.form['password']
              email      = request.form['email']
              security_question = request.form['security_question']
              answer     = request.form['answer']
                # for users table
              first_name = request.form['first_name']
              last_name  = request.form['last_name']
              DOB        = request.form['DOB']
              phone      = request.form['phone']
              address1   = request.form['address1']
              address2   = request.form['address2']
              city       = request.form['city']
              state      = request.form['state']
              zipcode    = request.form['zipcode']
              active     = 'y'
                # generate user_id
              id_exists = True
              while id_exists:
                new_user_id = str(random.randrange(10**11,10**12-1))
                query = """
                  SELECT *
                  FROM haslogin
                  WHERE user_id = %s
                """
                cursor = g.conn.execute(query, new_user_id)
                if not cursor.fetchone():
                  id_exists = False
              cursor.close()
              user_id = new_user_id
              
              query = """
                INSERT INTO login 
                VALUES (%s,%s,%s,%s,%s)
              """
              g.conn.execute(query, \
                             (username,email,password,security_question,answer))
              query = """
                INSERT INTO users 
                VALUES (%s,%s,%s,%s,%s,  %s,%s,%s,%s,%s,%s)
              """
              g.conn.execute(query, \
                             (user_id, first_name, last_name, DOB, phone, \
                              address1, address2, city, state, zipcode, active))
                
              # warning: haslogin must be operated as the last table.
              query = """
                INSERT INTO haslogin
                VALUES (%s,%s,NULL)
              """
              g.conn.execute(query, \
                             (username,user_id))
  
    return render_template("register.html",msg=msg)
  except Exception as e:
    print(e)
    return render_template("register.html", msg='server error !')



# Example of adding new data to the database
# use ctrl4/5 to comment/uncomment
# =============================================================================
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
#   return render_template("another.html") #redirect('/')
# =============================================================================

# use ctrl4/5 to comment/uncomment
# =============================================================================
# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()
# 
# =============================================================================

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.secret_key = 'this is a sercret key'
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()




