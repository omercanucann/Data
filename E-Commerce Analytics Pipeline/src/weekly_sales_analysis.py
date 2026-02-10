import pandas as pd
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("data/processed", exist_ok=True)

sales_df = pd.read_csv(
    "data/E-commerece sales data 2024.csv",
    names=["user_id", "product_id", "interaction_type", "timestamp", "extra"],
    skiprows=1,
)
sales_df.drop(columns=["extra"], inplace=True, errors="ignore")

product_df = pd.read_csv("data/product_details.csv")
product_df.rename(
    columns={
        "Uniqe Id": "product_id",
        "Product Name": "product_name",
        "Category": "category",
        "Selling Price": "selling_price",
        "List Price": "list_price",
    },
    inplace=True,
)


sales_df.dropna(subset=["interaction_type"], inplace=True)
sales_df["interaction_type"] = sales_df["interaction_type"].str.strip()

sales_df["timestamp"] = pd.to_datetime(sales_df["timestamp"], format="mixed", dayfirst=True)

for col in ["selling_price", "list_price"]:
    product_df[col] = (
        product_df[col]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    product_df[col] = pd.to_numeric(product_df[col], errors="coerce")

merged_df = sales_df.merge(product_df[["product_id", "product_name", "category", "selling_price", "list_price"]], 
                           on="product_id", how="left")

merged_df["week"] = merged_df["timestamp"].dt.isocalendar().week.astype(int)
merged_df["year"] = merged_df["timestamp"].dt.year
merged_df["year_week"] = merged_df["year"].astype(str) + "-W" + merged_df["week"].astype(str).str.zfill(2)
merged_df["week_start"] = merged_df["timestamp"].dt.to_period("W").apply(lambda r: r.start_time)

purchases_df = merged_df[merged_df["interaction_type"] == "purchase"].copy()

weekly_sales_count = (
    purchases_df.groupby("year_week")
    .size()
    .reset_index(name="total_sales")
    .sort_values("year_week")
)

print("=" * 60)
print("HAFTALIK SATIŞ SAYISI")
print("=" * 60)
print(weekly_sales_count.to_string(index=False))

weekly_revenue = (
    purchases_df.groupby("year_week")["selling_price"]
    .agg(["sum", "mean", "count"])
    .rename(columns={"sum": "total_revenue", "mean": "avg_order_value", "count": "order_count"})
    .reset_index()
    .sort_values("year_week")
)

print("\n" + "=" * 60)
print("HAFTALIK TAHMİNİ GELİR")
print("=" * 60)
print(weekly_revenue.to_string(index=False))

weekly_interactions = (
    merged_df.groupby(["year_week", "interaction_type"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
    .sort_values("year_week")
)

print("\n" + "=" * 60)
print("HAFTALIK ETKİLEŞİM DAĞILIMI")
print("=" * 60)
print(weekly_interactions.to_string(index=False))

weekly_top_categories = (
    purchases_df.groupby(["year_week", "category"])
    .size()
    .reset_index(name="sales_count")
    .sort_values(["year_week", "sales_count"], ascending=[True, False])
)
top_categories = weekly_top_categories.groupby("year_week").head(5)

print("\n" + "=" * 60)
print("HAFTALIK EN ÇOK SATAN KATEGORİLER (Top 5)")
print("=" * 60)
print(top_categories.to_string(index=False))

weekly_top_products = (
    purchases_df.groupby(["year_week", "product_name"])
    .size()
    .reset_index(name="sales_count")
    .sort_values(["year_week", "sales_count"], ascending=[True, False])
)
top_products = weekly_top_products.groupby("year_week").head(5)

print("\n" + "=" * 60)
print("HAFTALIK EN ÇOK SATAN ÜRÜNLER (Top 5)")
print("=" * 60)
print(top_products.to_string(index=False))

weekly_conversion = merged_df.groupby("year_week").apply(
    lambda x: pd.Series({
        "total_interactions": len(x),
        "total_purchases": (x["interaction_type"] == "purchase").sum(),
        "conversion_rate": (x["interaction_type"] == "purchase").sum() / len(x) * 100,
    })
).reset_index().sort_values("year_week")

print("\n" + "=" * 60)
print("HAFTALIK DÖNÜŞÜM ORANI (%)")
print("=" * 60)
print(weekly_conversion.to_string(index=False))

fig, axes = plt.subplots(3, 2, figsize=(18, 14))
fig.suptitle("Haftalık Satış Analizi", fontsize=16, fontweight="bold")

# 1. Haftalık Satış Sayısı
ax1 = axes[0, 0]
ax1.plot(weekly_sales_count["year_week"], weekly_sales_count["total_sales"], 
         marker="o", color="#2196F3", linewidth=1.5, markersize=4)
ax1.set_title("Haftalık Satış Sayısı")
ax1.set_xlabel("Hafta")
ax1.set_ylabel("Satış Sayısı")
ax1.tick_params(axis="x", rotation=90, labelsize=6)
ax1.grid(True, alpha=0.3)

# 2. Haftalık Tahmini Gelir
ax2 = axes[0, 1]
ax2.bar(weekly_revenue["year_week"], weekly_revenue["total_revenue"], color="#4CAF50", alpha=0.8)
ax2.set_title("Haftalık Tahmini Gelir ($)")
ax2.set_xlabel("Hafta")
ax2.set_ylabel("Toplam Gelir ($)")
ax2.tick_params(axis="x", rotation=90, labelsize=6)
ax2.grid(True, alpha=0.3)

# 3. Haftalık Etkileşim Dağılımı (Stacked)
ax3 = axes[1, 0]
interaction_cols = [c for c in weekly_interactions.columns if c != "year_week"]
weekly_interactions.plot(
    x="year_week", y=interaction_cols, kind="bar", stacked=True, ax=ax3,
    color=["#FF9800", "#2196F3", "#4CAF50"]
)
ax3.set_title("Haftalık Etkileşim Dağılımı")
ax3.set_xlabel("Hafta")
ax3.set_ylabel("Etkileşim Sayısı")
ax3.tick_params(axis="x", rotation=90, labelsize=6)
ax3.legend(title="Etkileşim Tipi", fontsize=8)
ax3.grid(True, alpha=0.3)

# 4. Dönüşüm Oranı
ax4 = axes[1, 1]
ax4.plot(weekly_conversion["year_week"], weekly_conversion["conversion_rate"], 
         marker="s", color="#F44336", linewidth=1.5, markersize=4)
ax4.set_title("Haftalık Dönüşüm Oranı (%)")
ax4.set_xlabel("Hafta")
ax4.set_ylabel("Dönüşüm Oranı (%)")
ax4.tick_params(axis="x", rotation=90, labelsize=6)
ax4.grid(True, alpha=0.3)

# 5. Ortalama Sipariş Değeri
ax5 = axes[2, 0]
ax5.plot(weekly_revenue["year_week"], weekly_revenue["avg_order_value"], 
         marker="d", color="#9C27B0", linewidth=1.5, markersize=4)
ax5.set_title("Haftalık Ortalama Sipariş Değeri ($)")
ax5.set_xlabel("Hafta")
ax5.set_ylabel("Ort. Değer ($)")
ax5.tick_params(axis="x", rotation=90, labelsize=6)
ax5.grid(True, alpha=0.3)

# 6. Genel Kategori Bazlı Satış Dağılımı (Pie)
ax6 = axes[2, 1]
category_sales = (
    purchases_df.dropna(subset=["category"])
    .groupby("category")
    .size()
    .nlargest(8)
)
ax6.pie(category_sales.values, labels=[c[:30] + "..." if len(c) > 30 else c for c in category_sales.index],
        autopct="%1.1f%%", textprops={"fontsize": 7})
ax6.set_title("Genel Kategori Bazlı Satış Dağılımı (Top 8)")

plt.tight_layout()
plt.savefig("data/processed/weekly_sales_analysis.png", dpi=150, bbox_inches="tight")
plt.show()

print("\n" + "=" * 60)
print("GENEL ÖZET")
print("=" * 60)
print(f"Toplam Etkileşim Sayısı     : {len(merged_df):,}")
print(f"Toplam Satış (purchase)     : {len(purchases_df):,}")
print(f"Toplam Görüntüleme (view)   : {len(merged_df[merged_df['interaction_type'] == 'view']):,}")
print(f"Toplam Beğeni (like)        : {len(merged_df[merged_df['interaction_type'] == 'like']):,}")
print(f"Genel Dönüşüm Oranı        : {len(purchases_df) / len(merged_df) * 100:.2f}%")
print(f"Toplam Tahmini Gelir        : ${purchases_df['selling_price'].sum():,.2f}")
print(f"Ortalama Sipariş Değeri     : ${purchases_df['selling_price'].mean():,.2f}")
print(f"Benzersiz Ürün Sayısı       : {purchases_df['product_id'].nunique():,}")
print(f"Analiz Dönemi               : {merged_df['timestamp'].min().date()} - {merged_df['timestamp'].max().date()}")
print(f"Toplam Hafta Sayısı         : {merged_df['year_week'].nunique()}")