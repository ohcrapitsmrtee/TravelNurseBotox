import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calplot
import matplotlib.pyplot as plt

# Custom CSS for a more professional look and readable text
st.markdown(
    """
    <style>
    .main {
        background-color: #000000;
        color: #FFFFFF;
    }
    .sidebar .sidebar-content {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stButton>button {
        color: #000000;
        background-color: #4CAF50;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background-color: #45A049;
    }
    .css-1offfwp, .css-2trqyj, .css-1n76uvr, .css-1vq4p4l, .css-10trblm, .css-1r6slb0, .css-1y4p8pa, .css-1a32fsj, .css-1b9gcw7 {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Simulated database
users_db = {"user1": {"password": "pass1", "appointments": []}}
providers_db = {
    "Dr. Smith": {"availability": []}
}

# Generate availability for weekdays between 1:00 PM and 5:00 PM for the next 30 days
start_date = datetime.now().replace(hour=13, minute=0, second=0, microsecond=0)
for day_offset in range(30):
    day = start_date + timedelta(days=day_offset)
    if day.weekday() < 5:  # Weekdays only
        for hour_offset in range(4):  # 1:00 PM to 5:00 PM
            providers_db["Dr. Smith"]["availability"].append(day + timedelta(hours=hour_offset))

# User authentication function
def authenticate(username, password):
    if username in users_db and users_db[username]["password"] == password:
        return True
    return False

# User login
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
        else:
            st.sidebar.error("Invalid username or password")

# User logout
def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None

# Main app
def main():
    st.title("Botox Nurse Visit Scheduler")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
    else:
        st.sidebar.title("User")
        st.sidebar.write(f"Welcome, {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            logout()

        st.subheader("Book an Appointment")
        provider = "Dr. Smith"  # Hardcoded for simplicity

        # Create a DataFrame for the provider's availability
        availability_df = pd.DataFrame(providers_db[provider]["availability"], columns=["DateTime"])
        availability_df["Date"] = availability_df["DateTime"].dt.date
        availability_df["Time"] = availability_df["DateTime"].dt.time
        availability_df["Available"] = True

        # Count the number of available slots per day
        availability_df['Count'] = 1
        calendar_df = availability_df.groupby('Date').size().reset_index(name='Count')
        calendar_df['Date'] = pd.to_datetime(calendar_df['Date'])  # Ensure 'Date' is datetime
        calendar_df.set_index('Date', inplace=True)

        # Create a calendar heatmap
        fig, ax = calplot.calplot(calendar_df['Count'], how='sum',
                                  suptitle='Availability Calendar', cmap='YlGn', edgecolor='w')

        st.pyplot(fig)

        # Selecting an appointment time
        st.write("### Select a date and time for your appointment:")
        selected_date = st.date_input("Select a date", min_value=datetime.today().date())

        if selected_date:
            available_times = availability_df[availability_df['Date'] == selected_date]['Time']
            selected_time = st.selectbox("Select a time", available_times)

            if st.button("Book Appointment"):
                appointment_time = datetime.combine(selected_date, selected_time)
                book_appointment(provider, appointment_time)

        st.subheader("Your Appointments")
        username = st.session_state["username"]
        appointments = users_db[username]["appointments"]
        if appointments:
            appointments_df = pd.DataFrame(appointments)
            st.table(appointments_df)
        else:
            st.write("No appointments booked yet.")

# Booking an appointment
def book_appointment(provider, appointment_time):
    username = st.session_state["username"]
    users_db[username]["appointments"].append({"provider": provider, "time": appointment_time})
    providers_db[provider]["availability"].remove(appointment_time)
    st.success(f"Appointment booked with {provider} at {appointment_time}")

if __name__ == "__main__":
    main()
