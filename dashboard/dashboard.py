import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
orders = pd.read_csv('../data/order_df.csv') 
order_items = pd.read_csv('../data/order_items_df.csv')  
products = pd.read_csv('../data/product_df.csv')  
payments = pd.read_csv('../data/order_payments_df.csv') 
customer = pd.read_csv('../data/customer_df.csv') 

# Gabungkan data orders dengan customer untuk mendapatkan kota
order_customer = pd.merge(
    left=orders,
    right=customer[['customer_id', 'customer_city']],
    on='customer_id',
    how='left'
)

# Preprocessing Data
order_customer['order_purchase_date'] = pd.to_datetime(order_customer['order_purchase_timestamp'])
order_customer['year'] = order_customer['order_purchase_date'].dt.year
order_customer['month'] = order_customer['order_purchase_date'].dt.month

# Dapatkan 5 produk terlaris
order_items_products = pd.merge(
    left=order_items,
    right=products[['product_id', 'product_category_name']],
    on='product_id',
    how='left'
)

# Tambahkan kolom 'order_purchase_date' ke order_items_products
order_items_products = pd.merge(
    left=order_items_products,
    right=order_customer[['order_id', 'order_purchase_date']],
    on='order_id',
    how='left'
)

# Dapatkan 5 kategori produk terlaris
top_5_products = (
    order_items_products['product_category_name']
    .value_counts()
    .head(5)
    .index.tolist()
)

# Sidebar Filters
st.sidebar.title("Filters")

# Slider untuk Rentang Tahun
min_year = order_customer['year'].min()
max_year = order_customer['year'].max()
selected_year = st.sidebar.slider("Pilih Rentang Tahun", min_year, max_year, (min_year, max_year))

# Slider untuk Rentang Tanggal dalam Tahun Terpilih
filtered_by_year = order_customer[
    (order_customer['year'] >= selected_year[0]) & 
    (order_customer['year'] <= selected_year[1])
]
min_date = filtered_by_year['order_purchase_date'].min().date()
max_date = filtered_by_year['order_purchase_date'].max().date()
selected_date_range = st.sidebar.slider("Pilih Rentang Tanggal", min_date, max_date, (min_date, max_date))

# Combobox untuk memilih kategori produk
selected_product = st.sidebar.selectbox("Pilih Produk Top", options=top_5_products)

# Filter Data Berdasarkan Input
filtered_orders = filtered_by_year[
    (filtered_by_year['order_purchase_date'].dt.date >= selected_date_range[0]) & 
    (filtered_by_year['order_purchase_date'].dt.date <= selected_date_range[1])
]
filtered_order_items = order_items_products[
    (order_items_products['product_category_name'] == selected_product)
]

# Dashboard Content
st.title("5 Top Brazil E-Commerce Category Product Dashboard")

# Total Orders dan Revenue untuk Produk Terpilih
total_orders = filtered_order_items['order_id'].nunique()
total_revenue = filtered_order_items['price'].sum()

st.markdown(f"### Total Orders (Produk: {selected_product}): {total_orders}")
st.markdown(f"### Total Revenue: ${total_revenue:,.2f}")

# Plot Total Orders by Month
monthly_orders = (
    filtered_order_items.groupby(filtered_order_items['order_purchase_date'].dt.month)['order_id']
    .nunique()
)
fig, ax = plt.subplots()
monthly_orders.plot(kind='line', ax=ax, color='skyblue', marker='o')
ax.set_title(f'Total Orders by Month (Produk: {selected_product})')
ax.set_xlabel('Month')
ax.set_ylabel('Number of Orders')
st.pyplot(fig)

# Plot Distribusi Metode Pembayaran
payment_method_count = payments[payments['order_id'].isin(filtered_orders['order_id'])]['payment_type'].value_counts()
fig2, ax2 = plt.subplots()
payment_method_count.plot(kind='bar', ax=ax2, color='lightgreen')
ax2.set_title('Payment Methods Distribution')
ax2.set_xlabel('Payment Type')
ax2.set_ylabel('Count')
st.pyplot(fig2)

# Plot Distribusi Rating Produk
if 'review_score' in order_items.columns:
    product_reviews = order_items[order_items['product_id'].isin(filtered_order_items['product_id'])]
    fig3, ax3 = plt.subplots()
    sns.histplot(product_reviews['review_score'], bins=5, kde=False, ax=ax3, color='coral')
    ax3.set_title('Product Review Distribution')
    ax3.set_xlabel('Review Score')
    ax3.set_ylabel('Frequency')
    st.pyplot(fig3)

# Plot Distribusi Waktu Pengiriman
if 'shipping_limit_date' in order_items.columns:
    filtered_order_items['delivery_time'] = (
        pd.to_datetime(filtered_order_items['shipping_limit_date']) - pd.to_datetime(filtered_order_items['order_purchase_date'])
    ).dt.days
    fig4, ax4 = plt.subplots()
    sns.histplot(filtered_order_items['delivery_time'], bins=10, kde=True, ax=ax4, color='purple')
    ax4.set_title('Delivery Time Distribution')
    ax4.set_xlabel('Days')
    ax4.set_ylabel('Frequency')
    st.pyplot(fig4)

# Plot Peta Kota Pelanggan
city_distribution = filtered_orders['customer_city'].value_counts().head(10)
fig5, ax5 = plt.subplots()
city_distribution.plot(kind='bar', ax=ax5, color='gold')
ax5.set_title('Top 10 Customer Cities')
ax5.set_xlabel('City')
ax5.set_ylabel('Number of Customers')
st.pyplot(fig5)
