
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__, template_folder="templates")
app.secret_key = 'your_secret_key'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Cs@1512005',
    'database': 'tneaa',
    'auth_plugin': 'mysql_native_password'
}

# Define the database connection function
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin:
            return redirect(url_for('admindashboard'))
        else:
            error = 'Invalid email or password'
    return render_template('admin_login.html', error=error)

@app.route('/admindashboard')
def admindashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM colleges")
    colleges = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admindashboard.html', colleges=colleges)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        phone = request.form['phone']
        aadhaar = request.form['aadhaar']
        address = request.form['address']
        state = request.form['state']
        district = request.form['district']
        pincode = request.form['pincode']
        school_12th = request.form['school_12th']
        board_12th = request.form['board_12th']
        marks_math = request.form['marks_math']
        marks_physics = request.form['marks_physics']
        marks_chemistry = request.form['marks_chemistry']
        cutoff = request.form.get('cutoff', '').strip()  # Get value safely
        cutoff = float(cutoff) if cutoff else None  # Convert to float if available
        community = request.form['community']
        tamil_medium = request.form.get('tamil_medium', 'No')
        first_graduate = request.form.get('first_graduate', 'No')
        marks = request.form['marks']

        conn = get_db_connection()
        cursor = conn.cursor()

        # FIX: Make sure placeholders match the number of parameters
        sql_query = '''INSERT INTO student 
                       (name, dob, gender, email, phone, aadhaar, address, state, district, pincode,
                        school_12th, board_12th, marks_math, marks_physics, marks_chemistry, cutoff, 
                        community, tamil_medium, first_graduate, marks)
                       VALUES 
                       (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        
        values = (name, dob, gender, email, phone, aadhaar, address, state, district, pincode,
                  school_12th, board_12th, marks_math, marks_physics, marks_chemistry, cutoff, 
                  community, tamil_medium, first_graduate, marks)

        cursor.execute(sql_query, values)
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('register_success'))
    
    return render_template('register.html')


@app.route('/registersuccess')
def register_success():
    return render_template('registersuccess.html')

@app.route('/add')
def add():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM colleges")
    colleges = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('manage.html', colleges=colleges)

@app.route('/add_college', methods=['POST'])
def add_college():
    collegename = request.form.get('collegename')
    affiliation = request.form.get('affiliation')
    location = request.form.get('location')
    branch = request.form.get('branch')
    seats = int(request.form.get('seats', 0))
    cutoff = float(request.form.get('cutoff', 0))
    tnea_code = int(request.form.get('tnea_code', 0))

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """INSERT INTO colleges (collegename, affiliation, location, branch, seats, cutoff, tnea_code) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (collegename, affiliation, location, branch, seats, cutoff, tnea_code))
    conn.commit()
    cursor.close()
    conn.close()

    flash("College added successfully!", "success")
    return redirect(url_for('add'))

@app.route('/edit_college/<int:c_id>', methods=['GET', 'POST'])
def edit_college(c_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM colleges WHERE c_id = %s", (c_id,))
    college = cursor.fetchone()

    if not college:
        flash('College not found!', 'error')
        return redirect(url_for('add'))

    if request.method == 'POST':
        collegename = request.form['collegename']
        affiliation = request.form['affiliation']
        location = request.form['location']
        branch = request.form['branch']
        seats = int(request.form['seats'])
        cutoff = float(request.form['cutoff'])
        tnea_code = int(request.form['tnea_code'])

        cursor.execute('''
            UPDATE colleges
            SET collegename = %s, affiliation = %s, location = %s, branch = %s,
                seats = %s, cutoff = %s, tnea_code = %s
            WHERE c_id = %s
        ''', (collegename, affiliation, location, branch, seats, cutoff, tnea_code, c_id))

        conn.commit()
        flash('College updated successfully!', 'success')
        return redirect(url_for('add'))

    cursor.close()
    conn.close()
    return render_template('edit_college.html', college=college)

@app.route('/delete_college/<int:c_id>', methods=['GET'])
def delete_college(c_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM colleges WHERE c_id = %s", (c_id,))
    conn.commit()

    cursor.close()
    conn.close()
    flash("College deleted successfully!", "success")
    return redirect(url_for('add'))


@app.route('/college_list')
def college_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM colleges")
    colleges = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('college_list.html', colleges=colleges)
@app.route('/login', methods=['GET', 'POST'])
def u_login():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Ensure dictionary mode
        cursor.execute("SELECT id FROM student WHERE name = %s AND dob = %s AND email = %s", (name, dob, email))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['student_id'] = user['id']  # Store student ID in session
            print("Session Data:", session)  # Debugging
            return redirect('/result')
        else:
            return "Invalid login credentials!"  # Can replace with flash messages

    return render_template('login.html')
@app.route('/result')
def show_result():
    if 'student_id' not in session:
        return redirect(url_for('u_login'))  # Redirect if not logged in

    student_id = session['student_id']  # Get logged-in student ID
    conn = get_db_connection()
    cursor =  conn.cursor(dictionary=True)

    try:
        # Fetch the student's name, cutoff, and counseling round
        cursor.execute("SELECT name, cutoff, counseling_round FROM student WHERE id = %s", (student_id,))
        student = cursor.fetchone()

        if not student:
            return "Student not found!", 404  # If student does not exist

        # Check if the student is eligible for counseling round 1
        if student['counseling_round'] != 2:
            return redirect(url_for('not_in_round'))  # Restrict access

        # Fetch eligible colleges based on cutoff
        cursor.execute("SELECT * FROM colleges WHERE cutoff <= %s", (student['cutoff'],))
        colleges = cursor.fetchall()

        return render_template('result.html', student=student, colleges=colleges)

    finally:
        cursor.close()
        conn.close()  # Ensure database connection is closed


@app.route('/not_in_round')
def not_in_round():
    return render_template('second.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/student_dashboard')
def student_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all student details
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student.html', students=students)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/announce_results', methods=['POST'])
def submit_choices():
    student_name = request.form['studentName']
    dob = request.form['dob']
    round_number = request.form['round_number']
    choice1 = request.form['choice1']
    choice2 = request.form['choice2']

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO choices (student_name, dob, round_number, choice1, choice2) VALUES (%s, %s, %s, %s, %s)"
    values = (student_name, dob, round_number, choice1, choice2)
    cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()

    return "Choices Submitted Successfully!"




if __name__ == '__main__':
    app.run(debug=True)
