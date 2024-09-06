import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Configure database URI
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

class pr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pr_id = db.Column(db.String(200), nullable=False)
    sourceBranchName = db.Column(db.String(200), nullable=False)
    targetBranchName = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<PR %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = request.json
        if 'pullrequest' in data:
            pr_data = data['pullrequest']
            pr_id = pr_data['id']
            source_branch = pr_data['source']['branch']['name']
            target_branch = pr_data['destination']['branch']['name']
            files_diff = get_files_diff(pr_id)
            new_pr_diff = pr(pr_id=pr_id, sourceBranchName=source_branch, targetBranchName=target_branch, content=files_diff)
            process_files_diff(files_diff)
            try:
                db.session.add(new_pr_diff)
                db.session.commit()
                return redirect('/summary/')
            except:
                return 'There was an issue adding a new pull request to the db.'
        return "OK", 200
    else:
        return render_template('index.html')

def get_files_diff(pr_id):
    url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_USERNAME}/{BITBUCKET_REPO_SLUG}/pullrequests/{pr_id}/diff"
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        diff_data = response.json()
        detailed_changes = []
        for file in diff_data.get('values', []):
            file_info = {'path': file['path'], 'lines_added': [], 'lines_removed': []}
            for line in file.get('lines', []):
                if line['type'] == 'add':
                    file_info['lines_added'].append(line['content'])
                elif line['type'] == 'remove':
                    file_info['lines_removed'].append(line['content'])
            detailed_changes.append(file_info)
        return detailed_changes
    else:
        print(f"Failed to retrieve PR diff: {response.status_code} - {response.text}")
        return []

def process_files_diff(files_diff):
    pass

@app.route('/summary/')
def summary():
    return render_template('summary.html')

@app.route('/chatbot/')
def chatbot():
    return render_template('chatbot.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
