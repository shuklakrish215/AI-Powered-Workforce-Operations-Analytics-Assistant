# 👥 Workforce & HR Query Assistant

An AI-powered, natural language-to-SQL analytics tool designed for HR managers and Operations Directors. This application allows non-technical users to query complex workforce data, track absenteeism, monitor performance metrics, and analyze attrition rates using plain English.

## ✨ Features
* **Natural Language Processing:** Ask business questions in plain English (e.g., "Which shift has the highest absenteeism?").
* **Automated Text-to-SQL:** Leverages Google's Gemini LLM to instantly translate human questions into accurate, executable SQL queries.
* **Instant Data Visualization:** Retrieves data from the backend SQLite database and dynamically renders it into clean, readable tables via Streamlit.
* **Comprehensive HR Analytics:** Supports queries on attrition, headcount planning, overtime abuse, leave requests, and Root Cause Analysis (RCA) for performance drops.

## 🛠️ Tech Stack
* **Frontend UI:** Streamlit (Python)
* **LLM Engine:** Google Gemini API (`gemini-1.5-flash` or `gemini-pro`)
* **Database:** SQLite
* **Environment Management:** `python-dotenv`

## 🗄️ Database Schema
The application queries a local SQLite database (`workforce.db`) structured with a star-schema design for operational analytics:
1. `EMPLOYEE_MASTER`: Anchor table containing core employee details (Full-Time/Contract, Role, Department).
2. `FACILITY_DIMENSION`: Lookup table for physical locations, regions, shifts, and managers.
3. `ATTENDANCE_LOGS`: Operational core tracking scheduled vs. actual hours, overtime, and attendance status.
4. `PERFORMANCE_METRICS`: KPI table tracking daily targets, efficiency, and error rates.
5. `LEAVE_REQUESTS`: Secondary context table tracking approved time off.

## 🚀 Getting Started

### Prerequisites
* Python 3.8+
* A valid Google Gemini API Key
