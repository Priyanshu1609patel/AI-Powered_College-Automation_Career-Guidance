-- ============================================================
-- AI-Powered College Automation & Career Guidance System
-- Complete Database Schema for Supabase PostgreSQL
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. AUTHENTICATION & USERS
-- ============================================================

-- Users table (students + admins)
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password        TEXT NOT NULL,
    role            VARCHAR(20) NOT NULL DEFAULT 'student'
                        CHECK (role IN ('student', 'admin')),
    enrollment_no   VARCHAR(50),
    semester        INTEGER CHECK (semester BETWEEN 1 AND 8),
    branch          VARCHAR(50) DEFAULT 'CSE',
    phone           VARCHAR(15),
    profile_pic_url TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================
-- 2. CHATBOT TABLES
-- ============================================================

-- Chat sessions
CREATE TABLE IF NOT EXISTS chats (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) DEFAULT 'New Chat',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chats_user_id ON chats(user_id);
CREATE INDEX idx_chats_created_at ON chats(created_at DESC);

-- Individual messages within a chat
CREATE TABLE IF NOT EXISTS messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id         UUID NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sender          VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'bot')),
    content         TEXT NOT NULL,
    intent          VARCHAR(100),
    confidence      REAL DEFAULT 0.0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Questions the bot could not answer
CREATE TABLE IF NOT EXISTS unanswered_queries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    query_text      TEXT NOT NULL,
    detected_intent VARCHAR(100),
    times_asked     INTEGER NOT NULL DEFAULT 1,
    is_resolved     BOOLEAN NOT NULL DEFAULT FALSE,
    admin_response  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX idx_unanswered_resolved ON unanswered_queries(is_resolved);

-- ============================================================
-- 3. ACADEMIC TABLES
-- ============================================================

-- Semesters
CREATE TABLE IF NOT EXISTS semesters (
    id              SERIAL PRIMARY KEY,
    semester_number INTEGER UNIQUE NOT NULL CHECK (semester_number BETWEEN 1 AND 8),
    semester_name   VARCHAR(50) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Subjects (CSE curriculum)
CREATE TABLE IF NOT EXISTS subjects (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    semester_id     INTEGER NOT NULL REFERENCES semesters(id) ON DELETE CASCADE,
    subject_code    VARCHAR(20) UNIQUE NOT NULL,
    subject_name    VARCHAR(200) NOT NULL,
    credits         INTEGER NOT NULL DEFAULT 3 CHECK (credits BETWEEN 1 AND 12),
    subject_type    VARCHAR(20) NOT NULL DEFAULT 'theory'
                        CHECK (subject_type IN ('theory', 'practical', 'elective')),
    syllabus_brief  TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subjects_semester ON subjects(semester_id);
CREATE INDEX idx_subjects_code ON subjects(subject_code);
CREATE INDEX idx_subjects_name ON subjects(subject_name);

-- Study materials (Google Drive links per subject)
CREATE TABLE IF NOT EXISTS subject_materials (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subject_id      UUID NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    material_title  VARCHAR(255) NOT NULL,
    material_type   VARCHAR(50) NOT NULL DEFAULT 'notes'
                        CHECK (material_type IN ('notes', 'pyq', 'syllabus', 'book', 'video', 'other')),
    drive_link      TEXT NOT NULL,
    uploaded_by     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_materials_subject ON subject_materials(subject_id);
CREATE INDEX idx_materials_type ON subject_materials(material_type);

-- Academic rules (exam patterns, policies, etc.)
CREATE TABLE IF NOT EXISTS academic_rules (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_category   VARCHAR(100) NOT NULL,
    rule_title      VARCHAR(255) NOT NULL,
    rule_content    TEXT NOT NULL,
    keywords        TEXT,  -- comma-separated keywords for chatbot matching
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rules_category ON academic_rules(rule_category);

-- Notices / Announcements
CREATE TABLE IF NOT EXISTS notices (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,
    notice_type     VARCHAR(50) NOT NULL DEFAULT 'general'
                        CHECK (notice_type IN ('general', 'exam', 'event', 'holiday', 'result', 'urgent')),
    posted_by       INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notices_type ON notices(notice_type);
CREATE INDEX idx_notices_active ON notices(is_active, created_at DESC);

-- ============================================================
-- 4. ANALYTICS
-- ============================================================

-- Query logs for analytics
CREATE TABLE IF NOT EXISTS query_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    query_text      TEXT NOT NULL,
    detected_intent VARCHAR(100),
    response_text   TEXT,
    confidence      REAL DEFAULT 0.0,
    response_time_ms INTEGER,
    was_helpful     BOOLEAN,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_query_logs_intent ON query_logs(detected_intent);
CREATE INDEX idx_query_logs_created ON query_logs(created_at DESC);
CREATE INDEX idx_query_logs_user ON query_logs(user_id);

-- ============================================================
-- 5. CAREER GUIDANCE INTEGRATION
-- (These tables support the existing sub-project)
-- ============================================================

-- Career guidance user preferences (linked to main auth)
CREATE TABLE IF NOT EXISTS career_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interests       TEXT[],
    skills          TEXT[],
    career_goal     VARCHAR(255),
    personality_type VARCHAR(10),
    quiz_completed  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 6. HELPER FUNCTIONS
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_chats_updated
    BEFORE UPDATE ON chats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_subjects_updated
    BEFORE UPDATE ON subjects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_rules_updated
    BEFORE UPDATE ON academic_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_career_profiles_updated
    BEFORE UPDATE ON career_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- 7. ROW LEVEL SECURITY (Supabase)
-- ============================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;

-- Policies: allow service_role full access (used by Flask backend)
CREATE POLICY "Service role full access on users"
    ON users FOR ALL
    USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "Service role full access on chats"
    ON chats FOR ALL
    USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "Service role full access on messages"
    ON messages FOR ALL
    USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "Service role full access on query_logs"
    ON query_logs FOR ALL
    USING (TRUE) WITH CHECK (TRUE);
