-- ============================================================
-- SEED DATA: CSE B.Tech Demo Data
-- Run AFTER schema.sql
-- ============================================================

-- ============================================================
-- 1. DEFAULT ADMIN USER
-- Password: admin123 (hashed with werkzeug)
-- ============================================================
INSERT INTO users (name, email, password_hash, role, branch)
VALUES (
    'Admin',
    'admin@college.edu',
    'scrypt:32768:8:1$salt$adminhashedpassword',  -- Replace at runtime
    'admin',
    'CSE'
) ON CONFLICT (email) DO NOTHING;

-- Demo student
INSERT INTO users (name, email, password_hash, role, enrollment_no, semester, branch)
VALUES (
    'Priyanshu Kumar',
    'student@college.edu',
    'scrypt:32768:8:1$salt$studenthashedpassword',  -- Replace at runtime
    'student',
    'CSE2021001',
    6,
    'CSE'
) ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- 2. SEMESTERS
-- ============================================================
INSERT INTO semesters (semester_number, semester_name) VALUES
(1, '1st Semester - First Year'),
(2, '2nd Semester - First Year'),
(3, '3rd Semester - Second Year'),
(4, '4th Semester - Second Year'),
(5, '5th Semester - Third Year'),
(6, '6th Semester - Third Year'),
(7, '7th Semester - Fourth Year'),
(8, '8th Semester - Fourth Year')
ON CONFLICT (semester_number) DO NOTHING;

-- ============================================================
-- 3. SUBJECTS (CSE B.Tech Curriculum)
-- ============================================================

-- Semester 1
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(1, 'MA101', 'Engineering Mathematics - I', 4, 'theory', 'Calculus, Differential Equations, Linear Algebra, Series & Sequences'),
(1, 'PH101', 'Engineering Physics', 3, 'theory', 'Optics, Quantum Mechanics, Semiconductors, Electromagnetic Theory'),
(1, 'CH101', 'Engineering Chemistry', 3, 'theory', 'Electrochemistry, Polymers, Corrosion, Water Treatment'),
(1, 'CS101', 'Programming Fundamentals (C)', 4, 'theory', 'Variables, Data Types, Control Structures, Functions, Arrays, Pointers, Structures'),
(1, 'ME101', 'Engineering Graphics', 2, 'practical', 'Orthographic Projection, Isometric Views, AutoCAD Basics'),
(1, 'CS101L', 'C Programming Lab', 2, 'practical', 'C Programs: Arrays, Pointers, File Handling, Sorting')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 2
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(2, 'MA201', 'Engineering Mathematics - II', 4, 'theory', 'Probability, Statistics, Numerical Methods, Laplace Transform'),
(2, 'CS201', 'Data Structures', 4, 'theory', 'Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hashing, Sorting Algorithms'),
(2, 'CS202', 'Digital Logic Design', 3, 'theory', 'Boolean Algebra, Combinational Circuits, Sequential Circuits, Flip-Flops, Counters'),
(2, 'EC201', 'Basic Electronics', 3, 'theory', 'Diodes, Transistors, Op-Amps, Digital Electronics Basics'),
(2, 'CS201L', 'Data Structures Lab', 2, 'practical', 'Implement Stack, Queue, Linked List, BST, Graph Traversal, Sorting'),
(2, 'HU201', 'Communication Skills', 2, 'theory', 'Technical Writing, Presentations, Group Discussion, Interview Skills')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 3
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(3, 'CS301', 'Object Oriented Programming (Java/C++)', 4, 'theory', 'Classes, Inheritance, Polymorphism, Abstraction, Exception Handling, Collections'),
(3, 'CS302', 'Computer Organization & Architecture', 3, 'theory', 'CPU Design, Memory Hierarchy, Pipelining, I/O Organization, RISC vs CISC'),
(3, 'CS303', 'Discrete Mathematics', 4, 'theory', 'Set Theory, Relations, Graph Theory, Combinatorics, Mathematical Logic'),
(3, 'MA301', 'Engineering Mathematics - III', 3, 'theory', 'Complex Analysis, Fourier Series, Z-Transform, Partial Differential Equations'),
(3, 'CS301L', 'OOP Lab', 2, 'practical', 'Java/C++ Programs: Inheritance, Polymorphism, File I/O, GUI Basics'),
(3, 'CS304', 'Database Management Systems', 4, 'theory', 'ER Model, SQL, Normalization, Transactions, Concurrency, Indexing')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 4
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(4, 'CS401', 'Operating Systems', 4, 'theory', 'Process Management, CPU Scheduling, Deadlock, Memory Management, File Systems'),
(4, 'CS402', 'Theory of Computation', 3, 'theory', 'Finite Automata, Regular Languages, CFG, Pushdown Automata, Turing Machines'),
(4, 'CS403', 'Design & Analysis of Algorithms', 4, 'theory', 'Divide & Conquer, Greedy, DP, Backtracking, Graph Algorithms, NP-Completeness'),
(4, 'CS404', 'Software Engineering', 3, 'theory', 'SDLC, Agile, UML, Testing, Software Design Patterns, Project Management'),
(4, 'CS401L', 'OS Lab', 2, 'practical', 'Process Scheduling Simulation, Memory Management, Shell Scripts, System Calls'),
(4, 'CS405', 'Computer Networks', 4, 'theory', 'OSI/TCP Model, Routing, Switching, IP Addressing, HTTP, DNS, Network Security')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 5
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(5, 'CS501', 'Compiler Design', 3, 'theory', 'Lexical Analysis, Parsing, Syntax Trees, Code Generation, Optimization'),
(5, 'CS502', 'Artificial Intelligence', 4, 'theory', 'Search Algorithms, Knowledge Representation, ML Basics, NLP, Expert Systems'),
(5, 'CS503', 'Web Technologies', 3, 'theory', 'HTML, CSS, JavaScript, PHP/Python, REST APIs, Databases, Frameworks'),
(5, 'CS504', 'Microprocessors & Interfacing', 3, 'theory', '8086 Architecture, Assembly Language, Interrupts, Interfacing Devices'),
(5, 'CS501L', 'Compiler Design Lab', 2, 'practical', 'Lexer, Parser, Symbol Table, Code Generator implementation'),
(5, 'CS505', 'Information Security', 3, 'elective', 'Cryptography, Network Security, Firewalls, Ethical Hacking, Security Protocols')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 6
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(6, 'CS601', 'Machine Learning', 4, 'theory', 'Regression, Classification, Clustering, Neural Networks, SVM, Decision Trees'),
(6, 'CS602', 'Cloud Computing', 3, 'theory', 'Virtualization, AWS/Azure, Docker, Kubernetes, Serverless, Cloud Security'),
(6, 'CS603', 'Data Mining & Warehousing', 3, 'theory', 'Association Rules, Clustering, Classification, OLAP, ETL, Data Preprocessing'),
(6, 'CS604', 'Mobile Application Development', 3, 'theory', 'Android/Flutter, UI Design, SQLite, APIs, Sensors, Publishing'),
(6, 'CS601L', 'ML Lab', 2, 'practical', 'Python: Scikit-learn, Regression, Classification, Clustering, Neural Networks'),
(6, 'CS605', 'Internet of Things', 3, 'elective', 'IoT Architecture, Sensors, Arduino, Raspberry Pi, MQTT, IoT Security')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 7
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(7, 'CS701', 'Deep Learning', 4, 'theory', 'CNN, RNN, LSTM, GANs, Transfer Learning, NLP with Transformers'),
(7, 'CS702', 'Big Data Analytics', 3, 'theory', 'Hadoop, Spark, MapReduce, NoSQL, Stream Processing, Data Lakes'),
(7, 'CS703', 'Blockchain Technology', 3, 'elective', 'Distributed Ledger, Consensus, Smart Contracts, Ethereum, Hyperledger'),
(7, 'CS704', 'Natural Language Processing', 3, 'elective', 'Text Processing, Sentiment Analysis, Named Entity Recognition, Chatbots'),
(7, 'CS700', 'Minor Project', 4, 'practical', 'Guided project on chosen domain with documentation and presentation'),
(7, 'CS705', 'Cyber Security', 3, 'elective', 'Threat Modeling, Penetration Testing, Forensics, Incident Response')
ON CONFLICT (subject_code) DO NOTHING;

-- Semester 8
INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief) VALUES
(8, 'CS801', 'Major Project', 10, 'practical', 'Industry-level project with research paper, presentation, and viva'),
(8, 'CS802', 'Seminar & Technical Writing', 2, 'practical', 'Literature survey, technical paper writing, presentation on emerging tech'),
(8, 'CS803', 'Professional Ethics & IPR', 2, 'theory', 'Engineering Ethics, Intellectual Property, Patents, Cyber Law, Privacy'),
(8, 'CS804', 'Entrepreneurship Development', 2, 'elective', 'Startup Ecosystem, Business Plans, Funding, Lean Startup, Innovation')
ON CONFLICT (subject_code) DO NOTHING;

-- ============================================================
-- 4. STUDY MATERIALS (Google Drive Links - Demo)
-- ============================================================
INSERT INTO subject_materials (subject_id, material_title, material_type, drive_link) VALUES
((SELECT id FROM subjects WHERE subject_code = 'CS101'), 'C Programming Complete Notes', 'notes', 'https://drive.google.com/drive/folders/DEMO_C_PROGRAMMING_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS101'), 'C Programming PYQs 2020-2024', 'pyq', 'https://drive.google.com/drive/folders/DEMO_C_PYQ'),
((SELECT id FROM subjects WHERE subject_code = 'CS201'), 'Data Structures Notes (Handwritten)', 'notes', 'https://drive.google.com/drive/folders/DEMO_DS_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS201'), 'DS Previous Year Papers', 'pyq', 'https://drive.google.com/drive/folders/DEMO_DS_PYQ'),
((SELECT id FROM subjects WHERE subject_code = 'CS201'), 'Data Structures Video Lectures', 'video', 'https://drive.google.com/drive/folders/DEMO_DS_VIDEOS'),
((SELECT id FROM subjects WHERE subject_code = 'CS304'), 'DBMS Complete Notes', 'notes', 'https://drive.google.com/drive/folders/DEMO_DBMS_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS304'), 'DBMS Textbook - Navathe', 'book', 'https://drive.google.com/drive/folders/DEMO_DBMS_BOOK'),
((SELECT id FROM subjects WHERE subject_code = 'CS403'), 'DAA Algorithm Notes', 'notes', 'https://drive.google.com/drive/folders/DEMO_DAA_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS403'), 'DAA PYQ Collection', 'pyq', 'https://drive.google.com/drive/folders/DEMO_DAA_PYQ'),
((SELECT id FROM subjects WHERE subject_code = 'CS405'), 'Computer Networks Notes', 'notes', 'https://drive.google.com/drive/folders/DEMO_CN_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS502'), 'AI Complete Notes + PPTs', 'notes', 'https://drive.google.com/drive/folders/DEMO_AI_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS601'), 'Machine Learning Notes & Code', 'notes', 'https://drive.google.com/drive/folders/DEMO_ML_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS601'), 'ML Lab Programs', 'notes', 'https://drive.google.com/drive/folders/DEMO_ML_LAB'),
((SELECT id FROM subjects WHERE subject_code = 'CS701'), 'Deep Learning Notes', 'notes', 'https://drive.google.com/drive/folders/DEMO_DL_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS301'), 'OOP Java Complete Notes', 'notes', 'https://drive.google.com/drive/folders/DEMO_OOP_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS401'), 'Operating Systems Notes (Galvin)', 'notes', 'https://drive.google.com/drive/folders/DEMO_OS_NOTES'),
((SELECT id FROM subjects WHERE subject_code = 'CS401'), 'OS PYQ 2020-2024', 'pyq', 'https://drive.google.com/drive/folders/DEMO_OS_PYQ');

-- ============================================================
-- 5. ACADEMIC RULES
-- ============================================================
INSERT INTO academic_rules (rule_category, rule_title, rule_content, keywords) VALUES

-- Attendance Rules
('attendance', 'Minimum Attendance Requirement',
 'Students must maintain a minimum of 75% attendance in each subject to be eligible for end-semester examinations. Students with attendance between 65-75% may be allowed with a fine. Below 65% attendance results in being debarred from examinations.',
 'attendance,minimum,requirement,percentage,75%,eligible,debarred'),

('attendance', 'Attendance Shortage Procedure',
 'Students falling short of attendance must apply to the Dean with valid medical certificates or documented reasons. The committee reviews cases individually. Condonation is granted only once during the entire program.',
 'attendance,shortage,medical,condonation,dean,apply'),

('attendance', 'Proxy Attendance Policy',
 'Proxy attendance is strictly prohibited. If caught, both the proxy giver and receiver face disciplinary action including suspension for one semester.',
 'proxy,attendance,disciplinary,suspension,prohibited'),

-- Exam Rules
('examination', 'Exam Pattern - Theory',
 'Theory exams follow this pattern: Internal Assessment (30 marks) = 2 mid-terms (15 marks each) OR best of 3 mid-terms. End Semester Exam (70 marks) = 5 questions, attempt any 3, each 14 marks (2 sub-parts). Total passing marks: 40% overall with minimum 28 marks in end-sem.',
 'exam,pattern,theory,internal,assessment,mid-term,end,semester,marks,passing'),

('examination', 'Exam Pattern - Practical',
 'Practical exams: Internal Assessment (50 marks) = Lab work (20) + Viva (10) + Lab Record (10) + Attendance (10). End Semester Practical Exam (50 marks) = Experiment performance (30) + Viva (10) + Record (10). Minimum 40% required to pass.',
 'practical,exam,lab,viva,record,experiment,marks'),

('examination', 'Supplementary / Back Paper Exam',
 'Students who fail in end-semester exams can appear for supplementary exams conducted before the next semester begins. Maximum 3 attempts allowed for each subject. Fee: Rs. 500 per subject per attempt. Results declared within 2 weeks.',
 'supplementary,back,paper,fail,reappear,attempt,fee'),

('examination', 'Exam Malpractice Policy',
 'Any form of cheating or malpractice during exams results in: First offense - cancellation of that paper. Second offense - cancellation of entire semester exams. Third offense - rustication from the university.',
 'malpractice,cheating,copying,rustication,cancellation'),

-- CGPA/SGPA Rules
('grading', 'SGPA Calculation Method',
 'SGPA (Semester Grade Point Average) = Sum of (Credit × Grade Point) / Total Credits. Grade Points: O=10, A+=9, A=8, B+=7, B=6, C=5, P=4, F=0. Example: If you have subjects with credits 4,3,3,4,2 and grades A+,A,B+,O,A then SGPA = (4×9+3×8+3×7+4×10+2×9)/(4+3+3+4+2) = 137/16 = 8.56',
 'sgpa,calculation,grade,point,credit,semester,formula'),

('grading', 'CGPA Calculation Method',
 'CGPA (Cumulative Grade Point Average) = Sum of (SGPA × Semester Credits) / Total Credits across all semesters. CGPA to Percentage: Multiply CGPA by 10. Example: CGPA 8.5 = 85%. First class: CGPA >= 6.5, Distinction: CGPA >= 8.0.',
 'cgpa,cumulative,calculation,percentage,distinction,first,class'),

('grading', 'Grade Improvement Policy',
 'Students can improve grades by re-appearing in the next regular exam cycle. The better grade is considered. Maximum improvement allowed for 4 subjects per semester. Improvement exam fee: Rs. 300 per subject.',
 'grade,improvement,reappear,better,fee'),

-- Academic Policies
('policy', 'Credit Requirements for Degree',
 'Total credits required for B.Tech CSE degree: 160 credits. Minimum CGPA: 5.0. All core subjects must be passed. Maximum duration: 6 years from admission. Students must complete at least 80% credits by 6th semester to be eligible for placement.',
 'credit,requirement,degree,btech,total,160,minimum,cgpa'),

('policy', 'Branch Change Policy',
 'Branch change is allowed after 1st year based on: SGPA of both semesters (weightage 60%), JEE rank (weightage 40%). Only top 5% of students in each branch are eligible. Seats limited to 10% of branch intake.',
 'branch,change,transfer,sgpa,criteria,eligible'),

('policy', 'Semester Registration',
 'Students must register for subjects within the first week of each semester. Late registration attracts a fine of Rs. 1000. Students with outstanding fees or library dues cannot register. Registration is mandatory even for back papers.',
 'registration,semester,fee,fine,mandatory,deadline'),

('policy', 'Academic Probation',
 'Students with SGPA below 4.0 in any semester are placed on academic probation. They must achieve SGPA >= 5.0 in the next semester to be removed from probation. Two consecutive semesters on probation may lead to relegation.',
 'probation,academic,sgpa,below,relegation,warning');

-- ============================================================
-- 6. SAMPLE NOTICES
-- ============================================================
INSERT INTO notices (title, content, notice_type) VALUES
('Mid-Semester Exam Schedule Released',
 'Mid-semester examinations for all branches will commence from March 15, 2025. Detailed timetable is available on the university portal. Students must carry their ID cards. Seating arrangement will be displayed one day before exams.',
 'exam'),

('Annual Technical Fest - TechVista 2025',
 'The annual technical festival TechVista 2025 will be held from April 5-7, 2025. Events include: Hackathon (48hrs), Coding Competition, Robotics Challenge, Paper Presentation, and Gaming Tournament. Register on the fest website.',
 'event'),

('Holiday Notice - Holi',
 'The college will remain closed on March 14, 2025 on account of Holi. Regular classes resume from March 17, 2025. Students staying in hostels should register with the warden.',
 'holiday'),

('Placement Drive - TCS & Infosys',
 'TCS and Infosys campus placement drive scheduled for March 20-21, 2025. Eligible: B.Tech final year students with CGPA >= 6.0 and no active backlogs. Pre-placement talk on March 19. Register via placement cell portal by March 15.',
 'general'),

('6th Semester Results Declared',
 'Results for 6th semester examinations have been declared. Students can check their results on the university portal. Re-evaluation requests accepted until March 25, 2025. Fee: Rs. 500 per subject.',
 'result'),

('Library Book Return Deadline',
 'All borrowed library books must be returned by March 31, 2025 for annual stocktaking. Fine of Rs. 5 per day per book will be charged for overdue books. Digital library resources remain accessible.',
 'general');
