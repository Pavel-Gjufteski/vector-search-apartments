import streamlit as st
import pandas as pd

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("pazar3_scraped_data_test.csv")
    # Convert price to numeric (handle commas, coercing errors)
    df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',', '.'), errors='coerce')
    # Convert size to numeric, remove m², commas, strip spaces
    df['size'] = pd.to_numeric(
        df['size'].astype(str).str.replace('m²', '').str.replace(',', '.').str.strip(),
        errors='coerce'
    )
    # Drop rows with missing price or size
    df = df.dropna(subset=['price', 'size'])
    # Make sure location and title are strings
    df['location'] = df['location'].astype(str)
    df['title'] = df['title'].astype(str)
    return df

df = load_data()

st.title("🏢 Apartment Search - Skopje")

# Sidebar filters
locations = sorted(df['location'].unique())
selected_locations = st.sidebar.multiselect("Select Location(s)", locations, default=locations[:3])

min_price = float(df['price'].min())
max_price = float(df['price'].max())
price_range = st.sidebar.slider("Select Price Range (€)", min_price, max_price, (min_price, max_price))

min_size = float(df['size'].min())
max_size = float(df['size'].max())
size_range = st.sidebar.slider("Select Size Range (m²)", min_size, max_size, (min_size, max_size))

query = st.text_input("Search by Title (free text):")

# Filter dataframe based on inputs
filtered = df[
    (df['location'].isin(selected_locations)) &
    (df['price'].between(price_range[0], price_range[1])) &
    (df['size'].between(size_range[0], size_range[1])) &
    (df['title'].str.contains(query, case=False, na=False))
]

st.markdown(f"### Found {len(filtered)} listings matching filters")

for _, row in filtered.iterrows():
    st.subheader(row['title'])
    st.write(f"📍 Location: {row['location']}")
    st.write(f"💶 Price: {row['price']} €")
    st.write(f"📐 Size: {row['size']} m²")
    st.markdown("---")
