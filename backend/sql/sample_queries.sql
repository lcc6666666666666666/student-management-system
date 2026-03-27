-- 1. 查询所有开放课程及剩余名额
SELECT c.course_code, c.name, c.term, c.capacity,
       COUNT(e.id) AS selected_count,
       c.capacity - COUNT(e.id) AS remain_count
FROM course c
LEFT JOIN enrollment e ON e.course_id = c.id
WHERE c.status = 'open'
GROUP BY c.id;

-- 2. 查询某学生的已选课程
SELECT s.student_no, u.real_name, c.course_code, c.name, c.term
FROM enrollment e
JOIN student s ON s.id = e.student_id
JOIN sys_user u ON u.id = s.user_id
JOIN course c ON c.id = e.course_id
WHERE s.student_no = 'S2023001';

-- 3. 查询某学生的成绩单
SELECT s.student_no, u.real_name, c.course_code, c.name, e.score
FROM enrollment e
JOIN student s ON s.id = e.student_id
JOIN sys_user u ON u.id = s.user_id
JOIN course c ON c.id = e.course_id
WHERE s.student_no = 'S2023001'
ORDER BY c.course_code;

-- 4. 查询某教师授课课程及选课人数
SELECT t.teacher_no, u.real_name AS teacher_name, c.course_code, c.name,
       COUNT(e.id) AS selected_count
FROM teacher t
JOIN sys_user u ON u.id = t.user_id
JOIN course c ON c.teacher_id = t.id
LEFT JOIN enrollment e ON e.course_id = c.id
WHERE t.teacher_no = 'T2020001'
GROUP BY c.id;

-- 5. 查询某课程学生名单
SELECT c.course_code, c.name, s.student_no, u.real_name, e.score
FROM enrollment e
JOIN student s ON s.id = e.student_id
JOIN sys_user u ON u.id = s.user_id
JOIN course c ON c.id = e.course_id
WHERE c.course_code = 'DB101'
ORDER BY s.student_no;

-- 6. 统计每门课程平均分、最高分、最低分
SELECT c.course_code, c.name,
       AVG(e.score) AS avg_score,
       MAX(e.score) AS max_score,
       MIN(e.score) AS min_score
FROM course c
LEFT JOIN enrollment e ON e.course_id = c.id
GROUP BY c.id;

-- 7. 统计每个院系的学生人数
SELECT d.name AS department_name, COUNT(s.id) AS student_count
FROM department d
LEFT JOIN student s ON s.department_id = d.id
GROUP BY d.id;

-- 8. 查询未满员课程
SELECT c.course_code, c.name, c.capacity, COUNT(e.id) AS selected_count
FROM course c
LEFT JOIN enrollment e ON e.course_id = c.id
GROUP BY c.id
HAVING COUNT(e.id) < c.capacity;

-- 9. 查询成绩不及格的学生
SELECT s.student_no, u.real_name, c.course_code, c.name, e.score
FROM enrollment e
JOIN student s ON s.id = e.student_id
JOIN sys_user u ON u.id = s.user_id
JOIN course c ON c.id = e.course_id
WHERE e.score < 60;

-- 10. 查询选课人数最多的前 5 门课程
SELECT c.course_code, c.name, COUNT(e.id) AS selected_count
FROM course c
LEFT JOIN enrollment e ON e.course_id = c.id
GROUP BY c.id
ORDER BY selected_count DESC
LIMIT 5;

-- 11. 查询某学期课程数量
SELECT term, COUNT(*) AS course_count
FROM course
GROUP BY term;

-- 12. 查询教师名下课程通过率
SELECT t.teacher_no, u.real_name, c.course_code, c.name,
       ROUND(SUM(CASE WHEN e.score >= 60 THEN 1 ELSE 0 END) / COUNT(e.id) * 100, 2) AS pass_rate
FROM teacher t
JOIN sys_user u ON u.id = t.user_id
JOIN course c ON c.teacher_id = t.id
JOIN enrollment e ON e.course_id = c.id
WHERE t.teacher_no = 'T2020001'
GROUP BY c.id;
