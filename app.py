from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import hashlib
import timm  # Needed for ViT model creation

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key_here"

# In-memory user store (do not use in production)
users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load your model using state_dict
model_path = "vit_model_state.pth"  # Path to the model saved using state_dict

# Number of classes and labels (edit according to your dataset)
num_classes = 2  # e.g., Fresh vs Stale
class_labels = ["Fresh", "Stale"]  # Adjust to match your training labels

# Create the ViT model and load weights
model = timm.create_model("vit_base_patch16_224", pretrained=False, num_classes=num_classes)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == hash_password(password):
        session['user'] = username
        return redirect(url_for('index'))
    flash('Invalid credentials')
    return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if username in users:
            flash('Username exists.')
        elif password != confirm:
            flash('Passwords do not match.')
        else:
            users[username] = hash_password(password)
            flash('Registered! You can now log in.')
            return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/index')
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login_page'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['file']
    img = Image.open(file.stream).convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        output = model(img)
        _, pred = torch.max(output, 1)
        label = class_labels[pred.item()]

    return label  # Just return the label string


@app.route('/upload')
def upload_form():
    return render_template('predict.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run(debug=True)