from flask import Flask, request, jsonify, render_template, session, flash, redirect, url_for
import os
import mysql.connector as mysql

import traceback




app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.errorhandler(500)
def internal_error(error):
    return f"<pre>{traceback.format_exc()}</pre>", 500

def get_db_connection():
    return mysql.connect(host="localhost", user="root", password="mysql", database="jr")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/employee_dashboard', methods=['GET'])
def employee_dashboard():
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    return render_template("employee_dashboard.html")



@app.route('/register', methods=['POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor()

    data = request.form 
    name = data.get('name')
    username = data.get('username')
    user_type = data.get('user_type')
    password = data.get('password')

    # Check if username already exists
    cursor.execute("SELECT COUNT(*) FROM User WHERE Username = %s", (username,))
    if cursor.fetchone()[0] > 0:
        flash("Username already exists!", "danger")
        return redirect(url_for('index'))

    # Insert into User table
    sql = "INSERT INTO User (Name, Username, UserType, Password) VALUES (%s, %s, %s, %s)"
    values = (name, username, user_type, password)

    try:
        cursor.execute(sql, values)
        conn.commit()
        user_id = cursor.lastrowid  # Get the newly created user's ID
        session['user_id'] = user_id
        session['user_type'] = user_type

        flash("User registered successfully! Please complete your profile.", "success")

        if user_type == "Employer":
            return redirect(url_for('register_employer'))
        else:
            return redirect(url_for('register_employee'))

    except mysql.Error as err:
        flash(f"Database error: {err}", "danger")

    cursor.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/register_employer', methods=['GET', 'POST'])
def register_employer():
    if 'user_id' not in session or session.get('user_type') != "Employer":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        user_id = session['user_id']
        name_of_poc = request.form.get('name_of_poc')
        contact_info = request.form.get('contact_info')
        no_of_openings = 0

        sql = "INSERT INTO Employer (ID, NameOfPOC, ContactInfo, NoOfOpenings) VALUES (%s, %s, %s, %s)"
        values = (user_id, name_of_poc, contact_info, no_of_openings)

        try:
            cursor.execute(sql, values)
            conn.commit()
            flash("Employer profile completed! You can now log in.", "success")
            return redirect(url_for('login'))
        except mysql.Error as err:
            flash(f"Database error: {err}", "danger")

        cursor.close()
        conn.close()

    return render_template("register_employer.html")

@app.route('/update_resume', methods=['GET', 'POST'])
def update_resume():
    if 'user_id' not in session or session.get('user_type') != "Employee":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = session['user_id']

    if request.method == 'POST':
        new_resume = request.form.get('resume')

        # Update resume in the database
        sql = "UPDATE Employee SET Resume = %s WHERE ID = %s"
        cursor.execute(sql, (new_resume, user_id))
        conn.commit()

        flash("Resume updated successfully!", "success")
        return redirect(url_for('employee_dashboard'))

    # Fetch current resume details
    cursor.execute("SELECT Resume FROM Employee WHERE ID = %s", (user_id,))
    resume_data = cursor.fetchone()
    current_resume = resume_data[0] if resume_data else ""

    cursor.close()
    conn.close()

    return render_template('update_resume.html', resume=current_resume)

"""
@app.route('/add_skills', methods=['GET', 'POST'])
def add_skills():
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    candidate_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all available skills from the Skill table
    cursor.execute("SELECT Skill_ID, Name FROM Skill ORDER BY Name ASC")
    skills = cursor.fetchall()  # List of (ID, Name)

    if request.method == 'POST':
        selected_skills = request.form.getlist('skills')  # List of selected skill IDs

        try:
            selected_skills = [int(skill_id) for skill_id in selected_skills]  # Convert to integers
        except ValueError:
            flash("Invalid skill selection!", "danger")
            return redirect(url_for('add_skills'))

        # Insert selected skills into CandidateSkills table
        if selected_skills:
            sql = "INSERT IGNORE INTO candiskill (Cand_ID, Skill_ID) VALUES (%s, %s)"
            values = [(candidate_id, skill_id) for skill_id in selected_skills]
            cursor.executemany(sql, values)
            conn.commit()

            flash("Skills added successfully!", "success")
            return redirect(url_for('employee_dashboard'))

    cursor.close()
    conn.close()

    return render_template("add_skills.html", skills=skills)"""

@app.route('/add_skills', methods=['GET', 'POST'])
def add_skills():
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    candidate_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all available skills from the Skill table
    cursor.execute("SELECT Skill_ID, Name FROM Skill ORDER BY Name ASC")
    skills = cursor.fetchall()  # List of (ID, Name)

    if request.method == 'POST':
        selected_skills = request.form.getlist('skills')  # List of selected skill IDs

        try:
            selected_skills = [int(skill_id) for skill_id in selected_skills]  # Convert to integers
        except ValueError:
            flash("Invalid skill selection!", "danger")
            return redirect(url_for('add_skills'))

        # Insert selected skills into CandidateSkills table
        if selected_skills:
            sql = "INSERT IGNORE INTO candiskill (Cand_ID, Skill_ID) VALUES (%s, %s)"
            values = [(candidate_id, skill_id) for skill_id in selected_skills]
            cursor.executemany(sql, values)
            conn.commit()

            flash("Skills added successfully!", "success")
            return redirect(url_for('employee_dashboard'))

    cursor.close()
    conn.close()

    return render_template("add_skills.html", skills=skills)




@app.route('/register_employee', methods=['GET', 'POST'])
def register_employee():
    if 'user_id' not in session or session.get('user_type') != "Employee":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        user_id = session['user_id']
        resume = request.form.get('resume')
        email = request.form.get('email')
        status = "Active" 

        sql = "INSERT INTO Employee (ID, Resume, Email, Status) VALUES (%s, %s, %s, %s)"
        values = (user_id, resume, email, status)

        try:
            cursor.execute(sql, values)
            conn.commit()
            flash("Employee profile completed! You can now log in.", "success")
            return redirect(url_for('login'))
        except mysql.Error as err:
            flash(f"Database error: {err}", "danger")

        cursor.close()
        conn.close()

    return render_template("register_employee.html")




#@app.route('/login', methods=['POST'])

"""@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")  # Show the login page

    conn = get_db_connection()
    cursor = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        # Fetch user details
        cursor.execute("SELECT ID, UserType FROM User WHERE Username = %s AND Password = %s", (username, password))
        user = cursor.fetchone()

        if not user:  # If user does not exist
            flash("Invalid username or password.", "danger")
            return redirect(url_for('login'))

        user_id, user_type = user
        session['username'] = username
        session['user_type'] = user_type
        session['user_id'] = user_id  # Store user ID in session

        # Redirect based on user type
        if user_type == "Employer":
            flash("Login successful!", "success")
            return redirect(url_for('employer_dashboard'))

        elif user_type == "Employee":
            flash("Login successful!", "success")
            return redirect(url_for('employee_dashboard'))

        flash("Unauthorized user type.", "danger")
        return redirect(url_for('login'))

    finally:
        cursor.close()
        conn.close()  


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("admin_login.html")  # Admin login page

    admin_username = request.form.get('admin_username')
    admin_password = request.form.get('admin_password')

    # Hardcoded admin credentials (Replace with database lookup if needed)
    ADMIN_CREDENTIALS = {
        "admin": "securepassword123"
    }

    if admin_username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[admin_username] == admin_password:
        session['admin'] = admin_username  # Store admin session
        flash("Admin login successful!", "success")
        return redirect(url_for('admin_dashboard'))

    flash("Invalid admin credentials!", "danger")
    return redirect(url_for('admin_login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('admin_login'))

    return render_template("admin_dashboard.html")  # Create this page"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")  # Show login page

    conn = get_db_connection()
    cursor = conn.cursor()

    username = request.form.get('username')
    password = request.form.get('password')

    try:
        # Fetch user details
        cursor.execute("SELECT ID, UserType, Password FROM User WHERE Username = %s", (username,))
        user = cursor.fetchone()

        if not user or user[2]!=password:  # Verify password hash
            flash("Invalid username or password.", "danger")
            return redirect(url_for('login'))

        user_id, user_type = user[:2]
        session['username'] = username
        session['user_type'] = user_type
        session['user_id'] = user_id  # Store user ID in session

        # Redirect based on user type
        if user_type == "Employer":
            flash("Login successful!", "success")
            return redirect(url_for('employer_dashboard'))
        elif user_type == "Employee":
            flash("Login successful!", "success")
            return redirect(url_for('employee_dashboard'))

        flash("Unauthorized user type.", "danger")
        return redirect(url_for('login'))

    finally:
        cursor.close()
        conn.close()

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("admin_login.html")

    admin_username = request.form.get('admin_username')
    admin_password = request.form.get('admin_password')

    # Set credentials (Hardcoded for now, use env variables in production)
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "securepassword123"

    if admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD:
        session['username'] = admin_username
        session['user_type'] = "admin"
        flash("Admin login successful!", "success")
        return redirect(url_for('admin_dashboard'))

    flash("Invalid admin credentials!", "danger")
    return redirect(url_for('admin_login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    
    if 'username' not in session or session.get('user_type') != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('admin_login'))

    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get total number of users
    cursor.execute("SELECT COUNT(*) FROM User")
    total_users = cursor.fetchone()[0]

    # Get total recruiters
    cursor.execute("SELECT COUNT(*) FROM User WHERE UserType = 'Recruiter'")
    total_recruiters = cursor.fetchone()[0]

    # Get total candidates
    cursor.execute("SELECT COUNT(*) FROM User WHERE UserType = 'Employee'")
    total_candidates = cursor.fetchone()[0]

    # Get total jobs posted
    cursor.execute("SELECT COUNT(*) FROM Job")
    total_jobs = cursor.fetchone()[0]

    # Get total open jobs
    cursor.execute("SELECT COUNT(*) FROM Job WHERE Status = 'Open'")
    open_jobs = cursor.fetchone()[0]

    # Get total applications
    cursor.execute("SELECT COUNT(*) FROM Application")
    total_applications = cursor.fetchone()[0]

    # Get scheduled interviews
    cursor.execute("SELECT COUNT(*) FROM Interview WHERE Status = 'Scheduled'")
    scheduled_interviews = cursor.fetchone()[0]

    # Get recent complaints (last 5 complaints)
    cursor.execute("SELECT Description FROM Complaint ORDER BY Complaint_ID DESC LIMIT 5")
    recent_complaints = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_recruiters=total_recruiters,
                           total_candidates=total_candidates,
                           total_jobs=total_jobs,
                           open_jobs=open_jobs,
                           total_applications=total_applications,
                           scheduled_interviews=scheduled_interviews,
                           recent_complaints=recent_complaints)



@app.route('/employer_dashboard')
def employer_dashboard():
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    return render_template("employer_dashboard.html")


@app.route('/view_applicants')
def view_applicants():
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    emp_id = session.get('emp_id')

    # Fetch candidates who applied to the employer’s jobs
    cursor.execute("""
        SELECT U.Name, E.Email, E.resume 
        FROM User U
        JOIN Employee E ON U.ID = E.ID
        JOIN Application A ON E.ID = A.User_ID
        JOIN Job J ON A.Job_ID = J.Job_ID
        WHERE J.Emp_ID = %s
    """, (emp_id,))
    
    candidates = cursor.fetchall()

    if not candidates:
        flash("No applicants yet!", "warning")
        return render_template("view_applicants.html", candidates=[])

    cursor.close()
    conn.close()

    return render_template("view_applicants.html", candidates=candidates)


@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if 'username' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')  # Get logged-in user's ID
    user_type = session.get('user_type')  # Get whether Employer or Employee
    description = request.form.get('description')

    if not description:
        flash("Complaint description cannot be empty!", "warning")
        return redirect(url_for('dashboard'))  # Redirect to respective dashboard

    # Insert the complaint into the Complaint table
    cursor.execute(
        "INSERT INTO Complaint (Complainer_ID, Description) VALUES (%s, %s)", 
        (user_id, description)
    )
    conn.commit()

    flash("Complaint submitted successfully!", "success")

    # Redirect user back to their respective dashboard
    if user_type == "Employer":
        return redirect(url_for('employer_dashboard'))
    elif user_type == "Employee":
        return redirect(url_for('employee_dashboard'))
    else:
        return redirect(url_for('login'))  # Fallback case




@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all skills from the Skill table for the dropdown
    cursor.execute("SELECT skill_ID, Name FROM Skill ORDER BY Name ASC")
    skills = cursor.fetchall()  # List of (ID, Name)

    if request.method == 'POST':
        emp_id = session.get('emp_id')
        salary = request.form.get('salary')
        description = request.form.get('description')
        locations = request.form.get('locations')
        job_type = request.form.get('job_type')
        selected_skills = request.form.getlist('skills')  # List of skill IDs from the form

        if not salary or not salary.replace('.', '', 1).isdigit():
            flash("Invalid salary input!", "danger")
            return render_template("post_job.html", skills=skills)
        try:
            selected_skills = [int(skill_id) for skill_id in selected_skills]  # Convert to integers
        except ValueError:
            flash("Invalid skill selection!", "danger")
            return redirect(url_for('post_job'))


        # Insert the new job into the Job table
        sql_job = """INSERT INTO Job (Emp_ID, Salary, Description, Locations, Type, TimeOfPosting, No_Apps, Status)
                     VALUES (%s, %s, %s, %s, %s, NOW(), 0, 'Open')"""
        values_job = (emp_id, salary, description, locations, job_type)

        try:
            cursor.execute(sql_job, values_job)
            job_id = cursor.lastrowid  # Get the last inserted job ID

            # Insert selected skills into JobQuali
            if selected_skills:
                sql_jobquali = "INSERT INTO JobQuali (Job_ID, Skill_ID) VALUES (%s, %s)"
                values_jobquali = [(job_id, skill_id) for skill_id in selected_skills]
                cursor.executemany(sql_jobquali, values_jobquali)

            conn.commit()
            flash("Job posted successfully!", "success")
            return redirect(url_for('employer_dashboard'))

        except mysql.Error as err:
            conn.rollback()  # Rollback on failure
            flash(f"Database error: {err}", "danger")

    cursor.close()
    conn.close()

    return render_template("post_job.html", skills=skills)


@app.route('/search_skills', methods=['GET'])
def search_skills():
    query = request.args.get('query', '').strip()

    if not query:  # Prevent unnecessary queries
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ID, Name FROM Skill WHERE Name LIKE %s LIMIT 10", ('%' + query + '%',))
    skills = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return jsonify(skills)

@app.route('/apply_job/<int:job_id>')
def apply_job(job_id):
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    candidate_id = session.get('candidate_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user already applied
    cursor.execute("SELECT * FROM Application WHERE User_ID = %s AND Job_ID = %s", (candidate_id, job_id))
    if cursor.fetchone():
        flash("You have already applied for this job.", "warning")
    else:
        # Insert application with default status 'Applied'
        cursor.execute("INSERT INTO Application (User_ID, Job_ID, Status) VALUES (%s, %s, 'Applied')", (candidate_id, job_id))
        conn.commit()
        flash("Applied successfully!", "success")

    cursor.close()
    conn.close()

    return redirect(url_for('view_jobs'))




@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Unauthorized access! Please log in.", "danger")
        return redirect(url_for('index'))
    
    user_type = session.get('user_type')
    
    if user_type == "Employer":
        return redirect(url_for('employer_dashboard'))
    elif user_type == "Employee":
        return redirect(url_for('employee_dashboard'))
    
    flash("Unauthorized access!", "danger")
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash("Logged out successfully!", "info")
    return redirect(url_for('index'))  # Redirect to login page

if __name__ == '__main__':
    app.run(debug=True)
