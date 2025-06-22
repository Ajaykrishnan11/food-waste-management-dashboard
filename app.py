import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ---- DATABASE CONNECTION ----
DB_USER = "postgres"          
DB_PASS = "Ajay2000"               
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "Food_waste"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ---- STREAMLIT SETUP ----
st.set_page_config(page_title="Food Waste Dashboard", layout="wide")
st.title("🌱 Food Waste Management Dashboard")

# ---- FILTER OPTIONS ----
city_list = pd.read_sql("SELECT DISTINCT city FROM providers_data", engine)['city'].tolist()
food_types = pd.read_sql("SELECT DISTINCT food_type FROM food_listings_data", engine)['food_type'].tolist()
meal_types = pd.read_sql("SELECT DISTINCT meal_type FROM food_listings_data", engine)['meal_type'].tolist()

selected_city = st.sidebar.selectbox("Filter by City", ["All"] + city_list)
selected_food = st.sidebar.selectbox("Filter by Food Type", ["All"] + food_types)
selected_meal = st.sidebar.selectbox("Filter by Meal Type", ["All"] + meal_types)

# ---- REPORT MENU ----
menu = st.sidebar.selectbox("Choose a report", [
    "Total Providers per City",
    "Total Receivers per City",
    "Top Contributing Provider Type",
    "Top Food Receiver",
    "Total Quantity of Food Available",
    "City with Highest Food Listings",
    "Most Common Food Types",
    "Claims per Food Item",
    "Top Provider by Completed Claims",
    "Claims Status % Distribution",
    "Average Quantity Claimed per Receiver",
    "Top Claimed Meal Type",
    "Total Quantity Donated by Each Provider",
    "Unclaimed Food Items",
    "Receiver Types with Most Claims",
    "Duplicate Food Listings",
    "Providers with Multiple Meal Types",
    "Top Food Listing Days",
    "Providers with Avg Quantity > 10",
    "Vegetarian/Vegan Only Providers",
    "City with Most Cancelled Claims",
    "Add New Food Listing",
    "Delete a Food Item"
])

# ---- MAIN QUERIES ----
queries = {
    "Total Providers per City": """
        SELECT city, COUNT(*) AS total_providers
        FROM providers_data
        GROUP BY city ORDER BY total_providers DESC;
    """,
    "Total Receivers per City": """
        SELECT city, COUNT(*) AS total_receivers
        FROM receivers_data
        GROUP BY city ORDER BY total_receivers DESC;
    """,
    "Top Contributing Provider Type": """
        SELECT type, COUNT(*) AS count FROM providers_data
        GROUP BY type ORDER BY count DESC LIMIT 1;
    """,
    "Top Food Receiver": """
        SELECT r.name AS receiver_name, COUNT(c.claim_id) AS total_claims
        FROM receivers_data r JOIN claims_data c ON r.receiver_id = c.receiver_id
        GROUP BY r.name ORDER BY total_claims DESC LIMIT 1;
    """,
    "Total Quantity of Food Available": """
        SELECT SUM(quantity) AS total_quantity FROM food_listings_data;
    """,
    "City with Highest Food Listings": """
        SELECT location AS city, COUNT(*) AS total_listings
        FROM food_listings_data GROUP BY location ORDER BY total_listings DESC LIMIT 1;
    """,
    "Most Common Food Types": """
        SELECT food_type, COUNT(*) AS count FROM food_listings_data
        GROUP BY food_type ORDER BY count DESC LIMIT 2;
    """,
    "Claims per Food Item": """
        SELECT food_name, COUNT(*) AS number_of_claims
        FROM claims_data c JOIN food_listings_data f ON c.food_id = f.food_id
        GROUP BY food_name;
    """,
    "Top Provider by Completed Claims": """
        SELECT p.name, COUNT(*) AS successful_claims
        FROM claims_data c
        JOIN food_listings_data f ON c.food_id = f.food_id
        JOIN providers_data p ON f.provider_id = p.provider_id
        WHERE c.status = 'Completed'
        GROUP BY p.name ORDER BY successful_claims DESC LIMIT 1;
    """,
    "Claims Status % Distribution": """
        SELECT status, COUNT(*) AS claim_count,
        ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data)), 2) AS percentage
        FROM claims_data GROUP BY status;
    """,
    "Average Quantity Claimed per Receiver": """
        SELECT r.name, AVG(f.quantity) AS avg_quantity
        FROM claims_data c
        JOIN food_listings_data f ON c.food_id = f.food_id
        JOIN receivers_data r ON c.receiver_id = r.receiver_id
        GROUP BY r.name;
    """,
    "Top Claimed Meal Type": """
        SELECT meal_type, COUNT(*) AS count
        FROM claims_data c
        JOIN food_listings_data f ON c.food_id = f.food_id
        GROUP BY meal_type ORDER BY count DESC LIMIT 1;
    """,
    "Total Quantity Donated by Each Provider": """
        SELECT p.name AS provider_name, SUM(f.quantity) AS total_quantity
        FROM food_listings_data f
        JOIN providers_data p ON f.provider_id = p.provider_id
        GROUP BY p.name ORDER BY total_quantity DESC;
    """,
    "Unclaimed Food Items": """
        SELECT f.food_name, f.food_id FROM food_listings_data f
        LEFT JOIN claims_data c ON f.food_id = c.food_id
        WHERE c.claim_id IS NULL;
    """,
    "Receiver Types with Most Claims": """
        SELECT r.type, COUNT(*) AS total_claims FROM claims_data c
        JOIN receivers_data r ON c.receiver_id = r.receiver_id
        GROUP BY r.type ORDER BY total_claims DESC;
    """,
    "Duplicate Food Listings": """
        SELECT food_name, provider_id, COUNT(*) AS duplicates
        FROM food_listings_data GROUP BY food_name, provider_id
        HAVING COUNT(*) > 1;
    """,
    "Providers with Multiple Meal Types": """
        SELECT provider_id FROM food_listings_data
        GROUP BY provider_id HAVING COUNT(DISTINCT meal_type) > 1;
    """,
    "Top Food Listing Days": """
        SELECT expiry_date, COUNT(*) AS new_listings FROM food_listings_data
        GROUP BY expiry_date ORDER BY new_listings DESC LIMIT 5;
    """,
    "Providers with Avg Quantity > 10": """
        SELECT provider_id, AVG(quantity) AS avg_quantity FROM food_listings_data
        GROUP BY provider_id HAVING AVG(quantity) > 10;
    """,
    "Vegetarian/Vegan Only Providers": """
        SELECT provider_id FROM food_listings_data
        GROUP BY provider_id HAVING COUNT(DISTINCT food_type) = 1
        AND MIN(food_type) IN ('Vegetarian', 'Vegan');
    """,
    "City with Most Cancelled Claims": """
        SELECT r.city, COUNT(*) AS cancelled_claims
        FROM claims_data c JOIN receivers_data r ON c.receiver_id = r.receiver_id
        WHERE c.status = 'Cancelled'
        GROUP BY r.city ORDER BY cancelled_claims DESC LIMIT 1;
    """
}

# ---- QUERY EXECUTION ----
def run_query(query):
    return pd.read_sql(text(query), engine)

if menu in queries:
    df = run_query(queries[menu])
    st.subheader(menu)
    if menu == "Claims Status % Distribution":
        st.bar_chart(df.set_index("status")["percentage"])
    else:
        st.dataframe(df)

# ---- CRUD: ADD FOOD ----
elif menu == "Add New Food Listing":
    st.subheader("➕ Add New Food Listing")
    with st.form("add_form"):
        food_id = st.text_input("Food ID")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", step=1)
        expiry_date = st.date_input("Expiry Date")
        provider_id = st.text_input("Provider ID")
        provider_type = st.text_input("Provider Type")
        location = st.selectbox("City", city_list)
        food_type = st.selectbox("Food Type", food_types)
        meal_type = st.selectbox("Meal Type", meal_types)
        submit = st.form_submit_button("Add Food")

        if submit:
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO food_listings_data
                    (food_id, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
                    VALUES (:food_id, :food_name, :quantity, :expiry_date, :provider_id, :provider_type, :location, :food_type, :meal_type)
                """), locals())
            st.success("✅ Food item added successfully.")

# ---- CRUD: DELETE FOOD ----
elif menu == "Delete a Food Item":
    st.subheader("🗑️ Delete a Food Listing")
    df = run_query("SELECT food_id, food_name FROM food_listings_data")
    selected = st.selectbox("Select Food ID to delete", df['food_id'])
    if st.button("Delete"):
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM food_listings_data WHERE food_id = :fid"), {"fid": selected})
        st.success(f"✅ Deleted food item with ID {selected}.")

