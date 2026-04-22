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


def load_data():
    df = pd.read_csv("main_data.csv")
    df.columns = df.columns.str.strip()

    # datetime
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])

    # cleaning (harus sama persis)
    df = df.dropna(subset=["delivery_time", "review_score"])
    df = df[df["delivery_time"] >= 0]

    df["review_score"] = df["review_score"].astype(int)

    return df

df = load_data()

st.write("MAX delivery:", df["delivery_time"].max())

st.title("📊 Dashboard Analisis E-Commerce")

col1, col2 = st.columns(2)
col1.metric("Total Transaksi", len(df))
col2.metric("Rata-rata Review", round(df["review_score"].mean(), 2))

st.markdown("---")

st.header("🚚 Hubungan Delivery Time dengan Review Score")

order = sorted(df["review_score"].unique())

fig1, ax1 = plt.subplots(figsize=(8,5))
sns.boxplot(
    x="review_score",
    y="delivery_time",
    data=df,
    order=order,
    ax=ax1
)

ax1.set_title("Hubungan Delivery Time dengan Review Score (2017–2018)")
ax1.set_xlabel("Review Score")
ax1.set_ylabel("Delivery Time (Hari)")

st.pyplot(fig1)
plt.close(fig1)

avg_delivery = (
    df.groupby("review_score")["delivery_time"]
    .mean()
    .sort_index()
)

fig2, ax2 = plt.subplots(figsize=(8,5))
ax2.plot(
    avg_delivery.index,
    avg_delivery.values,
    marker="o"
)

ax2.set_title("Rata-rata Delivery Time berdasarkan Review Score (2017–2018)")
ax2.set_xlabel("Review Score")
ax2.set_ylabel("Rata-rata Delivery Time (Hari)")
ax2.grid(True)

st.pyplot(fig2)
plt.close(fig2)

st.markdown("---")

st.header("📊 Kategori Produk dengan Review Tertinggi dan Terendah")

cat_review = df.groupby("category_clean")["review_score"].mean()


top_5 = cat_review.sort_values(ascending=False).head(5)
bottom_5 = cat_review.sort_values().head(5)

combined = pd.concat([top_5, bottom_5])

fig3, ax3 = plt.subplots(figsize=(10,5))
combined.sort_values().plot(kind="barh", ax=ax3)

ax3.set_title("Kategori Produk dengan Review Tertinggi dan Terendah (2017–2018)")
ax3.set_xlabel("Rata-rata Review Score")
ax3.set_ylabel("Kategori Produk")

st.pyplot(fig3)
plt.close(fig3)
