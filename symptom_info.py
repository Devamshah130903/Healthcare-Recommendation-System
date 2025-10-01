import csv

def load_symptom_data(file_path="symptoms_description.csv"):
    symptom_dict = {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symptom = row["symptom"].strip().lower().replace(" ", "_")
            symptom_dict[symptom] = {
                "description": row["description"].strip(),
                "medication": row["medication"].strip(),
                "diet": row["diet"].strip(),
                "precautions": row["precautions"].strip()
            }
    return symptom_dict

def get_user_symptoms():
    user_input = input("Enter your symptoms separated by commas: ")
    # Normalize input for matching
    return [s.strip().lower().replace(" ", "_") for s in user_input.split(",")]

def get_symptom_details(user_symptoms, symptom_data):
    result = {}
    for symptom in user_symptoms:
        if symptom in symptom_data:
            result[symptom] = symptom_data[symptom]
        else:
            result[symptom] = {
                "description": "No description found.",
                "medication": "No medication info.",
                "diet": "No diet info.",
                "precautions": "No precautions info."
            }
    return result

if __name__ == "__main__":
    symptom_data = load_symptom_data()
    user_symptoms = get_user_symptoms()
    details = get_symptom_details(user_symptoms, symptom_data)

    for symptom, info in details.items():
        print(f"\nSymptom: {symptom}")
        print(f"Description: {info['description']}")
        print(f"Medication: {info['medication']}")
        print(f"Diet: {info['diet']}")
        print(f"Precautions: {info['precautions']}")