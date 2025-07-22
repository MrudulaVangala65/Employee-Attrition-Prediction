import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import joblib

def load_data(file_path):
    """Load the dataset from a CSV file."""
    df = pd.read_csv(file_path)
    return df

def preprocess_data(df):
    """Preprocess the dataset for training."""
    # Convert categorical variables to dummy/indicator variables
    df = pd.get_dummies(df, columns=['BusinessTravel', 'Department', 'EducationField',
                                      'Gender', 'JobRole', 'MaritalStatus', 'Over18', 'OverTime'])

    # Define features and target variable
    X = df.drop(columns=['Attrition'])  # Features
    y = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)  # Target variable as binary

    return X, y

def balance_data(X_train, y_train):
    """Balance the training data using SMOTE."""
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    return X_resampled, y_resampled

def train_model(X_train, y_train, X_test, y_test):
    """Train the Random Forest model and evaluate it."""
    # Initialize Random Forest model with tuned parameters
    clf = RandomForestClassifier(
        n_estimators=100,  # Number of trees
        max_depth=10,      # Limit depth to reduce overfitting
        random_state=42    # Ensure reproducibility
    )
    
    # Train the model
    clf.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred_train = clf.predict(X_train)
    y_pred_test = clf.predict(X_test)

    print("Training Data Evaluation")
    print("Accuracy Score: {:.2f}%".format(accuracy_score(y_train, y_pred_train) * 100))
    print("Classification Report:\n", classification_report(y_train, y_pred_train))
    print("Confusion Matrix:\n", confusion_matrix(y_train, y_pred_train))

    print("\nTesting Data Evaluation")
    print("Accuracy Score: {:.2f}%".format(accuracy_score(y_test, y_pred_test) * 100))
    print("Classification Report:\n", classification_report(y_test, y_pred_test))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_test))

    return clf

def save_model(model, model_columns, model_path, columns_path):
    """Save the trained model and model columns."""
    joblib.dump(model, model_path)  # Save model for future predictions
    joblib.dump(model_columns, columns_path)  # Save model columns

if __name__ == "__main__":
    # Set file paths
    file_path = 'WA_Fn-UseC_-HR-Employee-Attrition.csv'
    model_path = 'rf_model.pkl'
    columns_path = 'model_columns.pkl'

    # Load and preprocess the data
    df = load_data(file_path)
    X, y = preprocess_data(df)

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # Balance the training data
    X_train_balanced, y_train_balanced = balance_data(X_train, y_train)

    # Scale numerical features
    scaler = StandardScaler()
    X_train_balanced = scaler.fit_transform(X_train_balanced)
    X_test = scaler.transform(X_test)

    # Train and evaluate the model
    model = train_model(X_train_balanced, y_train_balanced, X_test, y_test)

    # Save the trained model and its columns
    save_model(model, X.columns.tolist(), model_path, columns_path)
