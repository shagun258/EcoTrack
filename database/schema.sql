-- EcoTrack PostgreSQL schema (reference copy).
-- The source of truth is backend/alembic/versions/*.py; this file documents
-- the same schema in plain SQL for quick reading / manual setup.
-- Generated to match: backend/app/models/*.py

CREATE TYPE user_role AS ENUM ('USER', 'COLLECTOR', 'ADMIN');
CREATE TYPE waste_category AS ENUM ('Plastic','Paper','Glass','Metal','Organic','E-Waste','Textile','Other');
CREATE TYPE report_status AS ENUM ('PENDING','VERIFIED','REJECTED','RESOLVED');
CREATE TYPE pickup_status AS ENUM ('PENDING','ASSIGNED','ACCEPTED','PICKED_UP','COMPLETED','CANCELLED');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'USER',
    phone VARCHAR(20),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    points INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_users_email ON users(email);

CREATE TABLE waste_reports (
    id SERIAL PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    description TEXT,
    category waste_category NOT NULL,
    manual_category_override BOOLEAN NOT NULL DEFAULT FALSE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address VARCHAR(500),
    status report_status NOT NULL DEFAULT 'PENDING',
    possible_duplicate_of INTEGER REFERENCES waste_reports(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_waste_reports_reporter_id ON waste_reports(reporter_id);

CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    waste_report_id INTEGER UNIQUE NOT NULL REFERENCES waste_reports(id) ON DELETE CASCADE,
    predicted_category VARCHAR(50) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    recyclable BOOLEAN NOT NULL DEFAULT TRUE,
    recommended_disposal VARCHAR(255) NOT NULL DEFAULT 'Recycling Center',
    mode VARCHAR(20) NOT NULL DEFAULT 'demo',
    model_version VARCHAR(50) NOT NULL DEFAULT 'v1',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE pickup_requests (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    collector_id INTEGER REFERENCES users(id),
    waste_type VARCHAR(50) NOT NULL,
    quantity_kg DOUBLE PRECISION NOT NULL,
    address VARCHAR(500) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time TIME NOT NULL,
    notes TEXT,
    proof_image_url VARCHAR(500),
    status pickup_status NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_pickup_requests_requester_id ON pickup_requests(requester_id);
CREATE INDEX ix_pickup_requests_collector_id ON pickup_requests(collector_id);

CREATE TABLE recycling_centers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    phone VARCHAR(20),
    opening_hours VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recycling_center_waste_types (
    id SERIAL PRIMARY KEY,
    center_id INTEGER NOT NULL REFERENCES recycling_centers(id) ON DELETE CASCADE,
    waste_type VARCHAR(50) NOT NULL
);
CREATE INDEX ix_recycling_center_waste_types_center_id ON recycling_center_waste_types(center_id);

CREATE TABLE rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_rewards_user_id ON rewards(user_id);

CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    points_required INTEGER NOT NULL,
    icon VARCHAR(50) NOT NULL DEFAULT 'award'
);

CREATE TABLE user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id INTEGER NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_user_badges_user_id ON user_badges(user_id);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_notifications_user_id ON notifications(user_id);

CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_complaints_user_id ON complaints(user_id);

CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ix_activity_logs_user_id ON activity_logs(user_id);
