import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the Streamlit page
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

# Function to load data
@st.cache_data
def load_data():
    return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

# Title
st.title("Personal Finance Tracker")

# Sidebar for user input
st.sidebar.header("Add a new expense")

with st.sidebar.form("expense_form"):
    date = st.date_input("Date")
    category = st.selectbox(
        "Category", ["Food", "Transport", "Rent", "Utilities", "Entertainment", "Others"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_expense = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Description": [description],
            "Amount": [amount]
        })
        st.session_state.data = pd.concat(
            [st.session_state.data, new_expense], ignore_index=True)
        st.success("Expense added successfully!")

# Main area
st.header("Expenses Overview")

# Display the dataframe
st.dataframe(st.session_state.data)

# Plot expenses by category
st.subheader("Expenses by Category")
if not st.session_state.data.empty:
    fig = px.pie(st.session_state.data, names="Category",
                 values="Amount", title="Expenses by Category")
    st.plotly_chart(fig)

# Monthly expenses
st.subheader("Monthly Expenses")
if not st.session_state.data.empty:
    st.session_state.data["Month"] = pd.to_datetime(
        st.session_state.data["Date"]).dt.to_period("M").astype(str)
    monthly_expenses = st.session_state.data.groupby(
        "Month").sum()["Amount"].reset_index()
    fig = px.line(monthly_expenses, x="Month",
                  y="Amount", title="Monthly Expenses")
    st.plotly_chart(fig)

# Budget tracking
st.sidebar.header("Set Budget")

budget_data = {}
if "budget_data" in st.session_state:
    budget_data = st.session_state.budget_data

with st.sidebar.form("budget_form"):
    budget_category = st.selectbox("Budget Category", [
                                   "Food", "Transport", "Rent", "Utilities", "Entertainment", "Others"])
    budget_amount = st.number_input(
        "Budget Amount", min_value=0.0, format="%.2f")
    budget_submitted = st.form_submit_button("Set Budget")

    if budget_submitted:
        budget_data[budget_category] = budget_amount
        st.session_state.budget_data = budget_data
        st.success("Budget set successfully!")

# Display budgets and expenses comparison
st.subheader("Budget vs Expenses")
if budget_data and not st.session_state.data.empty:
    expenses_by_category = st.session_state.data.groupby("Category").sum()[
        "Amount"]
    budget_df = pd.DataFrame(budget_data.items(), columns=[
                             "Category", "Budget"])
    budget_df["Expenses"] = budget_df["Category"].map(expenses_by_category)
    budget_df.fillna(0, inplace=True)
    budget_df["Difference"] = budget_df["Budget"] - budget_df["Expenses"]
    st.dataframe(budget_df)

    fig = px.bar(budget_df, x="Category", y=[
                 "Budget", "Expenses"], barmode="group", title="Budget vs Expenses")
    st.plotly_chart(fig)

# Recommendations
st.subheader("Recommendations")
if not st.session_state.data.empty:
    total_expenses = st.session_state.data["Amount"].sum()
    st.write(f"Total expenses: ${total_expenses:.2f}")
    if budget_data:
        total_budget = sum(budget_data.values())
        if total_expenses > total_budget:
            st.warning(
                f"You have exceeded your total budget by ${total_expenses - total_budget:.2f}. Consider reducing your expenses.")
        else:
            st.success(
                f"You are within your budget. You have ${total_budget - total_expenses:.2f} left.")
    else:
        st.info("No budget set. Set a budget to track your expenses.")
