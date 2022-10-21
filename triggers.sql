DELIMITER $$
CREATE TRIGGER TRG1
AFTER INSERT ON course_register
FOR EACH ROW
BEGIN
INSERT INTO grades VALUES(NEW.roll_no, NEW.course_code, 0, 0, 0, 0, "NN", 0);
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER TRG2
BEFORE INSERT ON grades
FOR EACH ROW
BEGIN
SET NEW.total_marks=NEW.midsem_marks+NEW.quiz_marks+NEW.endsem_marks;
IF NEW.total_marks>=80 THEN SET NEW.grade="AA", NEW.gpa=10;
ELSEIF NEW.total_marks>=70 THEN SET NEW.grade="AB", NEW.gpa=9;
ELSEIF NEW.total_marks>=60 THEN SET NEW.grade="BB", NEW.gpa=8;
ELSEIF NEW.total_marks>=50 THEN SET NEW.grade="BC", NEW.gpa=7;
ELSEIF NEW.total_marks>=40 THEN SET NEW.grade="CC", NEW.gpa=6;
ELSEIF NEW.total_marks>=30 THEN SET NEW.grade="DD", NEW.gpa=5;
ELSEIF NEW.total_marks<30 THEN SET NEW.grade="FR", NEW.gpa=0;
END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER TRG3
BEFORE UPDATE ON grades
FOR EACH ROW
BEGIN
SET NEW.total_marks=NEW.midsem_marks+NEW.quiz_marks+NEW.endsem_marks;
IF NEW.total_marks>=80 THEN SET NEW.grade="AA", NEW.gpa=10;
ELSEIF NEW.total_marks>=70 THEN SET NEW.grade="AB", NEW.gpa=9;
ELSEIF NEW.total_marks>=60 THEN SET NEW.grade="BB", NEW.gpa=8;
ELSEIF NEW.total_marks>=50 THEN SET NEW.grade="BC", NEW.gpa=7;
ELSEIF NEW.total_marks>=40 THEN SET NEW.grade="CC", NEW.gpa=6;
ELSEIF NEW.total_marks>=30 THEN SET NEW.grade="DD", NEW.gpa=5;
ELSEIF NEW.total_marks<30 THEN SET NEW.grade="FR", NEW.gpa=0;
END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER TRG4
BEFORE DELETE ON user_group
FOR EACH ROW
BEGIN
IF OLD.user_type=1 THEN
DELETE FROM attendance WHERE roll_no=ALL(SELECT roll_no FROM student WHERE username=OLD.username);
DELETE FROM grades WHERE roll_no=ALL(SELECT roll_no FROM student WHERE username=OLD.username);
DELETE FROM course_register WHERE roll_no=ALL(SELECT roll_no FROM student WHERE username=OLD.username);
DELETE FROM student WHERE username=OLD.username;
ELSEIF OLD.user_type=2 THEN
DELETE FROM faculty WHERE username=OLD.username;
END IF;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER TRG5
BEFORE DELETE ON courses
FOR EACH ROW
BEGIN
DELETE FROM attendance WHERE course_code=OLD.course_code;
DELETE FROM grades WHERE course_code=OLD.course_code;
DELETE FROM course_register WHERE course_code=OLD.course_code;
END$$
DELIMITER ;
