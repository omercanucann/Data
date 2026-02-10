import pandas as pd
import numpy as np
import re
import warnings
import os

warnings.filterwarnings("ignore")

INPUT_PATH = "data/product_details.csv"
OUTPUT_PATH = "data/cleaned_product_details.csv"

df = pd.read_csv(INPUT_PATH)
print(f"Orijinal veri: {df.shape[0]} satır, {df.shape[1]} sütun")
print(f"Sütunlar: {df.columns.tolist()}\n")

df.rename(columns={
    "Uniqe Id": "product_id",
    "Product Name": "product_name",
    "Brand Name": "brand",
    "Asin": "asin",
    "Category": "category",
    "Upc Ean Code": "upc_ean_code",
    "List Price": "list_price",
    "Selling Price": "selling_price",
    "Quantity": "quantity",
    "Model Number": "model_number",
    "About Product": "about_product",
    "Product Specification": "product_specification",
    "Technical Details": "technical_details",
    "Shipping Weight": "shipping_weight",
    "Product Dimensions": "product_dimensions",
    "Image": "image_urls",
    "Variants": "variants",
    "Sku": "sku",
    "Product Url": "product_url",
    "Stock": "stock",
    "Product Details": "product_details",
    "Dimensions": "dimensions",
    "Color": "color",
    "Ingredients": "ingredients",
    "Direction To Use": "direction_to_use",
    "Is Amazon Seller": "is_amazon_seller",
    "Size Quantity Variant": "size_quantity_variant",
    "Product Description": "product_description",
}, inplace=True)

print("✅ Sütun isimleri standartlaştırıldı.\n")

dup_count_before = df.duplicated().sum()
df.drop_duplicates(inplace=True)
dup_id_before = df.duplicated(subset=["product_id"]).sum()
df.drop_duplicates(subset=["product_id"], keep="first", inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"✅ Tam tekrar eden satır kaldırıldı: {dup_count_before}")
print(f"✅ Aynı product_id'ye sahip tekrar eden satır kaldırıldı: {dup_id_before}\n")

def clean_price(series):
    """Fiyat sütunlarını temizler: $, virgül kaldırır, aralık varsa min değeri alır."""
    def parse_price(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip()
        if val == "" or val.lower() in ["nan", "none"]:
            return np.nan
        range_match = re.search(r"\$\s*([\d,.]+)\s*-\s*\$\s*([\d,.]+)", val)
        if range_match:
            val = range_match.group(1)
        else:
            val = val.replace("$", "")
        val = val.replace(",", "").strip()
        if val == "" or val == ".":
            return np.nan
        try:
            return float(val)
        except ValueError:
            return np.nan
    return series.apply(parse_price)

df["selling_price"] = clean_price(df["selling_price"])
df["list_price"] = clean_price(df["list_price"])

print(f"✅ Fiyat sütunları temizlendi.")
print(f"   selling_price NaN: {df['selling_price'].isna().sum()}")
print(f"   list_price NaN: {df['list_price'].isna().sum()}\n")

def clean_quantity(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip().replace(",", "")
    if val == "" or val == "." or val.lower() in ["nan", "none"]:
        return np.nan
    match = re.search(r"(\d+\.?\d*)", val)
    if match:
        num = float(match.group(1))
        return int(num) if num == int(num) else num
    return np.nan

df["quantity"] = df["quantity"].apply(clean_quantity)
print(f"✅ Quantity sütunu temizlendi. NaN: {df['quantity'].isna().sum()}\n")

def clean_weight(val):
    """Shipping weight'i ounce cinsinden sayıya çevirir."""
    if pd.isna(val):
        return np.nan
    val = str(val).strip().lower()
    if val in ["", "nan", "none", "."]:
        return np.nan
    val = re.sub(r"\(.*?\)", "", val).strip()
    
    weight_oz = 0.0
    match_lbs = re.search(r"(\d[\d,.]*)\s*(pounds?|lbs?)", val)
    if match_lbs:
        num_str = match_lbs.group(1).replace(",", "")
        # Sadece nokta olan veya boş olan değerleri atla
        if num_str not in ("", "."):
            try:
                weight_oz += float(num_str) * 16
            except ValueError:
                pass
    match_oz = re.search(r"(\d[\d,.]*)\s*(ounces?|oz)", val)
    if match_oz:
        num_str = match_oz.group(1).replace(",", "")
        if num_str not in ("", "."):
            try:
                weight_oz += float(num_str)
            except ValueError:
                pass
    
    if weight_oz == 0.0:
        clean_val = re.sub(r"[^0-9.]", "", val)
        if clean_val and clean_val != ".":
            try:
                weight_oz = float(clean_val) * 16
            except ValueError:
                return np.nan
    
    return weight_oz if weight_oz > 0 else np.nan

df["shipping_weight_oz"] = df["shipping_weight"].apply(clean_weight)
print(f"✅ Shipping weight sayısallaştırıldı (ounces). NaN: {df['shipping_weight_oz'].isna().sum()}\n")

def clean_dimensions(val):
    """Boyut stringinden inches cinsinden (L, W, H) çıkarır."""
    if pd.isna(val):
        return np.nan, np.nan, np.nan
    val = str(val).strip()
    match = re.search(r"([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)", val, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1)), float(match.group(2)), float(match.group(3))
        except ValueError:
            return np.nan, np.nan, np.nan
    match2 = re.search(r"([\d.]+)\s*x\s*([\d.]+)", val, re.IGNORECASE)
    if match2:
        try:
            return float(match2.group(1)), float(match2.group(2)), np.nan
        except ValueError:
            return np.nan, np.nan, np.nan
    return np.nan, np.nan, np.nan

dims = df["product_dimensions"].apply(clean_dimensions)
df["dim_length"] = dims.apply(lambda x: x[0])
df["dim_width"] = dims.apply(lambda x: x[1])
df["dim_height"] = dims.apply(lambda x: x[2])
print(f"✅ Product dimensions ayrıştırıldı (L/W/H inches).\n")

def extract_main_category(val):
    if pd.isna(val):
        return "Unknown"
    val = str(val).strip()
    if val == "":
        return "Unknown"
    parts = val.split("|")
    return parts[0].strip() if parts else "Unknown"

def extract_sub_category(val):
    if pd.isna(val):
        return "Unknown"
    val = str(val).strip()
    parts = val.split("|")
    if len(parts) >= 2:
        return parts[1].strip()
    return "Unknown"

df["main_category"] = df["category"].apply(extract_main_category)
df["sub_category"] = df["category"].apply(extract_sub_category)
print(f"✅ Kategoriler ayrıştırıldı.")
print(f"   Ana kategori dağılımı:\n{df['main_category'].value_counts().head(10)}\n")

def clean_product_name(val):
    if pd.isna(val):
        return "Unknown"
    val = str(val).strip()
    val = val.strip('"').strip("'")
    val = re.sub(r"\s+", " ", val)
    return val if val else "Unknown"

df["product_name"] = df["product_name"].apply(clean_product_name)
print(f"✅ Ürün isimleri temizlendi.\n")

df["brand"] = df["brand"].fillna("Unknown").astype(str).str.strip()
df.loc[df["brand"].isin(["", "nan", "None"]), "brand"] = "Unknown"
print(f"✅ Brand temizlendi. Unknown sayısı: {(df['brand'] == 'Unknown').sum()}\n")

def clean_boolean(val):
    if pd.isna(val):
        return False
    val = str(val).strip().upper()
    return val in ["Y", "YES", "TRUE", "1"]

df["is_amazon_seller"] = df["is_amazon_seller"].apply(clean_boolean)
print(f"✅ is_amazon_seller boolean'a çevrildi. True: {df['is_amazon_seller'].sum()}\n")

def count_images(val):
    if pd.isna(val):
        return 0
    urls = str(val).split("|")
    valid = [u for u in urls if "http" in u and "transparent-pixel" not in u]
    return len(valid)

df["image_count"] = df["image_urls"].apply(count_images)
print(f"✅ Görsel sayısı hesaplandı. Ortalama: {df['image_count'].mean():.1f}\n")

mask_swap = (df["selling_price"].notna() & df["list_price"].notna() & 
             (df["selling_price"] > df["list_price"]))
swap_count = mask_swap.sum()
df.loc[mask_swap, ["selling_price", "list_price"]] = (
    df.loc[mask_swap, ["list_price", "selling_price"]].values
)
print(f"✅ Fiyat tutarsızlıkları düzeltildi (selling > list swap): {swap_count}\n")

mask_no_sell = df["selling_price"].isna() & df["list_price"].notna()
df.loc[mask_no_sell, "selling_price"] = df.loc[mask_no_sell, "list_price"] * 0.85
filled_sell = mask_no_sell.sum()

mask_no_list = df["list_price"].isna() & df["selling_price"].notna()
df.loc[mask_no_list, "list_price"] = df.loc[mask_no_list, "selling_price"] * 1.15
filled_list = mask_no_list.sum()

print(f"✅ Eksik fiyat tahmini yapıldı.")
print(f"   selling_price doldurulan: {filled_sell}")
print(f"   list_price doldurulan: {filled_list}\n")

df["discount_amount"] = df["list_price"] - df["selling_price"]
df["discount_pct"] = ((df["discount_amount"] / df["list_price"]) * 100).round(2)
df.loc[df["discount_pct"] < 0, "discount_pct"] = 0.0
print(f"✅ İndirim oranları hesaplandı. Ortalama indirim: %{df['discount_pct'].mean():.1f}\n")

def clean_about_product(val):
    if pd.isna(val):
        return ""
    val = str(val).strip()
    val = val.replace("Make sure this fits by entering your model number.", "").strip()
    val = val.lstrip("| ").strip()
    return val

df["about_product"] = df["about_product"].apply(clean_about_product)
print(f"✅ About product temizlendi.\n")

print("=" * 60)
print("📊 EKSİK VERİ ÖZETİ")
print("=" * 60)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(1)
missing_df = pd.DataFrame({"Eksik": missing, "Yüzde (%)": missing_pct})
missing_df = missing_df[missing_df["Eksik"] > 0].sort_values("Yüzde (%)", ascending=False)
print(missing_df.to_string())
print()

print("=" * 60)
print("📊 SAYISAL SÜTUN İSTATİSTİKLERİ")
print("=" * 60)
numeric_cols = ["selling_price", "list_price", "quantity", "shipping_weight_oz",
                "discount_pct", "image_count"]
existing_numeric = [c for c in numeric_cols if c in df.columns]
print(df[existing_numeric].describe().round(2).to_string())
print()

print("=" * 60)
print("📊 AYKIRI DEĞER TESPİTİ (Fiyat)")
print("=" * 60)
for col in ["selling_price", "list_price"]:
    if col in df.columns and df[col].notna().sum() > 0:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((df[col] < lower) | (df[col] > upper)).sum()
        print(f"  {col}: Q1={Q1:.2f}, Q3={Q3:.2f}, IQR={IQR:.2f}")
        print(f"    Alt sınır: {lower:.2f}, Üst sınır: {upper:.2f}")
        print(f"    Aykırı değer sayısı: {outliers}")
print()

output_cols = [
    "product_id", "product_name", "brand", "asin",
    "main_category", "sub_category", "category",
    "upc_ean_code", "list_price", "selling_price",
    "discount_amount", "discount_pct",
    "quantity", "model_number",
    "about_product", "product_specification", "technical_details",
    "shipping_weight_oz", "dim_length", "dim_width", "dim_height",
    "image_urls", "image_count", "variants", "sku",
    "product_url", "stock", "color",
    "is_amazon_seller", "product_description"
]
output_cols = [c for c in output_cols if c in df.columns]
df_out = df[output_cols]

os.makedirs(os.path.dirname(OUTPUT_PATH) if os.path.dirname(OUTPUT_PATH) else ".", exist_ok=True)
df_out.to_csv(OUTPUT_PATH, index=False)
print(f"✅ Temizlenmiş veri kaydedildi: {OUTPUT_PATH}")
print(f"   Son veri: {df_out.shape[0]} satır, {df_out.shape[1]} sütun")