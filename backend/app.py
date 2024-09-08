import os
import logging
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import requests

# Configure logging, remove after production
logging.basicConfig(level=logging.INFO)

# Load environment variables from a .env file
load_dotenv()

# Fetch values from environment variables
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_REPO_SLUG = os.getenv("BITBUCKET_REPO_SLUG")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

app = Flask(__name__)
CORS(app)

# Configure database URI
database_url = os.environ.get('DATABASE_URL', 'sqlite:///test.db').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

db = SQLAlchemy(app)

class pr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pr_id = db.Column(db.String(200), nullable=False)
    sourceBranchName = db.Column(db.String(200), nullable=False)
    targetBranchName = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    feedback = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

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
            files_diff = process_files_diff(files_diff)
            
            # Retrieve prompt text
            prompt_file_path = 'prompttext'
            try:
                with open(prompt_file_path, 'r') as file:
                    prompt_text = file.read().strip()
            except FileNotFoundError:
                logging.error(f"Prompt file not found: {prompt_file_path}")
                return 'Prompt file not found', 404

            # Send to LLM
            feedback = analyze_code_with_llm(prompt_text, files_diff)

            # Add to DB
            new_pr_diff = pr(pr_id=pr_id, sourceBranchName=source_branch, targetBranchName=target_branch, content=files_diff, feedback=feedback)
            try:
                db.session.add(new_pr_diff)
                db.session.commit()
                return redirect('/summary/')
            except Exception as e:
                logging.error(f"Error adding pull request to the database: {e}")
                return 'There was an issue adding a new pull request to the db.', 500
        return "OK", 200
    else:
        return render_template('index.html')

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
        logging.error(f"Failed to retrieve PR diff: {response.status_code} - {response.text}")
        return []

def process_files_diff(files_diff):
    """
    Processes the files diff and send it to chatgpt to review.
    """
    pass

def analyze_code_with_llm(prompt, data):
    """
    Sends the data and prompt to Groq AI.
    """
    # Fetch the API key from the environment variable
    groq_API = os.getenv("GROQ_API_KEY")

    # Initialize the Groq client correctly
    client = Groq()

    # Set API key or configure the client as required by the library
    client.api_key = groq_API

    if data is None:
        data = ""  # Provide a default value if data is None

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please help to review the following pull request data: " + "\n" + data}
            ],
            model=os.getenv("GROQ_MODEL_NAME", "llama3-8b-8192"),
            temperature=0.5,
            max_tokens=8192,
            top_p=1,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        logging.error(f"Request error: {e}")
        return "An error occurred while processing the request."


@app.route('/summary/')
def summary():
    # Query to get the latest pull request reviewed
    latest_entry = pr.query.order_by(pr.date_created.desc()).first()
    return render_template('summary.html', entry=latest_entry)

@app.route('/chatbot/')
def chatbot():
    return render_template('chatbot.html')

def create_sample_pr_entry():
    with app.app_context():
        sample_entry = pr(
            pr_id="12345",
            sourceBranchName="main",
            targetBranchName="feature-branch",
            content="This is a sample pull request content.",
            feedback="This is some sample feedback.",
            date_created=datetime.now()
        )
        db.session.add(sample_entry)
        db.session.commit()
        logging.info("Sample entry added successfully!")

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 5000))
#    app.run(host='0.0.0.0', port=port)

# This allows changes to reflect live on localhost:5000 instead of having to rerun app.py
if __name__ == "__main__":
    # Create DB if it does not exist
    with app.app_context():
        db.create_all()
    #create_sample_pr_entry()
    app.run(debug=True)