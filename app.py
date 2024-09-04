from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app) # initialize db with settings from app

class pr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pr_id = db.Column(db.String(200), nullable=False)
    sourceBranchName = db.Column(db.String(200), nullable=False)
    targetBranchName = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1000), nullable=False) # Cannot be blank, max 1000 chars
    date_created = db.Column(db.DateTime, default=datetime.utcnow) # Automatically set the time when it is added
    def __repr__(self):
        return '<PR %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Main page. Endpoint for the root of the Flask app.
    Listens for incoming payload from the bitbucket webhook, checks if it is a pull request.
    If so, processes the PR data and sends to chatgpt for review. 
    Also adds the PR data to the db and redirects the user to a summary page of the code review.
    """
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

# Bitbucket credentials and repository details
BITBUCKET_USERNAME = 'your_username'
BITBUCKET_REPO_SLUG = 'your_repo_slug'
ACCESS_TOKEN = 'your_access_token' # Need to find out how to get our access token

def get_files_diff(pr_id):
    """
    Gets the file diff from bitbucket based on the given pr_id, and extracts the required data into 'detailed_changes'.
    'detailed_changes' is a list of files that have changed. For each file, there is a dict containing the path of the file,
    a list of lines added, and a list of lines removed.

    Example of files_diff:
    files_diff = [
    {'path': "src/main.py",
        'lines_added': ["print('Hello, world!')", "print('Bye, world!')"],
        'lines_removed': ["print('Remove me')]"]
        }, 

    {'path': "src/quickMaths.py",
        'lines_added': ["x = 1", "y = 2", "z = 3"],
        'lines_removed': []
        }
    ]
    """
    url = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_USERNAME}/{BITBUCKET_REPO_SLUG}/pullrequests/{pr_id}/diff"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        diff_data = response.json()
        
        detailed_changes = []
        for file in diff_data.get('values', []):
            file_info = {
                'path': file['path'],
                'lines_added': [],
                'lines_removed': []
            }
            
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
    """
    Processes the files diff and send it to chatgpt to review.
    """
    return

@app.route('/summary/')
def summary():
    """
    This page will contain the code review of the latest PR made.
    """
    return render_template('summary.html')

@app.route('/chatbot/')
def chatbot():
    """
    This page will allow the user to chat with the AI about its suggested changes to the latest PR.
    """
    return render_template('chatbot.html')

if __name__ == "__main__":
    app.run(debug=True)