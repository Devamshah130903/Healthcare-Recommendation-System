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
<img width="1919" height="1083" alt="Screenshot 2025-09-29 203326" src="https://github.com/user-attachments/assets/b69e9cf0-e80b-4b39-b965-36d21a39f15e" />
<img width="1919" height="1059" alt="Screenshot 2025-09-29 203343" src="https://github.com/user-attachments/assets/f6782d90-be2c-42b0-8c2c-1525f84f36da" />
<img width="1919" height="1029" alt="Screenshot 2025-09-29 203411" src="https://github.com/user-attachments/assets/5cd455bb-e474-479f-9a97-d4c7695b09ea" />
<img width="1919" height="1021" alt="Screenshot 2025-09-29 203425" src="https://github.com/user-attachments/assets/b028f0f7-0fb0-489c-a4be-9e0f99e29772" />




👨‍💻 Author

Developed by Devam Shah# Healthcare-Recommention-System
