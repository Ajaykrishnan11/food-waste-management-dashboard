import streamlit as st
import pandas as pd
import os

# ---- STREAMLIT SETUP ----
st.set_page_config(page_title="Food Waste Dashboard", layout="wide")
st.title("🌱 Food Waste Management Dashboard")

# ---- LOAD DATA FROM CSV ----
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    providers = pd.read_csv(os.path.join(base_path, 'providers_data.csv'))
    receivers = pd.read_csv(os.path.join(base_path, 'receivers_data.csv'))
    food = pd.read_csv(os.path.join(base_path, 'food_listings_data.csv'))
    claims = pd.read_csv(os.path.join(base_path, 'claims_data.csv'))
    return providers, receivers, food, claims

providers, receivers, food, claims = load_data()

# ---- FILTER OPTIONS ----
city_list = sorted(providers['city'].dropna().unique().tolist())
food_types = sorted(food['food_type'].dropna().unique().tolist())
meal_types = sorted(food['meal_type'].dropna().unique().tolist())

selected_city = st.sidebar.selectbox("Filter by City", ["All"] + city_list)
selected_food = st.sidebar.selectbox("Filter by Food Type", ["All"] + food_types)
selected_meal = st.sidebar.selectbox("Filter by Meal Type", ["All"] + meal_types)

# ---- SIDEBAR MENU ----
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

# ---- ANALYTICS ----
if menu == "Total Providers per City":
    df = providers.groupby("city").size().reset_index(name="total_providers")
    st.dataframe(df)

elif menu == "Total Receivers per City":
    df = receivers.groupby("city").size().reset_index(name="total_receivers")
    st.dataframe(df)

elif menu == "Top Contributing Provider Type":
    df = providers['type'].value_counts().reset_index().rename(columns={'index': 'provider_type', 'type': 'count'})
    st.dataframe(df.head(1))

elif menu == "Top Food Receiver":
    df = claims.merge(receivers, on="receiver_id")
    df = df['name'].value_counts().reset_index().rename(columns={'index': 'receiver_name', 'name': 'total_claims'})
    st.dataframe(df.head(1))

elif menu == "Total Quantity of Food Available":
    st.metric("Total Quantity Available", int(food['quantity'].sum()))

elif menu == "City with Highest Food Listings":
    df = food['location'].value_counts().reset_index().rename(columns={'index': 'city', 'location': 'total_listings'})
    st.dataframe(df.head(1))

elif menu == "Most Common Food Types":
    df = food['food_type'].value_counts().reset_index().rename(columns={'index': 'food_type', 'food_type': 'count'})
    st.dataframe(df.head(2))

elif menu == "Claims per Food Item":
    df = claims.merge(food, on='food_id')
    df = df['food_name'].value_counts().reset_index().rename(columns={'index': 'food_name', 'food_name': 'number_of_claims'})
    st.dataframe(df)

elif menu == "Top Provider by Completed Claims":
    df = claims[claims['status'] == 'Completed'].merge(food, on='food_id').merge(providers, on='provider_id')
    df = df['name'].value_counts().reset_index().rename(columns={'index': 'provider_name', 'name': 'successful_claims'})
    st.dataframe(df.head(1))

elif menu == "Claims Status % Distribution":
    status_count = claims['status'].value_counts(normalize=True).mul(100).round(2).reset_index()
    status_count.columns = ['status', 'percentage']
    st.bar_chart(status_count.set_index('status'))

elif menu == "Average Quantity Claimed per Receiver":
    df = claims.merge(food, on='food_id').merge(receivers, on='receiver_id')
    df = df.groupby('name')['quantity'].mean().reset_index(name='avg_quantity')
    st.dataframe(df)

elif menu == "Top Claimed Meal Type":
    df = claims.merge(food, on='food_id')
    df = df['meal_type'].value_counts().reset_index().rename(columns={'index': 'meal_type', 'meal_type': 'count'})
    st.dataframe(df.head(1))

elif menu == "Total Quantity Donated by Each Provider":
    df = food.merge(providers, on='provider_id')
    df = df.groupby('name')['quantity'].sum().reset_index(name='total_quantity')
    st.dataframe(df)

elif menu == "Unclaimed Food Items":
    df = food[~food['food_id'].isin(claims['food_id'])]
    st.dataframe(df[['food_id', 'food_name']])

elif menu == "Receiver Types with Most Claims":
    df = claims.merge(receivers, on='receiver_id')
    df = df['type'].value_counts().reset_index().rename(columns={'index': 'receiver_type', 'type': 'total_claims'})
    st.dataframe(df)

elif menu == "Duplicate Food Listings":
    df = food.groupby(['food_name', 'provider_id']).size().reset_index(name='duplicates')
    df = df[df['duplicates'] > 1]
    st.dataframe(df)

elif menu == "Providers with Multiple Meal Types":
    df = food.groupby('provider_id')['meal_type'].nunique().reset_index()
    df = df[df['meal_type'] > 1]
    st.dataframe(df)

elif menu == "Top Food Listing Days":
    df = food['expiry_date'].value_counts().reset_index().rename(columns={'index': 'expiry_date', 'expiry_date': 'new_listings'})
    st.dataframe(df.head(5))

elif menu == "Providers with Avg Quantity > 10":
    df = food.groupby('provider_id')['quantity'].mean().reset_index()
    df = df[df['quantity'] > 10]
    st.dataframe(df)

elif menu == "Vegetarian/Vegan Only Providers":
    df = food.groupby('provider_id')['food_type'].nunique().reset_index()
    df = df[(df['food_type'] == 1) & (food.groupby('provider_id')['food_type'].min().isin(['Vegetarian', 'Vegan']))]
    st.dataframe(df)

elif menu == "City with Most Cancelled Claims":
    df = claims[claims['status'] == 'Cancelled'].merge(receivers, on='receiver_id')
    df = df['city'].value_counts().reset_index().rename(columns={'index': 'city', 'city': 'cancelled_claims'})
    st.dataframe(df.head(1))

elif menu == "Add New Food Listing":
    st.subheader("➕ Add New Food Listing (Temporary)")
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
            new_row = pd.DataFrame([{
                'food_id': food_id,
                'food_name': food_name,
                'quantity': quantity,
                'expiry_date': expiry_date,
                'provider_id': provider_id,
                'provider_type': provider_type,
                'location': location,
                'food_type': food_type,
                'meal_type': meal_type
            }])
            st.session_state['food_data'] = pd.concat([food, new_row], ignore_index=True)
            st.success("✅ Food item added (temporarily).")

elif menu == "Delete a Food Item":
    st.subheader("🗑️ Delete a Food Listing (Temporary)")
    selected = st.selectbox("Select Food ID to delete", food['food_id'])
    if st.button("Delete"):
        updated_df = food[food['food_id'] != selected]
        st.session_state['food_data'] = updated_df
        st.success(f"✅ Deleted food item with ID {selected} (temporarily).")

