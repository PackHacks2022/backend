import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# To reset the db, run: rm /tmp/test.db
db = SQLAlchemy(app)

# cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
    courses = Course.query.filter_by(instructor_id=instructor_id)
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
    past_sessions = PastSession.query.filter_by(course_id=course_id)
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
    tags = Tag.query.filter_by(course_id=course_id)
    return jsonify([tag.as_dict() for tag in tags])
  else:
    assert False, "Received non-GET request to /tags"

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