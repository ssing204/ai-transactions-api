import streamlit as st
import pandas as pd
import requests

# API address
API_URL = "http://127.0.0.1:5001"

# Configure dashboard
st.set_page_config(
    page_title="AI Billing Dashboard",
    layout="wide"
)

st.title("AI Billing Dashboard")
st.write("AI token usage and cost monitoring")

# Function to retrieve JSON from Flask
def fetch_data(endpoint):
    response = requests.get(
        f"{API_URL}{endpoint}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()

# Retrieve information 
try:
    transactions = fetch_data("/api/transactions")
    companies = fetch_data("/api/spending/companies")
    users = fetch_data("/api/spending/users")
    budgets = fetch_data("/api/budgets/companies")

except (requests.RequestException, ValueError) as error:
    st.error(f"Unable to retrieve API data: {error}")
    st.stop()

# Convert JSON responses into pandas DataFrames
transactions_df = pd.DataFrame(transactions)
companies_df = pd.DataFrame(companies)
users_df = pd.DataFrame(users)
budgets_df = pd.DataFrame(budgets)


# Calculate dashboard summary metrics
if not companies_df.empty:
    total_spending = pd.to_numeric(
        companies_df["total_spent"]
    ).sum()

    total_transactions = companies_df[
        "transaction_count"
    ].sum()

else:
    total_spending = 0
    total_transactions = 0

# Display summary metrics
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total AI Spending",
        f"${total_spending:,.2f}"
    )

with col2:
    st.metric(
        "Total Transactions",
        f"{total_transactions:,}"
    )


# Display transactions table
st.subheader("Transactions (First 20)")
st.dataframe(transactions_df)
st.caption(
    "Showing the first 20 transactions "
    "in transaction-number order."
)


# Company spending visualization
st.subheader("Company Spending")

if not companies_df.empty:

    # Convert spending values into numeric data
    companies_df["total_spent"] = pd.to_numeric(
        companies_df["total_spent"]
    )

    # Display company spending bar chart
    st.bar_chart(
        companies_df,
        x="company",
        y="total_spent"
        )

else:
    st.info("No company spending data available.")


# User spending visualization
st.subheader("Top 10 Users by Spending")

if not users_df.empty:

    # Convert spending values into numeric data
    users_df["total_spent"] = pd.to_numeric(
        users_df["total_spent"]
    )

    # Select the 10 highest-spending users
    top_users = users_df.nlargest(10, "total_spent")

    # Display user spending bar chart
    st.bar_chart(
        top_users,
        x="unique_id",
        y="total_spent"
    )

else:
    st.info("No user spending data available.")



# Company budget tracking
st.subheader("Company Budget Tracking")

if not budgets_df.empty:

    # Loop through each company's budget data
    for _, row in budgets_df.iterrows():

        company = row["company"]
        budget = float(row["budget_amount"])
        spent = float(row["total_spent"])
        remaining = float(row["remaining_budget"])

        # Calculate percentage of budget used
        percentage = (
            (spent / budget) * 100
            if budget > 0 else None
        )

        st.write(f"**{company}**")

        # Display budget utilization progress bar
        if percentage is not None:
            st.progress(
                min(max(percentage / 100, 0.0), 1.0),
                text=f"{percentage:.2f}% of budget used"
            )
        else:
            st.info("No budget allocated.")

        # Display budget metrics
        col1, col2, col3 = st.columns(3)

        col1.metric("Allocated Budget", f"${budget:,.2f}")
        col2.metric("Total Spent", f"${spent:,.8f}")
        col3.metric("Remaining", f"${remaining:,.8f}")

        # Warn when a company exceeds its budget
        if remaining < 0:
            st.warning(f"{company} has exceeded its budget.")

        st.divider()

else:
    st.info("No company budget data available.")
