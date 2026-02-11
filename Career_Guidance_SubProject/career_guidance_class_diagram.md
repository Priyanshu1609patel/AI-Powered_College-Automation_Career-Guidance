# Career Guidance AI - Class Diagram

## System Architecture Overview

This is a comprehensive class diagram for the Career Guidance AI application, showing all major components, database entities, and their relationships.

```mermaid
classDiagram
    %% Main Application Classes
    class FlaskApp {
        -secret_key: str
        -upload_folder: str
        +get_db() Connection
        +add_notification(user_id, message)
        +load_unread_notifications()
        +get_course_links_for_skills(skills)
    }

    class ResumeParser {
        -nlp: spacy
        -COMMON_SKILLS: list
        +extract_text(file_path) str
        +extract_text_from_pdf(path) str
        +extract_text_from_docx(path) str
        +extract_resume_data(text) dict
    }

    class DatabaseConnection {
        -host: str
        -user: str
        -password: str
        -database: str
        +connect() Connection
    }

    %% Database Entities
    class User {
        +id: int
        +name: str
        +email: str
        +password: str
        +plain_password: str
        +profile_pic: str
        +bio: text
        +linkedin: str
        +points: int
    }

    class Admin {
        +id: int
        +username: str
        +password: str
        +plain_password: str
    }

    class Resume {
        +id: int
        +user_id: int
        +title: str
        +summary: text
        +education: text
        +experience: text
        +skills: text
        +projects: text
        +certifications: text
        +contact_info: text
        +created_at: timestamp
    }

    class Career {
        +id: int
        +title: str
        +description: text
        +required_skills: text
        +category: str
        +salary_range: str
        +courses: text
        +path: text
    }

    class Job {
        +id: int
        +title: str
        +company: str
        +location: str
        +job_type: str
        +salary: int
        +url: str
        +description: text
        +requirements: str
        +posted_at: datetime
        +career_id: int
    }

    class Interest {
        +id: int
        +user_id: int
        +interest_area: str
        +resume_id: int
        +quiz_answers: text
    }

    class CareerProgress {
        +id: int
        +user_id: int
        +career_id: int
        +milestone: str
        +status: str
        +resume_id: int
        +note: text
    }

    class SavedCareer {
        +id: int
        +user_id: int
        +career_id: int
        +title: str
        +category: str
        +required_skills: text
        +description: text
        +path: text
        +notes: text
    }

    class SavedJob {
        +id: int
        +user_id: int
        +job_id: int
        +status: enum
        +notes: text
        +saved_at: timestamp
    }

    class JobApplication {
        +id: int
        +user_id: int
        +job_id: int
        +status: str
        +applied_at: timestamp
        +notes: text
    }

    class JobAlert {
        +id: int
        +user_id: int
        +keyword: str
        +company: str
        +location: str
        +created_at: timestamp
    }

    class Mentor {
        +id: int
        +name: str
        +expertise: str
        +bio: text
        +contact: str
        +profile_pic: str
    }

    class Notification {
        +id: int
        +user_id: int
        +message: text
        +is_read: boolean
        +created_at: timestamp
    }

    class Feedback {
        +id: int
        +user_id: int
        +message: text
        +created_at: timestamp
    }

    class CustomPath {
        +id: int
        +user_id: int
        +title: str
        +description: text
        +steps: text
        +shared: boolean
        +created_at: timestamp
    }

    class CareerMilestone {
        +id: int
        +career_id: int
        +milestone: str
        +description: text
        +order: int
    }

    class PeerGroup {
        +id: int
        +name: str
        +description: text
        +created_by: int
        +created_at: timestamp
    }

    class GroupMember {
        +id: int
        +group_id: int
        +user_id: int
        +joined_at: timestamp
    }

    %% Service Classes
    class EmailService {
        +send_notification_email(user_email, message)
        +send_job_alert_email(user_email, job_details)
    }

    class PDFGenerator {
        +generate_resume_pdf(resume_data) bytes
        +create_canvas() Canvas
    }

    class NotificationService {
        +add_notification(user_id, message)
        +mark_as_read(notification_id)
        +get_unread_count(user_id) int
    }

    class CareerRecommendationEngine {
        +analyze_resume(resume_data) dict
        +match_skills(user_skills, required_skills) list
        +calculate_match_score(user_profile, career) float
        +get_course_recommendations(missing_skills) list
    }

    class JobMatchingService {
        +find_matching_jobs(user_profile) list
        +filter_jobs_by_criteria(criteria) list
        +send_job_alerts(user_id)
    }

    %% Controller Classes (Flask Routes)
    class AuthController {
        +register()
        +login()
        +logout()
        +forgot_password()
        +reset_password()
    }

    class ResumeController {
        +upload_resume()
        +build_resume()
        +edit_resume()
        +my_resumes()
        +download_resume()
    }

    class CareerController {
        +recommendations()
        +career_path()
        +save_career()
        +saved_careers()
        +track_progress()
    }

    class JobController {
        +jobs()
        +job_detail()
        +save_job()
        +my_jobs()
        +job_alerts()
        +apply_job()
    }

    class AdminController {
        +admin_login()
        +admin_dashboard()
        +manage_users()
        +manage_careers()
        +manage_jobs()
        +analytics()
        +manage_feedback()
    }

    class ProfileController {
        +profile()
        +update_profile()
        +upload_profile_pic()
    }

    class NotificationController {
        +notifications()
        +mark_notification_read()
    }

    class GroupController {
        +peer_groups()
        +create_group()
        +group_detail()
        +join_group()
        +leave_group()
    }

    class MentorController {
        +mentors()
        +manage_mentors()
    }

    %% Relationships
    User ||--o{ Resume : "has many"
    User ||--o{ Interest : "has many"
    User ||--o{ CareerProgress : "tracks"
    User ||--o{ SavedCareer : "saves"
    User ||--o{ SavedJob : "saves"
    User ||--o{ JobApplication : "applies to"
    User ||--o{ JobAlert : "creates"
    User ||--o{ Notification : "receives"
    User ||--o{ Feedback : "submits"
    User ||--o{ CustomPath : "creates"
    User ||--o{ GroupMember : "joins"

    Career ||--o{ Job : "has many"
    Career ||--o{ CareerProgress : "tracked in"
    Career ||--o{ SavedCareer : "saved as"
    Career ||--o{ CareerMilestone : "has many"

    Resume ||--o{ Interest : "analyzed in"
    Resume ||--o{ CareerProgress : "used in"

    Job ||--o{ SavedJob : "saved as"
    Job ||--o{ JobApplication : "applied to"

    PeerGroup ||--o{ GroupMember : "contains"

    FlaskApp --> DatabaseConnection : "uses"
    FlaskApp --> ResumeParser : "uses"
    FlaskApp --> EmailService : "uses"
    FlaskApp --> PDFGenerator : "uses"
    FlaskApp --> NotificationService : "uses"

    AuthController --> User : "manages"
    ResumeController --> Resume : "manages"
    ResumeController --> ResumeParser : "uses"
    CareerController --> Career : "manages"
    CareerController --> CareerRecommendationEngine : "uses"
    JobController --> Job : "manages"
    JobController --> JobMatchingService : "uses"
    AdminController --> Admin : "manages"
    AdminController --> User : "manages"
    AdminController --> Career : "manages"
    AdminController --> Job : "manages"

    CareerRecommendationEngine --> Resume : "analyzes"
    CareerRecommendationEngine --> Career : "matches"
    JobMatchingService --> Job : "searches"
    JobMatchingService --> User : "matches for"
```

## Key Features Represented in the Diagram:

### 1. **Core Entities**
- **User Management**: User registration, authentication, profile management
- **Resume System**: Upload, parse, build, and manage resumes
- **Career Guidance**: Career recommendations, path tracking, progress monitoring
- **Job Management**: Job search, applications, alerts, and tracking

### 2. **Database Relationships**
- One-to-Many relationships between users and their data
- Many-to-Many relationships for saved careers and jobs
- Foreign key relationships maintaining data integrity

### 3. **Service Layer**
- **ResumeParser**: Extracts and analyzes resume content using NLP
- **CareerRecommendationEngine**: Matches user profiles with career paths
- **JobMatchingService**: Finds relevant job opportunities
- **EmailService**: Handles notifications and alerts
- **PDFGenerator**: Creates downloadable resume PDFs

### 4. **Controller Layer (Flask Routes)**
- **AuthController**: Handles user authentication and authorization
- **ResumeController**: Manages resume operations
- **CareerController**: Handles career guidance features
- **JobController**: Manages job-related functionality
- **AdminController**: Provides administrative functions

### 5. **Advanced Features**
- **Peer Groups**: Social learning and collaboration
- **Mentor System**: Expert guidance and support
- **Progress Tracking**: Career milestone monitoring
- **Custom Paths**: Personalized career roadmaps
- **Notifications**: Real-time updates and alerts

### 6. **Security & Admin**
- Separate admin authentication system
- User role management
- Secure password handling
- File upload security

This class diagram provides a comprehensive view of the Career Guidance AI system architecture, showing how all components interact to deliver a complete career guidance platform.
