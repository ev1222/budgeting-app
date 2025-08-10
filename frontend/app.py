import streamlit as st
import plotly.express as px
import requests
import pandas as pd
from datetime import date, timedelta
from typing import Optional
from fuzzywuzzy import fuzz, process

st.set_page_config(
    page_title="Budgeting App",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Budgeting Dashboard")

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

def query_purchases(start_date: Optional[date] = None, end_date: Optional[date] = None, 
                   categories: Optional[list] = None, descriptions: Optional[list] = None,
                   trip: Optional[str] = None, min_amount: Optional[float] = None, 
                   max_amount: Optional[float] = None):
    query = """
    query getPurchases($startDate: Date, $endDate: Date, $categories: [String!], 
                      $descriptions: [String!], $trip: String, $minAmount: Float, $maxAmount: Float) {
        purchases(filters: {startDate: $startDate, endDate: $endDate, categories: $categories,
                           descriptions: $descriptions, tripId: $trip, minAmount: $minAmount, maxAmount: $maxAmount}) {
            date
            amount
            description
            category
            tripId
        }
    }
    """
    
    variables = {}
    if start_date:
        variables["startDate"] = start_date.isoformat()
    if end_date:
        variables["endDate"] = end_date.isoformat()
    if categories:
        variables["categories"] = categories
    if descriptions:
        variables["descriptions"] = descriptions
    if trip:
        variables["trip"] = trip
    if min_amount is not None:
        variables["minAmount"] = min_amount
    if max_amount is not None:
        variables["maxAmount"] = max_amount
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to backend API. Make sure the backend is running at http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"⚠️ Error querying data: {str(e)}")
        return None

def get_all_purchases():
    query = """
    query getAllPurchases {
        purchases {
            category
            description
            tripId
            amount
        }
    }
    """
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except:
        return None

st.sidebar.header("🔍 Filters")

st.sidebar.subheader("📅 Date Range")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=365),
        key="start_date"
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=date.today(),
        key="end_date"
    )

if start_date > end_date:
    st.sidebar.error("Start date must be before end date")
    st.stop()

all_data = get_all_purchases()
if all_data and "data" in all_data and all_data["data"]["purchases"]:
    all_purchases = all_data["data"]["purchases"]
    
    available_categories = sorted(list(set(p["category"] for p in all_purchases if p["category"])))
    available_descriptions = sorted(list(set(p["description"] for p in all_purchases if p["description"])))
    available_trips = sorted(list(set(p["tripId"] for p in all_purchases if p["tripId"])))
    
    all_amounts = [float(p["amount"]) for p in all_purchases if p["amount"]]
    min_possible = min(all_amounts) if all_amounts else 0
    max_possible = max(all_amounts) if all_amounts else 1000
else:
    available_categories = []
    available_descriptions = []
    available_trips = []
    min_possible, max_possible = 0, 1000

st.sidebar.subheader("🏷️ Categories")
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=available_categories,
    default=[],
    key="categories"
)

st.sidebar.subheader("📝 Description Search")
description_search = st.sidebar.text_input(
    "Search descriptions (fuzzy matching)",
    value="",
    placeholder="e.g., coffee, restaurant, gas",
    key="description_search"
)

st.sidebar.subheader("✈️ Trip")
selected_trip = st.sidebar.selectbox(
    "Select Trip",
    options=["All"] + available_trips,
    index=0,
    key="trip"
)

st.sidebar.subheader("💵 Amount Range")
amount_col1, amount_col2 = st.sidebar.columns(2)
with amount_col1:
    min_amount = st.number_input(
        "Min Amount",
        min_value=0.0,
        max_value=float(max_possible),
        value=0.0,
        step=1.0,
        key="min_amount"
    )

with amount_col2:
    max_amount = st.number_input(
        "Max Amount", 
        min_value=0.0,
        max_value=float(max_possible),
        value=float(max_possible),
        step=1.0,
        key="max_amount"
    )

filter_trip = None if selected_trip == "All" else selected_trip
filter_categories = selected_categories if selected_categories else None  
filter_min_amount = min_amount if min_amount > 0 else None
filter_max_amount = max_amount if max_amount < max_possible else None

# Get data without description filter first (we'll apply fuzzy matching client-side)
data = query_purchases(
    start_date, end_date, filter_categories, None, 
    filter_trip, filter_min_amount, filter_max_amount
)

if data is None:
    st.stop()

if "errors" in data:
    st.error(f"GraphQL Error: {data['errors']}")
    st.stop()

purchases = data.get("data", {}).get("purchases", [])

# Apply fuzzy matching for description search
if description_search.strip():
    search_terms = [term.strip().lower() for term in description_search.split(',')]
    filtered_purchases = []
    
    for purchase in purchases:
        description = purchase.get('description', '').lower()
        # Check if any search term has a fuzzy match above threshold (70%)
        for term in search_terms:
            if fuzz.partial_ratio(term, description) >= 70:
                filtered_purchases.append(purchase)
                break  # Found a match, no need to check other terms
    
    purchases = filtered_purchases

active_filters = []
if filter_categories:
    active_filters.append(f"Categories: {', '.join(filter_categories)}")
if description_search.strip():
    active_filters.append(f"Description: '{description_search}'")
if filter_trip:
    active_filters.append(f"Trip: {filter_trip}")
if filter_min_amount is not None or filter_max_amount is not None:
    min_txt = f"${filter_min_amount}" if filter_min_amount else "0"
    max_txt = f"${filter_max_amount}" if filter_max_amount else "∞"
    active_filters.append(f"Amount: {min_txt} - {max_txt}")

if active_filters:
    st.info(f"🔍 **Active Filters:** {' | '.join(active_filters)}")

if not purchases:
    st.warning("No purchase data found for the selected filters.")
    st.stop()

df = pd.DataFrame(purchases)
df['date'] = pd.to_datetime(df['date'])
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

df_sorted = df.sort_values('date')

st.subheader("📈 Spending Over Time")

chart_type = st.selectbox(
    "Chart Type",
    ["Line Chart", "Scatter Plot", "Daily Totals", "Cumulative Spending"],
    index=2
)

if chart_type == "Line Chart":
    fig = px.line(
        df_sorted, 
        x='date', 
        y='amount',
        title=f"Individual Purchases ({len(df)} transactions)",
        hover_data=['description', 'category', 'tripId']
    )
elif chart_type == "Scatter Plot":
    fig = px.scatter(
        df_sorted, 
        x='date', 
        y='amount',
        title=f"Purchase Amounts ({len(df)} transactions)",
        hover_data=['description', 'category', 'tripId'],
        color='category'
    )
elif chart_type == "Daily Totals":
    daily_totals = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_totals.columns = ['date', 'total_amount']
    
    fig = px.bar(
        daily_totals,
        x='date',
        y='total_amount',
        title=f"Daily Spending Totals ({len(daily_totals)} days)"
    )
elif chart_type == "Cumulative Spending":
    df_sorted['cumulative'] = df_sorted['amount'].cumsum()
    fig = px.line(
        df_sorted,
        x='date',
        y='cumulative',
        title="Cumulative Spending Over Time"
    )

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Amount ($)",
    hovermode='x unified',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Spending",
        f"${df['amount'].sum():.2f}",
        f"{len(df)} transactions"
    )

with col2:
    avg_daily = df['amount'].sum() / max((end_date - start_date).days, 1)
    st.metric(
        "Daily Average",
        f"${avg_daily:.2f}",
        f"over {(end_date - start_date).days} days"
    )

with col3:
    st.metric(
        "Largest Purchase",
        f"${df['amount'].max():.2f}",
        f"on {df.loc[df['amount'].idxmax(), 'date'].strftime('%Y-%m-%d')}"
    )

if st.checkbox("Show Raw Data"):
    st.subheader("📋 Purchase Details")
    st.dataframe(
        df_sorted[['date', 'amount', 'description', 'category', 'trip']].reset_index(drop=True),
        use_container_width=True
    )
