import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")

st.set_page_config(
    page_title="Dashboard Analisis E-Commerce",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df.columns = df.columns.str.strip()

    # datetime
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])

    # cleaning
    df = df.dropna(subset=["delivery_time", "review_score"])
    df = df[df["delivery_time"] >= 0]

    # filter sesuai analisis (time-bound 2017–2018)
    df = df[
        (df["order_purchase_timestamp"].dt.year >= 2017) &
        (df["order_purchase_timestamp"].dt.year <= 2018)
    ]

    # kategori
    df["category_clean"] = (
        df["category_clean"]
        .astype(str)
        .str.replace("_", " ")
        .str.title()
    )

    df["review_score"] = df["review_score"].astype(int)

    return df

df = load_data()

# SIDEBAR
st.sidebar.header("Filter Data")

selected_score = st.sidebar.multiselect(
    "Pilih Review Score",
    sorted(df["review_score"].unique()),
    default=sorted(df["review_score"].unique())
)

df = df[df["review_score"].isin(selected_score)]

st.title("📊 Dashboard Analisis E-Commerce")

col1, col2 = st.columns(2)
col1.metric("Total Transaksi", len(df))
col2.metric("Rata-rata Review", round(df["review_score"].mean(), 2))

st.markdown("---")

# PERTANYAAN 1
st.header("1. Hubungan Delivery Time dengan Review Score")

st.markdown(
    "Visualisasi berikut menunjukkan bagaimana lama waktu pengiriman memengaruhi tingkat kepuasan pelanggan."
)

# Boxplot
fig1, ax1 = plt.subplots(figsize=(8,5))
sns.boxplot(data=df, x="review_score", y="delivery_time", ax=ax1)
ax1.set_xlabel("Review Score")
ax1.set_ylabel("Delivery Time (Hari)")
st.pyplot(fig1)
plt.close(fig1)

# Rata-rata
avg_delivery = (
    df.groupby("review_score")["delivery_time"]
    .mean()
    .reset_index()
)

fig2, ax2 = plt.subplots(figsize=(8,5))
sns.lineplot(data=avg_delivery, x="review_score", y="delivery_time", marker="o", ax=ax2)
ax2.set_ylabel("Rata-rata Delivery Time")
st.pyplot(fig2)
plt.close(fig2)

st.info(
    "Semakin lama waktu pengiriman, cenderung review yang diberikan semakin rendah. "
    "Pengiriman yang cepat umumnya menghasilkan kepuasan pelanggan yang lebih tinggi."
)

st.markdown("---")

# PERTANYAAN 2
st.header("2. Kategori Produk dengan Kepuasan Tertinggi dan Terendah")

category_mean = (
    df.groupby("category_clean")["review_score"]
    .mean()
    .sort_values(ascending=False)
)

top10 = category_mean.head(10)
bottom10 = category_mean.tail(10).sort_values()

colA, colB = st.columns(2)

with colA:
    st.subheader("Top 10 Kategori")
    fig3, ax3 = plt.subplots(figsize=(8,5))
    sns.barplot(x=top10.values, y=top10.index, ax=ax3)
    st.pyplot(fig3)
    plt.close(fig3)

with colB:
    st.subheader("Bottom 10 Kategori")
    fig4, ax4 = plt.subplots(figsize=(8,5))
    sns.barplot(x=bottom10.values, y=bottom10.index, ax=ax4)
    st.pyplot(fig4)
    plt.close(fig4)

# Insight
st.info(
    "Terdapat perbedaan tingkat kepuasan antar kategori produk. "
    "Beberapa kategori memiliki performa tinggi, sementara kategori lain masih perlu evaluasi lebih lanjut."
)
