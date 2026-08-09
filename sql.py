import sqlite3

# Connect to SQLite database (creates workforce.db if it doesn't exist)
connection = sqlite3.connect("workforce.db")
cursor = connection.cursor()

# ---------------------------------------------------------
# 1. CREATE TABLES
# ---------------------------------------------------------

cursor.executescript("""
-- 1. Facility/Shift Dimension (Lookup Table)
CREATE TABLE IF NOT EXISTS FACILITY_DIMENSION (
    facility_id VARCHAR(20) PRIMARY KEY,
    facility_name VARCHAR(50),
    region VARCHAR(50),
    shift_name VARCHAR(20),
    manager_name VARCHAR(50)
);

-- 2. Employee Master (Anchor Table)
CREATE TABLE IF NOT EXISTS EMPLOYEE_MASTER (
    employee_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50),
    employment_type VARCHAR(20),
    role VARCHAR(50),
    department VARCHAR(50),
    facility_id VARCHAR(20),
    shift_type VARCHAR(20),
    join_date DATE,
    exit_date DATE,
    status VARCHAR(20),
    FOREIGN KEY(facility_id) REFERENCES FACILITY_DIMENSION(facility_id)
);

-- 3. Attendance & Shift Logs (Highest-Value Table)
CREATE TABLE IF NOT EXISTS ATTENDANCE_LOGS (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20),
    date DATE,
    facility_id VARCHAR(20),
    shift_type VARCHAR(20),
    scheduled_hours DECIMAL(4, 2),
    actual_hours DECIMAL(4, 2),
    status VARCHAR(20),
    overtime_hours DECIMAL(4, 2),
    FOREIGN KEY(employee_id) REFERENCES EMPLOYEE_MASTER(employee_id),
    FOREIGN KEY(facility_id) REFERENCES FACILITY_DIMENSION(facility_id)
);

-- 4. Productivity/Performance (RCA + KPI Depth)
CREATE TABLE IF NOT EXISTS PERFORMANCE_METRICS (
    perf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20),
    date DATE,
    task_type VARCHAR(50),
    units_processed INT,
    target_units INT,
    efficiency_pct DECIMAL(5, 2),
    errors_flagged INT,
    FOREIGN KEY(employee_id) REFERENCES EMPLOYEE_MASTER(employee_id)
);

-- 5. Leave Requests (Secondary for Absenteeism Drill-downs)
CREATE TABLE IF NOT EXISTS LEAVE_REQUESTS (
    leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(20),
    leave_type VARCHAR(30),
    start_date DATE,
    end_date DATE,
    approved_by VARCHAR(50),
    FOREIGN KEY(employee_id) REFERENCES EMPLOYEE_MASTER(employee_id)
);
""")

# ---------------------------------------------------------
# 2. INSERT SAMPLE DATA
# ---------------------------------------------------------

# Insert Facilities
cursor.execute("""
INSERT OR IGNORE INTO FACILITY_DIMENSION VALUES
('FAC-01', 'North Distribution Hub', 'North', 'Morning', 'Sarah Connor'),
('FAC-02', 'South Manufacturing', 'South', 'Night', 'John Smith')
""")

# Insert Employees
cursor.execute("""
INSERT OR IGNORE INTO EMPLOYEE_MASTER VALUES
('EMP-1001', 'Aarav Patel', 'FT', 'Machine Operator', 'Production', 'FAC-02', 'Night', '2023-01-15', NULL, 'Active'),
('EMP-1002', 'Neha Sharma', 'Contract', 'Packer', 'Logistics', 'FAC-01', 'Morning', '2024-03-01', NULL, 'Active'),
('EMP-1003', 'Rohan Gupta', 'FT', 'Quality Inspector', 'Quality', 'FAC-01', 'Morning', '2022-11-10', '2024-07-01', 'Terminated'),
('EMP-1004', 'Priya Singh', 'Contract', 'Forklift Driver', 'Warehouse', 'FAC-02', 'Night', '2024-05-20', NULL, 'Active')
""")

# Insert Attendance Logs
# Simulating a scenario: EMP-1002 does heavy overtime, EMP-1004 is absent.
cursor.execute("""
INSERT INTO ATTENDANCE_LOGS (employee_id, date, facility_id, shift_type, scheduled_hours, actual_hours, status, overtime_hours) VALUES
('EMP-1001', '2024-07-15', 'FAC-02', 'Night', 8.0, 8.0, 'Present', 0.0),
('EMP-1002', '2024-07-15', 'FAC-01', 'Morning', 8.0, 11.5, 'Present', 3.5),
('EMP-1004', '2024-07-15', 'FAC-02', 'Night', 8.0, 0.0, 'Absent', 0.0),
('EMP-1001', '2024-07-16', 'FAC-02', 'Night', 8.0, 8.5, 'Present', 0.5),
('EMP-1002', '2024-07-16', 'FAC-01', 'Morning', 8.0, 12.0, 'Present', 4.0)
""")

# Insert Performance Metrics
# Simulating RCA: EMP-1002 is working heavy overtime, causing a drop in efficiency and high errors.
cursor.execute("""
INSERT INTO PERFORMANCE_METRICS (employee_id, date, task_type, units_processed, target_units, efficiency_pct, errors_flagged) VALUES
('EMP-1001', '2024-07-15', 'Assembly', 105, 100, 105.00, 1),
('EMP-1002', '2024-07-15', 'Packaging', 150, 200, 75.00, 12),
('EMP-1001', '2024-07-16', 'Assembly', 100, 100, 100.00, 0),
('EMP-1002', '2024-07-16', 'Packaging', 140, 200, 70.00, 15)
""")

# Insert Leave Requests
cursor.execute("""
INSERT INTO LEAVE_REQUESTS (employee_id, leave_type, start_date, end_date, approved_by) VALUES
('EMP-1004', 'Sick Leave', '2024-07-14', '2024-07-16', 'John Smith'),
('EMP-1003', 'Annual Vacation', '2024-06-01', '2024-06-15', 'Sarah Connor')
""")

# ---------------------------------------------------------
# 3. VERIFY DATA (Optional Output)
# ---------------------------------------------------------

print("--- RECENT ATTENDANCE RECORDS ---")
data = cursor.execute("""
    SELECT a.date, e.name, a.status, a.overtime_hours 
    FROM ATTENDANCE_LOGS a
    JOIN EMPLOYEE_MASTER e ON a.employee_id = e.employee_id
""")
for row in data:
    print(row)

print("\n--- PERFORMANCE ISSUES (Efficiency < 80%) ---")
rca_data = cursor.execute("""
    SELECT date, employee_id, task_type, efficiency_pct, errors_flagged 
    FROM PERFORMANCE_METRICS 
    WHERE efficiency_pct < 80.0
""")
for row in rca_data:
    print(row)

# Commit changes and close
connection.commit()
connection.close()