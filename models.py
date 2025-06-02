from datetime import datetime
from sqlalchemy import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Date,
    Float,
)
from sqlalchemy.orm import relationship
from database import Base
from passlib.context import CryptContext
from werkzeug.security import generate_password_hash, check_password_hash

pwd_context = CryptContext(schemes=["scrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    school_name = Column(String(200), nullable=True)
    school_logo = Column(Text, nullable=True)
    password_hash = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)

    classes = relationship(
        "Class", backref="teacher", lazy=True, cascade="all, delete-orphan"
    )
    wagoll_examples = relationship(
        "WagollExample", backref="teacher", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self, db_session) -> dict:
        """Converts user to dictionary with metrics using injected DB session"""

        class_count = len(self.classes)

        student_count = (
            db_session.query(Student)
            .join(Class)
            .filter(Class.teacher_id == self.id)
            .count()
        )

        upload_count = (
            db_session.query(Writing)
            .join(Student)
            .join(Class)
            .filter(Class.teacher_id == self.id)
            .count()
        )

        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "school_name": self.school_name,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "class_count": class_count,
            "student_count": student_count,
            "upload_count": upload_count,
        }


class Class(Base):

    __tablename__ = "class"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    year_group = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    teacher_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    students = relationship(
        "Student", backref="class_group", lazy=True, cascade="all, delete-orphan"
    )
    assignments = relationship(
        "Assignment", backref="class_group", lazy=True, cascade="all, delete-orphan"
    )


class Student(Base):

    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    student_id = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    class_id = Column(
        Integer, ForeignKey("class.id", ondelete="CASCADE"), nullable=False
    )
    writing_samples = relationship(
        "Writing", backref="student", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def name(self):
        """Maintain backwards compatibility with existing code"""
        return f"{self.first_name} {self.last_name}"


class Writing(Base):

    __tablename__ = "writing"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    text_content = Column(Text, nullable=False)
    writing_age = Column(String(50))
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    student_id = Column(
        Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False
    )
    assignment_id = Column(
        Integer, ForeignKey("assignment.id", ondelete="SET NULL"), nullable=True
    )
    total_marks_percentage = Column(Float, nullable=True)
    criteria_marks = relationship(
        "CriteriaMark", backref="writing", lazy=True, cascade="all, delete-orphan"
    )
    analysis_feedback = relationship(
        "AnalysisFeedback", backref="writing", lazy=True, cascade="all, delete-orphan"
    )


class Assignment(Base):

    __tablename__ = "assignment"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    curriculum = Column(String(50), nullable=True)
    genre = Column(String(50), nullable=True)
    year_group = Column(String(50), nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    class_id = Column(
        Integer, ForeignKey("class.id", ondelete="CASCADE"), nullable=False
    )
    criteria = relationship(
        "Criteria", backref="assignment", lazy=True, cascade="all, delete-orphan"
    )
    submissions = relationship("Writing", backref="assignment", lazy=True)


class Criteria(Base):

    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False)
    assignment_id = Column(
        Integer, ForeignKey("assignment.id", ondelete="CASCADE"), nullable=False
    )
    # Add relationship to marks with cascade delete
    marks = relationship(
        "CriteriaMark", backref="criteria", lazy=True, cascade="all, delete-orphan"
    )


class CriteriaMark(Base):

    __tablename__ = "criteria_mark"

    id = Column(Integer, primary_key=True)
    score = Column(
        Integer, nullable=False
    )  # 0=not met, 1=partially met, 2=confidently used
    writing_id = Column(
        Integer, ForeignKey("writing.id", ondelete="CASCADE"), nullable=False
    )
    criteria_id = Column(
        Integer, ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.now)


class AnalysisFeedback(Base):

    __tablename__ = "analysis_feedback"

    id = Column(Integer, primary_key=True)
    writing_id = Column(
        Integer, ForeignKey("writing.id", ondelete="CASCADE"), nullable=False
    )
    is_helpful = Column(Boolean, nullable=False)
    writing_age_accurate = Column(Boolean, nullable=True)
    strengths_accurate = Column(Boolean, nullable=True)
    development_accurate = Column(Boolean, nullable=True)
    criteria_accurate = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class WagollExample(Base):

    __tablename__ = "wagoll_example"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    explanations = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False)
    assignment_id = Column(
        Integer, ForeignKey("assignment.id", ondelete="SET NULL"), nullable=True
    )
    teacher_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Add relationship to assignment
    assignment = relationship("Assignment", backref="wagollexamples", lazy=True)


# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50), nullable=False)
#     last_name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     school_name = db.Column(db.String(200), nullable=True)
#     school_logo = db.Column(db.Text, nullable=True)
#     password_hash = db.Column(db.String(256), nullable=False)
#     is_admin = db.Column(db.Boolean, default=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     last_login = db.Column(db.DateTime, nullable=True)

#     # Add relationship to classes for teachers with cascade delete
#     classes = db.relationship('Class', backref='teacher', lazy=True,
#                             cascade='all, delete-orphan')
#     # Add relationship to WAGOLL examples with cascade delete
#     wagoll_examples = db.relationship('WagollExample', backref='teacher', lazy=True,
#                                     cascade='all, delete-orphan')

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     @property
#     def name(self):
#         """Maintain backwards compatibility with existing code"""
#         return f"{self.first_name} {self.last_name}"

#     @property
#     def class_count(self):
#         """Get the total number of classes for this user"""
#         return len(self.classes)

#     @property
#     def student_count(self):
#         """Get the total number of students across all classes"""
#         return db.session.query(Student).join(Class).filter(Class.teacher_id == self.id).count()

#     @property
#     def upload_count(self):
#         """Get the total number of writing samples across all students"""
#         return db.session.query(Writing).join(Student).join(Class).filter(Class.teacher_id == self.id).count()

#     def to_dict(self):
#         """Convert user object to dictionary with metrics"""
#         return {
#             'id': self.id,
#             'first_name': self.first_name,
#             'last_name': self.last_name,
#             'email': self.email,
#             'school_name': self.school_name,
#             'is_admin': self.is_admin,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'last_login': self.last_login.isoformat() if self.last_login else None,
#             'class_count': self.class_count,
#             'student_count': self.student_count,
#             'upload_count': self.upload_count
#         }

# class Class(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     year_group = db.Column(db.String(20), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
#     # Add relationship to students with cascade delete
#     students = db.relationship('Student', backref='class_group', lazy=True,
#                              cascade='all, delete-orphan')
#     # Add relationship to assignments with cascade delete
#     assignments = db.relationship('Assignment', backref='class_group', lazy=True,
#                                 cascade='all, delete-orphan')


# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.String(50), nullable=True)  # Optional student ID
#     first_name = db.Column(db.String(50), nullable=False)
#     last_name = db.Column(db.String(50), nullable=False)
#     date_of_birth = db.Column(db.Date, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'), nullable=False)
#     # Add relationship to writing samples with cascade delete
#     writing_samples = db.relationship('Writing', backref='student', lazy=True,
#                                     cascade='all, delete-orphan')

#     @property
#     def name(self):
#         """Maintain backwards compatibility with existing code"""
#         return f"{self.first_name} {self.last_name}"

# class Writing(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String(255), nullable=False)
#     text_content = db.Column(db.Text, nullable=False)
#     writing_age = db.Column(db.String(50))
#     feedback = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
#     # Add relationship to assignment submission
#     assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id', ondelete='SET NULL'), nullable=True)
#     # Store calculated total marks percentage
#     total_marks_percentage = db.Column(db.Float, nullable=True)
#     # Add relationship to criteria marks with cascade delete
#     criteria_marks = db.relationship('CriteriaMark', backref='writing', lazy=True,
#                                    cascade='all, delete-orphan')
#     # Add relationship to analysis feedback with cascade delete
#     analysis_feedback = db.relationship('AnalysisFeedback', backref='writing', lazy=True,
#                                       cascade='all, delete-orphan')


# class Assignment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     curriculum = db.Column(db.String(50), nullable=True)
#     genre = db.Column(db.String(50), nullable=True)
#     year_group = db.Column(db.String(50), nullable=True)
#     due_date = db.Column(db.DateTime, nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     class_id = db.Column(db.Integer, db.ForeignKey('class.id', ondelete='CASCADE'), nullable=False)
#     # Add relationship to success criteria with cascade delete
#     criteria = db.relationship('Criteria', backref='assignment', lazy=True,
#                              cascade='all, delete-orphan')
#     # Add relationship to submissions
#     submissions = db.relationship('Writing', backref='assignment', lazy=True)


# class Criteria(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     description = db.Column(db.String(500), nullable=False)
#     assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id', ondelete='CASCADE'), nullable=False)
#     # Add relationship to marks with cascade delete
#     marks = db.relationship('CriteriaMark', backref='criteria', lazy=True,
#                           cascade='all, delete-orphan')


# class CriteriaMark(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     score = db.Column(db.Integer, nullable=False)  # 0=not met, 1=partially met, 2=confidently used
#     writing_id = db.Column(db.Integer, db.ForeignKey('writing.id', ondelete='CASCADE'), nullable=False)
#     criteria_id = db.Column(db.Integer, db.ForeignKey('criteria.id', ondelete='CASCADE'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)


# class AnalysisFeedback(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     writing_id = db.Column(db.Integer, db.ForeignKey('writing.id', ondelete='CASCADE'), nullable=False)
#     is_helpful = db.Column(db.Boolean, nullable=False)
#     writing_age_accurate = db.Column(db.Boolean, nullable=True)
#     strengths_accurate = db.Column(db.Boolean, nullable=True)
#     development_accurate = db.Column(db.Boolean, nullable=True)
#     criteria_accurate = db.Column(db.Boolean, nullable=True)
#     comment = db.Column(db.Text, nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.now)


# class WagollExample(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     explanations = db.Column(db.Text, nullable=True)
#     is_public = db.Column(db.Boolean, default=False)  # Whether this can be shared with other teachers
#     assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id', ondelete='SET NULL'), nullable=True)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
#     # Add relationship to assignment
#     assignment = db.relationship('Assignment', backref=db.backref('wagoll_examples', lazy=True))
