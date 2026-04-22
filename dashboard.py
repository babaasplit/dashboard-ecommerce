import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    page_icon="📊",
    layout="wide"
)

sns.set(style="whitegrid")

# Fungsi untuk memuat dan membersihkan data
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df.columns = df.columns.str.strip()

    # Konversi tipe data datetime
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])

    # Pembersihan data
    df = df.dropna(subset=["delivery_time", "review_score"])
    df = df[df["delivery_time"] >= 0]

    # Filter data tahun 2017–2018
    df = df[
        (df["order_purchase_timestamp"].dt.year >= 2017) &
        (df["order_purchase_timestamp"].dt.year <= 2018)
    ]

    return df

# Memuat data
df = load_data()

st.sidebar.header("Filter Data")
selected_score = st.sidebar.multiselect(
    "Pilih Review Score",
    sorted(df["review_score"].unique()),
    default=sorted(df["review_score"].unique())
)

df_filtered = df[df["review_score"].isin(selected_score)].copy()

st.title("📊 Dashboard Analisis E-Commerce")

col1, col2 = st.columns(2)
col1.metric("Total Transaksi", len(df_filtered))
col2.metric("Rata-rata Review", round(df_filtered["review_score"].mean(), 2))

st.markdown("---")

st.header("1. Hubungan Delivery Time dengan Review Score (2017–2018)")

order = sorted(df_filtered['review_score'].unique())

fig1, ax1 = plt.subplots(figsize=(8,5))
sns.boxplot(
    x='review_score',
    y='delivery_time',
    data=df_filtered,
    order=order,
    ax=ax1
)

ax1.set_title('Hubungan Delivery Time dengan Review Score (2017–2018)')
ax1.set_xlabel('Review Score')
ax1.set_ylabel('Delivery Time (Hari)')

plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

# Rata-rata delivery time
avg_delivery = (
    df_filtered.groupby('review_score')['delivery_time']
    .mean()
    .sort_index()
)

fig2, ax2 = plt.subplots(figsize=(8,5))
ax2.plot(
    avg_delivery.index,
    avg_delivery.values,
    marker='o'
)

ax2.set_title('Rata-rata Delivery Time berdasarkan Review Score (2017–2018)')
ax2.set_xlabel('Review Score')
ax2.set_ylabel('Rata-rata Delivery Time (Hari)')
ax2.grid(True)

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

st.markdown("---")

st.header("2. Kategori Produk dengan Review Tertinggi dan Terendah (2017–2018)")

# Pilih kolom kategori yang tersedia
if 'product_category_name_english' in df_filtered.columns:
    category_col = 'product_category_name_english'
elif 'product_category_name' in df_filtered.columns:
    category_col = 'product_category_name'
elif 'category_clean' in df_filtered.columns:
    category_col = 'category_clean'
else:
    st.error("Kolom kategori produk tidak ditemukan dalam dataset.")
    st.stop()

# Cleaning kategori
df_filtered['category_clean'] = (
    df_filtered[category_col]
    .fillna('Other')
    .astype(str)
    .str.replace('_', ' ', regex=False)
    .str.title()
)

# Rata-rata review per kategori
cat_review = df_filtered.groupby('category_clean')['review_score'].mean()

# Top 5 dan Bottom 5
top_5 = cat_review.sort_values(ascending=False).head(5)
bottom_5 = cat_review.sort_values().head(5)

combined = pd.concat([top_5, bottom_5])

fig3, ax3 = plt.subplots(figsize=(10,5))
combined.sort_values().plot(
    kind='barh',
    ax=ax3
)

ax3.set_title('Kategori Produk dengan Review Tertinggi dan Terendah (2017–2018)')
ax3.set_xlabel('Rata-rata Review Score')
ax3.set_ylabel('Kategori Produk')

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)
