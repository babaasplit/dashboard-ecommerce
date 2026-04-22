import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Analisis E-Commerce")

@st.cache_data
def load_data():
    customers_df = pd.read_csv('customers_dataset.csv')
    items_df = pd.read_csv('order_items_dataset.csv')
    reviews_df = pd.read_csv('order_reviews_dataset.csv')
    orders_df = pd.read_csv('orders_dataset.csv')
    category_df = pd.read_csv('product_category_name_translation.csv')
    products_df = pd.read_csv('products_dataset.csv')

    # Convert datetime
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
    reviews_df['review_creation_date'] = pd.to_datetime(reviews_df['review_creation_date'])

    # Drop missing penting
    orders_df = orders_df.dropna(subset=['order_delivered_customer_date'])

    # Merge
    df = orders_df.merge(reviews_df, on='order_id')
    df = df.merge(items_df, on='order_id')
    df = df.merge(products_df, on='product_id')
    df = df.merge(category_df, on='product_category_name', how='left')

    # Delivery time
    df['delivery_time'] = (
        df['order_delivered_customer_date'] -
        df['order_purchase_timestamp']
    ).dt.days

    df = df[df['delivery_time'].notna()]
    df = df[df['delivery_time'] >= 0]

    df = df[
        (df['order_purchase_timestamp'].dt.year >= 2017) &
        (df['order_purchase_timestamp'].dt.year <= 2018)
    ]

    return df

main_data = load_data()

st.header("📦 Analisis Delivery Time")

st.write("Statistik Deskriptif Delivery Time (dalam hari):")
st.write(main_data['delivery_time'].describe())

fig1, ax1 = plt.subplots(figsize=(8,5))
ax1.hist(main_data['delivery_time'], bins=30)
ax1.set_title('Distribusi Delivery Time')
ax1.set_xlabel('Hari')
ax1.set_ylabel('Jumlah')
st.pyplot(fig1)

st.header("⭐ Analisis Review Score")

st.write("Distribusi Review Score:")
st.write(main_data['review_score'].value_counts())

fig2, ax2 = plt.subplots(figsize=(6,4))
sns.countplot(x='review_score', data=main_data, ax=ax2)
ax2.set_title('Distribusi Review Score')
st.pyplot(fig2)

st.header("🚚 Hubungan Delivery Time dengan Review Score")

st.write("Rata-rata Delivery Time berdasarkan Review Score:")
st.write(main_data.groupby('review_score')['delivery_time'].mean())

order = sorted(main_data['review_score'].unique())

fig3, ax3 = plt.subplots(figsize=(8,5))
sns.boxplot(
    x='review_score',
    y='delivery_time',
    data=main_data,
    order=order,
    ax=ax3
)

ax3.set_title('Hubungan Delivery Time dengan Review Score (2017–2018)')
ax3.set_xlabel('Review Score')
ax3.set_ylabel('Delivery Time (Hari)')
st.pyplot(fig3)

avg_delivery = (
    main_data.groupby('review_score')['delivery_time']
    .mean()
    .sort_index()
)

fig4, ax4 = plt.subplots(figsize=(8,5))
ax4.plot(
    avg_delivery.index,
    avg_delivery.values,
    marker='o'
)

ax4.set_title('Rata-rata Delivery Time berdasarkan Review Score (2017–2018)')
ax4.set_xlabel('Review Score')
ax4.set_ylabel('Rata-rata Delivery Time (Hari)')
ax4.grid(True)
st.pyplot(fig4)

st.header("📊 Analisis Kategori Produk")

main_data['category_clean'] = (
    main_data['product_category_name_english']
    .fillna('Other')
    .str.replace('_', ' ', regex=False)
    .str.title()
)

cat_review = main_data.groupby('category_clean')['review_score'].mean()

top_5 = cat_review.sort_values(ascending=False).head(5)
bottom_5 = cat_review.sort_values().head(5)

combined = pd.concat([top_5, bottom_5])

fig5, ax5 = plt.subplots(figsize=(10,5))
combined.sort_values().plot(kind='barh', ax=ax5)

ax5.set_title('Kategori Produk dengan Review Tertinggi dan Terendah (2017–2018)')
ax5.set_xlabel('Rata-rata Review Score')
ax5.set_ylabel('Kategori Produk')
st.pyplot(fig5)

st.header("⏱️ Delivery Time per Kategori Produk")

cat_delivery = main_data.groupby('category_clean')['delivery_time'].mean()

fast_5 = cat_delivery.sort_values().head(5)
slow_5 = cat_delivery.sort_values(ascending=False).head(5)

st.write("Kategori dengan pengiriman tercepat:")
st.write(fast_5)

st.write("Kategori dengan pengiriman terlama:")
st.write(slow_5)

combined2 = pd.concat([fast_5, slow_5])

fig6, ax6 = plt.subplots(figsize=(10,5))
combined2.sort_values().plot(kind='barh', ax=ax6)

ax6.set_title('Kategori dengan Delivery Time Tercepat & Terlama')
ax6.set_xlabel('Rata-rata Delivery Time (Hari)')
ax6.set_ylabel('Kategori Produk')
st.pyplot(fig6)
