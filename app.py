from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Instructor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(80), unique=False, nullable=False)
  last_name = db.Column(db.String(80), unique=False, nullable=False)
  email = db.Column(db.String(120), unique=False, nullable=False)

  def __repr__(self):
      return '<Instructor %r>' % f'{self.id} {self.email}'

class Course(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
  department = db.Column(db.String(80), unique=False, nullable=False)
  number = db.Column(db.String(80), unique=False, nullable=False)
  title = db.Column(db.String(80), unique=False, nullable=False)

  def __repr__(self):
    return '<Course %r>' % f'{self.id} {self.department} {self.number} {self.title}'

class Tag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False, nullable=False)
  course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
  
  def __repr__(self):
    return '<Tag %r>' % f'{self.id} {self.name}'

# Testing out the db

# To reset the db, run
# rm /tmp/test.db

# Initialize the DB
db.create_all()

# Create Instructors
john = Instructor(first_name='john', last_name='doe', email='john@ncsu.edu')
jane = Instructor(first_name='jane', last_name='doe', email='jane@ncsu.edu')
sam = Instructor(first_name='sam', last_name='doe', email='sam@ncsu.edu')
db.session.add(john)
db.session.add(jane)
db.session.add(sam)
db.session.commit()
print("\nAdded Instructors")

# Create Courses
course1 = Course(instructor_id=john.id,department='Comp Sci',number='1A',title='CSC 100')
course2 = Course(instructor_id=jane.id,department='Physics',number='2A',title='PY 208')
db.session.add(course1)
db.session.add(course2)
db.session.commit()
print("Added Courses")

# Create Tags
polymorphism = Tag(name = "polymorphism", course_id = course1.id)
OOPS = Tag(name = "OOPS", course_id = course1.id)
dataStructures = Tag(name = "Data Structures", course_id = course1.id)

electroMag = Tag(name = "Electromagnatism", course_id = course2.id)
friction = Tag(name = "friction", course_id = course2.id)
force = Tag(name = "force", course_id = course2.id)

db.session.add(polymorphism)
db.session.add(OOPS)
db.session.add(dataStructures)
db.session.add(electroMag)
db.session.add(friction)
db.session.add(force)
db.session.commit()
print("Added Tags")

print()
print(Instructor.query.all())
print(Course.query.all())
print(Tag.query.all())

print("\nAll instructors with name starting with 'j':",
      Instructor.query.filter(Instructor.first_name.startswith('j')).all())
print("Courses taught by jane:",
      Course.query.filter_by(instructor_id=jane.id).all())
print("Tags for physics:",
      Tag.query.filter_by(course_id=course2.id).all())
print()

#@app.route("/")
#def hello_world():
    #return "<p>Hello, World!</p>"