import os
import sqlite3
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

# Configure Gemini API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY is missing in your .env file!")
else:
    genai.configure(api_key=api_key)

# 2. Function to Get SQL Query from Gemini
def get_gemini_response(question, prompt):
    # Updated to the latest available Flash model 
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()

# 3. Function to Execute SQL Query on SQLite Database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        
        # Get column names for formatted output
        column_names = [description[0] for description in cur.description] if cur.description else []
        
        conn.commit()
        conn.close()
        return column_names, rows
    except sqlite3.Error as e:
        return [], [f"Database Error: {e}"]

# 4. System Prompt for Text-to-SQL Conversion
prompt = [
    """
    You are an expert in converting English natural language questions into valid SQL queries!
    The SQL database is named workforce.db and contains 5 tables related to HR, Attendance, and Performance.

    Table 1: FACILITY_DIMENSION
    Columns: facility_id, facility_name, region, shift_name, manager_name
    
    Table 2: EMPLOYEE_MASTER (Anchor table)
    Columns: employee_id, name, employment_type (e.g., 'FT', 'Contract'), role, department, facility_id, shift_type, join_date, exit_date, status (e.g., 'Active', 'Terminated')
    
    Table 3: ATTENDANCE_LOGS
    Columns: log_id, employee_id, date, facility_id, shift_type, scheduled_hours, actual_hours, status (e.g., 'Present', 'Absent', 'Late'), overtime_hours
    
    Table 4: PERFORMANCE_METRICS
    Columns: perf_id, employee_id, date, task_type, units_processed, target_units, efficiency_pct, errors_flagged
    
    Table 5: LEAVE_REQUESTS
    Columns: leave_id, employee_id, leave_type, start_date, end_date, approved_by

    Examples:
    
    Example 1 - Show attrition rate by facility ->
    SELECT facility_id, COUNT(employee_id) AS terminated_count FROM EMPLOYEE_MASTER WHERE status = 'Terminated' GROUP BY facility_id;

    Example 2 - Which shift has the highest absenteeism? ->
    SELECT shift_type, COUNT(log_id) AS absences FROM ATTENDANCE_LOGS WHERE status = 'Absent' GROUP BY shift_type ORDER BY absences DESC LIMIT 1;

    Example 3 - List contract workers with overtime > 2 hrs ->
    SELECT e.name, a.date, a.overtime_hours FROM EMPLOYEE_MASTER e JOIN ATTENDANCE_LOGS a ON e.employee_id = a.employee_id WHERE e.employment_type = 'Contract' AND a.overtime_hours > 2.0;

    Example 4 - Why did efficiency drop (show efficiency and errors for low performers)? ->
    SELECT e.name, p.date, p.efficiency_pct, p.errors_flagged FROM PERFORMANCE_METRICS p JOIN EMPLOYEE_MASTER e ON p.employee_id = e.employee_id WHERE p.efficiency_pct < 80.0;

    CRITICAL RULES:
    1. Output ONLY the raw SQL query. 
    2. Do NOT enclose it in markdown code blocks like ```sql or ```.
    3. Do NOT include the word 'sql' anywhere in the output.
    """
]

# 5. Streamlit Frontend UI
st.set_page_config(page_title="Workforce Analytics Bot", page_icon="👥", layout="wide")

st.title("👥 Workforce & HR Query Assistant")
st.markdown("Ask natural language questions to query employee attendance, performance metrics, facility shifts, and attrition rates.")

# User Query Input
question = st.text_input("Enter your HR/Operations query:", placeholder="e.g., List all contract workers with overtime > 2 hrs")
submit = st.button("Ask Assistant")

# Execution Workflow
if submit:
    if not question.strip():
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("Generating SQL query..."):
            sql_query = get_gemini_response(question, prompt)
            
            # Clean output in case LLM appends backticks
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        st.subheader("Generated SQL Query:")
        st.code(sql_query, language="sql")

        with st.spinner("Executing query on database..."):
            # Ensure it points to the new database file
            columns, data = read_sql_query(sql_query, "workforce.db")

        st.subheader("Query Results:")
        if data:
            if columns:
                # Format output cleanly using a table layout
                st.table([dict(zip(columns, row)) for row in data])
            else:
                for row in data:
                    st.write(row)
        else:
            st.info("No matching records found in the workforce database.")
