-- -------------------------------------
-- 1. ADMIN TABLE
-- -------------------------------------
CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    last_login TIMESTAMP
);


-- -------------------------------------
-- 2. DEPARTMENTS TABLE
-- -------------------------------------
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL
);


-- -------------------------------------
-- 3. STAFF TABLE  (CORRECTED)
-- -------------------------------------
CREATE TABLE staff (
    staff_id VARCHAR(10) PRIMARY KEY,
    staff_name VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,        -- fixed typo
    phone VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff',
    last_login TIMESTAMP,

    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);


-- -------------------------------------
-- 4. USERS TABLE
-- -------------------------------------
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);


-- -------------------------------------
-- 5. COMPLAINTS TABLE
-- -------------------------------------
CREATE TABLE complaints (
    complaint_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    admin_comment TEXT,
    staff_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    assigned_to VARCHAR(10),
    assigned_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (assigned_to) REFERENCES staff(staff_id)
);


-- -------------------------------------
-- 6. USER REVIEW TABLE
-- -------------------------------------
CREATE TABLE user_review (
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    rating VARCHAR(10) NOT NULL,
    user_message TEXT NOT NULL,
    admin_reply TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


-- -------------------------------------
-- 7. AUDIT LOGS TABLE
-- -------------------------------------
CREATE TABLE audit_log (
    log_id SERIAL PRIMARY KEY,
    actor_id TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    complaint_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);


-- -----------------------------------------
-- 8. SAMPLE INSERT VALUES
-- -----------------------------------------

INSERT INTO admins (admin_name, email, role, password)
VALUES ('Super Admin', 'admin@example.com', 'admin', '<HASHED_PASSWORD_HERE>');


INSERT INTO departments (department_name)
VALUES 
('Electrical'),
('Water'),
('Public Works'),
('Health Care');


INSERT INTO staff (staff_id, staff_name, department_id, email, phone, role, password)
VALUES
('E01', 'Electrical Staff', 1, 'electrical.staff@example.com', '9876543210', 'staff', '<HASHED_PASSWORD_HERE>'),
('W01', 'Water Staff', 2, 'water.staff@example.com', '9876543211', 'staff', '<HASHED_PASSWORD_HERE>'),
('P01', 'Public Works Staff', 3, 'publicworks.staff@example.com', '9876543212', 'staff', '<HASHED_PASSWORD_HERE>'),
('H01', 'Health Care Staff', 4, 'health.staff@example.com', '9876543213', 'staff', '<HASHED_PASSWORD_HERE>');
