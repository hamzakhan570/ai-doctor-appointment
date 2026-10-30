import os
import sqlite3
from datetime import date, datetime, time, timedelta

import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "appointments.db")

DEPARTMENTS = {
    "General Medicine": ["Dr. Ayesha Khan", "Dr. Hamza Ali"],
    "Cardiology": ["Dr. Sara Ahmed", "Dr. Bilal Shah"],
    "Dermatology": ["Dr. Maryam Noor", "Dr. Usman Tariq"],
    "Pediatrics": ["Dr. Fatima Iqbal", "Dr. Ahmed Raza"],
    "Orthopedics": ["Dr. Zain Malik", "Dr. Hira Aslam"],
    "ENT": ["Dr. Sana Javed", "Dr. Omar Farooq"],
}

TIME_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM", "12:00 PM", "02:00 PM",
    "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                department TEXT NOT NULL,
                doctor TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(doctor, appointment_date, appointment_time)
            )
            """
        )


def list_appointments():
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, patient_name, phone, department, doctor,
                   appointment_date, appointment_time, reason
            FROM appointments
            ORDER BY appointment_date, appointment_time
            """
        ).fetchall()


def booked_slots(doctor, appointment_date):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT appointment_time FROM appointments
            WHERE doctor = ? AND appointment_date = ?
            """,
            (doctor, appointment_date.isoformat()),
        ).fetchall()
    return {row["appointment_time"] for row in rows}


def create_appointment(data):
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO appointments
                (patient_name, phone, email, department, doctor,
                 appointment_date, appointment_time, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["patient_name"],
                    data["phone"],
                    data["email"],
                    data["department"],
                    data["doctor"],
                    data["appointment_date"].isoformat(),
                    data["appointment_time"],
                    data["reason"],
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            return cursor.lastrowid, None
    except sqlite3.IntegrityError:
        return None, "That doctor and time slot has just been booked. Please choose another slot."
    except sqlite3.Error as exc:
        return None, f"Could not save the appointment: {exc}"


def cancel_appointment(appointment_id, phone):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM appointments WHERE id = ? AND phone = ?",
            (appointment_id, phone.strip()),
        )
        return cursor.rowcount > 0


def ask_groq(question):
    api_key = os.getenv("GROQ_API_KEY", "")
    try:
        if not api_key:
            api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

    if not api_key or Groq is None:
        return (
            "The AI helper is not configured yet. You can still book an appointment "
            "using the form. Add GROQ_API_KEY to your environment or Streamlit secrets "
            "to enable AI-powered department guidance."
        )

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a hospital appointment information assistant. "
                        "Help users understand which listed department may be relevant "
                        "for booking, and explain general appointment steps. Do not "
                        "diagnose, prescribe, interpret emergencies as routine, or "
                        "claim to replace a clinician. If symptoms could be urgent, "
                        "tell the user to contact local emergency services or go to "
                        "the nearest emergency department immediately. Keep answers "
                        "brief and say that department suggestions are not a diagnosis. "
                        "Available departments: " + ", ".join(DEPARTMENTS.keys())
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0.2,
            max_completion_tokens=500,
        )
        return response.choices[0].message.content or "Sorry, no response was returned."
    except Exception as exc:
        return f"The AI helper is temporarily unavailable: {exc}"


st.set_page_config(
    page_title="CareConnect | Doctor Appointments",
    page_icon="🏥",
    layout="wide",
)

initialize_database()

st.title("🏥 CareConnect")
st.caption("AI-assisted doctor appointment booking — a demonstration application.")

with st.sidebar:
    st.header("About CareConnect")
    st.write(
        "Find a department, choose a doctor, and reserve an available "
        "demonstration appointment slot."
    )
    st.info(
        "Demo notice: The doctors and time slots in this app are sample data. "
        "This is not connected to a real hospital."
    )
    st.markdown("---")
    st.caption("Do not enter sensitive medical details or emergency information.")

tab_book, tab_helper, tab_manage = st.tabs(
    ["📅 Book appointment", "🤖 AI department helper", "📋 Appointments"]
)

with tab_book:
    st.subheader("Book a doctor appointment")
    left, right = st.columns(2)

    with st.form("appointment_form", clear_on_submit=True):
        with left:
            patient_name = st.text_input("Patient name *", max_chars=80)
            phone = st.text_input("Phone number *", max_chars=30)
            email = st.text_input("Email (optional)", max_chars=120)
            department = st.selectbox("Department *", list(DEPARTMENTS.keys()))
        with right:
            doctor = st.selectbox("Doctor *", DEPARTMENTS[department])
            appointment_date = st.date_input(
                "Appointment date *",
                value=date.today() + timedelta(days=1),
                min_value=date.today(),
            )
            available = [
                slot for slot in TIME_SLOTS
                if slot not in booked_slots(doctor, appointment_date)
            ]
            appointment_time = st.selectbox(
                "Available time *",
                available if available else ["No slots available"],
                disabled=not available,
            )
            reason = st.text_area(
                "Short note (optional)",
                placeholder="Keep this general; do not include private medical details.",
                max_chars=250,
            )

        submitted = st.form_submit_button(
            "Confirm appointment", type="primary", use_container_width=True
        )

    if submitted:
        if not patient_name.strip() or not phone.strip():
            st.error("Please enter the patient's name and phone number.")
        elif email.strip() and ("@" not in email or "." not in email.split("@")[-1]):
            st.error("Please enter a valid email address or leave it blank.")
        elif not available:
            st.warning("No time slots are available for this doctor on that date.")
        else:
            appointment_id, error = create_appointment(
                {
                    "patient_name": patient_name.strip(),
                    "phone": phone.strip(),
                    "email": email.strip(),
                    "department": department,
                    "doctor": doctor,
                    "appointment_date": appointment_date,
                    "appointment_time": appointment_time,
                    "reason": reason.strip(),
                }
            )
            if error:
                st.error(error)
            else:
                st.success(f"Appointment booked! Your demo booking ID is #{appointment_id}.")
                st.write(
                    f"**{doctor}** · {department} · "
                    f"{appointment_date.strftime('%d %b %Y')} · {appointment_time}"
                )

with tab_helper:
    st.subheader("AI department helper")
    st.write(
        "Describe what kind of appointment information you need. "
        "The assistant can suggest a department from the list, but it cannot diagnose."
    )
    question = st.text_area(
        "What would you like help with?",
        placeholder="Example: I need a routine appointment for a skin concern.",
        height=100,
        key="helper_question",
    )
    if st.button("Ask AI assistant", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Preparing guidance..."):
                st.markdown(ask_groq(question))

    st.warning(
        "If someone may be experiencing a medical emergency, do not use this app "
        "to decide what to do. Contact local emergency services or go to the "
        "nearest emergency department immediately."
    )

with tab_manage:
    st.subheader("Manage demonstration appointments")
    st.caption(
        "For this classroom demo, appointments are stored in a local SQLite database."
    )
    appointments = list_appointments()
    if not appointments:
        st.info("No appointments have been booked yet.")
    else:
        display_rows = [
            {
                "ID": row["id"],
                "Patient": row["patient_name"],
                "Phone": row["phone"],
                "Department": row["department"],
                "Doctor": row["doctor"],
                "Date": row["appointment_date"],
                "Time": row["appointment_time"],
            }
            for row in appointments
        ]
        st.dataframe(display_rows, use_container_width=True, hide_index=True)

        st.markdown("#### Cancel a demo appointment")
        with st.form("cancel_form"):
            cancel_id = st.number_input(
                "Booking ID", min_value=1, step=1, value=1
            )
            cancel_phone = st.text_input("Phone number used for booking")
            cancel_submitted = st.form_submit_button("Cancel appointment")
        if cancel_submitted:
            if not cancel_phone.strip():
                st.error("Enter the phone number used for the booking.")
            elif cancel_appointment(int(cancel_id), cancel_phone):
                st.success("The demonstration appointment was cancelled.")
                st.rerun()
            else:
                st.error("No matching appointment was found.")

st.markdown("---")
st.caption(
    "CareConnect is an educational prototype. It is not a real booking service "
    "and must not be used for clinical decisions."
)
