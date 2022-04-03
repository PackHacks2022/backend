import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_sqlalchemy import SQLAlchemy
import random
import string
import spacy

app = Flask(__name__)

# db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# To reset the db, run: rm /tmp/test.db
db = SQLAlchemy(app)

# cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# socket
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# nlp
nlp = spacy.load("en_core_web_md")

class Instructor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(80), unique=False, nullable=False)
  last_name = db.Column(db.String(80), unique=False, nullable=False)
  email = db.Column(db.String(120), unique=False, nullable=False)

  def __repr__(self):
    return '<Instructor %r>' % f'{self.id} {self.email}'

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Course(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
  department = db.Column(db.String(80), unique=False, nullable=False)
  number = db.Column(db.String(80), unique=False, nullable=False)
  title = db.Column(db.String(80), unique=False, nullable=False)

  def __repr__(self):
    return '<Course %r>' % f'{self.id} {self.department} {self.number} {self.title}'

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Tag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False, nullable=False)
  course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
  
  def __repr__(self):
    return '<Tag %r>' % f'{self.id} {self.name}'

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PastSession(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime, unique=False, nullable=False)
  engagement_percent = db.Column(db.Float, unique=False, nullable=False)
  course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

  def __repr__(self):
    return '<Tag %r>' % f'{self.id} {self.name}'

  def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

db.create_all()

# Testing out the db

# john = Instructor(first_name='john', last_name='doe', email='john@ncsu.edu')
# jane = Instructor(first_name='jane', last_name='doe', email='jane@ncsu.edu')
# sam = Instructor(first_name='sam', last_name='doe', email='sam@ncsu.edu')
# db.session.add(john)
# db.session.add(jane)
# db.session.add(sam)
# db.session.commit()
# print("\nAdded Instructors")

# course1 = Course(instructor_id=john.id,department='Comp Sci',number='1A',title='CSC 100')
# course2 = Course(instructor_id=jane.id,department='Physics',number='2A',title='PY 208')
# db.session.add(course1)
# db.session.add(course2)
# db.session.commit()
# print("Added Courses")

# polymorphism = Tag(name = "polymorphism", course_id = course1.id)
# OOPS = Tag(name = "OOPS", course_id = course1.id)
# dataStructures = Tag(name = "Data Structures", course_id = course1.id)

# electroMag = Tag(name = "Electromagnatism", course_id = course2.id)
# friction = Tag(name = "friction", course_id = course2.id)
# force = Tag(name = "force", course_id = course2.id)

# db.session.add(polymorphism)
# db.session.add(OOPS)
# db.session.add(dataStructures)
# db.session.add(electroMag)
# db.session.add(friction)
# db.session.add(force)
# db.session.commit()
# print("Added Tags")

# print()
# print(Instructor.query.all())
# print(Course.query.all())
# print(Tag.query.all())

# print("\nAll instructors with name starting with 'j':",
#       Instructor.query.filter(Instructor.first_name.startswith('j')).all())
# print("Courses taught by jane:",
#       Course.query.filter_by(instructor_id=jane.id).all())
# print("Tags for physics:",
#       Tag.query.filter_by(course_id=course2.id).all())
# print()

# More test data

bob = Instructor(first_name='Bob', last_name='Evans', email='rjevans@ncsu.edu')
db.session.add(bob)
db.session.commit()

csc116 = Course(instructor_id=bob.id, department='CSC', number=116, title='Introduction to Computing')
csc216 = Course(instructor_id=bob.id, department='CSC', number=216, title='Software Development Fundamentals')
csc226 = Course(instructor_id=bob.id, department='CSC', number=226, title='Discrete Mathematics for Computer Scientists')
csc230 = Course(instructor_id=bob.id, department='CSC', number=230, title='C and Software Tools')
db.session.add(csc116)
db.session.add(csc216)
db.session.add(csc226)
db.session.add(csc230)
db.session.commit()

# conditionals = Tag(name="If and Else", course_id=csc116.id)
classes = Tag(name="Classes", course_id=csc116.id)
polymorphism = Tag(name="OOP", course_id=csc116.id)

# db.session.add(conditionals)
db.session.add(classes)
db.session.add(polymorphism)
db.session.commit()

queues = Tag(name="Queue", course_id=csc216.id)
recursion = Tag(name="Recursion", course_id=csc216.id)
if_and_else = Tag(name="Flow", course_id=csc216.id)

db.session.add(queues)
db.session.add(recursion)
db.session.add(if_and_else)
db.session.commit()

recurrences = Tag(name="Recurrences", course_id=csc226.id)
induction = Tag(name="Induction", course_id=csc226.id)
graph_theory = Tag(name="Graphs", course_id=csc226.id)

db.session.add(recurrences)
db.session.add(induction)
db.session.add(graph_theory)
db.session.commit()

memory = Tag(name="Memory", course_id=csc230.id)
pointers = Tag(name="Pointers", course_id=csc230.id)
system_calls = Tag(name="Sys Calls", course_id=csc230.id)

db.session.add(memory)
db.session.add(pointers)
db.session.add(system_calls)
db.session.commit()

csc116_stats = [
  ("2/14/2022", 0.73),
  ("2/21/2022", 0.72),
  ("2/28/2022", 0.79),
  ("3/7/2022", 0.80),
  ("3/14/2022", 0.85),
  ("3/21/2022", 0.89),
  ("3/28/2022", 0.94),
]

csc216_stats = [
  ("2/14/2022", 0.78),
  ("2/21/2022", 0.69),
  ("2/28/2022", 0.74),
  ("3/7/2022", 0.89),
  ("3/14/2022", 0.86),
  ("3/21/2022", 0.90),
  ("3/28/2022", 0.91),
]

csc226_stats = [
  ("2/14/2022", 0.75),
  ("2/21/2022", 0.76),
  ("2/28/2022", 0.79),
  ("3/7/2022", 0.85),
  ("3/14/2022", 0.86),
  ("3/21/2022", 0.96),
  ("3/28/2022", 0.98),
]

csc230_stats = [
  ("2/14/2022", 0.67),
  ("2/21/2022", 0.64),
  ("2/28/2022", 0.56),
  ("3/7/2022", 0.74),
  ("3/14/2022", 0.76),
  ("3/21/2022", 0.87),
  ("3/28/2022", 0.78),
]

format_date = lambda date: datetime.datetime.strptime(date, '%m/%d/%Y')
for date, percent in csc116_stats:
  session = PastSession(timestamp=format_date(date), engagement_percent=percent, course_id=csc116.id)
  db.session.add(session)
  db.session.commit()
for date, percent in csc216_stats:
  session = PastSession(timestamp=format_date(date), engagement_percent=percent, course_id=csc216.id)
  db.session.add(session)
  db.session.commit()
for date, percent in csc226_stats:
  session = PastSession(timestamp=format_date(date), engagement_percent=percent, course_id=csc226.id)
  db.session.add(session)
  db.session.commit()
for date, percent in csc230_stats:
  session = PastSession(timestamp=format_date(date), engagement_percent=percent, course_id=csc230.id)
  db.session.add(session)
  db.session.commit()

# Usage: POST /instructor (fields in request body)
@app.route("/instructor", methods=["POST"])
@cross_origin()
def create_instructor():
  if request.method == "POST":
    json_data = request.json

    first_name = json_data["first_name"]
    last_name = json_data["last_name"]
    email = json_data["email"]

    instructor = Instructor(first_name=first_name, last_name=last_name, email=email)
    db.session.add(instructor)
    db.session.commit()

    return instructor.as_dict()
  else:
    assert False, "Received non-POST request to /instructor"

# Usage: GET /instructor/<id>
@app.route("/instructor/<int:id>", methods=["GET"])
@cross_origin()
def get_instructor(id):
  if request.method == "GET":
    instructor = Instructor.query.filter_by(id=id).first()
    return instructor.as_dict()
  else:
    assert False, "Received non-GET request to /instructor"

# Usage: POST /course (fields in request body)
@app.route("/course", methods=["POST"])
@cross_origin()
def create_course():
  if request.method == "POST":
    json_data = request.json

    instructor_id = json_data["instructor_id"]
    department = json_data["department"]
    number = json_data["number"]
    title = json_data["title"]
    course = Course(instructor_id=instructor_id, department=department, number=number, title=title)
    db.session.add(course)
    db.session.commit()

    return course.as_dict()
  else:
    assert False, "Received non-POST request to /course"

# Get course info fields
# Usage: GET /course/<id>
# For a specific id, will provide course
@app.route("/course/<int:id>", methods=["GET"])
@cross_origin()
def get_course(id):
  if request.method == "GET":
    course = Course.query.filter_by(id=id).first()
    return course.as_dict()
  else:
    assert False, "Received non-POST request to /course/<int:id>"

# Usage: GET /courses?instructor_id=<instructor_id>
# Could provide multiple courses for a single instructor
@app.route("/courses", methods=["GET"])
@cross_origin()
def get_courses_by_instructor_id():
  if request.method == "GET":
    instructor_id = request.args["instructor_id"]
    courses = Course.query.filter_by(instructor_id=instructor_id).all()
    return jsonify([course.as_dict() for course in courses])
  else:
    assert False, "Received non-POST request to /courses"

# Usage: POST /past_session (fields in request body)
@app.route("/past_session", methods=["POST"])
@cross_origin()
def create_past_session():
  if request.method == "POST":
    json_data = request.json

    timestamp = datetime.datetime.now()
    engagement_percent = json_data["engagement_percent"]
    course_id = json_data["course_id"]

    past_session = PastSession(timestamp=timestamp, engagement_percent=engagement_percent, course_id=course_id)
    db.session.add(past_session)
    db.session.commit()

    return past_session.as_dict()
  else:
    assert False, "Received non-POST request to /past_session"

# Usage: GET /past_sessions?course_id=<course_id>
@app.route("/past_sessions", methods=["GET"])
@cross_origin()
def get_past_sessions_by_course_id():
  if request.method == "GET":
    course_id = request.args["course_id"]
    past_sessions = PastSession.query.filter_by(course_id=course_id).all()
    return jsonify([past_session.as_dict() for past_session in past_sessions])
  else:
    assert False, "Received non-GET request to /past_sessions"

# Usage: POST /tag (fields in requestbody)
@app.route("/tag", methods=["POST"])
@cross_origin()
def create_tag():
  if request.method == "POST":
    json_data = request.json

    name = json_data["name"]
    course_id = json_data["course_id"]

    tag = Tag(name = name, course_id = course_id)
    db.session.add(tag)
    db.session.commit()

    return tag.as_dict()
  else:
    assert False, "Received non-POST request to /tag"

# Usage: GET /tags?course_id=<course_id>
@app.route("/tags", methods=["GET"])
@cross_origin()
def get_tags_by_course_instructor():
  if request.method == "GET":
    course_id = request.args["course_id"]
    tags = Tag.query.filter_by(course_id=course_id).all()
    return jsonify([tag.as_dict() for tag in tags])
  else:
    assert False, "Received non-GET request to /tags"

# Login function, which sends the instructor id (to identify which instructor is logged in)
# and a special phrase as a password.
@app.route("/login", methods=["GET"])
@cross_origin()
def login():
  if request.method == "GET":
    email = request.args["email"]
    instructor = Instructor.query.filter_by(email=email).first()

    if not instructor:
      return jsonify(None)
    else:
      return jsonify({"instructor_id": instructor.id, "phrase": "GOPACK"})

created_sessions = []  # keeps track of all active session codes
connected_clients = {} # keeps track of all clients for the specified session (connected_clients[session_code])
questions = {}         # keeps track of all question for the specified session (question[session_code])

# Starts a session (called by an instructor), generating a random session id
@app.route("/create_session", methods=["GET"])
@cross_origin()
def create_session():
  phrase = request.args["phrase"]
  session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
  created_sessions.append(session_code)
  connected_clients[session_code] = [] # there are no clients when the session is established
  questions[session_code] = []         # there are no questions when the session is established
  print("Created sessions:", created_sessions)
  return jsonify(session_code)

sent_tags = None

# Consumes tags sent from the instructor's dashboard to the
# student's view of the session
@socketio.on('accept_tags')
def provide_tags(data):
  global sent_tags
  sent_tags = data
  emit('provide_tags', data, broadcast=True)

# Consumes the "create_question" event sent from a client
# and adds it to the list of questions for that session code (questions[session_code]).
# Emits the updated list of questions back to the clients to update the
# frontend in real time.
@socketio.on('create_question')
def create_question(data):
  title = data['title']
  question_body = data['question_body']
  session_code = data['session_code']
  
  assert sent_tags

  # determine the tag with the greatest similarity score
  best_tag = None
  best_score = None
  for tag in sent_tags:
    doc1 = nlp(title + ". " + question_body)
    doc2 = nlp(tag["name"])

    score = doc1.similarity(doc2)
    
    if not best_score or not best_tag or score > best_score:
      best_score = score
      best_tag = tag["name"]

  # update the questions list with the new question and its assigned tag
  questions[session_code] = [{
    "title": title,
    "question_body": question_body,
    "tag": best_tag
  }] + questions[session_code]

  # emit updated questions event to all connected clients
  emit('updated_questions', questions[session_code], broadcast=True)

# Connects a client to the specified room, given by a session code.
@socketio.on('join')
def on_join(data):
  name = data['name']
  room = data['room']
  print(name, "joined room", room)
  join_room(room)
  connected_clients[room] = connected_clients[room] + [name]
  print("Clients connected to", room, connected_clients[room])
  send(connected_clients[room], broadcast=True, to=room)

"""

function: matchQuestionToTags
input: question (schema unknown), course id (course whose tags you want to use)
output: question (with schema updated with the tag)

{
  title: ...,
  question_body: ...
}

becomes...

{
  title: ...,
  question_body: ...,
  tag: tag_id
}

function: useNlpPrediction
input: question_body, tag
output: similarity score
(using spacy: https://spacy.io/usage/linguistic-features#vectors-similarity)

compare question with all tags, assign the tag with highest similarity

Question: Q1
Tags: T1, T2

Q1, T1 --> 0.75
Q1, T2 --> 0.43

"""

"""

Instructor -> creates a session (aka room, identified by a code)
https://flask-socketio.readthedocs.io/en/latest/getting_started.html#rooms

Students join a session (using the code)
Student -- join room event (name, room) --> S
Session code will be passed in the join event

C -- create question event --> S
S: predicts using NLP, adds a tag ({title, question_body, tag_id (null)} -> {title, question_body, tag_id})
S: update list of questions with the new question added
S -- broadcast all updated questions --> C1
S -- broadcast all updated questions --> C2
S -- broadcast all updated questions - C3

"""

if __name__ == '__main__':
  socketio.run(app)