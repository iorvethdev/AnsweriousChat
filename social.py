from flask import Flask, render_template_string, request, redirect, url_for
import os
import json

app = Flask(__name__)

# Define the upload folder inside the static directory
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File to store questions
QUESTIONS_FILE = "questions.json"

# Load questions from JSON file if it exists, else use an empty list
if os.path.exists(QUESTIONS_FILE):
    with open(QUESTIONS_FILE, "r") as file:
        questions = json.load(file)
else:
    questions = []

# Function to save questions to JSON file
def save_questions():
    with open(QUESTIONS_FILE, "w") as file:
        json.dump(questions, file, indent=4)

# HTML Templates
home_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Answerious</title>
    <style>
    body { 
    color: green;
    background-color: black;
    font-family: consolas;
    }
    h1 {
    color: white;
    font-family: Arial, sans-serif;
    }
    input {
    color: green;
    font-family: consolas;
    background-color: black;
    }
    textarea {
    color: green;
    font-family: consolas;
    background-color: black;
    }
    img {
    max-width: 300px;
    display: block;
    margin-top: 10px;
    }
    </style>
</head>
<body>
    <h1>Welcome</h1>
    <form method="POST" action="/post-question" enctype="multipart/form-data">
        <label>Post something:</label><br>
        <input type="text" name="username" placeholder="Name" required><br>
        <textarea name="question" placeholder="Text" required></textarea><br>
        <label>Upload a file (optional):</label><br>
        <input type="file" name="image"><br>
        <button type="submit">Post</button>
    </form>
    <hr>
    <h2>Feed:</h2>
    {% for question in questions %}
        <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
            <h3>{{ question['text'] }}</h3>
            <p><strong>Posted by:</strong> {{ question['username'] }}</p>
            {% if question['image'] %}
                <img src="{{ question['image'] }}" alt="file">
            {% endif %}
            <hr>
            <h4>Comments:</h4>
            {% if question['answers'] %}
                <ul>
                {% for answer in question['answers'] %}
                    <li><strong>{{ answer['username'] }}:</strong> {{ answer['text'] }}</li>
                {% endfor %}
                </ul>
            {% else %}
                <p>No comments yet. Be the first to comment!</p>
            {% endif %}
            <a href="/answer/{{ loop.index0 }}">Comment</a>
        </div>
    {% endfor %}
</body>
</html>
"""

answer_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Answer</title>
    <style>
    body { 
    color: green;
    background-color: black;
    font-family: consolas;
    }
    h1 {
    color: white;
    font-family: Arial, sans-serif;
    }
    input {
    color: green;
    font-family: consolas;
    background-color: black;
    }
    textarea {
    color: green;
    font-family: consolas;
    background-color: black;
    }
    img {
    max-width: 300px;
    display: block;
    margin-top: 10px;
    }
    </style>
</head>
<body>
    <p><strong>Comment:</strong> {{ question['text'] }}</p>
    {% if question['image'] %}
        <img src="{{ question['image'] }}" alt="Uploaded image">
    {% endif %}
    <form method="POST">
        <label>Your Answer:</label><br>
        <input type="text" name="username" placeholder="Name" required><br>
        <textarea name="answer" placeholder="Your Answer" required></textarea><br>
        <button type="submit">Post Answer</button>
    </form>
    <hr>
    <h2>All Comments:</h2>
    {% for answer in question['answers'] %}
        <p><strong>{{ answer['username'] }}:</strong> {{ answer['text'] }}</p>
    {% endfor %}
    <a href="/">Back to Home</a>
</body>
</html>
"""

# Routes
@app.route("/")
def home():
    return render_template_string(home_template, questions=questions)

@app.route("/post-question", methods=["POST"])
def post_question():
    username = request.form["username"]
    question_text = request.form["question"]
    image_file = request.files.get("image")
    image_url = None

    if image_file and image_file.filename:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
        image_file.save(image_path)
        image_url = url_for('static', filename=f"uploads/{image_file.filename}")

    new_question = {"username": username, "text": question_text, "answers": [], "image": image_url}
    questions.append(new_question)

    # Save questions to the JSON file after posting
    save_questions()

    return redirect(url_for("home"))

@app.route("/answer/<int:question_id>", methods=["GET", "POST"])
def answer_question(question_id):
    question = questions[question_id]
    if request.method == "POST":
        username = request.form["username"]
        answer_text = request.form["answer"]
        question["answers"].append({"username": username, "text": answer_text})

        # Save questions after adding an answer
        save_questions()

        return redirect(url_for("home"))
    return render_template_string(answer_template, question=question)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
