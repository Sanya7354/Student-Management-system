DELIMITER $$
CREATE PROCEDURE profile_student(usernm VARCHAR(20))
BEGIN
SELECT student.username, first_name, middle_name, last_name, mobile_no, address, email, roll_no, department_name, student.dep_id FROM student INNER JOIN user_group ON user_group.username=student.username INNER JOIN department ON student.dep_id=department.department_id WHERE student.username=usernm;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE profile_faculty(usernm VARCHAR(20))
BEGIN
SELECT faculty.username, first_name, middle_name, last_name, mobile_no, address, email, department_name, faculty.dep_id, faculty_id FROM faculty INNER JOIN user_group ON user_group.username=faculty.username INNER JOIN department ON faculty.dep_id=department.department_id WHERE faculty.username=usernm;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE profile_admin(usernm VARCHAR(20))
BEGIN
SELECT username, first_name, middle_name, last_name, mobile_no, address, email FROM user_group WHERE user_group.username=usernm;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE update_student(rollno INTEGER, firstname VARCHAR(50), middlename VARCHAR(50), lastname VARCHAR(50), addr VARCHAR(255), mobileno VARCHAR(10), depid INTEGER)
BEGIN
UPDATE user_group SET first_name=firstname, middle_name=middlename, last_name=lastname, address=addr, mobile_no=mobileno WHERE username=ANY(SELECT username from student where roll_no=rollno);
UPDATE student SET dep_id=depid WHERE roll_no=rollno;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE update_faculty(facid INTEGER, firstname VARCHAR(50), middlename VARCHAR(50), lastname VARCHAR(50), addr VARCHAR(255), mobileno VARCHAR(10), depid INTEGER)
BEGIN
UPDATE user_group SET first_name=firstname, middle_name=middlename, last_name=lastname, address=addr, mobile_no=mobileno WHERE username=ANY(SELECT username from faculty where faculty_id=facid);
UPDATE faculty SET dep_id=depid WHERE faculty_id=facid;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE viewcourses()
BEGIN
SELECT course_code, course_name, credits, semester_no, CONCAT("Dr. ",first_name, " ", middle_name, " ", last_name) FROM courses INNER JOIN faculty ON courses.instructor_id=faculty.faculty_id INNER JOIN user_group ON faculty.username=user_group.username;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE allstudent(dep_id INTEGER)
BEGIN
SELECT roll_no, CONCAT(first_name, " ", middle_name, " ", last_name), department_code FROM student INNER JOIN user_group ON student.username=user_group.username INNER JOIN department ON student.dep_id=department.department_id WHERE department_id=dep_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE allfaculty(dep_id INTEGER)
BEGIN
SELECT faculty_id, CONCAT("Dr. ", first_name, " ", middle_name, " ", last_name), department_code FROM faculty INNER JOIN user_group ON faculty.username=user_group.username INNER JOIN department ON faculty.dep_id=department.department_id WHERE department_id=dep_id;
END$$
DELIMITER ;