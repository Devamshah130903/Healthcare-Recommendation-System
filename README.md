🏥 Healthcare Recommendation System

A Flask-based web application that provides personalized healthcare recommendations such as diseases, medications, precautions, and diets based on user-input symptoms.

🚀 Features

🔐 User Authentication (Register & Login system)

🧾 Symptom-based Disease Prediction (using ML model)

💊 Recommendations for:

Medications

Precautions

Workouts

Diet Plans

📊 Interactive and user-friendly UI (Bootstrap-based)

🌐 Deployable on Heroku / Render / Railway

📂 Project Structure
Healthcare-Recommendation-System/
│── static/                # CSS, JS, Images
│── templates/             # HTML templates (Flask Jinja2)
│── model/                 # Trained ML model + datasets
│── model_training.ipynb   # Notebook for training ML model
│── app.py                 # Main Flask application
│── requirements.txt       # Project dependencies
│── README.md              # Project documentation
│── .gitignore             # Ignored files for Git

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/yourusername/healthcare-recommendation-system.git
cd healthcare-recommendation-system

2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # On Windows
source venv/bin/activate # On Mac/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Dataset Download

This project uses a healthcare dataset available at:
👉 Mendeley Dataset - Symptoms, Precautions, Medicines, Workouts, and Diets

Download and place the dataset files into the model/ directory.

5️⃣ Train the Model 

You need to retrain the model:

Open model_training.ipynb in Jupyter Notebook / VS Code.

Run all cells.

This will generate the following .pkl files inside the model/ folder:

disease_prediction.pkl (trained ML model)

symptom_vectorizer.pkl (vectorizer for input symptoms)

label_encoder.pkl (encoder for disease labels)

6️⃣ Run the Application
python app.py


Open your browser and visit:
👉 http://127.0.0.1:5000/

🛠️ Tech Stack

Frontend: HTML, CSS (Bootstrap), JavaScript

Backend: Flask (Python)

Database: SQLite / MySQL (configurable)

ML Model: Support Vector Classifier (SVC) trained on healthcare dataset

📸 Screenshots

(Add screenshots here after running the app)

👨‍💻 Author

Developed by Devam Shah# Healthcare-Recoomention-System
