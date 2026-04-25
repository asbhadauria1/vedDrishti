-- =====================================================
-- VEDDRISHTI - Exam Prediction Engine
-- Database Schema
-- =====================================================

-- =====================================================
-- 1. COURSES TABLE
-- Stores information about each course
-- =====================================================
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE NOT NULL,
    course_name TEXT NOT NULL,
    semester TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. PAST PAPERS TABLE
-- Stores metadata about past exam papers
-- =====================================================
CREATE TABLE IF NOT EXISTS past_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    exam_type TEXT CHECK(exam_type IN ('Midterm', 'Final', 'Quiz', 'Other')),
    file_path TEXT,
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- =====================================================
-- 3. TOPICS TABLE
-- Stores topics extracted from papers and transcripts
-- =====================================================
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    topic_name TEXT NOT NULL,
    frequency_in_papers INTEGER DEFAULT 0,
    frequency_in_transcripts INTEGER DEFAULT 0,
    probability_score REAL DEFAULT 0.0,
    source TEXT CHECK(source IN ('paper', 'transcript', 'both')),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- =====================================================
-- 4. GRADING WEIGHTS TABLE
-- Stores how grades are distributed
-- =====================================================
CREATE TABLE IF NOT EXISTS grading_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    component TEXT NOT NULL CHECK(component IN ('Midterm', 'Final', 'Homework', 'Lab', 'Project', 'Quiz', 'Participation')),
    weight REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- =====================================================
-- 5. DEADLINES TABLE
-- Stores assignment and exam deadlines
-- =====================================================
CREATE TABLE IF NOT EXISTS deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    due_date DATE NOT NULL,
    estimated_hours REAL DEFAULT 1.0,
    priority INTEGER DEFAULT 5,
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- =====================================================
-- 6. STUDY PLAN TABLE
-- Stores your personalized study schedule
-- =====================================================
CREATE TABLE IF NOT EXISTS study_plan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    priority_score REAL DEFAULT 0.0,
    completed BOOLEAN DEFAULT 0,
    study_minutes INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

-- =====================================================
-- 7. PREDICTION_HISTORY TABLE
-- Tracks prediction accuracy over time
-- =====================================================
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    prediction_date DATE NOT NULL,
    topic_name TEXT NOT NULL,
    predicted_probability REAL,
    actual_occurrence BOOLEAN,
    accuracy_score REAL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- =====================================================
-- SAMPLE DATA FOR COMP2012 (for testing)
-- =====================================================

-- Insert COMP2012 course
INSERT OR IGNORE INTO courses (course_code, course_name, semester) 
VALUES ('COMP2012', 'Object-Oriented Programming and Data Structures', 'Spring 2026');

-- Insert grading weights for COMP2012
INSERT OR IGNORE INTO grading_weights (course_id, component, weight, notes) 
VALUES 
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Midterm', 25, 'Week 7'),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Final', 45, 'Cumulative'),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Homework', 20, 'Weekly assignments'),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Labs', 10, 'Weekly labs');

-- Insert sample deadlines
INSERT OR IGNORE INTO deadlines (course_id, task_name, due_date, estimated_hours, priority)
VALUES 
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Assignment 1', '2026-04-20', 5, 7),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Midterm Exam', '2026-04-28', 15, 10),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Assignment 2', '2026-05-05', 8, 6),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Final Project', '2026-05-20', 20, 9),
    ((SELECT id FROM courses WHERE course_code='COMP2012'), 'Final Exam', '2026-05-25', 20, 10);

-- =====================================================
-- USEFUL QUERIES (for reference)
-- =====================================================

-- Query 1: Get all topics with probability > 70%
-- SELECT topic_name, probability_score FROM topics 
-- WHERE course_id = (SELECT id FROM courses WHERE course_code='COMP2012') 
-- AND probability_score > 0.7 ORDER BY probability_score DESC;

-- Query 2: Get grading distribution for a course
-- SELECT component, weight FROM grading_weights 
-- WHERE course_id = (SELECT id FROM courses WHERE course_code='COMP2012') 
-- ORDER BY weight DESC;

-- Query 3: Find workload spikes (multiple deadlines same week)
-- SELECT due_date, COUNT(*) as deadline_count 
-- FROM deadlines 
-- WHERE course_id = (SELECT id FROM courses WHERE course_code='COMP2012')
-- GROUP BY due_date HAVING deadline_count > 1;

-- Query 4: Join topics with study plan
-- SELECT t.topic_name, sp.scheduled_date, sp.priority_score 
-- FROM topics t JOIN study_plan sp ON t.id = sp.topic_id 
-- WHERE t.course_id = (SELECT id FROM courses WHERE course_code='COMP2012')
-- ORDER BY sp.scheduled_date;