import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import io
import sqlite3
from datetime import datetime

# Import your existing backend logic
from modules.input_processing import load_project_data
from modules.scheduler import run_ga
from modules.traditional_scheduler import run_cpm, run_pert
from visualization.graphs import plot_comparison_chart
from visualization.gantt_charts import plot_gantt

# --- 1. DATABASE INITIALIZATION ---
def init_db():
    """Initializes the SQLite database and creates necessary tables."""
    conn = sqlite3.connect('sepm_project.db')
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    # Create Reports Table (Replaces published_report.json and published_tasks.json)
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports 
                      (id INTEGER PRIMARY KEY, 
                       duration REAL, 
                       cost REAL, 
                       risk REAL, 
                       cpm_duration REAL, 
                       tasks_json TEXT, 
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Pre-populate default users if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_users = [
            ("admin", "123", "System Administrator"),
            ("pm", "123", "Project Manager"),
            ("dev", "123", "Software Team Member"),
            ("boss", "123", "Management")
        ]
        cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", default_users)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_db_connection():
    return sqlite3.connect('sepm_project.db')

# --- 2. SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None

# --- 3. LOGIN UI ---
def login_screen():
    st.title("🔐 SEPM AI Optimization System (SQL Edition)")
    st.markdown("### Secure Login Portal")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            st.session_state['logged_in'] = True
            st.session_state['role'] = user[0]
            st.success(f"Welcome, {user[0]}!")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# --- 4. VISUAL PDF/IMAGE REPORT ENGINE ---
def create_visual_report_file(tasks_list, report_metrics):
    """Creates a high-resolution visual report for PDF export with accurate timeline."""
    fig = plt.figure(figsize=(10, 12))
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 4, 3])

    ax0 = fig.add_subplot(gs[0])
    ax0.axis('off')
    ax0.text(0.5, 0.9, "PROJECT EXECUTION REPORT", ha='center', fontsize=22, weight='bold', color='#2c3e50')
    
    metrics = [
        (f"Duration: {report_metrics['duration']}d", "lightblue"),
        (f"Budget: ₹{int(report_metrics['cost'])}", "lightgreen"),
        (f"Risk: {report_metrics['risk']:.2f}", "orange")
    ]
    for i, (txt, clr) in enumerate(metrics):
        ax0.text(0.2 + i*0.3, 0.5, txt, ha='center', va='center', fontsize=14, 
                bbox=dict(boxstyle="round,pad=0.5", fc=clr, alpha=0.3, ec="gray"))

    ax1 = fig.add_subplot(gs[1])
    df = pd.DataFrame(tasks_list)
    for i, row in df.iterrows():
        start_pos = row.get('es', 0)
        ax1.barh(row['name'], row['duration'], left=start_pos, color='#3498db', edgecolor='black')
        ax1.text(start_pos + row['duration']/2, i, f"{row['duration']}d", va='center', ha='center', color='black', fontweight='bold')

    ax1.set_title("Project Timeline Visualization", fontsize=16, pad=10)
    ax1.invert_yaxis()
    ax1.grid(True, axis='x', linestyle='--', alpha=0.5)

    ax2 = fig.add_subplot(gs[2])
    ax2.axis('off')
    table_data = df[['id', 'name', 'duration', 'dependencies']].values
    the_table = ax2.table(cellText=table_data, colLabels=['ID', 'Task', 'Days', 'Deps'], loc='center', cellLoc='center')
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(10)
    the_table.scale(1, 1.5)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    return buf

# --- 5. SHARED VISUAL DASHBOARD COMPONENT ---
def render_full_visual_report(role_label):
    """Renders formatted metrics and Gantt charts from SQLite."""
    conn = get_db_connection()
    # Fetch the most recent report
    report_df = pd.read_sql_query("SELECT * FROM reports ORDER BY timestamp DESC LIMIT 1", conn)
    conn.close()
    
    if not report_df.empty:
        # Extract row data
        db_row = report_df.iloc[0]
        report = {
            "duration": db_row['duration'],
            "cost": db_row['cost'],
            "risk": db_row['risk'],
            "cpm_duration": db_row['cpm_duration']
        }
        tasks_list = json.loads(db_row['tasks_json'])
            
        st.divider()
        st.subheader(f"📊 Detailed Project Report - {role_label}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Optimized Duration", f"{report.get('duration')} Days")
        m2.metric("Total Cost", f"₹{int(report.get('cost'))}")
        m3.metric("Risk Exposure", f"{report.get('risk'):.2f}")
        
        st.write("### 📅 Project Schedule Visual")
        class DummyChromosome:
            def __init__(self, order): self.order = order
        fig = plot_gantt(DummyChromosome(tasks_list))
        st.pyplot(fig)
        
        st.write("### 📋 Task Breakdown")
        df = pd.DataFrame(tasks_list)
        st.dataframe(df[['id', 'name', 'duration', 'dependencies']], use_container_width=True)
        
        st.divider()
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download CSV Data", csv, f'report.csv', 'text/csv')
        with col_dl2:
            report_buf = create_visual_report_file(tasks_list, report)
            st.download_button(f"🖼️ Download Visual Report (PNG)", report_buf, f'Visual_Report.png', 'image/png')
    else:
        st.info("🕒 Awaiting Project Manager to publish the final optimized schedule...")

# --- 6. ROLE-BASED DASHBOARDS ---

def project_manager_dashboard():
    st.header("🛠️ Project Manager Dashboard")
    st.write("Upload data, set constraints, and run AI optimization with SQL Storage.")
    
    st.sidebar.header("💰 Financial Parameters")
    daily_overhead = st.sidebar.number_input("Daily Overhead (₹/Day)", min_value=0, value=400, step=50)
    
    col1, col2 = st.columns(2)
    with col1:
        deadline = st.number_input("Target Deadline (Days)", min_value=1, value=30)
    with col2:
        budget = st.number_input("Max Budget (₹)", min_value=1000, value=25000, step=1000)

    uploaded_file = st.file_uploader("Upload Project JSON", type="json")
    
    if uploaded_file is not None and st.button("🚀 Run AI Optimization"):
        try:
            raw_data = json.load(uploaded_file)
            os.makedirs("data", exist_ok=True)
            with open("data/temp_upload.json", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            tasks = load_project_data("data/temp_upload.json")
            best_ga = run_ga(tasks=tasks, deadline=deadline, budget=budget, overhead=daily_overhead)
            cpm_res = run_cpm(tasks)
            
            def extract_duration(res):
                if isinstance(res, dict): return res.get('duration', res.get('project_duration', 0))
                elif isinstance(res, (list, tuple)): return res[0]
                return res

            cpm_dur = extract_duration(cpm_res)
            total_ga_cost = best_ga.cost + (best_ga.duration * daily_overhead)
            total_ga_risk = best_ga.risk + (best_ga.duration * 0.08)

            if total_ga_cost > budget or best_ga.duration > deadline:
                st.error("❌ INFEASIBLE SCHEDULE")
                st.stop() 

            st.success("✅ Optimization Complete!")

            # SAVE DATA TO SQLITE
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO reports (duration, cost, risk, cpm_duration, tasks_json) 
                              VALUES (?, ?, ?, ?, ?)''', 
                           (best_ga.duration, total_ga_cost, total_ga_risk, cpm_dur, json.dumps(best_ga.order)))
            conn.commit()
            conn.close()

            st.subheader("🏆 AI Recommended Metrics")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Duration", f"{best_ga.duration} Days")
            res_col2.metric("Total Cost", f"₹{int(total_ga_cost)}")
            res_col3.metric("Risk", f"{total_ga_risk:.2f}")
            
            st.pyplot(plot_gantt(best_ga))
            st.divider()
            render_full_visual_report("PM Final")

        except Exception as e:
            st.error(f"System Error: {str(e)}")

def management_dashboard():
    st.header("📈 Management Dashboard")
    render_full_visual_report("Management")
    
    conn = get_db_connection()
    report_df = pd.read_sql_query("SELECT * FROM reports ORDER BY timestamp DESC LIMIT 1", conn)
    conn.close()
    
    if not report_df.empty:
        report = report_df.iloc[0]
        savings = report['cpm_duration'] - report['duration']
        if savings > 0:
            st.info(f"💡 AI Optimization saved **{savings:.1f} days** vs Traditional.")

def dev_dashboard():
    st.header("💻 Software Team Member Dashboard")
    render_full_visual_report("Developer")

def admin_dashboard():
    st.header("⚙️ System Administrator")
    st.subheader("Database User Management")
    
    conn = get_db_connection()
    df_users = pd.read_sql_query("SELECT username, role FROM users", conn)
    conn.close()
    st.table(df_users)
    
    st.divider()
    st.subheader("Add New System User to SQLite")
    with st.form("add_user"):
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password")
        new_role = st.selectbox("Assign Role", ["Project Manager", "Management", "Software Team Member", "System Administrator"])
        if st.form_submit_button("Register in DB"):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                               (new_user, new_pass, new_role))
                conn.commit()
                st.success(f"User {new_user} saved to Database!")
            except sqlite3.IntegrityError:
                st.error("User already exists!")
            conn.close()
            st.rerun()

def main():
    if st.session_state['logged_in']:
        st.sidebar.title("Navigation")
        st.sidebar.write(f"Role: **{st.session_state['role']}**")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

        role = st.session_state['role']
        if role == "Project Manager": project_manager_dashboard()
        elif role == "Management": management_dashboard()
        elif role == "Software Team Member": dev_dashboard()
        elif role == "System Administrator": admin_dashboard()
    else:
        login_screen()

if __name__ == "__main__":
    main()