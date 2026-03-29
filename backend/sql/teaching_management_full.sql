DROP DATABASE IF EXISTS teaching_management;
CREATE DATABASE teaching_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE teaching_management;

DROP TABLE IF EXISTS enrollment_operation_log;
DROP TABLE IF EXISTS course_schedule;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS sys_user;
DROP TABLE IF EXISTS department;

CREATE TABLE department (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE sys_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NULL,
    email VARCHAR(100) NULL UNIQUE,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE student (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    student_no VARCHAR(20) NOT NULL UNIQUE,
    department_id INT NULL,
    gender VARCHAR(10) NULL,
    grade VARCHAR(20) NULL,
    class_name VARCHAR(50) NULL,
    admission_year INT NULL,
    CONSTRAINT fk_student_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT fk_student_department FOREIGN KEY (department_id) REFERENCES department(id)
) ENGINE=InnoDB;

CREATE TABLE teacher (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    teacher_no VARCHAR(20) NOT NULL UNIQUE,
    department_id INT NULL,
    title VARCHAR(30) NULL,
    office VARCHAR(50) NULL,
    CONSTRAINT fk_teacher_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT fk_teacher_department FOREIGN KEY (department_id) REFERENCES department(id)
) ENGINE=InnoDB;

CREATE TABLE admin (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    admin_no VARCHAR(20) NOT NULL UNIQUE,
    level VARCHAR(20) NOT NULL DEFAULT 'super',
    CONSTRAINT fk_admin_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB;

CREATE TABLE course (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    credit DECIMAL(3,1) NOT NULL,
    hours INT NOT NULL,
    capacity INT NOT NULL,
    term VARCHAR(30) NOT NULL,
    status ENUM('open', 'closed') NOT NULL DEFAULT 'open',
    description TEXT NULL,
    teacher_id INT NOT NULL,
    department_id INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_course_teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id),
    CONSTRAINT fk_course_department FOREIGN KEY (department_id) REFERENCES department(id),
    CONSTRAINT chk_course_credit CHECK (credit > 0),
    CONSTRAINT chk_course_hours CHECK (hours > 0),
    CONSTRAINT chk_course_capacity CHECK (capacity > 0)
) ENGINE=InnoDB;

CREATE TABLE course_schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL,
    weekday INT NOT NULL,
    start_section INT NOT NULL,
    end_section INT NOT NULL,
    start_week INT NOT NULL,
    end_week INT NOT NULL,
    location VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_course_schedule_course FOREIGN KEY (course_id) REFERENCES course(id),
    CONSTRAINT chk_course_schedule_weekday CHECK (weekday BETWEEN 1 AND 7),
    CONSTRAINT chk_course_schedule_start_section CHECK (start_section BETWEEN 1 AND 20),
    CONSTRAINT chk_course_schedule_end_section CHECK (end_section BETWEEN 1 AND 20),
    CONSTRAINT chk_course_schedule_section_order CHECK (start_section <= end_section),
    CONSTRAINT chk_course_schedule_start_week CHECK (start_week BETWEEN 1 AND 30),
    CONSTRAINT chk_course_schedule_end_week CHECK (end_week BETWEEN 1 AND 30),
    CONSTRAINT chk_course_schedule_week_order CHECK (start_week <= end_week)
) ENGINE=InnoDB;

CREATE TABLE enrollment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    score DECIMAL(5,2) NULL,
    selected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_enrollment_student FOREIGN KEY (student_id) REFERENCES student(id),
    CONSTRAINT fk_enrollment_course FOREIGN KEY (course_id) REFERENCES course(id),
    CONSTRAINT uk_student_course UNIQUE (student_id, course_id),
    CONSTRAINT chk_score_range CHECK (score BETWEEN 0 AND 100 OR score IS NULL)
) ENGINE=InnoDB;

CREATE TABLE enrollment_operation_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    operator_user_id INT NOT NULL,
    operation_type ENUM('student_select', 'student_drop', 'admin_assign', 'admin_drop') NOT NULL,
    reason VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_enrollment_log_student FOREIGN KEY (student_id) REFERENCES student(id),
    CONSTRAINT fk_enrollment_log_course FOREIGN KEY (course_id) REFERENCES course(id),
    CONSTRAINT fk_enrollment_log_operator FOREIGN KEY (operator_user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB;

CREATE INDEX idx_user_role ON sys_user(role);
CREATE INDEX idx_student_department ON student(department_id);
CREATE INDEX idx_teacher_department ON teacher(department_id);
CREATE INDEX idx_course_teacher ON course(teacher_id);
CREATE INDEX idx_course_term_status ON course(term, status);
CREATE INDEX idx_course_schedule_course ON course_schedule(course_id);
CREATE INDEX idx_enrollment_student ON enrollment(student_id);
CREATE INDEX idx_enrollment_course ON enrollment(course_id);
CREATE INDEX idx_enrollment_log_student ON enrollment_operation_log(student_id);
CREATE INDEX idx_enrollment_log_course ON enrollment_operation_log(course_id);
CREATE INDEX idx_enrollment_log_operator ON enrollment_operation_log(operator_user_id);

INSERT INTO department (name, code, description) VALUES
('计算机学院', 'CS', '负责软件、数据与人工智能方向教学'),
('数学学院', 'MATH', '负责数学建模与分析课程'),
('管理学院', 'MGMT', '负责管理类通识课程');

INSERT INTO sys_user (username, password_hash, role, real_name, phone, email) VALUES
('student01', 'pbkdf2_sha256$120000$6ca741d2215db5976c8eeadf32af7df1$xq9zkE5l32bUHvL0uppmqzRhDRhrth4nlHYa19h2fhQ=', 'student', '张明', '13800000001', 'student01@example.com'),
('student02', 'pbkdf2_sha256$120000$6ca741d2215db5976c8eeadf32af7df1$xq9zkE5l32bUHvL0uppmqzRhDRhrth4nlHYa19h2fhQ=', 'student', '李华', '13800000002', 'student02@example.com'),
('student03', 'pbkdf2_sha256$120000$6ca741d2215db5976c8eeadf32af7df1$xq9zkE5l32bUHvL0uppmqzRhDRhrth4nlHYa19h2fhQ=', 'student', '王蕾', '13800000003', 'student03@example.com'),
('teacher01', 'pbkdf2_sha256$120000$6ca741d2215db5976c8eeadf32af7df1$xq9zkE5l32bUHvL0uppmqzRhDRhrth4nlHYa19h2fhQ=', 'teacher', '陈老师', '13900000001', 'teacher01@example.com'),
('teacher02', 'pbkdf2_sha256$120000$6ca741d2215db5976c8eeadf32af7df1$xq9zkE5l32bUHvL0uppmqzRhDRhrth4nlHYa19h2fhQ=', 'teacher', '刘老师', '13900000002', 'teacher02@example.com'),
('admin01', 'pbkdf2_sha256$120000$6ca741d2215db5976c8eeadf32af7df1$xq9zkE5l32bUHvL0uppmqzRhDRhrth4nlHYa19h2fhQ=', 'admin', '系统管理员', '13700000001', 'admin01@example.com');

INSERT INTO student (user_id, student_no, department_id, gender, grade, class_name, admission_year) VALUES
(1, 'S2023001', 1, '男', '2023级', '计科1班', 2023),
(2, 'S2023002', 1, '女', '2023级', '计科2班', 2023),
(3, 'S2023003', 2, '女', '2023级', '数科1班', 2023);

INSERT INTO teacher (user_id, teacher_no, department_id, title, office) VALUES
(4, 'T2020001', 1, '副教授', '信息楼 A-308'),
(5, 'T2020002', 2, '讲师', '理科楼 B-512');

INSERT INTO admin (user_id, admin_no, level) VALUES
(6, 'A0001', 'super');

INSERT INTO course (course_code, name, credit, hours, capacity, term, status, description, teacher_id, department_id) VALUES
('DB101', '数据库系统原理', 3.5, 48, 60, '2025-2026-2', 'open', '面向数据库课程设计的核心课程，涵盖 SQL、事务与范式设计。', 1, 1),
('SE202', '软件工程', 3.0, 40, 45, '2025-2026-2', 'open', '面向项目开发流程、需求分析与系统设计。', 1, 1),
('NW301', '计算机网络', 3.0, 40, 50, '2025-2026-2', 'closed', '课程已关闭选课，用于演示状态控制。', 1, 1),
('MA103', '高等数学实践', 4.0, 56, 80, '2025-2026-2', 'open', '通过建模案例训练数学分析能力。', 2, 2),
('DA204', '数据分析基础', 2.5, 32, 55, '2025-2026-2', 'open', '面向统计分析与可视化展示的基础课程。', 2, 2);

INSERT INTO course_schedule (course_id, weekday, start_section, end_section, start_week, end_week, location) VALUES
(1, 1, 1, 2, 1, 16, '博学楼 A101'),
(1, 3, 3, 4, 1, 16, '博学楼 A101'),
(2, 1, 3, 4, 1, 16, '博学楼 A202'),
(3, 2, 1, 2, 1, 16, '网络实验室 1'),
(4, 3, 1, 2, 1, 16, '理学楼 B301'),
(5, 1, 1, 2, 1, 16, '理学楼 B402');

INSERT INTO enrollment (student_id, course_id, score) VALUES
(1, 1, 92),
(1, 2, NULL),
(2, 1, 86),
(2, 4, 90),
(3, 2, 78),
(3, 5, NULL);

DROP VIEW IF EXISTS v_course_selection_summary;
CREATE VIEW v_course_selection_summary AS
SELECT
    c.id AS course_id,
    c.course_code,
    c.name AS course_name,
    c.term,
    c.status,
    c.capacity,
    t.teacher_no,
    u.real_name AS teacher_name,
    COUNT(e.id) AS selected_count,
    c.capacity - COUNT(e.id) AS remaining_seats
FROM course c
JOIN teacher t ON t.id = c.teacher_id
JOIN sys_user u ON u.id = t.user_id
LEFT JOIN enrollment e ON e.course_id = c.id
GROUP BY c.id;

DROP VIEW IF EXISTS v_student_grade_report;
CREATE VIEW v_student_grade_report AS
SELECT
    s.id AS student_id,
    s.student_no,
    su.real_name AS student_name,
    c.id AS course_id,
    c.course_code,
    c.name AS course_name,
    tu.real_name AS teacher_name,
    c.term,
    e.score
FROM enrollment e
JOIN student s ON s.id = e.student_id
JOIN sys_user su ON su.id = s.user_id
JOIN course c ON c.id = e.course_id
JOIN teacher t ON t.id = c.teacher_id
JOIN sys_user tu ON tu.id = t.user_id;

DROP PROCEDURE IF EXISTS sp_enroll_course;
DELIMITER $$
CREATE PROCEDURE sp_enroll_course(IN p_student_id INT, IN p_course_id INT)
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_selected_count INT;
    DECLARE v_status VARCHAR(10);
    DECLARE v_exists INT;

    SELECT capacity, status INTO v_capacity, v_status
    FROM course
    WHERE id = p_course_id;

    IF v_capacity IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '课程不存在';
    END IF;

    IF v_status <> 'open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '课程未开放选课';
    END IF;

    SELECT COUNT(*) INTO v_exists
    FROM enrollment
    WHERE student_id = p_student_id AND course_id = p_course_id;

    IF v_exists > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '不能重复选课';
    END IF;

    SELECT COUNT(*) INTO v_selected_count
    FROM enrollment
    WHERE course_id = p_course_id;

    IF v_selected_count >= v_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '课程容量已满';
    END IF;

    INSERT INTO enrollment (student_id, course_id, score) VALUES (p_student_id, p_course_id, NULL);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_update_score;
DELIMITER $$
CREATE PROCEDURE sp_update_score(IN p_enrollment_id INT, IN p_score DECIMAL(5,2))
BEGIN
    IF p_score < 0 OR p_score > 100 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '成绩必须在 0 到 100 之间';
    END IF;

    UPDATE enrollment
    SET score = p_score
    WHERE id = p_enrollment_id;
END $$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_enrollment_before_insert;
DELIMITER $$
CREATE TRIGGER trg_enrollment_before_insert
BEFORE INSERT ON enrollment
FOR EACH ROW
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_selected_count INT;
    DECLARE v_status VARCHAR(10);

    SELECT capacity, status INTO v_capacity, v_status
    FROM course
    WHERE id = NEW.course_id;

    IF v_status <> 'open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '当前课程未开放选课';
    END IF;

    SELECT COUNT(*) INTO v_selected_count
    FROM enrollment
    WHERE course_id = NEW.course_id;

    IF v_selected_count >= v_capacity THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '当前课程容量已满';
    END IF;

    IF NEW.score IS NOT NULL AND (NEW.score < 0 OR NEW.score > 100) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '成绩必须在 0 到 100 之间';
    END IF;
END $$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_enrollment_before_update;
DELIMITER $$
CREATE TRIGGER trg_enrollment_before_update
BEFORE UPDATE ON enrollment
FOR EACH ROW
BEGIN
    IF NEW.score IS NOT NULL AND (NEW.score < 0 OR NEW.score > 100) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '成绩必须在 0 到 100 之间';
    END IF;
END $$
DELIMITER ;

DROP TRIGGER IF EXISTS trg_course_before_delete;
DELIMITER $$
CREATE TRIGGER trg_course_before_delete
BEFORE DELETE ON course
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count FROM enrollment WHERE course_id = OLD.id;
    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '课程存在选课记录，禁止删除';
    END IF;
END $$
DELIMITER ;
