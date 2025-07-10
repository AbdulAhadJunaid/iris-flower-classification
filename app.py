# Smart Finance Manager + AI Budget Chatbot using Streamlit

import streamlit as st
import pandas as pd
import datetime
import openai
import json
from streamlit_calendar import calendar

# Set OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Add this in .streamlit/secrets.toml

# App title
st.set_page_config(page_title="Smart Finance Manager", layout="wide")
st.title("\U0001F4B8 Smart Finance Manager + AI Budget Chatbot")

# Session state initialization
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])
if "categories" not in st.session_state:
    st.session_state.categories = ["Food", "Transport", "Utilities", "Subscriptions"]
if "reminders" not in st.session_state:
    st.session_state.reminders = []

# Sidebar Navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to:", ["Dashboard", "Add Expense", "Budget Settings", "AI Suggestions", "Reminders & Calendar", "Consultation Booking"])

# Dashboard View
if section == "Dashboard":
    st.subheader("Expense Overview")
    if st.session_state.expenses.empty:
        st.info("No expenses recorded yet.")
    else:
        st.dataframe(st.session_state.expenses.sort_values(by="Date", ascending=False))
        st.bar_chart(st.session_state.expenses.groupby("Category")["Amount"].sum())

# Add Expense
elif section == "Add Expense":
    st.subheader("Add a New Expense")
    with st.form("expense_form"):
        date = st.date_input("Date", datetime.date.today())
        category = st.selectbox("Category", st.session_state.categories)
        desc = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        submit = st.form_submit_button("Add")

        if submit:
            new_exp = pd.DataFrame([[date, category, desc, amount]], columns=st.session_state.expenses.columns)
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_exp], ignore_index=True)
            st.success("Expense added!")

# Budget Settings
elif section == "Budget Settings":
    st.subheader("Customize Budget Categories")
    new_cat = st.text_input("Add New Category")
    if st.button("Add Category"):
        if new_cat and new_cat not in st.session_state.categories:
            st.session_state.categories.append(new_cat)
    del_cat = st.selectbox("Delete Category", st.session_state.categories)
    if st.button("Delete Selected"):
        if del_cat in st.session_state.categories:
            st.session_state.categories.remove(del_cat)
    st.write("Current Categories:", st.session_state.categories)

# AI Suggestions
elif section == "AI Suggestions":
    st.subheader("AI Financial Insights")
    if st.session_state.expenses.empty:
        st.warning("Add some expenses first to get insights.")
    else:
        # Format data for GPT
        prompt = f"""
        Analyze this expense data and provide budgeting suggestions, potential savings, and financial tips:
        {st.session_state.expenses.to_json(orient='records')}
        """
        if st.button("Get AI Suggestions"):
            with st.spinner("Analyzing with AI..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a financial advisor."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    ai_msg = response.choices[0].message.content
                    st.markdown(ai_msg)
                except Exception as e:
                    st.error(f"Error: {e}")

# Reminders & Calendar
elif section == "Reminders & Calendar":
    st.subheader("Set Financial Reminders")
    with st.form("reminder_form"):
        title = st.text_input("Reminder Title")
        date = st.date_input("Reminder Date", min_value=datetime.date.today())
        time = st.time_input("Reminder Time")
        submit = st.form_submit_button("Add Reminder")
        if submit:
            st.session_state.reminders.append({"title": title, "date": str(date), "time": str(time)})
            st.success("Reminder added!")

    if st.session_state.reminders:
        st.markdown("### Upcoming Reminders")
        for r in st.session_state.reminders:
            st.write(f"**{r['title']}** - {r['date']} at {r['time']}")

    # Calendar View
    events = [
        {"title": r["title"], "start": f"{r['date']}T{r['time']}", "end": f"{r['date']}T{r['time']}"}
        for r in st.session_state.reminders
    ]
    calendar(events=events, options={"initialView": "dayGridMonth"})

# Appointment Booking
elif section == "Consultation Booking":
    st.subheader("Book a Financial Consultation")
    with st.form("booking_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email")
        date = st.date_input("Preferred Date")
        time = st.time_input("Preferred Time")
        note = st.text_area("Additional Notes")
        if st.form_submit_button("Book Appointment"):
            st.success("Appointment booked successfully! You will receive a confirmation soon.")

# Footer
st.markdown("---")
st.markdown("© 2025 Smart Finance Manager. Built with ❤️ using Streamlit")
