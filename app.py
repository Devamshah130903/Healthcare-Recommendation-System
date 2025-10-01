import os
import pickle
import pandas as pd
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from rapidfuzz import process, fuzz

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='patient')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ML assets & symptom descriptions
FULL_SYMPTOMS_LIST = []
FULL_SYMPTOMS_SET = set()
DISEASE_NAMES = []
SVC_MODEL = None
SYMPTOMS_DESCRIPTION = {}

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
SYMPTOM_DESC_CSV = os.path.join(os.path.dirname(__file__), "symptoms_description.csv")

def normalize_symptom(s: str) -> str:
    """Normalize symptom name: lowercase, replace spaces with underscores"""
    return s.strip().lower().replace(" ", "_")

def load_symptom_descriptions(csv_path=SYMPTOM_DESC_CSV):
    """Load symptom descriptions from CSV file"""
    desc = {}
    if not os.path.exists(csv_path):
        print(f"⚠️ symptoms_description.csv not found at {csv_path}")
        return desc
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"\n📋 CSV File Info:")
        print(f"   - Columns: {df.columns.tolist()}")
        print(f"   - Total rows: {len(df)}")
        
        df.columns = df.columns.str.strip().str.lower()
        
        # Ensure expected columns exist
        for col in ("symptom", "description", "medication", "diet", "precautions"):
            if col not in df.columns:
                print(f"   ⚠️ Missing column: {col}")
                df[col] = ""
        
        for idx, row in df.iterrows():
            raw = str(row.get("symptom", "")).strip()
            if not raw:
                continue
            
            key = normalize_symptom(raw)
            desc[key] = {
                "description": str(row.get("description", "")).strip() or "No description available",
                "medication": str(row.get("medication", "")).strip() or "N/A",
                "diet": str(row.get("diet", "")).strip() or "N/A",
                "precautions": str(row.get("precautions", "")).strip() or "N/A",
            }
        
        print(f"✅ Loaded {len(desc)} symptom descriptions")
        print(f"   Sample keys: {list(desc.keys())[:5]}")
        
    except Exception as e:
        print(f"❌ Error loading symptom descriptions: {e}")
        import traceback
        traceback.print_exc()
    
    return desc

def load_ml_assets():
    """Load ML model and symptom/disease lists"""
    global FULL_SYMPTOMS_LIST, FULL_SYMPTOMS_SET, DISEASE_NAMES, SVC_MODEL, SYMPTOMS_DESCRIPTION
    
    try:
        with open(os.path.join(MODELS_DIR, "symptoms_list.pkl"), "rb") as f:
            FULL_SYMPTOMS_LIST = pickle.load(f)
        
        # Normalize saved list
        FULL_SYMPTOMS_LIST = [normalize_symptom(s) for s in FULL_SYMPTOMS_LIST]
        FULL_SYMPTOMS_SET = set(FULL_SYMPTOMS_LIST)

        with open(os.path.join(MODELS_DIR, "diseases_list.pkl"), "rb") as f:
            DISEASE_NAMES = pickle.load(f)

        with open(os.path.join(MODELS_DIR, "health_model.pkl"), "rb") as f:
            SVC_MODEL = pickle.load(f)

        # Load symptom descriptions
        SYMPTOMS_DESCRIPTION = load_symptom_descriptions(SYMPTOM_DESC_CSV)

        print(f"\n✅ ML Assets Loaded:")
        print(f"   - Symptoms in model: {len(FULL_SYMPTOMS_LIST)}")
        print(f"   - Diseases: {len(DISEASE_NAMES)}")
        print(f"   - Symptoms with descriptions: {len(SYMPTOMS_DESCRIPTION)}")
        
        # Check coverage
        covered = sum(1 for s in FULL_SYMPTOMS_LIST if s in SYMPTOMS_DESCRIPTION)
        coverage_pct = (covered / len(FULL_SYMPTOMS_LIST) * 100) if FULL_SYMPTOMS_LIST else 0
        print(f"   - Description coverage: {covered}/{len(FULL_SYMPTOMS_LIST)} ({coverage_pct:.1f}%)")
        
        # Show missing symptoms (first 10)
        missing = [s for s in FULL_SYMPTOMS_LIST if s not in SYMPTOMS_DESCRIPTION][:10]
        if missing:
            print(f"   ⚠️ First 10 symptoms missing descriptions: {missing}")
        
    except Exception as e:
        print(f"❌ Error loading ML assets: {e}")
        import traceback
        traceback.print_exc()
        FULL_SYMPTOMS_LIST = []
        FULL_SYMPTOMS_SET = set()
        DISEASE_NAMES = []
        SVC_MODEL = None
        SYMPTOMS_DESCRIPTION = {}

def vectorize_symptoms(input_symptoms_string: str):
    """Convert symptom string to vector for ML model"""
    input_tokens = {normalize_symptom(s) for s in input_symptoms_string.split(",") if s.strip()}
    matched = [s for s in FULL_SYMPTOMS_LIST if s in input_tokens]
    input_vector = [1 if s in input_tokens else 0 for s in FULL_SYMPTOMS_LIST]
    unmatched = [t for t in input_tokens if t not in FULL_SYMPTOMS_SET]
    return [input_vector], matched, unmatched

def get_fuzzy_suggestions(unmatched_symptoms, limit=4, score_cutoff=60):
    """Get fuzzy matching suggestions for unmatched symptoms"""
    suggestions = {}
    if not FULL_SYMPTOMS_LIST:
        return suggestions
    
    human_list = [s.replace("_", " ") for s in FULL_SYMPTOMS_LIST]
    
    for sym in unmatched_symptoms:
        query = sym.replace("_", " ")
        matches = process.extract(query, human_list, scorer=fuzz.WRatio, limit=limit)
        filtered = []
        for match_text, score, idx in matches:
            if score >= score_cutoff:
                canonical = FULL_SYMPTOMS_LIST[idx]
                filtered.append(canonical.replace("_", " ").title())
        suggestions[sym.replace("_", " ").title()] = filtered
    
    return suggestions

# Routes - Auth
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        pwd = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Account already exists with this email", "danger")
            return redirect(url_for("register"))
        hash_pw = generate_password_hash(pwd, method="pbkdf2:sha256")
        user = User(name=name, email=email, password=hash_pw)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, pwd):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("login"))

# Core routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    prediction_data = None
    fuzzy_suggestions = None

    if request.method == "POST":
        input_symptoms = request.form.get("symptoms", "").strip()
        if not input_symptoms:
            flash("Enter symptoms to get prediction", "warning")
            return render_template("dashboard.html", user=current_user)

        if SVC_MODEL is None or not FULL_SYMPTOMS_LIST:
            flash("Model or symptom list not loaded", "danger")
            return render_template("dashboard.html", user=current_user)

        try:
            X_vec, matched, unmatched = vectorize_symptoms(input_symptoms)
            fuzzy_suggestions = get_fuzzy_suggestions(unmatched)

            # Debug logging
            print(f"\n🔍 Prediction Request:")
            print(f"   - Input: {input_symptoms}")
            print(f"   - Matched: {matched}")
            print(f"   - Unmatched: {unmatched}")

            # Predict disease
            pred_raw = SVC_MODEL.predict(X_vec)[0]
            pred_display = str(pred_raw)

            # Build symptom_info dict
            symptom_info = {}
            for s in matched:
                info = SYMPTOMS_DESCRIPTION.get(s)
                
                # Debug each symptom lookup
                print(f"   - Looking up '{s}': {'Found' if info else 'NOT FOUND'}")
                
                if not info:
                    info = {
                        "description": "No description available",
                        "medication": "N/A",
                        "diet": "N/A",
                        "precautions": "N/A"
                    }
                
                pretty = s.replace("_", " ").title()
                symptom_info[pretty] = info

            prediction_data = {
                "disease": pred_display.title(),
                "matched_symptoms": [s.replace("_", " ").title() for s in matched],
                "unmatched_symptoms": [s.replace("_", " ").title() for s in unmatched],
                "symptom_info": symptom_info
            }

            flash(f"Disease predicted: {prediction_data['disease']}. See results below.", "success")
        
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            import traceback
            traceback.print_exc()
            flash(f"Error during prediction: {e}", "danger")

    return render_template("dashboard.html", user=current_user, prediction_data=prediction_data, fuzzy_suggestions=fuzzy_suggestions)

@app.route("/maps")
@login_required
def maps():
    return render_template("maps.html")

# API endpoints
@app.route("/api/symptoms")
@login_required
def api_symptoms():
    pretty = [s.replace("_", " ").title() for s in FULL_SYMPTOMS_LIST]
    return jsonify({"symptoms": pretty})

@app.route("/api/diseases")
@login_required
def api_diseases():
    return jsonify({"diseases": DISEASE_NAMES})

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template("500.html"), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        load_ml_assets()
        print("\n🚀 Starting app — ML assets loaded.\n")
    app.run(debug=True)