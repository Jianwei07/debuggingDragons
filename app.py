from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app) # initialize db with settings from our app

class pr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False) # Cannot be blank, max 1000 chars
    date_created = db.Column(db.DateTime, default=datetime.utcnow) # Automatically set the time when it is added
    def __repr__(self):
        return '<PR %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/summary/')
def summary():
    return render_template('summary.html')

@app.route('/chatbot/')
def chatbot():
    return render_template('chatbot.html')

if __name__ == "__main__":
    app.run(debug=True)