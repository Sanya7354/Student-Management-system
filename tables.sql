CREATE TABLE user_group
(
	first_name VARCHAR(50) NOT NULL,
	middle_name VARCHAR(50),
	last_name VARCHAR(50) NOT NULL,
	mobile_no VARCHAR(10) NOT NULL,
	address VARCHAR(255) NOT NULL,
	email VARCHAR(50) NOT NULL,
	username VARCHAR(20) NOT NULL,
	password VARCHAR(255) NOT NULL,
	user_type INTEGER(1),
	PRIMARY KEY (username)
);

CREATE TABLE department
(
	department_id INTEGER auto_increment,
	department_code VARCHAR(5),
	department_name VARCHAR(255) NOT NULL,
	PRIMARY KEY (department_id)
);

CREATE TABLE faculty
(
	faculty_id INTEGER NOT NULL,
	username VARCHAR(20),
	dep_id INTEGER,
	PRIMARY KEY (faculty_id),
	FOREIGN KEY (dep_id) REFERENCES department(department_id),
	FOREIGN KEY (username) REFERENCES user_group(username)
);

CREATE TABLE student
(
	roll_no INTEGER NOT NULL,
	username VARCHAR(20),
	dep_id INTEGER,
	PRIMARY KEY (roll_no),
	FOREIGN KEY (username) REFERENCES user_group(username),
	FOREIGN KEY (dep_id) REFERENCES department(department_id)
);

CREATE TABLE courses
(
	course_code VARCHAR(5) NOT NULL,
	course_name VARCHAR(255) NOT NULL,
	credits DECIMAL NOT NULL,
	semester_no INTEGER(2) NOT NULL,
	instructor_id INTEGER NOT NULL,
	PRIMARY KEY (course_code),
	FOREIGN KEY (instructor_id) REFERENCES faculty(faculty_id)
);

CREATE TABLE attendance
(
	roll_no INTEGER,
	course_code VARCHAR(5),
	att_date DATE,
	attended VARCHAR(1) NOT NULL,
	FOREIGN KEY (roll_no) REFERENCES student(roll_no),
	FOREIGN KEY (course_code) REFERENCES courses(course_code),
	PRIMARY KEY (roll_no, course_code, att_date)
);

CREATE TABLE grades
(
	roll_no INTEGER,
	course_code VARCHAR(5),
	midsem_marks DECIMAL DEFAULT 0.0,
	endsem_marks DECIMAL DEFAULT 0.0,
	quiz_marks DECIMAL DEFAULT 0.0,
	total_marks DECIMAL DEFAULT 0.0,
	grade VARCHAR(2) DEFAULT "NN",
	gpa DECIMAL DEFAULT 0.0,
	FOREIGN KEY (roll_no) REFERENCES student(roll_no),
	FOREIGN KEY (course_code) REFERENCES courses(course_code),
	PRIMARY KEY (roll_no, course_code)
);

CREATE TABLE course_register
(
	roll_no INTEGER(9),
	course_code VARCHAR(5),
	FOREIGN KEY (roll_no) REFERENCES student(roll_no),
	FOREIGN KEY (course_code) REFERENCES courses(course_code),
	PRIMARY KEY (roll_no, course_code)
);
