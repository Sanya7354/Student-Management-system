from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector, os
import hashlib

conn=mysql.connector.connect(host='localhost', user='user', passwd='passwd', database='project')
cur=conn.cursor()
d1={'roll_no' : "Roll No.", "username":"Username", "first_name" : "First Name", "middle_name" : "Middle Name", 'last_name' : 'Last Name', 'mobile_no' : "Mobile No.", 'address' : "Address", 'email' : "Email", 'department_name' : "Department Name", 'faculty_id': "Faculty Id"}

app=Flask('__name__')
app.secret_key=os.urandom(64)

@app.before_request
def make_session_permanent():
    session.permanent = False

@app.route('/', methods=['GET', 'POST'])
def main():
	msg=request.args.get('msg')
	if(session.get('username') is not None):
		if(session['type']==1):
			return render_template('base.html', type=1, name=session['name'], message=msg)
		if(session['type']==2):
			return render_template('base.html', type=2, name=session['name'], message=msg)
		if(session['type']==3):
			return render_template('base.html', type=3, name=session['name'], message=msg)
	return render_template('login.html', error=0)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if(request.method=='POST'):
		l=[request.form['username'], hashlib.sha256(request.form['password'].encode()).hexdigest()]
		query="SELECT * FROM user_group WHERE username=%s AND password=%s"
		cur.execute(query, l)
		x=cur.fetchone()
		if(x==None):
			return render_template('login.html', error="!!! Invalid Username or Password !!!")
		else:
			session['username']=request.form['username']
			session['type']=x[-1]
			session['name']=x[0]+' '+x[1]+' '+x[2]
			session['mobile_no']=x[3]
			session['address']=x[4]
			session['email']=x[5]
			if(session['type']==1):
				cur.execute("SELECT roll_no FROM student where username=%s", [session['username']])
				session['rollno']=cur.fetchone()[0]
			elif(session['type']==2):
				cur.execute("SELECT faculty_id FROM faculty where username=%s", [session['username']])
				session['id']=cur.fetchone()[0]
			return redirect(url_for('main'))
	else:
		return redirect(url_for('main'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	d={}
	a=(session['username'],)
	if(session['type']==1):
		d['type']=1;
		cur.callproc('profile_student', a)
	elif(session['type']==2):
		d['type']=2;
		cur.callproc('profile_faculty', a)
	else:
		d['type']=3;
		cur.callproc('profile_admin', a)
	x=list(cur.stored_results())[0].fetchone()
	y=list(cur.stored_results())[0].column_names
	if(session['type']==1):
		session['rollno']=x[7]
	for i in range(len(x)):
		if(y[i]!='dep_id'):
			d[d1[y[i]]]=x[i]
	return render_template('profile.html', dict=d, type=session['type'], name=session['name'])

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	session.clear()
	return redirect(url_for('login'))

@app.route('/coursesel', methods=['GET'])
def attendance_course():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']==1):
		query="SELECT DISTINCT course_code FROM course_register WHERE roll_no=%s";
		cur.execute(query, [session['rollno']])
		x=cur.fetchall()
		return render_template('coursesel.html', lst=x, hrf='/attendance', type=session['type'], name=session['name'])
	elif(session['type']==2):
		query="SELECT DISTINCT course_code FROM courses WHERE instructor_id=%s"
		cur.execute(query, [session['id']])
		x=cur.fetchall()
		return render_template('coursesel.html', lst=x, hrf='/attendance', type=session['type'], name=session['name'])
	else:
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])

@app.route('/attendance', methods=['POST'])
def attendance():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(request.form.get('course') is None):
		return redirect(url_for('attendance_course'))
	try:
		c=request.form['course']
	except KeyError:
		return redirect(url_for('attendance_course'))
	if(session['type']==1):
		cur=conn.cursor()
		query="SELECT att_date, attended FROM attendance WHERE roll_no=%s AND course_code=%s"
		cur.execute(query, [session['rollno'], c])
		return render_template('attendance_student.html', lst=cur, type=session['type'], name=session['name'])
	elif(session['type']==2):
		query="select att_date, roll_no, attended from attendance where course_code=%s"
		cur=conn.cursor()
		l1=[]
		l2=[]
		d={}
		cur.execute(query, [c])
		for i in cur:
			l1.append(i[0].strftime("%d-%m-%Y"))
			l2.append(i[1])
			d[(i[0].strftime("%d-%m-%Y"), i[1])]=i[2]
		l1=list(set(l1))
		l2=list(set(l2))
		return render_template('attendance_faculty.html', dict=d, c=l2, r=l1, type=session['type'], name=session['name'])
	else:
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])

@app.route('/coursesel_grades', methods=['GET'])
def grades_course():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	cur=conn.cursor()
	if(session['type']==1):
		return redirect(url_for('grades'))
	elif(session['type']==2):
		query="SELECT DISTINCT course_code FROM courses WHERE instructor_id=%s"
		cur.execute(query, [session['id']])
		x=cur.fetchall()
		return render_template('coursesel_grades.html', lst=x, type=session['type'], name=session['name'])
	else:
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])

@app.route('/grades', methods=['POST', 'GET'])
def grades():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	cur=conn.cursor()
	if(session['type']==1):
		query='SELECT course_code, midsem_marks, endsem_marks, quiz_marks, total_marks, grade, gpa FROM grades where roll_no=%s'
		cur.execute(query, [session['rollno']])
		return render_template('grades_student.html', dict=cur, type=session['type'], name=session['name'])
	elif(session['type']==2):
		if(request.method=='GET'):
			return redirect(url_for('grades_course'))
		if(request.form.get('course') is None):
			return redirect(url_for('grades_course'))
		c=request.form['course']
		query='SELECT roll_no, midsem_marks, endsem_marks, quiz_marks, total_marks, grade, gpa FROM grades where course_code=%s'
		cur.execute(query, [c])
		return render_template('grades_faculty.html', dict=cur, type=session['type'], name=session['name'])
	else:
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])

@app.route('/coursendate', methods=['GET', 'POST'])
def coursendate():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="select course_code from courses where instructor_id=%s"
	cur.execute(query, [session['id']])
	x=cur.fetchall()
	y=[]
	for i in x:
		y.append(i[0])
	return render_template('coursendate.html', lst=y, type=session['type'], name=session['name'])


@app.route('/addattendance', methods=['POST', 'GET'])
def addattendance():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		return redirect(url_for('coursendate'))
	session['course']=request.form['course']
	session['date']=request.form['date']
	cur=conn.cursor()
	query="select count(*) from attendance where course_code=%s and att_date=%s"
	cur.execute(query, [session['course'], session['date']])
	if(cur.fetchone()[0]!=0):
		return redirect(url_for('editattendance'))
	query="select roll_no from course_register where course_code=%s"
	cur.execute(query, [session['course']])
	x=[]
	for i in cur:
		x.append(i[0])
	return render_template('addattendance.html', lst=x, dt=request.form['date'], type=session['type'], name=session['name'])

@app.route('/addattendance2', methods=['POST', 'GET'])	
def addattendance2():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		return redirect(url_for('coursendate'))
	for i in request.form:
		query="insert into attendance values(%s, %s, %s, %s)"
		cur.execute(query, [i, session['course'], session['date'], request.form[i]])
	conn.commit()
	del session['date']
	del session['course']
	return redirect(url_for('main', msg="Attendance added Successfully"))

@app.route('/editattendance', methods=['POST', 'GET'])
def editattendance():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		query="select roll_no, attended from attendance where course_code=%s and att_date=%s"
		cur=conn.cursor()
		cur.execute(query, [session['course'], session['date']])
		x=cur.fetchall()
		return render_template('editattendance.html', lst=x, type=session['type'], name=session['name'])
	else:
		cur=conn.cursor()
		for i in request.form:
			query="update attendance set attended=%s where roll_no=%s and course_code=%s and att_date=%s"
			cur.execute(query, [request.form[i], i, session['course'], session['date']])
		conn.commit()
		return redirect(url_for('main', msg="Attendance updated Successfully"))

@app.route('/course_addgrades', methods=['POST', 'GET'])
def course_addgrades():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	query="SELECT DISTINCT course_code FROM courses WHERE instructor_id=%s"
	cur.execute(query, [session['id']])
	x=cur.fetchall()
	return render_template('coursesel.html', lst=x, hrf='/addgrades', type=session['type'], name=session['name'])
 
@app.route('/addgrades', methods=['POST', 'GET'])
def addgrades():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	try:
		c=request.form['course']
	except KeyError:
		return redirect(url_for("course_addgrades"))
	query="select roll_no, midsem_marks, endsem_marks, quiz_marks, total_marks, grade, gpa from grades where course_code=%s"
	cur=conn.cursor()
	cur.execute(query, [c])
	x=cur.fetchall()
	cur.close()
	return render_template('addgrades.html', lst=x, course=c, type=session['type'], name=session['name'])

@app.route('/addgrades2', methods=['POST', 'GET'])
def addgrades2():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=2):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		return redirect(url_for('course_addgrades'))
	roll=request.form.getlist('rollno')
	mid=request.form.getlist('midsem')
	end=request.form.getlist('endsem')
	quiz=request.form.getlist('quiz')
	course=request.form['course']
	query="update grades set midsem_marks=%s, endsem_marks=%s, quiz_marks=%s where roll_no=%s and course_code=%s"
	cur=conn.cursor()
	for i in range(len(roll)):
		cur.execute(query, [mid[i], end[i], quiz[i], roll[i], course])
	conn.commit()
	return redirect(url_for('main', msg="Grades updated Successfully"))

@app.route('/viewstudent', methods=['GET', 'POST'])
def viewstudent():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=="GET"):
		return render_template('rollno.html', type=session['type'], name=session['name'])
	else:
		d={}
		x=request.form['rollno']
		cur=conn.cursor()
		query="select username from student where roll_no=%s"
		cur.execute(query, [x])
		try:
			a=cur.fetchone()[0]
		except:
			return render_template("rollno.html", error="!!! Invalid Roll No !!!", type=session['type'], name=session['name'])
		cur.callproc('profile_student', (a,))
		x=list(cur.stored_results())[0].fetchone()
		y=list(cur.stored_results())[0].column_names
		for i in range(len(x)):
			if(y[i]!='dep_id'):
				d[d1[y[i]]]=x[i]
		return render_template('profile.html', dict=d, edit=1, delete=1, type=session['type'], name=session['name'])

@app.route('/editstudent', methods=['GET', 'POST'])
def editstudent():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=="GET"):
		return render_template('rollno.html', type=session['type'], name=session['name'])
	else:
		username=request.form['username']
		cur=conn.cursor()
		d={}
		cur.callproc('profile_student', (username, ))
		x=list(cur.stored_results())[0].fetchone()
		y=list(cur.stored_results())[0].column_names
		for i in range(len(x)):
			d[y[i]]=x[i]
		cur.close()
		cur=conn.cursor()
		query="select department_id, department_code from department"
		cur.execute(query)
		x=cur.fetchall()
		return render_template('editstudent.html', dict=d, depts=x, type=session['type'], name=session['name'])

@app.route('/editstudent2', methods=['POST'])
def editstudent2():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	roll_no=request.form['roll_no']
	first_name=request.form['first_name']
	middle_name=request.form['middle_name']
	last_name=request.form['last_name']
	addr=request.form['address']
	mob=request.form['mobile_no']
	depid=request.form['dep_id']
	cur=conn.cursor()
	cur.callproc('update_student', (roll_no, first_name, middle_name, last_name, addr, mob, depid))
	conn.commit()
	cur=conn.cursor()
	query="select username from student where roll_no=%s"
	cur.execute(query, [roll_no])
	a=cur.fetchone()[0]
	d={}
	cur.callproc('profile_student', (a,))
	x=list(cur.stored_results())[0].fetchone()
	y=list(cur.stored_results())[0].column_names
	for i in range(len(x)):
		if(y[i]!='dep_id'):
			d[d1[y[i]]]=x[i]
	return render_template('profile.html', dict=d, edit=1, message="Updated Successfully", type=session['type'], name=session['name'])

@app.route('/addstudent', methods=['POST', 'GET'])
def addstudent():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="select department_id, department_code from department"
	cur.execute(query)
	dep=cur.fetchall()
	cur.close()
	if(request.method=='GET'):
		return render_template('addstudent.html', depts=dep, type=session['type'], name=session['name'])
	username=""
	for i in request.form:
		if(str(i[0])==request.form['dep_id']):
			username=i[1].lower()
	username+=request.form['roll_no']
	x=request.form
	cur=conn.cursor()
	query="insert into user_group values(%s, %s, %s, %s, %s, %s, %s, %s, 1)"
	try:
		cur.execute(query, (x['first_name'], x['middle_name'], x['last_name'], x['mobile_no'], x['address'], x['email'], username, hashlib.sha256(x['password'].encode()).hexdigest()))
		query="insert into student values(%s, %s, %s)"
		cur.execute(query, (x['roll_no'], username, x['dep_id']))
		conn.commit()
	except:
		return render_template('addstudent.html', depts=dep, error="!!! User Already Exists !!!", type=session['type'], name=session['name'])
	d={}
	cur.callproc('profile_student', (username,))
	x=list(cur.stored_results())[0].fetchone()
	y=list(cur.stored_results())[0].column_names
	for i in range(len(x)):
		if(y[i]!='dep_id'):
			d[d1[y[i]]]=x[i]
	return render_template('profile.html', dict=d, edit=1, message="Added Successfully", type=session['type'], name=session['name'])

@app.route('/viewfaculty', methods=['POST', 'GET'])
def viewfaculty():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		return render_template("facultyid.html", type=session['type'], name=session['name'])
	cur=conn.cursor()
	facid=request.form['faculty_id']
	query="select username from faculty where faculty_id=%s"
	cur.execute(query, [facid])
	try:
		usernm=cur.fetchone()[0]
	except:
		return render_template('facultyid.html', error="!!! Invalid Faculty Id !!!", type=session['type'], name=session['name'])
	d={}
	cur.callproc('profile_faculty', (usernm,))
	x=list(cur.stored_results())[0].fetchone()
	y=list(cur.stored_results())[0].column_names
	for i in range(len(x)):
		if(y[i]!='dep_id'):
			d[d1[y[i]]]=x[i]
	return render_template('profile.html', dict=d, edit=2, type=session['type'], name=session['name'])

@app.route('/editfaculty', methods=['POST', 'GET'])
def editfaculty():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=="GET"):
		return redirect(url_for('viewfaculty'))
	if(request.form.get('faculty_id') is None):
		username=request.form['username']
		cur=conn.cursor()
		d={}
		cur.callproc('profile_faculty', (username, ))
		x=list(cur.stored_results())[0].fetchone()
		y=list(cur.stored_results())[0].column_names
		for i in range(len(x)):
			d[y[i]]=x[i]
		cur.close()
		cur=conn.cursor()
		query="select department_id, department_code from department"
		cur.execute(query)
		x=cur.fetchall()
		return render_template('editfaculty.html', dict=d, depts=x, type=session['type'], name=session['name'])
	else:
		facid=request.form['faculty_id']
		first_name=request.form['first_name']
		middle_name=request.form['middle_name']
		last_name=request.form['last_name']
		addr=request.form['address']
		mob=request.form['mobile_no']
		depid=request.form['dep_id']
		cur=conn.cursor()
		cur.callproc('update_faculty', (facid, first_name, middle_name, last_name, addr, mob, depid))
		conn.commit()
		cur=conn.cursor()
		query="select username from faculty where faculty_id=%s"
		cur.execute(query, [facid])
		a=cur.fetchone()[0]
		d={}
		cur.callproc('profile_faculty', (a,))
		x=list(cur.stored_results())[0].fetchone()
		y=list(cur.stored_results())[0].column_names
		for i in range(len(x)):
			if(y[i]!='dep_id'):
				d[d1[y[i]]]=x[i]
		return render_template('profile.html', dict=d, edit=2, message="Updated Successfully", type=session['type'], name=session['name'])

@app.route('/addfaculty', methods=['GET', 'POST'])
def addfaculty():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="select department_id, department_code from department"
	cur.execute(query)
	x=cur.fetchall()
	if(request.method=="GET"):
		return render_template('addfaculty.html', depts=x, type=session['type'], name=session['name'])
	x=request.form
	query="insert into user_group values(%s, %s, %s, %s, %s, %s, %s, %s, 2)"
	try:
		cur.execute(query, (x['first_name'], x['middle_name'], x['last_name'], x['mobile_no'], x['address'], x['email'], x['username'], hashlib.sha256(x['password'].encode()).hexdigest()))
		query="insert into faculty values(%s, %s, %s)"
		cur.execute(query, (x['faculty_id'], x['username'], x['dep_id']))
		conn.commit()
	except:
		return render_template('addfaculty.html', error="!!! User Already Exists !!!", type=session['type'], name=session['name'])
	d={}
	cur.callproc('profile_faculty', (x['username'],))
	x=list(cur.stored_results())[0].fetchone()
	y=list(cur.stored_results())[0].column_names
	for i in range(len(x)):
		if(y[i]!='dep_id'):
			d[d1[y[i]]]=x[i]
	return render_template('profile.html', dict=d, edit=2, message="Added Successfully", type=session['type'], name=session['name'])

@app.route('/addepartment', methods=['GET', 'POST'])
def adddepartment():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=="GET"):
		return render_template('adddepartment.html', type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="insert into department(department_code, department_name) values(%s, %s)"
	cur.execute(query, [request.form['dep_code'], request.form['dep_name']])
	conn.commit()
	return redirect(url_for('viewdepartments'))

@app.route('/viewdepartments', methods=["GET", 'POST'])
def viewdepartments():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="select department_code, department_name from department"
	cur.execute(query)
	return render_template('viewdepartments.html', lst=cur.fetchall(), type=session['type'], name=session['name'])

@app.route("/viewcourses", methods=["GET", 'POST'])
def viewcourses():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	cur=conn.cursor()
	cur.callproc('viewcourses')
	x=list(cur.stored_results())[0].fetchall()
	return render_template('viewcourses.html', lst=x, type=session['type'], name=session['name'])

@app.route("/addcourse", methods=['GET', 'POST'])
def addcourse():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template('not_authorised.html', type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="select CONCAT('Dr. ', first_name, ' ', middle_name, ' ', last_name), faculty_id from faculty inner join user_group on faculty.username=user_group.username"
	cur.execute(query)
	fac=cur.fetchall()
	cur.close()
	if(request.method=='GET'):
		return render_template('addcourse.html', fac=fac, type=session['type'], name=session['name'])
	else:
		x=request.form
		try:
			query="insert into courses values(%s, %s, %s, %s, %s)"
			cur=conn.cursor()
			cur.execute(query, (x['code'], x['name'], x['cred'], x['sem'], x['ins_id']))
			conn.commit()
		except:
			return render_template('addcourse.html', fac=fac, error="!!! Course Already Exists !!!", type=session['type'], name=session['name'])
		cur.close()
		return redirect(url_for('viewcourses'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	cur=conn.cursor()
	query="select course_code from courses"
	cur.execute(query)
	x1=cur.fetchall()
	query="select department_id, department_code from department"
	cur.execute(query)
	y=cur.fetchall()
	if(request.method=='GET'):
		cur.close()
		return render_template('register.html', courses=x1, depts=y, type=session['type'], name=session['name'])
	else:
		cur=conn.cursor()
		query="select roll_no from student where dep_id=%s"
		cur.execute(query, [request.form['dep_id']])
		x=cur.fetchall()
		for i in x:
			try:
				query="insert into course_register values(%s, %s)"
				cur.execute(query, [i[0], request.form['code']])
			except:
				return render_template('register.html', courses=x1, depts=y, error="Already Registered", type=session['type'], name=session['name'])
		conn.commit()
		cur.close()
		return render_template('base.html', message="Registration Successful", type=session['type'], name=session['name'])

@app.route('/delstudent', methods=['GET', 'POST'])
def delstudent():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=="GET"):
		return render_template('rollno.html', type=session['type'], name=session['name'])
	x=request.form['username']
	query="DELETE FROM user_group WHERE username=%s"
	cur=conn.cursor()
	cur.execute(query, [x, ])
	conn.commit()
	return render_template("base.html", message="Student Deleted Successfully", type=session['type'], name=session['name'])

@app.route('/delfaculty', methods=['GET', 'POST'])
def delfaculty():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		return render_template('facultyid.html', type=session['type'], name=session['name'])
	x=request.form['username']
	query="DELETE FROM user_group WHERE username=%s"
	try:
		cur=conn.cursor()
		cur.execute(query, [x, ])
		conn.commit()
	except:
		return render_template('facultyid.html', type=session['type'], name=session['name'], error="!!! Deletion Not Possible !!!")
	return render_template("base.html", message="Faculty Deleted Successfully", type=session['type'], name=session['name'])

@app.route('/delcourse', methods=['GET', 'POST'])
def delcourse():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	if(request.method=='GET'):
		return render_template('coursecode.html', type=session['type'], name=session['name'])
	x=request.form['code']
	query="DELETE FROM courses WHERE course_code=%s"
	cur=conn.cursor()
	cur.execute(query, [x, ])
	conn.commit()
	return render_template("base.html", message="Course Deleted Successfully", type=session['type'], name=session['name'])

@app.route('/allstudent', methods=['GET', 'POST'])
def allstudent():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	query="select department_id, department_code from department"
	cur=conn.cursor()
	cur.execute(query)
	depts=cur.fetchall()
	if(request.method=='GET'):
		return render_template('seldepartment.html',  type=session['type'], name=session['name'], dept=depts, hrf="/allstudent")
	else:
		x=request.form.getlist('dep_id')
		if(x==[]):
			return render_template('seldepartment.html',  type=session['type'], name=session['name'], dept=depts, hrf="/allstudent", error="!!! Select atleast one department !!!")
		cur=conn.cursor()
		lst=[]
		for i in x:
			cur.callproc('allstudent', (i,))
			lst.extend(list(list(cur.stored_results())[0].fetchall()))
		return render_template('allstudent.html', type=session['type'], name=session['name'], lst=lst)

@app.route('/allfaculty', methods=['GET', 'POST'])
def allfaculty():
	if(session.get('username') is None):
		return redirect(url_for('main'))
	if(session['type']!=3):
		return render_template("base.html", error="Action not Permitted", type=session['type'], name=session['name'])
	query="select department_id, department_code from department"
	cur=conn.cursor()
	cur.execute(query)
	depts=cur.fetchall()
	if(request.method=='GET'):
		return render_template('seldepartment.html',  type=session['type'], name=session['name'], dept=depts, hrf="/allfaculty")
	else:
		x=request.form.getlist('dep_id')
		if(x==[]):
			return render_template('seldepartment.html',  type=session['type'], name=session['name'], dept=depts, hrf="/allstudent", error="!!! Select atleast one department !!!")
		cur=conn.cursor()
		lst=[]
		for i in x:
			cur.callproc('allfaculty', (i,))
			lst.extend(list(list(cur.stored_results())[0].fetchall()))
		return render_template('allfaculty.html', type=session['type'], name=session['name'], lst=lst)

if(__name__=='__main__'):
	app.debug=True
	app.run(port=8080)
