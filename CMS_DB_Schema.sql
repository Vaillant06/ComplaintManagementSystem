-- 1. ADMIN TABLE

CREATE TABLE admins (
    admin_id SERIAL PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, 
    role VARCHAR(20) DEFAULT 'admin',
    last_login TIMESTAMP
);


-- 2. DEPARTMENTS TABLE

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL
);



-- 3. STAFF TABLE

CREATE TABLE staff (
    staff_id VARCHAR(10) PRIMARY KEY,
    staff_name VARCHAR(100) NOT NULL,
    department_id INTEGER NOT NULL,
    email VARCHAR(255) not null,
    pasword varchar(100) not null,
    phone VARCHAR(50) not null,
    role varchar(20) default 'staff',
    last_login TIMESTAMP

    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);



-- 4. USER TABLE

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role varchar(20) default 'user',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);



-- 5. COMPLAINTS TABLE

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

--6. USER REVIEW TABLE

CREATE TABLE user_review (
    name varchar(100) NOT NULL,
    email varchar(255) NOT NULL,
    rating varchar(10) NOT NULL,
    user_message TEXT NOT NULL,
    admin_reply TEXT,
    created_at TIMESTAMP
);


-- INSERT VALUES

-- 1. FOR ADMIN
INSERT INTO admins (admin_name, email, password)
VALUES ('Super Admin', 'admin@example.com', '<HASHED_PASSWORD_HERE>');


-- 2. FOR DEPARTMENTS

INSERT INTO departments (department_name)
VALUES 
('Electrical'),
('Water'),
('Public Works'),
('Health Care');


-- 3. FOR STAFF

INSERT INTO staff (staff_name, department_id, email, phone)
VALUES
('Ramesh Kumar', 1, 'ramesh.electrical@example.com', '9876543210'),
('Sita Devi', 2, 'sita.water@example.com', '9876543211'),
('Arun Prakash', 3, 'arun.pworks@example.com', '9876543212'),
('Meera Thomas', 4, 'meera.health@example.com', '9876543213');

