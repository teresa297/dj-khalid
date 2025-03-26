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
    cursor.execute("SELECT Complaint_ID, Description, Status FROM Complaint ORDER BY Complaint_ID DESC LIMIT 5")
    recent_complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_dashboard.html", 
                            total_users=total_users, 
                            total_recruiters=total_recruiters, 
                            total_candidates=total_candidates, 
                            total_jobs=total_jobs, 
                            open_jobs=open_jobs, 
                            total_applications=total_applications, 
                            scheduled_interviews=scheduled_interviews,
                            recent_complaints=recent_complaints)


@app.route('/view_users')
def view_users():
    if 'username' not in session or session.get('user_type') != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ID, Username, UserType FROM User")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("view_users.html", users=users)

@app.route('/view_applicant_details/<int:cand_id>')
def view_applicant_details(cand_id):
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    cursor.execute("""
        SELECT U.ID, U.Name, U.Username, E.Email, E.resume, 
               GROUP_CONCAT(DISTINCT S.Name SEPARATOR ', ') AS Skills, 
               GROUP_CONCAT(DISTINCT A.Job_ID SEPARATOR ', ') AS Job_IDs,
               GROUP_CONCAT(DISTINCT J.Title SEPARATOR ', ') AS Job_Titles
        FROM User U
        JOIN Employee E ON U.ID = E.ID
        JOIN Application A ON E.ID = A.User_ID
        JOIN Job J ON A.Job_ID = J.Job_ID
        LEFT JOIN CandiSkill CS ON E.ID = CS.Cand_ID
        LEFT JOIN Skill S ON CS.Skill_ID = S.skill_ID
        WHERE U.ID = %s
        GROUP BY U.ID;
    """, (cand_id,))

    applicant = cursor.fetchone()

    cursor.close()
    conn.close()

    if not applicant:
        flash("Applicant not found.", "warning")
        return redirect(url_for('view_applicants'))

    # Convert comma-separated strings to lists
    job_ids = applicant[6].split(', ') if applicant[6] else []
    job_titles = applicant[7].split(', ') if applicant[7] else []

    return render_template("view_applicant_details.html", applicant=applicant, job_ids=job_ids, job_titles=job_titles, zip=zip)


@app.route('/view_scheduled_interviews')
def view_scheduled_interviews():
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    user_id = session.get('user_id')  # Assuming user ID is stored in session

    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    cursor.execute("""
        SELECT J.Title, I.Time, I.Mode, I.Status 
        FROM Interview I
        JOIN Job J ON I.Job_ID = J.Job_ID
        WHERE I.User_ID = %s
        ORDER BY I.Time ASC;
    """, (user_id,))

    interviews = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("view_scheduled_interviews.html", interviews=interviews)



@app.route('/schedule_interview/<int:cand_id>/<int:job_id>', methods=['GET', 'POST'])
def schedule_interview(cand_id, job_id):
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))
    
    print(f"Schedule Interview triggered for Candidate ID: {cand_id}, Job ID: {job_id}")

    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)  # Use buffered cursor to avoid unread results error

    # Check if an interview already exists
    cursor.execute("""
        SELECT COUNT(*) FROM Interview 
        WHERE User_ID = %s AND Job_ID = %s
    """, (cand_id, job_id))
    
    existing_interview = cursor.fetchone()  # Fetch result properly
    if existing_interview and existing_interview[0] > 0:
        flash("Interview already scheduled for this candidate and job.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for('view_applicant_details', cand_id=cand_id))

    if request.method == 'POST':
        interview_time = request.form.get('time')
        interview_mode = request.form.get('mode')

        if not interview_time or not interview_mode:
            flash("Please select a valid date, time, and mode.", "danger")
        else:
            cursor.execute("""
                INSERT INTO Interview (User_ID, Job_ID, Time, Mode, Status) 
                VALUES (%s, %s, %s, %s, 'Scheduled')
            """, (cand_id, job_id, interview_time, interview_mode))

            conn.commit()
            flash("Interview scheduled successfully!", "success")

        cursor.close()
        conn.close()

        return redirect(url_for('view_applicant_details', cand_id=cand_id))

    cursor.close()
    conn.close()

    return render_template("schedule_interview.html", cand_id=cand_id, job_id=job_id)





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

    emp_id = session.get('user_id')

    # Fetch only jobs that have at least one applicant
    cursor.execute("""
        SELECT J.job_id AS job_id, J.title AS job_title, U.ID AS cand_id, U.Name AS cand_name
        FROM Job J
        JOIN Application A ON J.Job_ID = A.Job_ID
        JOIN Employee E ON A.User_ID = E.ID
        JOIN User U ON E.ID = U.ID
        WHERE J.Emp_ID = %s
        ORDER BY J.title, U.Name;
    """, (emp_id,))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    print("Fetched Results:", results)  

    # Grouping candidates by job
    jobs_with_candidates = {}
    for job_id, job_title, cand_id, cand_name in results:
        if job_id not in jobs_with_candidates:
            jobs_with_candidates[job_id] = {
                'title': job_title,
                'candidates': []
            }
        jobs_with_candidates[job_id]['candidates'].append({'id': cand_id, 'name': cand_name})

    return render_template("view_applicants.html", jobs=jobs_with_candidates)


@app.route('/submit_complaint', methods=['GET', 'POST'])
def submit_complaint():
    if 'username' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':  # Handling form submission
        description = request.form.get('description')
        if not description.strip():
            flash("Complaint description cannot be empty!", "warning")
        else:
            cursor.execute("INSERT INTO Complaint (Complainer_ID, Description, Status) VALUES (%s, %s, %s)",
                           (user_id, description, "Pending"))
            conn.commit()
            flash("Complaint submitted successfully!", "success")

    # Fetch user's complaints for display
    cursor.execute("SELECT Complaint_ID, Description, Status FROM Complaint WHERE Complainer_ID = %s", (user_id,))
    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("submit_complaint.html", complaints=complaints)



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
        emp_id = session.get('user_id')
        salary = request.form.get('salary')
        description = request.form.get('description')
        locations = request.form.get('locations')
        title = request.form.get('title')
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
        sql_job = """INSERT INTO Job (Emp_ID, Salary, Description, Locations,Title, Type, TimeOfPosting, No_Apps, Status)
                     VALUES (%s, %s, %s, %s, %s, NOW(), 0, 'Open')"""
        values_job = (emp_id, salary, description, locations,title, job_type)

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


@app.route('/view_jobs', methods=['GET'])
def view_jobs():
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    sort_by = request.args.get('sort_by', 'date')  # Default sorting by date posted

    conn = get_db_connection()
    cursor = conn.cursor()

    # Sorting logic with FIXED SQL syntax
    if sort_by == 'salary':
        cursor.execute("""
            SELECT j.Job_ID, j.Title, j.Description, j.Type, j.Salary, u.Name AS Employer
            FROM Job j
            JOIN Employer e ON j.Emp_ID = e.ID
            JOIN User u ON e.ID = u.ID
            ORDER BY j.Salary DESC
        """)
    elif sort_by == 'title':
        cursor.execute("""
            SELECT j.Job_ID, j.Title, j.Description, j.Type, j.Salary, u.Name AS Employer
            FROM Job j
            JOIN Employer e ON j.Emp_ID = e.ID
            JOIN User u ON e.ID = u.ID
            ORDER BY j.Title ASC
        """)
    else:  # Default: Sort by newest jobs first
        cursor.execute("""
            SELECT j.Job_ID, j.Title, j.Description, j.Type, j.Salary,  u.Name AS Employer
            FROM Job j
            JOIN Employer e ON j.Emp_ID = e.ID
            JOIN User u ON e.ID = u.ID
            ORDER BY j.TimeOfPosting DESC
        """)

    jobs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view_jobs.html', jobs=jobs, sort_by=sort_by)




@app.route('/matching_jobs', methods=['GET'])
def matching_jobs():
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch jobs matching all employee's skills
    cursor.execute("""
        SELECT j.Job_ID, j.Description, j.Type, u.Name AS Employer
        FROM Job j
        JOIN Employer e ON j.Emp_ID = e.ID
        JOIN User u ON e.ID = u.ID
        JOIN JobQuali jq ON j.Job_ID = jq.Job_ID
        WHERE jq.Skill_ID IN (
            SELECT cs.Skill_ID
            FROM CandiSkill cs
            WHERE cs.Cand_ID = %s
        )
        GROUP BY j.Job_ID
        HAVING COUNT(DISTINCT jq.Skill_ID) = (
            SELECT COUNT(DISTINCT cs.Skill_ID)
            FROM CandiSkill cs
            WHERE cs.Cand_ID = %s
        );
    """, (user_id, user_id))
    perfect_match_jobs = cursor.fetchall()

    # Fetch jobs matching at least one skill
    cursor.execute("""
        SELECT DISTINCT j.Job_ID, j.Description, j.Type, u.Name AS Employer
        FROM Job j
        JOIN Employer e ON j.Emp_ID = e.ID
        JOIN User u ON e.ID = u.ID
        JOIN JobQuali jq ON j.Job_ID = jq.Job_ID
        WHERE jq.Skill_ID IN (
            SELECT cs.Skill_ID
            FROM CandiSkill cs
            WHERE cs.Cand_ID = %s
        );
    """, (user_id,))
    partial_match_jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('matching_jobs.html',
                           perfect_match_jobs=perfect_match_jobs,
                           partial_match_jobs=partial_match_jobs)







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

@app.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    if 'username' not in session or session.get('user_type') != 'Employee':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Debugging step
    if not user_id:
        flash("Error: User ID not found in session.", "danger")
        return redirect(url_for('view_jobs'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user has already applied for this job
    cursor.execute("SELECT * FROM Application WHERE User_ID = %s AND Job_ID = %s", (user_id, job_id))
    existing_application = cursor.fetchone()

    if existing_application:
        flash("You have already applied for this job!", "warning")
    else:
        cursor.execute("INSERT INTO Application (User_ID, Job_ID, Status) VALUES (%s, %s, 'Applied')", (user_id, job_id))
        conn.commit()
        flash("Application submitted successfully!", "success")

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


@app.route('/admin/complaints', methods=['GET', 'POST'])
def view_complaints():
    if 'username' not in session or session.get('user_type') != 'admin':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # If form is submitted, update complaint status
    if request.method == 'POST':
        complaint_id = request.form.get('complaint_id')
        new_status = request.form.get('status')

        if complaint_id and new_status:
            cursor.execute("UPDATE Complaint SET Status = %s WHERE Complaint_ID = %s", (new_status, complaint_id))
            conn.commit()
            flash("Complaint status updated successfully!", "success")

    # Fetch all complaints with user details
    cursor.execute("""
        SELECT c.Complaint_ID, u.ID, u.UserType, u.Name, c.Description, c.Status 
        FROM Complaint c 
        JOIN User u ON c.complainer_ID = u.ID
        ORDER BY c.Status DESC, c.Complaint_ID DESC
    """)
    complaints = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_complaints.html', complaints=complaints)


@app.route('/employer/interviews', methods=['GET', 'POST'])
def view_interviews():
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    employer_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # If the employer submits an update to interview status
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        job_id = request.form.get('job_id')
        new_status = request.form.get('status')

        cursor.execute("""
            UPDATE Interview 
            SET Status = %s 
            WHERE User_ID = %s AND Job_ID = %s
        """, (new_status, user_id, job_id))
        
        conn.commit()
        flash("Interview status updated successfully!", "success")

    # Fetch all scheduled interviews for this employer
    cursor.execute("""
        SELECT i.User_ID, u.Name, j.Job_ID, j.Title, i.Time, i.Mode, i.Status
        FROM Interview i
        JOIN User u ON i.User_ID = u.ID
        JOIN Job j ON i.Job_ID = j.Job_ID
        WHERE j.Emp_ID = %s
        ORDER BY i.Time ASC
    """, (employer_id,))
    
    interviews = cursor.fetchall()

    # Fetch all job postings by the employer
    cursor.execute("SELECT Job_ID, Title, Status FROM Job WHERE Emp_ID = %s", (employer_id,))
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('employer_interviews.html', interviews=interviews, jobs=jobs)



@app.route('/close_job/<int:job_id>', methods=['POST'])
def close_job(job_id):
    if 'username' not in session or session.get('user_type') != 'Employer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update job status to 'Closed'
    cursor.execute("UPDATE Jobs SET Status = 'Closed' WHERE Job_ID = %s", (job_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Job closed successfully!", "success")
    return redirect(url_for('view_interviews'))

