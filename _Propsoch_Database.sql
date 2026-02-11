-- PostgreSQL SQL Dump for Supabase
-- Converted from MySQL career_guidance_db

-- Table structure for table admin
CREATE TABLE admin (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  plain_password VARCHAR(255) DEFAULT NULL
);

-- Dumping data for table admin
INSERT INTO admin (id, username, password, plain_password) VALUES
(2, 'admin', 'pbkdf2:sha256:600000$SflKipodS1b7DrlN$b0aed58e712159f3b744693c855349b5276a9b27435a518690024fb4b2bf35a1', 'admin');

-- Table structure for table careers
CREATE TABLE careers (
  id SERIAL PRIMARY KEY,
  title VARCHAR(100) DEFAULT NULL,
  description TEXT DEFAULT NULL,
  required_skills TEXT DEFAULT NULL,
  category VARCHAR(100) DEFAULT NULL,
  salary_range VARCHAR(50) DEFAULT NULL,
  courses TEXT DEFAULT NULL,
  path TEXT DEFAULT NULL
);

-- Dumping data for table careers
INSERT INTO careers (id, title, description, required_skills, category, salary_range, courses, path) VALUES
(1, 'Data Analyst', 'Analyze and interpret data to support business decisions', 'Python, SQL, Excel', 'Data', '6-12 LPA', 'Python for Data Analysis, SQL for Data Science', 'Start with B.Sc/B.Tech → Learn Python & SQL → Build Projects → Internship → Data Analyst'),
(2, 'Software Developer', 'Develop applications using programming languages', 'Java, Python, Git', 'Technical', '5-10 LPA', 'Java Programming Masterclass, GitHub Essentials', 'Start with B.Tech in CS/IT → Learn Programming → Internship → Junior Developer → Senior Developer'),
(3, 'UI/UX Designer', 'Design intuitive user interfaces and experiences', 'Figma, HTML, CSS', 'Creative', '4-9 LPA', 'UI Design Fundamentals, Web Design with HTML/CSS', 'Start with Design Degree/Certification → Build Portfolio → Internship → UI/UX Designer'),
(4, 'Project Manager', 'Lead project teams to achieve goals', 'Leadership, Agile, Communication', 'Management', '7-15 LPA', 'Agile Project Management, Communication for Leaders', 'Start with B.Tech/BBA → Work as Analyst/Coordinator → PMP Certification → Project Manager'),
(5, 'Support Engineer', 'Resolve technical issues for clients', 'Troubleshooting, Networking, Windows/Linux', 'Support', '3-8 LPA', 'Tech Support Fundamentals, CompTIA A+', 'Start with B.Sc IT/B.Tech → Learn Networking Basics → Internship → Support Engineer'),
(6, 'Cloud Engineer', 'Design and manage cloud infrastructure and services', 'AWS, Azure, Linux, Python', 'Technical', '8-18 LPA', 'AWS Certified Solutions Architect, Azure Fundamentals', 'Start with B.Tech → Learn Cloud Platforms → Certification → Cloud Engineer'),
(7, 'Business Analyst', 'Bridge business needs with technology solutions', 'Excel, SQL, Communication, Analysis', 'Business', '6-14 LPA', 'Business Analysis Fundamentals, SQL for Business', 'Start with BBA/MBA → Learn Analysis Tools → Internship → Business Analyst'),
(8, 'Cybersecurity Specialist', 'Protect systems and networks from cyber threats', 'Networking, Security, Python, Linux', 'Security', '7-16 LPA', 'Certified Ethical Hacker, CompTIA Security+', 'Start with B.Tech → Learn Security Basics → Certification → Cybersecurity Specialist');

-- Table structure for table career_milestones
CREATE TABLE career_milestones (
  id SERIAL PRIMARY KEY,
  career_id INTEGER NOT NULL,
  milestone VARCHAR(255) NOT NULL,
  description TEXT DEFAULT NULL,
  FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
);

-- Table structure for table users
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  plain_password VARCHAR(255) DEFAULT NULL,
  profile_pic VARCHAR(255) DEFAULT NULL,
  bio TEXT DEFAULT NULL,
  linkedin VARCHAR(255) DEFAULT NULL,
  points INTEGER DEFAULT 0
);

-- Dumping data for table users
INSERT INTO users (id, name, email, password, plain_password, profile_pic, bio, linkedin, points) VALUES
(1, 'Test User', 'test@example.com', 'testpassword', 'testpassword', NULL, NULL, NULL, 0),
(2, 'Priyanshu Patel', 'ppriyanshu1609@gmail.com', 'pbkdf2:sha256:600000$6RLV20xPkIbEbQdU$e63384783100d7dd230a51673ee5a0a197a5d65ca50f7359e71b7a9dc070c2af', '12345678', 'profile_2_pexels-anjana-c-169994-674010.jpg', 'FULL STACK DEVELOPER', 'https://www.linkedin.com/in/priyanshupatel16/', 0);

-- Table structure for table resumes
CREATE TABLE resumes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  skills TEXT DEFAULT NULL,
  education TEXT DEFAULT NULL,
  experience TEXT DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table resumes
INSERT INTO resumes (id, user_id, skills, education, experience) VALUES
(14, 2, 'git, django, java, communication, html, excel, css, c++, javascript, python, leadership', 'www.linkedin.com/in/priyanshupatel16 \n \n•, Servlet, BootStrap, JSP, JSP & Servlets, HTML, Bootstrap, CSE, JavaScript, Information Technology, SASS, MS Excel, Power BI, PHP, Government Polytechnic, Software Developer, CSS, Indus University, React.js, PHP, E-Commerce, PowerBI, MySql, Personal-Life Expense-Tracker| GitHub \n● Developed, Object-Oriented Programming', 'May 2023, 9023463169, 2023, 2020, monthly'),
(15, 2, 'c++, python, html, git, css, java, communication, leadership, django, excel, javascript', 'Object-Oriented Programming, Indus University, Software Developer, E-Commerce, Bootstrap, React.js, PHP, Personal-Life Expense-Tracker| GitHub \n● Developed, HTML, Government Polytechnic, MS Excel, Power BI, JSP & Servlets, BootStrap, Servlet, PowerBI, CSS, PHP, JSP, www.linkedin.com/in/priyanshupatel16 \n \n•, SASS, CSE, Information Technology, MySql, JavaScript', 'May 2023, 2020, monthly, 2023, 9023463169'),
(16, 2, 'excel, python, javascript, flask, c++, html, git, css, java, django', 'IoT, Bootstrap, AI-Powered Career Guidance System, Servlet, CSS, PDF, PHP, SASS, Information Technology, DbDiagram\n Automation, FlutterFlow, UI, SQLite, Android, JSP & Servlets\n Mobile, DBMS, JavaScript, JSP & Servlets, FlutterFlow\n , Python Development Intern\nInternship — Infollabz IT Services Pvt, HTML, Power BI, AHMEDABAD\nBachelor of Technology, CSE, ASP.NET, JSP', '90234 63169, 2023, 2020'),
(17, 2, 'excel, python, javascript, flask, c++, html, git, css, java, django', 'IoT, Bootstrap, AI-Powered Career Guidance System, Servlet, CSS, PDF, PHP, SASS, Information Technology, DbDiagram\n Automation, FlutterFlow, UI, SQLite, Android, JSP & Servlets\n Mobile, DBMS, JavaScript, JSP & Servlets, FlutterFlow\n , Python Development Intern\nInternship — Infollabz IT Services Pvt, HTML, Power BI, AHMEDABAD\nBachelor of Technology, CSE, ASP.NET, JSP', '90234 63169, 2023, 2020');

-- Table structure for table career_progress
CREATE TABLE career_progress (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  career_id INTEGER DEFAULT NULL,
  milestone VARCHAR(255) DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'Not Started' CHECK (status IN ('Not Started', 'In Progress', 'Completed')),
  resume_id INTEGER DEFAULT NULL,
  note TEXT DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
);

-- Dumping data for table career_progress
INSERT INTO career_progress (id, user_id, career_id, milestone, status, resume_id, note) VALUES
(35, 2, 1, 'Learn Excel & SQL', 'Completed', NULL, NULL),
(36, 2, 1, 'Master Data Visualization Tools', 'Completed', NULL, NULL),
(37, 2, 1, 'Do Case Study Projects', 'Not Started', NULL, NULL),
(38, 2, 1, 'Internship in Analytics', 'Not Started', NULL, NULL),
(39, 2, 1, 'Prepare Resume', 'Not Started', NULL, NULL),
(40, 2, 1, 'Apply for Analyst Roles', 'Not Started', NULL, NULL),
(71, 2, 2, 'Learn Programming Language', 'Completed', 16, NULL),
(72, 2, 2, 'Complete Git & GitHub Course', 'Not Started', 16, NULL),
(73, 2, 2, 'Build Portfolio Website', 'Not Started', 16, NULL),
(74, 2, 2, 'Contribute to Open Source', 'Not Started', 16, NULL),
(75, 2, 2, 'Do Internship', 'Not Started', 16, NULL),
(76, 2, 2, 'Apply for Developer Jobs', 'Not Started', 16, NULL);

-- Table structure for table custom_paths
CREATE TABLE custom_paths (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  title VARCHAR(255) DEFAULT NULL,
  description TEXT DEFAULT NULL,
  steps TEXT DEFAULT NULL,
  shared BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table structure for table feedback
CREATE TABLE feedback (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  message TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table structure for table interests
CREATE TABLE interests (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  interest_area VARCHAR(100) DEFAULT NULL,
  resume_id INTEGER DEFAULT NULL,
  quiz_answers TEXT DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table interests
INSERT INTO interests (id, user_id, interest_area, resume_id, quiz_answers) VALUES
(1, 2, 'Creative', NULL, NULL),
(2, 2, 'Technical', NULL, NULL),
(3, 2, 'Data', NULL, NULL),
(4, 2, 'Technical', 4, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Technical", "q6": "Technical", "q7": "Technical", "q8": "Creative", "q9": "Technical", "q10": "Technical"}'),
(5, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(6, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(7, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(8, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(9, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(10, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(11, 2, 'Technical', 10, '{"q1": "Technical", "q2": "Technical", "q3": "Business", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(12, 2, 'Data', 12, '{"q1": "Data", "q2": "Management", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Data", "q7": "Data", "q8": "Data", "q9": "Data", "q10": "Data"}'),
(13, 2, 'Data', 12, '{"q1": "Data", "q2": "Management", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Data", "q7": "Data", "q8": "Data", "q9": "Data", "q10": "Data"}'),
(14, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(15, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(16, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(17, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(18, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(19, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(20, 2, 'Data', 12, '{"q1": "Data", "q2": "Management", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Data", "q7": "Data", "q8": "Data", "q9": "Data", "q10": "Data"}'),
(21, 2, 'Technical', 13, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Data", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(22, 2, 'Technical', 15, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Technical", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(23, 2, 'Technical', 15, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Technical", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Technical", "q10": "Technical"}'),
(24, 2, 'Technical', 16, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Creative", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Data", "q10": "Technical"}'),
(25, 2, 'Technical', 16, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Creative", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Data", "q10": "Technical"}'),
(26, 2, 'Technical', 16, '{"q1": "Technical", "q2": "Technical", "q3": "Data", "q4": "Data", "q5": "Creative", "q6": "Technical", "q7": "Technical", "q8": "Technical", "q9": "Data", "q10": "Technical"}');

-- Table structure for table jobs
CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) DEFAULT NULL,
  company VARCHAR(255) DEFAULT NULL,
  location VARCHAR(255) DEFAULT NULL,
  job_type VARCHAR(100) DEFAULT NULL,
  salary INTEGER DEFAULT NULL,
  url VARCHAR(255) DEFAULT NULL,
  description TEXT DEFAULT NULL,
  requirements VARCHAR(255) DEFAULT NULL,
  posted_at TIMESTAMP DEFAULT NULL,
  career_id INTEGER DEFAULT NULL,
  FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE SET NULL
);

-- Dumping data for table jobs
INSERT INTO jobs (id, title, company, location, job_type, salary, url, description, requirements, posted_at, career_id) VALUES
(1, 'Junior Data Analyst', 'Infosys', 'Bangalore', 'Full-time', 60000, 'https://www.infosys.com/careers/job1', 'Analyze business data and create reports using SQL and Excel.', 'Python, Django, REST APIs', '2025-07-22 13:15:23', 1),
(2, 'Business Data Analyst', 'Tata Consultancy Services', 'Mumbai', 'Part-time', 30000, 'https://www.tcs.com/careers/job2', 'Work with business teams to interpret data and provide insights.', 'Java, Spring Boot, Microservices', '2025-07-22 13:15:23', 1),
(3, 'Data Analyst Intern', 'Wipro', 'Hyderabad', 'Remote', 80000, 'https://www.wipro.com/careers/job3', 'Assist in data cleaning and visualization projects.', 'JavaScript, React, Redux', '2025-07-22 13:15:23', 1),
(4, 'SQL Data Analyst', 'Accenture', 'Pune', 'Internship', 15000, 'https://www.accenture.com/careers/job4', 'Develop SQL queries and dashboards for business intelligence.', 'SQL, Data Analysis, Excel', '2025-07-22 13:15:23', 1),
(5, 'Software Developer', 'Google', 'Bangalore', 'Full-time', 70000, 'https://careers.google.com/job6', 'Develop scalable web applications using Java and Python.', 'AWS, Docker, CI/CD', '2025-07-22 13:15:23', 2),
(6, 'Backend Developer', 'Microsoft', 'Hyderabad', 'Part-time', 25000, 'https://careers.microsoft.com/job7', 'Build REST APIs and microservices for cloud platforms.', 'HTML, CSS, Bootstrap', '2025-07-22 13:15:23', 2),
(7, 'Full Stack Developer', 'Zoho', 'Chennai', 'Remote', 90000, 'https://www.zoho.com/careers/job8', 'Work on both frontend and backend for SaaS products.', 'Node.js, Express, MongoDB', '2025-07-22 13:15:23', 2),
(8, 'Junior Java Developer', 'Cognizant', 'Pune', 'Internship', 12000, 'https://careers.cognizant.com/job9', 'Support enterprise Java applications and bug fixes.', 'C#, .NET, Azure', '2025-07-22 13:15:23', 2),
(9, 'UI Designer', 'Adobe', 'Bangalore', 'Full-time', 65000, 'https://www.adobe.com/careers/job11', 'Design user interfaces for web and mobile apps using Figma.', 'Python, Machine Learning, Pandas', '2025-07-22 13:15:23', 3),
(10, 'UX Researcher', 'Flipkart', 'Bangalore', 'Part-time', 28000, 'https://www.flipkartcareers.com/job12', 'Conduct user research and usability testing.', 'PHP, Laravel, MySQL', '2025-07-22 13:15:23', 3),
(11, 'Product Designer', 'Swiggy', 'Bangalore', 'Remote', 85000, 'https://careers.swiggy.com/job13', 'Work with product teams to design intuitive experiences.', 'Android, Kotlin, Firebase', '2025-07-22 13:15:23', 3),
(12, 'Web Designer', 'Freshworks', 'Chennai', 'Internship', 18000, 'https://www.freshworks.com/careers/job14', 'Create responsive web layouts and graphics.', 'iOS, Swift, UIKit', '2025-07-22 13:15:23', 3),
(13, 'Project Manager', 'L&T Infotech', 'Mumbai', 'Full-time', 72000, 'https://www.lntinfotech.com/careers/job15', 'Lead software development projects and manage teams.', 'UI/UX Design, Figma, Adobe XD', '2025-07-22 13:15:23', 4),
(14, 'Agile Project Coordinator', 'Mindtree', 'Bangalore', 'Part-time', 32000, 'https://www.mindtree.com/careers/job16', 'Coordinate agile sprints and project deliverables.', 'Project Management, Agile, Jira', '2025-07-22 13:15:23', 4),
(15, 'IT Project Manager', 'IBM', 'Pune', 'Remote', 95000, 'https://www.ibm.com/careers/job17', 'Oversee IT infrastructure and software projects.', 'Linux, Shell Scripting, Networking', '2025-07-22 13:15:23', 4),
(16, 'Junior Project Manager', 'HCL Technologies', 'Noida', 'Internship', 16000, 'https://www.hcltech.com/careers/job18', 'Assist in project planning and client communication.', 'Python, Data Visualization, Tableau', '2025-07-22 13:15:23', 4),
(17, 'Technical Support Engineer', 'Dell', 'Hyderabad', 'Full-time', 68000, 'https://jobs.dell.com/job19', 'Provide technical support for hardware and software issues.', 'JavaScript, Vue.js, REST APIs', '2025-07-22 13:15:23', 5),
(18, 'Customer Support Specialist', 'Amazon', 'Bangalore', 'Part-time', 27000, 'https://www.amazon.jobs/job20', 'Resolve customer queries and troubleshoot issues.', 'Ruby, Rails, PostgreSQL', '2025-07-22 13:15:23', 5),
(19, 'IT Helpdesk Engineer', 'Wipro', 'Pune', 'Remote', 87000, 'https://www.wipro.com/careers/job21', 'Support internal IT systems and users.', 'Go, Microservices, Kubernetes', '2025-07-22 13:15:23', 5),
(20, 'Support Analyst', 'TCS', 'Chennai', 'Internship', 14000, 'https://www.tcs.com/careers/job22', 'Monitor and resolve support tickets for enterprise clients.', 'C++, Embedded Systems, RTOS', '2025-07-22 13:15:23', 5),
(21, 'Cloud Engineer', 'Amazon Web Services', 'Bangalore', 'Full-time', 75000, 'https://aws.amazon.com/careers/job23', 'Deploy and manage cloud infrastructure on AWS.', 'Salesforce, CRM, Apex', '2025-07-22 13:15:23', 6),
(22, 'DevOps Engineer', 'Google Cloud', 'Hyderabad', 'Part-time', 35000, 'https://cloud.google.com/careers/job24', 'Automate CI/CD pipelines and cloud deployments.', 'SEO, Google Analytics, Content Marketing', '2025-07-22 13:15:23', 6),
(23, 'Azure Cloud Specialist', 'Microsoft', 'Noida', 'Remote', 99000, 'https://careers.microsoft.com/job25', 'Design and implement solutions on Azure.', 'Python, Flask, SQLAlchemy', '2025-07-22 13:15:23', 6),
(24, 'Cloud Solutions Architect', 'Infosys', 'Pune', 'Internship', 17000, 'https://www.infosys.com/careers/job26', 'Architect scalable cloud solutions for clients.', 'Java, Android, SQLite', '2025-07-22 13:15:23', 6),
(25, 'Business Analyst', 'EY', 'Gurgaon', 'Full-time', 66000, 'https://www.ey.com/careers/job27', 'Analyze business processes and recommend improvements.', 'React Native, Mobile Apps, Redux', '2025-07-22 13:15:23', 7),
(26, 'Junior Business Analyst', 'Deloitte', 'Mumbai', 'Part-time', 26000, 'https://www2.deloitte.com/careers/job28', 'Support business analysis and documentation.', 'Business Analysis, UML, BPMN', '2025-07-22 13:15:23', 7),
(27, 'Data Business Analyst', 'KPMG', 'Bangalore', 'Remote', 83000, 'https://home.kpmg/careers/job29', 'Work with data teams to deliver business insights.', 'QA Testing, Selenium, JIRA', '2025-07-22 13:15:23', 7),
(28, 'IT Business Analyst', 'Accenture', 'Hyderabad', 'Internship', 11000, 'https://www.accenture.com/careers/job30', 'Bridge business requirements with IT solutions.', 'DevOps, Jenkins, Ansible', '2025-07-22 13:15:23', 7),
(29, 'Cybersecurity Analyst', 'Cisco', 'Bangalore', 'Full-time', 71000, 'https://jobs.cisco.com/job31', 'Monitor and respond to security incidents.', 'Cloud Security, AWS, IAM', '2025-07-22 13:15:23', 8),
(30, 'Security Engineer', 'Palo Alto Networks', 'Mumbai', 'Part-time', 34000, 'https://www.paloaltonetworks.com/careers/job32', 'Implement and manage security solutions.', 'Python, NLP, spaCy', '2025-07-22 13:15:23', 8),
(31, 'Penetration Tester', 'HackerOne', 'Remote', 'Remote', 92000, 'https://www.hackerone.com/careers/job33', 'Conduct penetration tests and vulnerability assessments.', 'Data Engineering, ETL, Spark', '2025-07-22 13:15:23', 8),
(32, 'Network Security Specialist', 'Wipro', 'Chennai', 'Internship', 15500, 'https://www.wipro.com/careers/job34', 'Secure enterprise networks and perform audits.', 'Customer Support, Ticketing Systems, Communication', '2025-07-22 13:15:23', 8);

-- Table structure for table job_alerts
CREATE TABLE job_alerts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  keyword VARCHAR(255) DEFAULT NULL,
  company VARCHAR(255) DEFAULT NULL,
  location VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table job_alerts
INSERT INTO job_alerts (id, user_id, keyword, company, location, created_at) VALUES
(5, 2, 'Software Developer', 'Google', 'Bangalore', '2025-07-22 13:32:53'),
(6, 2, 'Backend Developer', '', '', '2025-07-22 13:34:06');

-- Table structure for table job_applications
CREATE TABLE job_applications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  job_id INTEGER DEFAULT NULL,
  status VARCHAR(50) DEFAULT NULL,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  notes TEXT DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Table structure for table mentors
CREATE TABLE mentors (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  expertise VARCHAR(255) DEFAULT NULL,
  bio TEXT DEFAULT NULL,
  contact VARCHAR(255) DEFAULT NULL,
  profile_pic VARCHAR(255) DEFAULT NULL
);

-- Dumping data for table mentors
INSERT INTO mentors (id, name, expertise, bio, contact, profile_pic) VALUES
(1, 'Dr. Priya Sharma', 'Data Science, Machine Learning', '10+ years in data science, ex-Google, loves mentoring students.', 'priya.sharma@email.com', NULL),
(2, 'John Doe', 'Web Development, Startups', 'Full-stack developer and startup founder. Passionate about teaching coding.', 'john.doe@email.com', NULL);

-- Table structure for table notifications
CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  message TEXT DEFAULT NULL,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table notifications
INSERT INTO notifications (id, user_id, message, is_read, created_at) VALUES
(1, 1, 'Welcome to Career Guidance AI!', FALSE, '2025-07-18 06:26:22'),
(2, 1, 'Your resume was parsed successfully.', FALSE, '2025-07-18 06:26:22'),
(3, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-21 17:33:16'),
(4, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-21 17:52:03'),
(5, 2, 'You started the Data Analyst career plan. Good luck!', TRUE, '2025-07-21 17:53:29'),
(6, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:20:16'),
(7, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:22:33'),
(8, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:29:25'),
(9, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:33:30'),
(10, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:41:00'),
(11, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:43:26'),
(12, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 05:51:23'),
(13, 2, 'You started the Software Developer career plan. Good luck!', TRUE, '2025-07-22 05:54:48'),
(14, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', TRUE, '2025-07-22 05:54:57'),
(15, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', TRUE, '2025-07-22 05:55:09'),
(16, 2, 'You started the Software Developer career plan. Good luck!', TRUE, '2025-07-22 06:04:42'),
(17, 2, 'You started the Software Developer career plan. Good luck!', TRUE, '2025-07-22 06:05:11'),
(18, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', TRUE, '2025-07-22 06:08:00'),
(19, 2, 'Congratulations! You completed the milestone: Learn Excel & SQL in Data Analyst.', TRUE, '2025-07-22 07:13:10'),
(20, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 07:14:18'),
(21, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 08:07:08'),
(22, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-22 09:21:55'),
(23, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-25 12:37:36'),
(24, 2, 'You started the Software Developer career plan. Good luck!', TRUE, '2025-07-25 12:40:54'),
(25, 2, 'You started the Software Developer career plan. Good luck!', TRUE, '2025-07-25 16:58:16'),
(26, 2, 'Congratulations! You completed the milestone: Complete Git & GitHub Course in Software Developer.', TRUE, '2025-07-25 16:59:41'),
(27, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2025-07-25 17:50:41'),
(28, 2, 'You started the Software Developer career plan. Good luck!', TRUE, '2025-07-25 18:03:25'),
(29, 2, 'You started the Cloud Engineer career plan. Good luck!', TRUE, '2025-09-21 05:00:56'),
(30, 2, 'Your resume was uploaded and parsed successfully.', TRUE, '2026-01-24 06:04:40'),
(31, 2, 'Congratulations! You completed the milestone: Learn Excel & SQL in Data Analyst.', FALSE, '2026-01-24 06:14:07'),
(32, 2, 'Congratulations! You completed the milestone: Master Data Visualization Tools in Data Analyst.', FALSE, '2026-01-24 06:14:24'),
(33, 2, 'Your resume was uploaded and parsed successfully.', FALSE, '2026-01-24 07:21:53'),
(34, 2, 'You started the Software Developer career plan. Good luck!', FALSE, '2026-01-24 07:22:55'),
(35, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', FALSE, '2026-01-24 07:23:17');

-- Table structure for table password_reset_tokens
CREATE TABLE password_reset_tokens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  token VARCHAR(255) DEFAULT NULL,
  expires_at TIMESTAMP DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table password_reset_tokens
INSERT INTO password_reset_tokens (id, user_id, token, expires_at) VALUES
(1, 2, 'wH9nlU1j3rA0VVNUAZb4LhmOl7A0S7cuhzV8I8P_UYM', '2025-07-23 12:37:21'),
(2, 2, 'ELZSGTds6QG8KbMy-kjNyt8gIgnBcrmalFq9YEt4yyA', '2025-07-23 12:38:18'),
(3, 2, 'N7xI8GvbHmPokhU9rAbdQMwZXjl6CSsQmZfZ5iY8bbE', '2025-07-23 12:40:24'),
(4, 2, 'Q4ESymFFlnXmp40KSB4_kBx4uP63CYWajOQ0QvW6MEY', '2025-07-23 12:40:26');

-- Table structure for table projects
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT DEFAULT NULL,
  skills VARCHAR(255) DEFAULT NULL,
  link VARCHAR(255) DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table projects
INSERT INTO projects (id, user_id, title, description, skills, link, created_at) VALUES
(2, 2, 'Build a Personal Portfolio Website', 'Choose a tech stack (HTML/CSS/JS, Flask, Django, etc.), Design the layout and sections (About, Projects, Contact), Implement navigation and responsive design, Deploy on GitHub Pages, Netlify, or Heroku', 'Java, Python, Git', '', '2025-07-22 06:24:02'),
(3, 2, 'Create a REST API with Flask', 'Set up a Flask project, Design API endpoints (CRUD), Connect to a database (SQLite/MySQL), Test with Postman and document the API', 'Java, Python, Git', '', '2025-07-22 06:24:07');

-- Table structure for table recommendations
CREATE TABLE recommendations (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  recommended_career_id INTEGER DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (recommended_career_id) REFERENCES careers(id)
);

-- Table structure for table resumes_builder
CREATE TABLE resumes_builder (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  title VARCHAR(255) DEFAULT NULL,
  summary TEXT DEFAULT NULL,
  education TEXT DEFAULT NULL,
  experience TEXT DEFAULT NULL,
  skills TEXT DEFAULT NULL,
  projects TEXT DEFAULT NULL,
  certifications TEXT DEFAULT NULL,
  contact_info TEXT DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dumping data for table resumes_builder
INSERT INTO resumes_builder (id, user_id, title, summary, education, experience, skills, projects, certifications, contact_info, created_at) VALUES
(2, 2, 'PRIYANSHU PATEL (Software Developer)', 'Skilled Software and Web Developer with experience in building responsive and real-time web applications
using HTML, CSS, JavaScript, PHP, Java (JSP & Servlets), and MySQL. Strong problem-solving ability with
hands-on project experience and a solid academic foundation (B.Tech CSE – 9.92 CGPA). Passionate about
writing clean code, learning new technologies, and contributing to impactful, user-focused solutions.', 'Bachelor of Technology in Computer Science (9.92 CGPA)
Indus University, Ahmedabad
Aug 2023 - Present
Diploma in Information Technology (9.45 CGPA)
Government Polytechnic, Ahmedabad
Aug 2020 – May 2023', '• Internship 1:
o Company : InfoLabz IT Services Pvt. Ltd.
o Technology : Python with Django, IOT
• Internship 2:
o Company : Indus University (Data Analytics Bootcamp)
o Technology : python, PowerBI, MS Excel
• Certification 1:
o Platform : Udemy (Web developer Bootcamp)
o Technology : HTML, CSS, JavaScript, React, Node, MongoDB, MySql', '• Programming Languages: C, C++, Java, Python, C#, VB.NET
• Web Development: HTML, CSS, Bootstrap, SASS, JavaScript, React.js, PHP, ASP.NET
• Mobile Development: Android
• Databases: MySQL, MongoDB, SQLite
• Tools & Platforms: Git, GitHub, XAMPP, GlassFish, MS Excel, Power BI, Cursor, Windsurf,
Lovable, Claude, dbdiagram.
• Core Concepts: Data Structures, Object-Oriented Programming (OOP),DBMS.', 'Rate-IT Web Application | GitHub
o Built a real world multiple Company review System based on User feedback and Poll with real-time
updates.
o Tech stack: HTML, CSS, JavaScript, SASS, JSP, Servlet, MySql.
Personal-Life Expense-Tracker| GitHub
o Developed a live Expense manager for our daily life and for family member for monthly tracking
based on budget and expense.
o Used java language such as using JSP, Servlet, HTML, CSS, javascript and MySql for real-time data
updates.
FlipKart Clone :
o Built Frontend and Backend for online shopping E-Commerce app.
o Used HTMl, CSS, JavaScript, PHP and MySql.
ChatAPI :
o Developed Real-Time Chat API for Enabling seamless user communication with efficient message
and database handling.
o Used HTML, CSS, BootStrap, JavaScript, Servlet, JSP and MySql.', 'Certification 1:
o Platform : Udemy (Web developer Bootcamp)
o Technology : HTML, CSS, JavaScript, React, Node, MongoDB, MySql', ' Ahmedabad, Gujarat
+91 9023463169
priyanshu.patel1609@gmail.com
', '2025-07-22 09:32:35'),
(3, 2, 'Vansh Pujara', 'Skilled Software and Web Developer with hands-on experience in building responsive, dynamic,
and real-time web applications using HTML, CSS, JavaScript, PHP, Java (JSP & Servlets), and
MySQL. Strong problem-solving abilities backed by practical project work and an excellent
academic record (B.Tech CSE – 9.88 CGPA). Passionate about writing clean, efficient code,
exploring new technologies, and delivering impactful, user-centric solutions', 'INDUS UNIVERSITY, AHMEDABAD
Bachelor of Technology in
Computer Science
CGPA: 9.88 / 10
2023 – Present
2020 – 2023
GOVERNMENT POLYTECHNIC,
AHMEDABAD
Diploma in Information Technology
CGPA: 9.45 / 10', 'Jul 2025 – Present
Lumos Logic
Web Development & Automation Intern
Developed responsive web interfaces and app screens
using FlutterFlow.
Built Playwright automation scripts for UI testing and
workflow validation.
Performed data scraping for structured dataset extraction.
Created n8n automation workflows for social media
posting and process automation.', 'Programming: C, C++
, Java,
Python, C#
Web: HTML, CSS, Bootstrap,
SASS, JavaScript, React.js,
PHP, ASP.NET, JSP & Servlets
Mobile: Android, FlutterFlow
Databases: MySQL, SQLite,
PostgreSQL
Tools: Git, GitHub, Excel,
Power BI, Cursor, Windsurf,
Lovable, Claude, DbDiagram
Automation: n8n Software
Core: DS, OOP, DBMS', 'Rate-IT Web Application | GitHub
Built a multi-company review & polling system with real-time
updates.
Tech: HTML, CSS, JavaScript, SASS, JSP, Servlet, MySQL
Personal Expense Tracker | GitHub
Developed a family-oriented expense manager with real-time
budget tracking.
Tech: JSP, Servlet, HTML, CSS, JavaScript, MySQL
Flipkart Clone
Created full-stack e-commerce web app (f rontend + backend).
Tech: HTML, CSS, JavaScript, PHP, MySQL
AI-Powered Career Guidance System
Built a website where users upload their resume and get
resume score, mistakes, job recommendations, suggested
projects, and an integrated resume builder that exports
resumes as PDF.
Tech: Python (Flask), HTML, CSS, JavaScript, MySQL', '', '+91 90234 63169
priyanshu.patel1609@gmail.com
Ahmedabad, Gujarat
in
www.linkedin.com/in/priyanshupatel16
https://github.com/Priyanshu1609patel', '2026-01-24 06:12:55');

-- Table structure for table saved_careers
CREATE TABLE saved_careers (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  career_id INTEGER DEFAULT NULL,
  title VARCHAR(255) DEFAULT NULL,
  category VARCHAR(255) DEFAULT NULL,
  required_skills TEXT DEFAULT NULL,
  description TEXT DEFAULT NULL,
  path TEXT DEFAULT NULL,
  notes TEXT DEFAULT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE
);

-- Dumping data for table saved_careers
INSERT INTO saved_careers (id, user_id, career_id, title, category, required_skills, description, path, notes) VALUES
(1, 2, 2, 'Software Developer', 'Technical', 'Java, Python, Git', 'Develop applications using programming languages', 'Start with B.Tech in CS/IT → Learn Programming → Internship → Junior Developer → Senior Developer', NULL);

-- Table structure for table saved_jobs
CREATE TABLE saved_jobs (
  id SERIAL PRIMARY KEY,
  user_id INTEGER DEFAULT NULL,
  job_id INTEGER DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'Not Applied' CHECK (status IN ('Not Applied', 'Applied', 'Interview', 'Offer', 'Rejected')),
  notes TEXT DEFAULT NULL,
  saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, job_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Dumping data for table saved_jobs
INSERT INTO saved_jobs (id, user_id, job_id, status, notes, saved_at) VALUES
(6, 2, 7, 'Not Applied', NULL, '2025-07-25 17:01:24');

-- Additional tables for peer groups functionality
CREATE TABLE peer_groups (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  image VARCHAR(255),
  created_by INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE group_members (
  id SERIAL PRIMARY KEY,
  group_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(group_id, user_id),
  FOREIGN KEY (group_id) REFERENCES peer_groups(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Reset sequences to match the inserted data
SELECT setval('admin_id_seq', (SELECT MAX(id) FROM admin));
SELECT setval('careers_id_seq', (SELECT MAX(id) FROM careers));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('resumes_id_seq', (SELECT MAX(id) FROM resumes));
SELECT setval('career_progress_id_seq', (SELECT MAX(id) FROM career_progress));
SELECT setval('interests_id_seq', (SELECT MAX(id) FROM interests));
SELECT setval('jobs_id_seq', (SELECT MAX(id) FROM jobs));
SELECT setval('job_alerts_id_seq', (SELECT MAX(id) FROM job_alerts));
SELECT setval('mentors_id_seq', (SELECT MAX(id) FROM mentors));
SELECT setval('notifications_id_seq', (SELECT MAX(id) FROM notifications));
SELECT setval('password_reset_tokens_id_seq', (SELECT MAX(id) FROM password_reset_tokens));
SELECT setval('projects_id_seq', (SELECT MAX(id) FROM projects));
SELECT setval('resumes_builder_id_seq', (SELECT MAX(id) FROM resumes_builder));
SELECT setval('saved_careers_id_seq', (SELECT MAX(id) FROM saved_careers));
SELECT setval('saved_jobs_id_seq', (SELECT MAX(id) FROM saved_jobs));