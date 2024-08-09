from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Like214!@localhost/assignment_sql'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
	__tablename__ = 'Members'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	name = db.Column(db.String(255), nullable=False)
	age = db.Column(db.Integer)
	workout_sessions = db.relationship('WorkoutSessions', backref='member', lazy=True)

class MemberSchema(ma.Schema):
	id = fields.Integer(dump_only=True)
	name = fields.String(required=True, validate=validate.Length(min=1))
	age = fields.Integer(required=True)
	
	class Meta:
		fields = ("id", "name", "age")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class WorkoutSessions(db.Model):
	__tablename__ = 'WorkoutSessions'
	date = db.Column(db.Date, nullable=False)
	session_time = db.Column(db.String, nullable=False)
	activity = db.Column(db.String(233), nullable=False)
	calories_burned = db.Column(db.Integer, nullable=False)
	duration_minutes = db.Column(db.Integer, nullable=False)
	session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	member_id = db.Column(db.Integer, db.ForeignKey('Members.id'), nullable=False)

class WorkoutSessionSchema(ma.Schema):
	session_id = fields.Integer(dump_only=True)
	date = fields.Date(required=True)
	session_time = fields.String(required=True)
	activity = fields.String(required=True)
	calories_burned = fields.Integer(required=True)
	duration_minutes = fields.Integer(required=True)
	member_id = fields.Integer(required=True)

	class Meta:
		fields = ("session_id", "date", "session_time", "activity", "calories_burned", "duration_minutes", "member_id")

workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

@app.route('/workout_sessions/<int:member_id>', methods=['POST'])
def add_workout_session(member_id):
	try:
		workout_session_data = workout_session_schema.load(request.json)
	except ValidationError as err:
		return jsonify(err.messages), 400
	new_workout_session = WorkoutSessions(date=workout_session_data['date'], session_time=workout_session_data['session_time'], activity=workout_session_data['activity'], calories_burned=workout_session_data['calories_burned'], duration_minutes=workout_session_data['duration_minutes'],member_id=member_id)
	db.session.add(new_workout_session)
	db.session.commit()
	return workout_session_schema.jsonify(new_workout_session), 201

@app.route('/members', methods=['POST'])
def add_member():
	try:
		member_data = member_schema.load(request.json)
	except ValidationError as err:
		return jsonify(err.messages), 400
	new_member = Member(name=member_data['name'], age=member_data['age'])
	db.session.add(new_member)
	db.session.commit()
	return member_schema.jsonify(new_member), 201

@app.route('/members', methods=['GET'])
def get_members():
	all_members = Member.query.all()
	result = members_schema.dump(all_members)
	return jsonify(result), 200

@app.route('/workout_sessions', methods=['GET'])
def get_workout_sessions():
	all_workout_sessions = WorkoutSessions.query.all()
	result = workout_sessions_schema.dump(all_workout_sessions)
	return jsonify(result), 200

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
	member = Member.query.get_or_404(id)
	return member_schema.jsonify(member), 200

@app.route('/workout_sessions/<int:session_id>', methods=['GET'])
def get_workout_session(session_id):
	workout_session = WorkoutSessions.query.get_or_404(session_id)
	return workout_session_schema.jsonify(workout_session), 200

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
	member = Member.query.get_or_404(id)
	try:
		member_data = member_schema.load(request.json)
	except ValidationError as err:
		return jsonify(err.messages), 400
	member.name = member_data['name']
	member.age = member_data['age']
	db.session.commit()
	return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/workout_sessions/<int:session_id>', methods=['PUT'])
def update_workout_session(session_id):
	workout_session = WorkoutSessions.query.get_or_404(session_id)
	try:
		workout_session_data = workout_session_schema.load(request.json)
	except ValidationError as err:
		return jsonify(err.messages), 400
	workout_session.date = workout_session_data['date']
	workout_session.session_time = workout_session_data['session_time']
	workout_session.activity = workout_session_data['activity']
	workout_session.calories_burned = workout_session_data['calories_burned']
	workout_session.duration_minutes = workout_session_data['duration_minutes']
	workout_session.member_id = workout_session_data['member_id']
	db.session.commit()
	return jsonify({"message": "Workout session details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
	member = Member.query.get_or_404(id)
	db.session.delete(member)
	db.session.commit()
	return jsonify({"message": "Member removed successfully"}), 200

@app.route('/workout_sessions/<int:session_id>', methods=['DELETE'])
def delete_workout_session(session_id):
	workout_session = WorkoutSessions.query.get_or_404(session_id)
	db.session.delete(workout_session)
	db.session.commit()
	return jsonify({"message": "Workout session removed successfully"}), 200

@app.route('/members/<int:id>/workout_sessions', methods=['GET'])
def get_member_workout_sessions(id):
	member = Member.query.get_or_404(id)
	workout_sessions = member.workout_sessions
	result = workout_sessions_schema.dump(workout_sessions)
	return jsonify(result), 200

if __name__ == '__main__':
	app.run(debug=True)