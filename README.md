# CareConnect — AI Doctor Appointment Assistant

CareConnect is a small educational project built with Python and Streamlit. It demonstrates a simple doctor appointment workflow and an optional Groq-powered assistant that provides general department-navigation information.

> **Important:** This is a classroom/demo prototype. The doctors and appointment slots are fictional sample data. It is not connected to a hospital, does not confirm real appointments, and must not be used for diagnosis, treatment, or emergency decisions.

## Features

- Select a hospital department and a sample doctor.
- Choose a date and an available demonstration time slot.
- Save appointments in a local SQLite database.
- Prevent two bookings for the same doctor, date, and time.
- View and cancel demo appointments using the booking ID and phone number.
- Optional AI department helper powered by Groq.
- Works without a Groq API key for appointment booking; the AI helper displays setup guidance.

## Project files

```text
ai-doctor-appointment-assistant/
├── app.py
├── requirements.txt
├── README.md
└── appointments.db       # created automatically when the app runs
```

## Requirements

- Python 3.10 or newer
- A Groq API key for the optional AI helper

## Run locally

1. Download or clone this project.
2. Open a terminal in the project folder.
3. (Recommended) Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Set your Groq API key if you want to use the AI helper.

   **Windows PowerShell**
   ```powershell
   $env:GROQ_API_KEY="your_groq_api_key"
   ```

   **macOS/Linux**
   ```bash
   export GROQ_API_KEY="your_groq_api_key"
   ```

   Get a key from [Groq Console](https://console.groq.com/keys). Keep it private and never commit it to GitHub.

6. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and connect your GitHub account.
3. Create an app, select the repository and branch, and set the main file path to `app.py`.
4. In the app's **Settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   ```

5. Deploy the app.

The SQLite database used here is local demo storage. Files on hosted app instances may not provide durable storage across restarts or redeployments. For a real appointment service, use a managed database and a properly secured backend.

## Testing checklist

- Book an appointment with a name and phone number.
- Try booking the same doctor, date, and time again; the duplicate should be rejected.
- Book another time slot and confirm it appears in the Appointments tab.
- Cancel an appointment using its booking ID and the same phone number.
- Ask the AI helper a general question after configuring `GROQ_API_KEY`.
- Try the app without a Groq key; appointment booking should still work.

## Privacy and safety

- Use fictional data for demonstrations.
- Do not enter patient records, diagnoses, prescriptions, or other sensitive health information.
- Do not use this prototype to make clinical decisions or determine emergency priority.
- A production deployment would require security, privacy, access control, audit logging, reliable database hosting, and review by the hospital's technical and clinical teams.
