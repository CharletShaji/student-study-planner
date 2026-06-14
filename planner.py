from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── DATABASE MODELS ──────────────────────────────────────────

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    trimester = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='In Progress')
    assignments = db.relationship('Assignment', backref='unit', lazy=True, cascade='all, delete')

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)

# ── ROUTES ───────────────────────────────────────────────────

@app.route('/')
def index():
    units = Unit.query.all()
    total = len(units)
    completed = len([u for u in units if u.status == 'Completed'])
    assignments = Assignment.query.all()
    pending = len([a for a in assignments if a.status == 'Pending'])
    overdue = len([a for a in assignments if a.status == 'Overdue'])
    return render_template('index.html', units=units, total=total,
                           completed=completed, pending=pending, overdue=overdue)

@app.route('/add_unit', methods=['POST'])
def add_unit():
    unit = Unit(
        code=request.form['code'],
        name=request.form['name'],
        trimester=request.form['trimester'],
        status=request.form['status']
    )
    db.session.add(unit)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_unit/<int:id>')
def delete_unit(id):
    unit = Unit.query.get_or_404(id)
    db.session.delete(unit)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_unit/<int:id>', methods=['POST'])
def update_unit(id):
    unit = Unit.query.get_or_404(id)
    unit.status = request.form['status']
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_assignment', methods=['POST'])
def add_assignment():
    assignment = Assignment(
        title=request.form['title'],
        due_date=request.form['due_date'],
        weight=request.form['weight'],
        status=request.form['status'],
        unit_id=request.form['unit_id']
    )
    db.session.add(assignment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_assignment/<int:id>')
def delete_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_assignment/<int:id>', methods=['POST'])
def update_assignment(id):
    assignment = Assignment.query.get_or_404(id)
    assignment.status = request.form['status']
    db.session.commit()
    return redirect(url_for('index'))

# ── RUN ──────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)