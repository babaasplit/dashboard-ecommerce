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

# =====================
# LOAD DATA
# =====================
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df.columns = df.columns.str.strip()

    # datetime
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")

    # cleaning WAJIB SAMA KAYAK NOTEBOOK
    df = df.dropna(subset=["delivery_time", "review_score"])
    df = df[df["delivery_time"] >= 0]

    # filter tahun
    df = df[
        (df["order_purchase_timestamp"].dt.year >= 2017) &
        (df["order_purchase_timestamp"].dt.year <= 2018)
    ]

    # kategori (jangan error kalau belum ada)
    if "category_clean" not in df.columns:
        if "product_category_name_english" in df.columns:
            df["category_clean"] = (
                df["product_category_name_english"]
                .fillna("Other")
                .str.replace("_", " ", regex=False)
                .str.title()
            )
        else:
            df["category_clean"] = "Other"

    df["review_score"] = df["review_score"].astype(int)

    return df

df = load_data()

# =====================
# SIDEBAR
# =====================
st.sidebar.header("Filter Data")

selected_score = st.sidebar.multiselect(
    "Pilih Review Score",
    sorted(df["review_score"].unique()),
    default=sorted(df["review_score"].unique())
)

df = df[df["review_score"].isin(selected_score)]

# =====================
# HEADER
# =====================
st.title("📊 Dashboard Analisis E-Commerce")

col1, col2 = st.columns(2)
col1.metric("Total Transaksi", len(df))
col2.metric("Rata-rata Review", round(df["review_score"].mean(), 2))

st.markdown("---")

# =====================
# 1. DISTRIBUSI DELIVERY TIME (SAMA KAYAK NOTEBOOK)
# =====================
st.header("📦 Distribusi Delivery Time")

st.write(df["delivery_time"].describe())

fig1, ax1 = plt.subplots(figsize=(8,5))
ax1.hist(df["delivery_time"], bins=30)
ax1.set_title("Distribusi Delivery Time")
ax1.set_xlabel("Hari")
ax1.set_ylabel("Jumlah")
st.pyplot(fig1)
plt.close(fig1)

# =====================
# 2. DISTRIBUSI REVIEW SCORE
# =====================
st.header("⭐ Distribusi Review Score")

st.write(df["review_score"].value_counts())

fig2, ax2 = plt.subplots(figsize=(6,4))
sns.countplot(x="review_score", data=df, ax=ax2)
ax2.set_title("Distribusi Review Score")
st.pyplot(fig2)
plt.close(fig2)

# =====================
# 3. HUBUNGAN DELIVERY vs REVIEW (INI YANG KAMU SALAH SEBELUMNYA)
# =====================
st.header("🚚 Hubungan Delivery Time dengan Review Score")

# BOXPLOT (WAJIB ADA)
fig3, ax3 = plt.subplots(figsize=(8,5))
sns.boxplot(x="review_score", y="delivery_time", data=df, ax=ax3)
ax3.set_title("Hubungan Delivery Time dengan Review Score (2017–2018)")
ax3.set_xlabel("Review Score")
ax3.set_ylabel("Delivery Time (Hari)")
st.pyplot(fig3)
plt.close(fig3)

# LINEPLOT RATA-RATA
avg_delivery = df.groupby("review_score")["delivery_time"].mean().sort_index()

fig4, ax4 = plt.subplots(figsize=(8,5))
ax4.plot(avg_delivery.index, avg_delivery.values, marker="o")
ax4.set_title("Rata-rata Delivery Time berdasarkan Review Score (2017–2018)")
ax4.set_xlabel("Review Score")
ax4.set_ylabel("Rata-rata Delivery Time (Hari)")
ax4.grid(True)
st.pyplot(fig4)
plt.close(fig4)

st.markdown("---")

# =====================
# 4. KATEGORI PRODUK (TOP & BOTTOM FIX)
# =====================
st.header("📊 Kategori Produk dengan Review Tertinggi & Terendah")

cat_review = df.groupby("category_clean")["review_score"].mean()

top5 = cat_review.sort_values(ascending=False).head(5)
bottom5 = cat_review.sort_values().head(5)

combined = pd.concat([top5, bottom5])

fig5, ax5 = plt.subplots(figsize=(10,5))
combined.sort_values().plot(kind="barh", ax=ax5)
ax5.set_title("Kategori Produk dengan Review Tertinggi dan Terendah (2017–2018)")
ax5.set_xlabel("Rata-rata Review Score")
ax5.set_ylabel("Kategori Produk")
st.pyplot(fig5)
plt.close(fig5)

# =====================
# 5. DELIVERY TIME PER KATEGORI
# =====================
st.header("⏱️ Delivery Time per Kategori Produk")

cat_delivery = df.groupby("category_clean")["delivery_time"].mean()

fast5 = cat_delivery.sort_values().head(5)
slow5 = cat_delivery.sort_values(ascending=False).head(5)

combined2 = pd.concat([fast5, slow5])

fig6, ax6 = plt.subplots(figsize=(10,5))
combined2.sort_values().plot(kind="barh", ax=ax6)
ax6.set_title("Kategori dengan Delivery Time Tercepat & Terlama")
ax6.set_xlabel("Rata-rata Delivery Time (Hari)")
ax6.set_ylabel("Kategori Produk")
st.pyplot(fig6)
plt.close(fig6)
