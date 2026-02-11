-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 23, 2025 at 09:09 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `career_guidance_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `plain_password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`, `plain_password`) VALUES
(2, 'admin', 'pbkdf2:sha256:600000$SflKipodS1b7DrlN$b0aed58e712159f3b744693c855349b5276a9b27435a518690024fb4b2bf35a1', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `careers`
--

CREATE TABLE `careers` (
  `id` int(11) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `required_skills` text DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `salary_range` varchar(50) DEFAULT NULL,
  `courses` text DEFAULT NULL,
  `path` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `careers`
--

INSERT INTO `careers` (`id`, `title`, `description`, `required_skills`, `category`, `salary_range`, `courses`, `path`) VALUES
(1, 'Data Analyst', 'Analyze and interpret data to support business decisions', 'Python, SQL, Excel', 'Data', '6-12 LPA', 'Python for Data Analysis, SQL for Data Science', 'Start with B.Sc/B.Tech → Learn Python & SQL → Build Projects → Internship → Data Analyst'),
(2, 'Software Developer', 'Develop applications using programming languages', 'Java, Python, Git', 'Technical', '5-10 LPA', 'Java Programming Masterclass, GitHub Essentials', 'Start with B.Tech in CS/IT → Learn Programming → Internship → Junior Developer → Senior Developer'),
(3, 'UI/UX Designer', 'Design intuitive user interfaces and experiences', 'Figma, HTML, CSS', 'Creative', '4-9 LPA', 'UI Design Fundamentals, Web Design with HTML/CSS', 'Start with Design Degree/Certification → Build Portfolio → Internship → UI/UX Designer'),
(4, 'Project Manager', 'Lead project teams to achieve goals', 'Leadership, Agile, Communication', 'Management', '7-15 LPA', 'Agile Project Management, Communication for Leaders', 'Start with B.Tech/BBA → Work as Analyst/Coordinator → PMP Certification → Project Manager'),
(5, 'Support Engineer', 'Resolve technical issues for clients', 'Troubleshooting, Networking, Windows/Linux', 'Support', '3-8 LPA', 'Tech Support Fundamentals, CompTIA A+', 'Start with B.Sc IT/B.Tech → Learn Networking Basics → Internship → Support Engineer'),
(6, 'Cloud Engineer', 'Design and manage cloud infrastructure and services', 'AWS, Azure, Linux, Python', 'Technical', '8-18 LPA', 'AWS Certified Solutions Architect, Azure Fundamentals', 'Start with B.Tech → Learn Cloud Platforms → Certification → Cloud Engineer'),
(7, 'Business Analyst', 'Bridge business needs with technology solutions', 'Excel, SQL, Communication, Analysis', 'Business', '6-14 LPA', 'Business Analysis Fundamentals, SQL for Business', 'Start with BBA/MBA → Learn Analysis Tools → Internship → Business Analyst'),
(8, 'Cybersecurity Specialist', 'Protect systems and networks from cyber threats', 'Networking, Security, Python, Linux', 'Security', '7-16 LPA', 'Certified Ethical Hacker, CompTIA Security+', 'Start with B.Tech → Learn Security Basics → Certification → Cybersecurity Specialist');

-- --------------------------------------------------------

--
-- Table structure for table `career_milestones`
--

CREATE TABLE `career_milestones` (
  `id` int(11) NOT NULL,
  `career_id` int(11) NOT NULL,
  `milestone` varchar(255) NOT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `career_progress`
--

CREATE TABLE `career_progress` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `career_id` int(11) DEFAULT NULL,
  `milestone` varchar(255) DEFAULT NULL,
  `status` enum('Not Started','In Progress','Completed') DEFAULT 'Not Started',
  `resume_id` int(11) DEFAULT NULL,
  `note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `career_progress`
--

INSERT INTO `career_progress` (`id`, `user_id`, `career_id`, `milestone`, `status`, `resume_id`, `note`) VALUES
(35, 2, 1, 'Learn Excel & SQL', 'Completed', NULL, NULL),
(36, 2, 1, 'Master Data Visualization Tools', 'Not Started', NULL, NULL),
(37, 2, 1, 'Do Case Study Projects', 'Not Started', NULL, NULL),
(38, 2, 1, 'Internship in Analytics', 'Not Started', NULL, NULL),
(39, 2, 1, 'Prepare Resume', 'Not Started', NULL, NULL),
(40, 2, 1, 'Apply for Analyst Roles', 'Not Started', NULL, NULL),
(47, 2, 2, 'Learn Programming Language', 'Completed', 10, NULL),
(48, 2, 2, 'Complete Git & GitHub Course', 'Not Started', 10, NULL),
(49, 2, 2, 'Build Portfolio Website', 'Not Started', 10, NULL),
(50, 2, 2, 'Contribute to Open Source', 'Not Started', 10, NULL),
(51, 2, 2, 'Do Internship', 'Not Started', 10, NULL),
(52, 2, 2, 'Apply for Developer Jobs', 'Not Started', 10, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `custom_paths`
--

CREATE TABLE `custom_paths` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `steps` text DEFAULT NULL,
  `shared` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `interests`
--

CREATE TABLE `interests` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `interest_area` varchar(100) DEFAULT NULL,
  `resume_id` int(11) DEFAULT NULL,
  `quiz_answers` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `interests`
--

INSERT INTO `interests` (`id`, `user_id`, `interest_area`, `resume_id`, `quiz_answers`) VALUES
(1, 2, 'Creative', NULL, NULL),
(2, 2, 'Technical', NULL, NULL),
(3, 2, 'Data', NULL, NULL),
(4, 2, 'Technical', 4, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Data\", \"q4\": \"Data\", \"q5\": \"Technical\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Creative\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(5, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(6, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(7, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(8, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(9, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(10, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(11, 2, 'Technical', 10, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Business\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(12, 2, 'Data', 12, '{\"q1\": \"Data\", \"q2\": \"Management\", \"q3\": \"Data\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Data\", \"q7\": \"Data\", \"q8\": \"Data\", \"q9\": \"Data\", \"q10\": \"Data\"}'),
(13, 2, 'Data', 12, '{\"q1\": \"Data\", \"q2\": \"Management\", \"q3\": \"Data\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Data\", \"q7\": \"Data\", \"q8\": \"Data\", \"q9\": \"Data\", \"q10\": \"Data\"}'),
(14, 2, 'Technical', 13, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Data\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(15, 2, 'Technical', 13, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Data\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}'),
(16, 2, 'Technical', 13, '{\"q1\": \"Technical\", \"q2\": \"Technical\", \"q3\": \"Data\", \"q4\": \"Data\", \"q5\": \"Data\", \"q6\": \"Technical\", \"q7\": \"Technical\", \"q8\": \"Technical\", \"q9\": \"Technical\", \"q10\": \"Technical\"}');

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `company` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `job_type` varchar(100) DEFAULT NULL,
  `salary` int(11) DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `requirements` varchar(255) DEFAULT NULL,
  `posted_at` datetime DEFAULT NULL,
  `career_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `jobs`
--

INSERT INTO `jobs` (`id`, `title`, `company`, `location`, `job_type`, `salary`, `url`, `description`, `requirements`, `posted_at`, `career_id`) VALUES
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

-- --------------------------------------------------------

--
-- Table structure for table `job_alerts`
--

CREATE TABLE `job_alerts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `keyword` varchar(255) DEFAULT NULL,
  `company` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `job_alerts`
--

INSERT INTO `job_alerts` (`id`, `user_id`, `keyword`, `company`, `location`, `created_at`) VALUES
(5, 2, 'Software Developer', 'Google', 'Bangalore', '2025-07-22 13:32:53'),
(6, 2, 'Backend Developer', '', '', '2025-07-22 13:34:06');

-- --------------------------------------------------------

--
-- Table structure for table `job_applications`
--

CREATE TABLE `job_applications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `job_id` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `applied_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mentors`
--

CREATE TABLE `mentors` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `expertise` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `contact` varchar(255) DEFAULT NULL,
  `profile_pic` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `mentors`
--

INSERT INTO `mentors` (`id`, `name`, `expertise`, `bio`, `contact`, `profile_pic`) VALUES
(1, 'Dr. Priya Sharma', 'Data Science, Machine Learning', '10+ years in data science, ex-Google, loves mentoring students.', 'priya.sharma@email.com', NULL),
(2, 'John Doe', 'Web Development, Startups', 'Full-stack developer and startup founder. Passionate about teaching coding.', 'john.doe@email.com', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `message`, `is_read`, `created_at`) VALUES
(1, 1, 'Welcome to Career Guidance AI!', 0, '2025-07-18 06:26:22'),
(2, 1, 'Your resume was parsed successfully.', 0, '2025-07-18 06:26:22'),
(3, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-21 17:33:16'),
(4, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-21 17:52:03'),
(5, 2, 'You started the Data Analyst career plan. Good luck!', 1, '2025-07-21 17:53:29'),
(6, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:20:16'),
(7, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:22:33'),
(8, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:29:25'),
(9, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:33:30'),
(10, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:41:00'),
(11, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:43:26'),
(12, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 05:51:23'),
(13, 2, 'You started the Software Developer career plan. Good luck!', 1, '2025-07-22 05:54:48'),
(14, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', 1, '2025-07-22 05:54:57'),
(15, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', 1, '2025-07-22 05:55:09'),
(16, 2, 'You started the Software Developer career plan. Good luck!', 1, '2025-07-22 06:04:42'),
(17, 2, 'You started the Software Developer career plan. Good luck!', 1, '2025-07-22 06:05:11'),
(18, 2, 'Congratulations! You completed the milestone: Learn Programming Language in Software Developer.', 1, '2025-07-22 06:08:00'),
(19, 2, 'Congratulations! You completed the milestone: Learn Excel & SQL in Data Analyst.', 1, '2025-07-22 07:13:10'),
(20, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 07:14:18'),
(21, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 08:07:08'),
(22, 2, 'Your resume was uploaded and parsed successfully.', 1, '2025-07-22 09:21:55');

-- --------------------------------------------------------

--
-- Table structure for table `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `token` varchar(255) DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `password_reset_tokens`
--

INSERT INTO `password_reset_tokens` (`id`, `user_id`, `token`, `expires_at`) VALUES
(1, 2, 'wH9nlU1j3rA0VVNUAZb4LhmOl7A0S7cuhzV8I8P_UYM', '2025-07-23 12:37:21'),
(2, 2, 'ELZSGTds6QG8KbMy-kjNyt8gIgnBcrmalFq9YEt4yyA', '2025-07-23 12:38:18'),
(3, 2, 'N7xI8GvbHmPokhU9rAbdQMwZXjl6CSsQmZfZ5iY8bbE', '2025-07-23 12:40:24'),
(4, 2, 'Q4ESymFFlnXmp40KSB4_kBx4uP63CYWajOQ0QvW6MEY', '2025-07-23 12:40:26');

-- --------------------------------------------------------

--
-- Table structure for table `projects`
--

CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `skills` varchar(255) DEFAULT NULL,
  `link` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `projects`
--

INSERT INTO `projects` (`id`, `user_id`, `title`, `description`, `skills`, `link`, `created_at`) VALUES
(2, 2, 'Build a Personal Portfolio Website', 'Choose a tech stack (HTML/CSS/JS, Flask, Django, etc.), Design the layout and sections (About, Projects, Contact), Implement navigation and responsive design, Deploy on GitHub Pages, Netlify, or Heroku', 'Java, Python, Git', '', '2025-07-22 06:24:02'),
(3, 2, 'Create a REST API with Flask', 'Set up a Flask project, Design API endpoints (CRUD), Connect to a database (SQLite/MySQL), Test with Postman and document the API', 'Java, Python, Git', '', '2025-07-22 06:24:07');

-- --------------------------------------------------------

--
-- Table structure for table `recommendations`
--

CREATE TABLE `recommendations` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `recommended_career_id` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `resumes`
--

CREATE TABLE `resumes` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `skills` text DEFAULT NULL,
  `education` text DEFAULT NULL,
  `experience` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `resumes`
--

INSERT INTO `resumes` (`id`, `user_id`, `skills`, `education`, `experience`) VALUES
(12, 2, 'html, css, javascript, python', 'CSS, Diploma - Computer Engineering\nRK University, Laravel, HTML CSS JavaScript, Infosys Springboard\n, JavaScript, PHP, HTML, Computer Science and Engineering', '2023, 9724365924, 2020'),
(13, 2, 'git, leadership, javascript, html, django, communication, c++, excel, python, css, java', 'Government Polytechnic, Servlet, MS Excel, Power BI, E-Commerce, Object-Oriented Programming, HTML, BootStrap, PHP, MySql, JSP, Software Developer, React.js, PHP, Indus University, PowerBI, SASS, www.linkedin.com/in/priyanshupatel16 \n \n•, CSE, Bootstrap, JSP & Servlets, JavaScript, Personal-Life Expense-Tracker| GitHub \n● Developed, Information Technology, CSS', '2023, 2020, monthly, May 2023, 9023463169');

-- --------------------------------------------------------

--
-- Table structure for table `resumes_builder`
--

CREATE TABLE `resumes_builder` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `summary` text DEFAULT NULL,
  `education` text DEFAULT NULL,
  `experience` text DEFAULT NULL,
  `skills` text DEFAULT NULL,
  `projects` text DEFAULT NULL,
  `certifications` text DEFAULT NULL,
  `contact_info` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `resumes_builder`
--

INSERT INTO `resumes_builder` (`id`, `user_id`, `title`, `summary`, `education`, `experience`, `skills`, `projects`, `certifications`, `contact_info`, `created_at`) VALUES
(2, 2, 'PRIYANSHU PATEL (Software Developer)', 'Skilled Software and Web Developer with experience in building responsive and real-time web applications\r\nusing HTML, CSS, JavaScript, PHP, Java (JSP & Servlets), and MySQL. Strong problem-solving ability with\r\nhands-on project experience and a solid academic foundation (B.Tech CSE – 9.92 CGPA). Passionate about\r\nwriting clean code, learning new technologies, and contributing to impactful, user-focused solutions.', 'Bachelor of Technology in Computer Science (9.92 CGPA)\r\nIndus University, Ahmedabad\r\nAug 2023 - Present\r\nDiploma in Information Technology (9.45 CGPA)\r\nGovernment Polytechnic, Ahmedabad\r\nAug 2020 – May 2023', '• Internship 1:\r\no Company : InfoLabz IT Services Pvt. Ltd.\r\no Technology : Python with Django, IOT\r\n• Internship 2:\r\no Company : Indus University (Data Analytics Bootcamp)\r\no Technology : python, PowerBI, MS Excel\r\n• Certification 1:\r\no Platform : Udemy (Web developer Bootcamp)\r\no Technology : HTML, CSS, JavaScript, React, Node, MongoDB, MySql', '• Programming Languages: C, C++, Java, Python, C#, VB.NET\r\n• Web Development: HTML, CSS, Bootstrap, SASS, JavaScript, React.js, PHP, ASP.NET\r\n• Mobile Development: Android\r\n• Databases: MySQL, MongoDB, SQLite\r\n• Tools & Platforms: Git, GitHub, XAMPP, GlassFish, MS Excel, Power BI, Cursor, Windsurf,\r\nLovable, Claude, dbdiagram.\r\n• Core Concepts: Data Structures, Object-Oriented Programming (OOP),DBMS.', 'Rate-IT Web Application | GitHub\r\no Built a real world multiple Company review System based on User feedback and Poll with real-time\r\nupdates.\r\no Tech stack: HTML, CSS, JavaScript, SASS, JSP, Servlet, MySql.\r\nPersonal-Life Expense-Tracker| GitHub\r\no Developed a live Expense manager for our daily life and for family member for monthly tracking\r\nbased on budget and expense.\r\no Used java language such as using JSP, Servlet, HTML, CSS, javascript and MySql for real-time data\r\nupdates.\r\nFlipKart Clone :\r\no Built Frontend and Backend for online shopping E-Commerce app.\r\no Used HTMl, CSS, JavaScript, PHP and MySql.\r\nChatAPI :\r\no Developed Real-Time Chat API for Enabling seamless user communication with efficient message\r\nand database handling.\r\no Used HTML, CSS, BootStrap, JavaScript, Servlet, JSP and MySql.', 'Certification 1:\r\no Platform : Udemy (Web developer Bootcamp)\r\no Technology : HTML, CSS, JavaScript, React, Node, MongoDB, MySql', ' Ahmedabad, Gujarat\r\n+91 9023463169\r\npriyanshu.patel1609@gmail.com\r\n', '2025-07-22 09:32:35');

-- --------------------------------------------------------

--
-- Table structure for table `saved_careers`
--

CREATE TABLE `saved_careers` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `career_id` int(11) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `required_skills` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `path` text DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `saved_careers`
--

INSERT INTO `saved_careers` (`id`, `user_id`, `career_id`, `title`, `category`, `required_skills`, `description`, `path`, `notes`) VALUES
(1, 2, 2, 'Software Developer', 'Technical', 'Java, Python, Git', 'Develop applications using programming languages', 'Start with B.Tech in CS/IT → Learn Programming → Internship → Junior Developer → Senior Developer', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `saved_jobs`
--

CREATE TABLE `saved_jobs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `job_id` int(11) DEFAULT NULL,
  `status` enum('Not Applied','Applied','Interview','Offer','Rejected') DEFAULT 'Not Applied',
  `notes` text DEFAULT NULL,
  `saved_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `saved_jobs`
--

INSERT INTO `saved_jobs` (`id`, `user_id`, `job_id`, `status`, `notes`, `saved_at`) VALUES
(5, 2, 5, 'Not Applied', NULL, '2025-07-23 05:07:21');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `plain_password` varchar(255) DEFAULT NULL,
  `profile_pic` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `linkedin` varchar(255) DEFAULT NULL,
  `points` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `plain_password`, `profile_pic`, `bio`, `linkedin`, `points`) VALUES
(1, 'Test User', 'test@example.com', 'testpassword', 'testpassword', NULL, NULL, NULL, 0),
(2, 'Priyanshu Patel', 'ppriyanshu1609@gmail.com', 'pbkdf2:sha256:600000$6RLV20xPkIbEbQdU$e63384783100d7dd230a51673ee5a0a197a5d65ca50f7359e71b7a9dc070c2af', '12345678', 'profile_2_pexels-anjana-c-169994-674010.jpg', 'FULL STACK DEVELOPER', 'https://www.linkedin.com/in/priyanshupatel16/', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `careers`
--
ALTER TABLE `careers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `career_milestones`
--
ALTER TABLE `career_milestones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `career_id` (`career_id`);

--
-- Indexes for table `career_progress`
--
ALTER TABLE `career_progress`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `career_id` (`career_id`);

--
-- Indexes for table `custom_paths`
--
ALTER TABLE `custom_paths`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `interests`
--
ALTER TABLE `interests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `career_id` (`career_id`);

--
-- Indexes for table `job_alerts`
--
ALTER TABLE `job_alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `job_applications`
--
ALTER TABLE `job_applications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `job_id` (`job_id`);

--
-- Indexes for table `mentors`
--
ALTER TABLE `mentors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `recommendations`
--
ALTER TABLE `recommendations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `recommended_career_id` (`recommended_career_id`);

--
-- Indexes for table `resumes`
--
ALTER TABLE `resumes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `resumes_builder`
--
ALTER TABLE `resumes_builder`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `saved_careers`
--
ALTER TABLE `saved_careers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `career_id` (`career_id`);

--
-- Indexes for table `saved_jobs`
--
ALTER TABLE `saved_jobs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`,`job_id`),
  ADD KEY `job_id` (`job_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `careers`
--
ALTER TABLE `careers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `career_milestones`
--
ALTER TABLE `career_milestones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `career_progress`
--
ALTER TABLE `career_progress`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT for table `custom_paths`
--
ALTER TABLE `custom_paths`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `interests`
--
ALTER TABLE `interests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `jobs`
--
ALTER TABLE `jobs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT for table `job_alerts`
--
ALTER TABLE `job_alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `job_applications`
--
ALTER TABLE `job_applications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `mentors`
--
ALTER TABLE `mentors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `recommendations`
--
ALTER TABLE `recommendations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `resumes`
--
ALTER TABLE `resumes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `resumes_builder`
--
ALTER TABLE `resumes_builder`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `saved_careers`
--
ALTER TABLE `saved_careers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `saved_jobs`
--
ALTER TABLE `saved_jobs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `career_milestones`
--
ALTER TABLE `career_milestones`
  ADD CONSTRAINT `career_milestones_ibfk_1` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `career_progress`
--
ALTER TABLE `career_progress`
  ADD CONSTRAINT `career_progress_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `career_progress_ibfk_2` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `custom_paths`
--
ALTER TABLE `custom_paths`
  ADD CONSTRAINT `custom_paths_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `interests`
--
ALTER TABLE `interests`
  ADD CONSTRAINT `interests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `jobs`
--
ALTER TABLE `jobs`
  ADD CONSTRAINT `jobs_ibfk_1` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `job_alerts`
--
ALTER TABLE `job_alerts`
  ADD CONSTRAINT `job_alerts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `job_applications`
--
ALTER TABLE `job_applications`
  ADD CONSTRAINT `job_applications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `job_applications_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD CONSTRAINT `password_reset_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `projects`
--
ALTER TABLE `projects`
  ADD CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `recommendations`
--
ALTER TABLE `recommendations`
  ADD CONSTRAINT `recommendations_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `recommendations_ibfk_2` FOREIGN KEY (`recommended_career_id`) REFERENCES `careers` (`id`);

--
-- Constraints for table `resumes`
--
ALTER TABLE `resumes`
  ADD CONSTRAINT `resumes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `resumes_builder`
--
ALTER TABLE `resumes_builder`
  ADD CONSTRAINT `resumes_builder_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `saved_careers`
--
ALTER TABLE `saved_careers`
  ADD CONSTRAINT `saved_careers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `saved_careers_ibfk_2` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `saved_jobs`
--
ALTER TABLE `saved_jobs`
  ADD CONSTRAINT `saved_jobs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `saved_jobs_ibfk_2` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
