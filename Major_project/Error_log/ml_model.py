import json
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder


def Error_Extraction(compilation_error):
    if "IndentationError" in compilation_error:
        return "IndentationError"
    elif "TypeError" in compilation_error:
        return "TypeError"
    elif "NameError" in compilation_error:
        return "NameError"
    elif "ModuleNotFoundError" in compilation_error:
        return "ModuleNotFoundError"
    elif "SyntaxError" in compilation_error:
        return "SyntaxError"
    elif "EOFError" in compilation_error:
        return "EOFError"
    elif "FileNotFoundError" in compilation_error:
        return "FileNotFoundError"
    elif "KeyError" in compilation_error:
        return "KeyError"
    elif "TclError" in compilation_error:
        return "TclError"
    elif "ValueError" in compilation_error:
        return "ValueError"
    elif "AttributeError" in compilation_error:
        return "AttributeError"
    elif "IndexError" in compilation_error:
        return "IndexError"
    elif "OSError" in compilation_error:
        return "OSError"
    elif "exec_timeout" in compilation_error:
        return "exec_timeout"
    elif "AssertionError" in compilation_error:
        return "AssertionError"
    else:
        return False

# Load the JSON data
with open('C:/Users/PRANAY KIRAN/Desktop/output_data4.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract features and labels
X = [entry["error_type"] for entry in data.values()]  
y = [entry["threat_level"] for entry in data.values()]

# Convert categorical features to numerical using LabelEncoder
le_error_type = LabelEncoder()
X_encoded = le_error_type.fit_transform(X)

# Convert labels to numerical
le_threat_level = LabelEncoder()
y_encoded = le_threat_level.fit_transform(y)

# Initialize the KNN classifier with class weights
knn_classifier = KNeighborsClassifier(n_neighbors=3, weights='distance', metric='manhattan')

# Train the classifier
knn_classifier.fit(X_encoded.reshape(-1, 1), y_encoded)

def predict_threat_level(compilation_error):
    # Use the Error_Extraction function to get the specific error type
    error_type = Error_Extraction(compilation_error)

    # Encode the input feature
    error_type_encoded = le_error_type.transform([error_type])
    input_features = np.array(error_type_encoded).reshape(1, -1)

    # Make predictions using the trained model
    threat_level_encoded = knn_classifier.predict(input_features)

    # Decode the predicted threat level
    predicted_threat_level = le_threat_level.inverse_transform(threat_level_encoded)[0]

    return predicted_threat_level
