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
