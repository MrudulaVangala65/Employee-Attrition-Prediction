from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash
from flask_sqlalchemy import SQLAlchemy
import pickle,joblib
import pandas as pd
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the CSV file path
csv_file_path = 'employee_attrition_data.csv'

# Create a CSV file if it doesn't exist with the appropriate headers
if not os.path.isfile(csv_file_path):
    headers = ['Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome', 'Education', 
               'EducationField', 'EmployeeCount', 'EmployeeNumber', 'EnvironmentSatisfaction', 
               'Gender', 'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction', 
               'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked', 'Over18', 
               'OverTime', 'PercentSalaryHike', 'PerformanceRating', 'RelationshipSatisfaction', 
               'StandardHours', 'StockOptionLevel', 'TotalWorkingYears', 'TrainingTimesLastYear', 
               'WorkLifeBalance', 'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion', 
               'YearsWithCurrManager', 'Prediction']

    pd.DataFrame(columns=headers).to_csv(csv_file_path, index=False)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Initialize the database and add default users
with app.app_context():
    db.create_all()
    # Add default users if they don't exist
    if not User.query.filter_by(username="admin").first():
        db.session.add(User(username="admin", password="admin"))
    if not User.query.filter_by(username="Admin").first():
        db.session.add(User(username="Admin", password="Admin123"))
    db.session.commit()

# Home route: Redirect to login if not logged in, otherwise to the dashboard
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

# User management route
@app.route('/users')
def users():
    if 'username' not in session:
        return redirect(url_for('login'))
    all_users = User.query.all()
    return render_template("user.html", users=all_users)

# Delete user route
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_to_delete = User.query.get(user_id)
    if user_to_delete and user_to_delete.username.lower() != 'admin':
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    elif user_to_delete.username.lower() == 'admin':
        flash('Cannot delete the admin user!', 'danger')
    else:
        flash('User not found!', 'danger')
    return redirect(url_for('users'))

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# About page route
@app.route('/about')
def about():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')

# Admin route
@app.route('/admin')
def admin_login():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')
# Load the model and model columns at the start
clf = joblib.load('your_best_model_path.pkl')  # Replace with your actual model path
model_columns = joblib.load('your_model_columns.pkl')  # Load your model's column names



# Notifications storage
notifications = []

# Function to preprocess input data
def preprocess_input(input_data):
    mappings = {
        'BusinessTravel': {'Rarely': 0, 'Frequently': 1, 'No Travel': 2},
        'Department': {'Research & Development': 0, 'Human Resources': 1, 'Sales': 2},
        'Gender': {'Male': 0, 'Female': 1},
        'EducationField': {'Life Sciences': 0, 'Medical': 1, 'Marketing': 2,
                           'Technical Degree': 3, 'Human Resources': 4, 'Other': 5},
        'JobRole': {'Sales Executive': 0, 'Research Scientist': 1, 'Laboratory Technician': 2,
                    'Manufacturing Director': 3, 'Healthcare Representative': 4, 'Manager': 5,
                    'Sales Representative': 6, 'Research Director': 7, 'Human Resources': 8},
        'Over18': {'Y': 1, 'N': 0},
        'OverTime': {'Yes': 1, 'No': 0}
    }

    for column, mapping in mappings.items():
        if column in input_data:
            input_data[column] = input_data[column].map(mapping)

    return input_data
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_handler():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user and username.lower() == 'admin':  # restrict to admin user
            session['username'] = user.username
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('admin_login.html')


@app.route('/index1', methods=['GET'])
def index1():
    return render_template('index1.html')

@app.route('/attrition-prediction', methods=['GET', 'POST'])
def attrition_prediction():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            # Create a DataFrame from the form data
            input_data = pd.DataFrame(request.form, index=[0])

            # Check if required fields are present
            required_fields = [
                'Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome',
                'Education', 'EducationField', 'EmployeeCount', 'EmployeeNumber',
                'EnvironmentSatisfaction', 'Gender', 'HourlyRate', 'JobInvolvement',
                'JobLevel', 'JobRole', 'JobSatisfaction', 'MaritalStatus', 'MonthlyIncome',
                'MonthlyRate', 'NumCompaniesWorked', 'Over18', 'OverTime', 'PercentSalaryHike',
                'PerformanceRating', 'RelationshipSatisfaction', 'StandardHours',
                'StockOptionLevel', 'TotalWorkingYears', 'TrainingTimesLastYear',
                'WorkLifeBalance', 'YearsAtCompany', 'YearsInCurrentRole',
                'YearsSinceLastPromotion', 'YearsWithCurrManager'
            ]
            if not all(field in input_data for field in required_fields):
                flash("Please fill in all required fields.", "error")
                return redirect(url_for('attrition_prediction'))

            # Preprocess the input data
            input_data = preprocess_input(input_data)

            # Ensure all columns match the model's input features
            input_data = input_data.reindex(columns=model_columns, fill_value=0)

            # Make prediction
            prediction = clf.predict(input_data)
            result = 'Attrition' if prediction[0] == 1 else 'No Attrition'

            # Add notification if attrition is predicted
            if prediction[0] == 1:
                employee_number = input_data['EmployeeNumber'].values[0]
                age = input_data['Age'].values[0]
                job_role = input_data['JobRole'].values[0]
                notifications.append(f"Alert: Employee {employee_number} (Age: {age}, Job Role: {job_role}) is likely to leave.")
                return render_template('result.html', prediction="The employee may leave.", 
                                       employee_number=employee_number, age=age, job_role=job_role)
            else:
                return render_template('result.html', prediction="The employee may not leave.")

        except Exception as e:
            flash("Error in prediction. Please check your input.", "error")
            return redirect(url_for('attrition_prediction'))

    # For GET requests, render the input form
    return render_template('index1.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract data from the form
        data = {
            'Age': request.form['Age'],
            'BusinessTravel': request.form['BusinessTravel'],
            'DailyRate': request.form['DailyRate'],
            'Department': request.form['Department'],
            'DistanceFromHome': request.form['DistanceFromHome'],
            'Education': request.form['Education'],
            'EducationField': request.form['EducationField'],
            'EmployeeCount': request.form['EmployeeCount'],
            'EmployeeNumber': request.form['EmployeeNumber'],
            'EnvironmentSatisfaction': request.form['EnvironmentSatisfaction'],
            'Gender': request.form['Gender'],
            'HourlyRate': request.form['HourlyRate'],
            'JobInvolvement': request.form['JobInvolvement'],
            'JobLevel': request.form['JobLevel'],
            'JobRole': request.form['JobRole'],
            'JobSatisfaction': request.form['JobSatisfaction'],
            'MaritalStatus': request.form['MaritalStatus'],
            'MonthlyIncome': request.form['MonthlyIncome'],
            'MonthlyRate': request.form['MonthlyRate'],
            'NumCompaniesWorked': request.form['NumCompaniesWorked'],
            'Over18': request.form['Over18'],
            'OverTime': request.form['OverTime'],
            'PercentSalaryHike': request.form['PercentSalaryHike'],
            'PerformanceRating': request.form['PerformanceRating'],
            'RelationshipSatisfaction': request.form['RelationshipSatisfaction'],
            'StandardHours': request.form['StandardHours'],
            'StockOptionLevel': request.form['StockOptionLevel'],
            'TotalWorkingYears': request.form['TotalWorkingYears'],
            'TrainingTimesLastYear': request.form['TrainingTimesLastYear'],
            'WorkLifeBalance': request.form['WorkLifeBalance'],
            'YearsAtCompany': request.form['YearsAtCompany'],
            'YearsInCurrentRole': request.form['YearsInCurrentRole'],
            'YearsSinceLastPromotion': request.form['YearsSinceLastPromotion'],
            'YearsWithCurrManager': request.form['YearsWithCurrManager']
        }

        # Preprocess input data
        input_data = pd.DataFrame([data])
        input_data = preprocess_input(input_data)

        # Ensure all columns match the model's input features
        input_data = input_data.reindex(columns=model_columns, fill_value=0)

        # Make prediction
        prediction = clf.predict(input_data)[0]
        data['Prediction'] = "The employee may leave." if prediction == 1 else "The employee may not leave."

        # Save input data to CSV
        df = pd.DataFrame([data])
        df.to_csv(csv_file_path, mode='a', header=False, index=False)

        # Render the result page
        return render_template('result.html', prediction=data['Prediction'], 
                               employee_number=data['EmployeeNumber'], age=data['Age'], job_role=data['JobRole'])

    except Exception as e:
        flash("Error in prediction. Please check your input.", "error")
        return redirect(url_for('attrition_prediction'))
@app.route('/notify_admin', methods=['POST'])
def notify_admin():
    # Generate a unique ID for the notification
    notification_id = len(session.get('notifications', [])) + 1

    # Example notification data with unique ID
    new_notification = {
        'id': notification_id,
        'employee_number': request.form.get('employee_number'),
        'age': request.form.get('age'),
        'job_role': request.form.get('job_role')
    }

    # Retrieve existing notifications from the session, or initialize an empty list
    notifications = session.get('notifications', [])
    
    # Append the new notification to the list
    notifications.append(new_notification)
    
    # Update the session with the modified list
    session['notifications'] = notifications

    return redirect(url_for('notifications'))

@app.route('/notifications')
def notifications():
    show_notifications = True
    notifications = session.get('notifications', [])
    return render_template('notifications.html', notifications=notifications, show_notifications=show_notifications)

# Admin Dashboard route with a unique endpoint
@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')  # Replace with your actual template

@app.route('/employee_dashboard')
def employee_dashboard():
    return render_template('dashboard.html')

@app.route('/notifications', methods=['GET', 'POST'])
def notifications_view():
    return render_template('notifications.html', notifications=notifications, show_notifications=True)


    

# Chatbot route
@app.route('/chatbot')
def chatbot():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot_index.html')

# Chatbot message handling route (AJAX)
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json['message']
    bot_response = f"You said: {user_message}"  # Placeholder response
    return jsonify({'response': bot_response})

# Query handling route
df = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")
@app.route('/query', methods=['POST'])
def query():
    user_input = request.json.get('query')

    # Initialize response
    response = "Invalid query format. Please check and try again."

    try:
        # Parse the input query for each condition separated by commas
        conditions = user_input.split(",")
        query_conditions = []

        for condition in conditions:
            condition = condition.strip()  # Remove any extra spaces
            
            # Handle "is" condition for exact matches
            if " is " in condition:
                col, value = condition.split(" is ")
                col, value = col.strip(), value.strip()
                if col in df.columns:
                    query_conditions.append(f"{col} == '{value}'")

            # Handle ">" and "<" conditions
            elif ">" in condition or "<" in condition:
                if ">=" in condition:
                    col, value = condition.split(">=")
                    col, value = col.strip(), value.strip()
                    if col in df.columns:
                        query_conditions.append(f"{col} >= {value}")
                elif "<=" in condition:
                    col, value = condition.split("<=")
                    col, value = col.strip(), value.strip()
                    if col in df.columns:
                        query_conditions.append(f"{col} <= {value}")
                elif ">" in condition:
                    col, value = condition.split(">")
                    col, value = col.strip(), value.strip()
                    if col in df.columns:
                        query_conditions.append(f"{col} > {value}")
                elif "<" in condition:
                    col, value = condition.split("<")
                    col, value = col.strip(), value.strip()
                    if col in df.columns:
                        query_conditions.append(f"{col} < {value}")

            # Handle "=" for exact match
            elif "=" in condition and "==" not in condition:
                col, value = condition.split("=")
                col, value = col.strip(), value.strip()
                if col in df.columns:
                    query_conditions.append(f"{col} == '{value}'")

        # Join all query conditions with "and" for combined filtering
        query_string = " and ".join(query_conditions)

        # Use the query method on the DataFrame with the generated query string
        filtered_data = df.query(query_string)
        if not filtered_data.empty:
            response = filtered_data.to_html(classes='data', header="true", index=False)
        else:
            response = "No records match your query."
    except Exception as e:
        response = f"Error processing query: {str(e)}"

    return jsonify(response=response)
# Load the dataset and drop the "Attrition" column if it exists
employees_df = pd.read_csv("emp dataset.csv")
if "Attrition" in employees_df.columns:
    employees_df = employees_df.drop(columns=["Attrition"])

# Define the view route
@app.route('/view')
def view_employees():
    employees = employees_df.to_dict(orient='records')
    return render_template('view.html', employees=employees)

# Define the update route
@app.route('/update', methods=['GET', 'POST'])
def update_employee():
    if request.method == 'POST':
        employee_number = request.form['EmployeeNumber']
        column_to_update = request.form['column']
        new_value = request.form[column_to_update]

        # Update the DataFrame based on the employee number
        employees_df.loc[employees_df['EmployeeNumber'] == int(employee_number), column_to_update] = new_value

        # Save updated DataFrame back to the CSV file to persist changes
        employees_df.to_csv("emp dataset.csv", index=False)

        # Redirect to view employees to see updated data
        return redirect(url_for('view_employees'))
    
    return render_template('update.html')
# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)  