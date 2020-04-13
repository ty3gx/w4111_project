
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
import sys
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.243.220.243/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.243.220.243/proj1part2"
#
DATABASEURI = "postgresql://ty2419:0590@35.231.103.173/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


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

#  # DEBUG: this is debugging code to see what request looks like
#  print(request.args)
#
#
#  #
#  # example of a database query
#  #
#  cursor = g.conn.execute("SELECT * FROM contact_person")
#  names = []
#  for result in cursor:
#    names.append(result['person_name'])  # can also be accessed using result[0]
#  cursor.close()
#
#  #
#  # Flask uses Jinja templates, which is an extension to HTML where you can
#  # pass data to a template and dynamically generate HTML based on the data
#  # (you can think of it as simple PHP)
#  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
#  #
#  # You can see an example template in templates/index.html
#  #
#  # context are the variables that are passed to the template.
#  # for example, "data" key in the context variable defined below will be 
#  # accessible as a variable in index.html:
#  #
#  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
#  #     <div>{{data}}</div>
#  #     
#  #     # creates a <div> tag for each element in data
#  #     # will print: 
#  #     #
#  #     #   <div>grace hopper</div>
#  #     #   <div>alan turing</div>
#  #     #   <div>ada lovelace</div>
#  #     #
#  #     {% for n in data %}
#  #     <div>{{n}}</div>
#  #     {% endfor %}
#  #
#  context = dict(data = names)
#
#
#  #
#  # render_template looks in the templates/ folder for files.
#  # for example, the below file reads template/index.html
#  #
#  return render_template("index.html", **context)
  return render_template('index.html')

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/add_project')
def add_project():
  return render_template('add_project.html')

@app.route('/add_agency')
def add_agency():
  return render_template('add_agency.html')

@app.route('/add_agency_action', methods=['POST'])
def add_agency_action():
  a_type_full = None
  a_type = request.form['type']
  name = request.form['name']
  s_type = request.form['s_type']
  o_type = request.form['other_type']
  #print(a_type, name, s_type, o_type, file=sys.stderr)
  if a_type == 'r':
    a_type_full = 'recipient'
  elif a_type == 'f':
    a_type_full = 'funding'
  elif a_type == 'i':
    a_type_full = 'implementing'

  if s_type == 'Other' and o_type != "":
    s_type = o_type

  q_string = "SELECT max(%s_agency_id) FROM %s_agency" % (a_type, a_type_full)
  cursor = g.conn.execute(text(q_string))
  a_id = cursor.fetchone()[0]
  cursor.close()

  a_id = int(a_id) + 1
  q_string = "INSERT INTO %s_agency VALUES (%i, '%s', '%s')" % (a_type_full, a_id, name, s_type)
  g.conn.execute(text(q_string))

  # check for success
  q_string = "SELECT * FROM %s_agency WHERE %s_agency_id=%i" % (a_type_full, a_type, a_id)
  cursor = g.conn.execute(text(q_string))
  try: 
    if not cursor.fetchone()[1] == name:
      return render_template('/add_agency_error.html', data = str(a_id))
  except:
    return render_template('/add_agency_error.html', data = str(a_id))

  return render_template('/add_agency_success.html', data = str(a_id))




@app.route('/add_person')
def add_person():
  return render_template('add_person.html')

@app.route('/add_person_action', methods=['POST'])
def add_person_action():
  name = request.form['name']

  q_string = "SELECT max(person_id) FROM contact_person"
  cursor = g.conn.execute(text(q_string))
  a_id = cursor.fetchone()[0]
  cursor.close()

  a_id = int(a_id) + 1
  q_string = "INSERT INTO contact_person VALUES (%i, '%s')" % (a_id, name)
  #print(q_string, file=sys.stderr)
  g.conn.execute(text(q_string))

  # check for success
  q_string = "SELECT * FROM contact_person WHERE person_id=%i" % (a_id)
  cursor = g.conn.execute(text(q_string))
  try: 
    if not cursor.fetchone()[1] == name:
      return render_template('/add_person_error.html', data = str(a_id))
  except:
    return render_template('/add_person_error.html', data = str(a_id))

  return render_template('/add_person_success.html', data = str(a_id))







@app.route('/add_r_area')
def add_r_area():
  return render_template('add_r_area.html')

@app.route('/add_r_area_action', methods=['POST'])
def add_r_area_action():
  name = request.form['name']
  region = request.form['region']
  other = request.form['other']

  if region == 'Other' and other != "":
    region = other

  q_string = "SELECT max(area_id) FROM recipient_area"
  cursor = g.conn.execute(text(q_string))
  a_id = cursor.fetchone()[0]
  cursor.close()

  a_id = int(a_id) + 1
  q_string = "INSERT INTO recipient_area VALUES (%i, '%s', '%s')" % (a_id, name, region)
  g.conn.execute(text(q_string))

  # check for success
  q_string = "SELECT * FROM recipient_area WHERE area_id=%i" % (a_id)
  cursor = g.conn.execute(text(q_string))
  try: 
    if not cursor.fetchone()[1] == name:
      return render_template('/add_r_area_error.html', data = str(a_id))
  except:
    return render_template('/add_r_area_error.html', data = str(a_id))

  return render_template('/add_r_area_success.html', data = str(a_id))



# Define main search
@app.route('/mainsearch')
def mainsearch():
  return render_template('mainsearch.html')

@app.route('/mainsearch_action', methods = ['POST'])
def mainsearch_action():
  project_id = request.form['project_id']
  project_name = request.form['project_name']
  fi_agency = request.form['fi_agency']
  r_agency = request.form['r_agency']
  contact = request.form['contact']
  region = request.form['region']
  year = request.form['year']
  aidtype = request.form['aidtype']
  intenttype = request.form['intenttype']
  
  mainsearch_result = []
  
    
  q_string = """SELECT 
  p.project_id, p.title, p.description, p.year,
  i2.i_agency_id, i2.i_agency_name, i2.i_agency_type, p.num_of_i_agency,
  f2.f_agency_id, f2.f_agency_name, f2.f_agency_type, p.num_of_f_agency,
  ra2.area_id, ra2.area_name, ra2.region,
  rg2.r_agency_id, rg2.r_agency_name, rg2.r_agency_type, p.num_of_r_agency,
  c2.person_id, c2.person_name
  FROM project as p 
  left join
  implement as i1 
  on p.project_id = i1.project_id
  left join
  implementing_agency as i2 
  on i1.i_agency_id = i2.i_agency_id 
  left join 
  fund as f1 
  on p.project_id = f1.project_id
  left join 
  funding_agency as f2
  on f1.f_agency_id = f2.f_agency_id
  left join
  receive_area as ra1
  on p.project_id = ra1.project_id
  left join
  recipient_area as ra2
  on ra1.area_id = ra2.area_id
  left join
  receive_agency as rg1
  on p.project_id = rg1.project_id
  left join
  recipient_agency as rg2
  on rg1.r_agency_id = rg2.r_agency_id
  left join
  contact as c1
  on p.project_id = c1.project_id
  left join
  contact_person as c2
  on c1.person_id = c2.person_id 
  WHERE 
  title != '' """
  
  if project_id != "":
    q_string = q_string + " and p.project_id = " + project_id
    
  if project_name != "":
    q_string = q_string + " and UPPER(title) LIKE UPPER('%%%s%%')" %(project_name)
    
  if fi_agency != "":
    q_string = q_string + " and (UPPER(i_agency_name) LIKE UPPER('%%%s%%') or UPPER(f_agency_name) LIKE UPPER('%%%s%%'))" %(fi_agency, fi_agency)
    
  if year != "":
    q_string = q_string + " and p.year = " + year
    
  if r_agency != "":
    q_string = q_string + " and UPPER(r_agency_name) LIKE UPPER('%%%s%%')" %(r_agency)
    
  if region != "Any":
    q_string = q_string + " and UPPER(region) LIKE UPPER('%%%s%%')" %(region)
    
  if contact != "":
    q_string = q_string + " and UPPER(person_name) LIKE UPPER('%%%s%%')" %(contact)
    
  if aidtype != "Any":
    q_string = q_string + " and UPPER(flow_type) LIKE UPPER('%%%s%%')" %(aidtype)
    
  if intenttype != "Any":
    q_string = q_string + " and UPPER(intent_type) LIKE UPPER('%%%s%%')" %(intenttype)
    
  # print(q_string, file=sys.stderr)
  
  cursor = g.conn.execute(text(q_string))
  mainsearch_result = list(cursor.fetchall())
  cursor.close()
    
  return render_template('mainsearch_result.html', project_id=project_id, \
    project_name = project_name, \
    mainsearch_result=mainsearch_result, \
    year=year, fi_agency=fi_agency, r_agency=r_agency, region=region, contact=contact, \
    aidtype = aidtype, intenttype = intenttype)


@app.route('/search_id')
def search_id():
  return render_template('search_id.html')

@app.route('/search_id_action', methods=['POST'])
def search_id_action():
  agency = request.form['agency']
  person = request.form['person']
  area = request.form['area']
  region = request.form['region']
  
  i_agency_result = []
  f_agency_result = []
  r_agency_result = []
  person_result = []
  area_result = []

  if agency != "":
    q_string = "SELECT * FROM implementing_agency WHERE UPPER(i_agency_name) LIKE UPPER('%%%s%%')" %(agency)
    cursor = g.conn.execute(text(q_string))
    i_agency_result = list(cursor.fetchall())
    cursor.close()

    q_string = "SELECT * FROM funding_agency WHERE UPPER(f_agency_name) LIKE UPPER('%%%s%%')" %(agency)
    cursor = g.conn.execute(text(q_string))
    f_agency_result = list(cursor.fetchall())
    cursor.close()

    q_string = "SELECT * FROM recipient_agency WHERE UPPER(r_agency_name) LIKE UPPER('%%%s%%')" %(agency)
    cursor = g.conn.execute(text(q_string))
    r_agency_result = list(cursor.fetchall())
    cursor.close()


  if person != "":
    q_string = "SELECT * FROM contact_person WHERE UPPER(person_name) LIKE UPPER('%%%s%%')" %(person)
    cursor = g.conn.execute(text(q_string))
    person_result = list(cursor.fetchall())
    cursor.close()

  if area != "" and region == "":
    q_string = "SELECT * FROM recipient_area WHERE UPPER(area_name) LIKE UPPER('%%%s%%')" %(area)
    cursor = g.conn.execute(text(q_string))
    area_result = list(cursor.fetchall())
    cursor.close()

  if area == "" and region != "":
    q_string = "SELECT * FROM recipient_area WHERE UPPER(region) LIKE UPPER('%%%s%%')" %(region)
    cursor = g.conn.execute(text(q_string))
    area_result = list(cursor.fetchall())
    cursor.close()

  if area != "" and region != "":
    q_string = "SELECT * FROM recipient_area WHERE UPPER(region) LIKE UPPER('%%%s%%') AND UPPER(area_name) LIKE UPPER('%%%s%%')"\
     %(region, area)
    cursor = g.conn.execute(text(q_string))
    area_result = list(cursor.fetchall())
    cursor.close()
    
  return render_template('search_id_result.html', agency=agency, i_agency_result=i_agency_result, \
    f_agency_result=f_agency_result, r_agency_result=r_agency_result, person_result=person_result, \
    area_result=area_result, person=person, area=area, region=region)









# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  i_id, f_id, r_id = request.form['i_id'], request.form['f_id'], request.form['r_id']
  des = request.form['des']
  a_id, cp_id = request.form['a_id'], request.form['cp_id']
  year = int(request.form['year'])
  i_type, f_type, amount, currency = request.form['i_type'], request.form['f_type'], request.form['amount'], request.form['currency']

  try:
    amount = int(amount)
  except:
    amount = -1

  i_id_list = []
  f_id_list = []
  r_id_list = []
  a_id_list = []
  cp_id_list = []

  if i_id != "":
    i_id_list = [int(x) for x in i_id.split(',')]
  if f_id != "":
    f_id_list = [int(x) for x in f_id.split(',')]
  if r_id != "":
    r_id_list = [int(x) for x in r_id.split(',')]
  if a_id != "":
    a_id_list = [int(x) for x in a_id.split(',')]
  if cp_id != "": 
    cp_id_list = [int(x) for x in cp_id.split(',')]


  # check for ids in database
  for i_id in i_id_list:
    try:
      q_string = "SELECT * FROM implementing_agency WHERE i_agency_id = %i" % (i_id)
      cursor = g.conn.execute(text(q_string))
      temp = list(cursor.fetchall())
      cursor.close()
      if temp == []:
        return render_template('/add_project_error.html')
    except:
      return render_template('/add_project_error.html')

  for f_id in f_id_list:
    try:
      q_string = "SELECT * FROM funding_agency WHERE f_agency_id = %i" % (f_id)
      cursor = g.conn.execute(text(q_string))
      temp = list(cursor.fetchall())
      cursor.close()
      if temp == []:
        return render_template('/add_project_error.html')
    except:
      return render_template('/add_project_error.html')

  for r_id in r_id_list:
    try:
      q_string = "SELECT * FROM recipient_agency WHERE r_agency_id = %i" % (r_id)
      cursor = g.conn.execute(text(q_string))
      temp = list(cursor.fetchall())
      cursor.close()
      if temp == []:
        return render_template('/add_project_error.html')
    except:
      return render_template('/add_project_error.html')

  for a_id in a_id_list:
    try:
      q_string = "SELECT * FROM recipient_area WHERE area_id = %i" % (a_id)
      cursor = g.conn.execute(text(q_string))
      temp = list(cursor.fetchall())
      cursor.close()
      if temp == []:
        return render_template('/add_project_error.html')
    except:
      return render_template('/add_project_error.html')

  for cp_id in cp_id_list:
    try:
      q_string = "SELECT * FROM contact_person WHERE person_id = %i" % (cp_id)
      cursor = g.conn.execute(text(q_string))
      temp = list(cursor.fetchall())
      cursor.close()
      if temp == []:
        return render_template('/add_project_error.html')
    except:
      return render_template('/add_project_error.html')





  q_string = "SELECT max(project_id) FROM project"
  cursor = g.conn.execute(text(q_string))
  p_id = cursor.fetchone()[0]
  cursor.close()

  p_id = int(p_id) + 1
  q_string = "INSERT INTO project VALUES (%i, '%s', '%s', %i, %i, %i, %i)" \
  % (p_id, name, des, year, len(i_id_list), len(f_id_list), len(r_id_list))
  g.conn.execute(text(q_string))

  # check for success
  q_string = "SELECT * FROM project WHERE project_id=%i" % (p_id)
  cursor = g.conn.execute(text(q_string))
  try: 
    if not cursor.fetchone()[1] == name:
      return render_template('/add_project_error.html', data = str(p_id))
  except:
    return render_template('/add_project_error.html', data = str(p_id))

  for iid in i_id_list:
    q_string = "INSERT INTO implement VALUES (%i, %i)" % (p_id, iid)
    g.conn.execute(text(q_string))
    q_string = "SELECT * FROM implement WHERE project_id=%i AND i_agency_id=%i" % (p_id, iid)
    cursor = g.conn.execute(text(q_string))
    try: 
      if not int(cursor.fetchone()[1]) == iid:
        return render_template('/add_project_error.html', data = str(p_id))
    except:
      return render_template('/add_project_error.html', data = str(p_id))

  for fid in f_id_list:
    q_string = "INSERT INTO fund VALUES (%i, %i)" % (p_id, fid)
    g.conn.execute(text(q_string))
    q_string = "SELECT * FROM fund WHERE project_id=%i AND f_agency_id=%i" % (p_id, fid)
    cursor = g.conn.execute(text(q_string))
    try: 
      if not int(cursor.fetchone()[1]) == fid:
        return render_template('/add_project_error.html', data = str(p_id))
    except:
      return render_template('/add_project_error.html', data = str(p_id))

  for aid in a_id_list:
    q_string = "INSERT INTO receive_area VALUES (%i, %i)" % (p_id, aid)
    g.conn.execute(text(q_string))
    q_string = "SELECT * FROM receive_area WHERE project_id=%i AND area_id=%i" % (p_id, aid)
    cursor = g.conn.execute(text(q_string))
    try: 
      if not int(cursor.fetchone()[1]) == aid:
        return render_template('/add_project_error.html', data = str(p_id))
    except:
      return render_template('/add_project_error.html', data = str(p_id))

  for cpid in cp_id_list:
    q_string = "INSERT INTO contact VALUES (%i, %i)" % (p_id, cpid)
    g.conn.execute(text(q_string))
    q_string = "SELECT * FROM contact WHERE project_id=%i AND person_id=%i" % (p_id, cpid)
    cursor = g.conn.execute(text(q_string))
    try: 
      if not int(cursor.fetchone()[1]) == cpid:
        return render_template('/add_project_error.html', data = str(p_id))
    except:
      return render_template('/add_project_error.html', data = str(p_id))


  for rid in r_id_list:
    if amount == -1:
      q_string = "INSERT INTO receive_agency VALUES (%i, %i, '%s', '%s', null, '%s')"\
      % (p_id, rid, i_type, f_type, currency)
    else:
      q_string = "INSERT INTO receive_agency VALUES (%i, %i, '%s', '%s', %i, '%s')"\
      % (p_id, rid, i_type, f_type, amount, currency)
    g.conn.execute(text(q_string))
    q_string = "SELECT * FROM receive_agency WHERE project_id=%i AND r_agency_id=%i" % (p_id, rid)
    cursor = g.conn.execute(text(q_string))
    try: 
      if not int(cursor.fetchone()[1]) == rid:
        return render_template('/add_project_error.html', data = str(p_id))
    except:
      return render_template('/add_project_error.html', data = str(p_id))





  return render_template('/add_project_success.html', data = str(p_id))



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
