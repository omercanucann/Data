import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import config

plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class NetflixEda:
    def __init__(self, data_path =config.DATA_PATH):
        self.data_path = data_path
        self.df = None
        self.numerical_cols = []
        self.categorical_cols = []
        self.result = {}
        self.create_directories()

    def create_directories(self):
        directories = ["outputs", "outputs/figures", "outputs/tables"]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def load_csv(self):
        print("Veri Yükleniyor...")

        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Veri Başarıyla Yüklendi: {self.df.shape[0]} satır {self.df.shape[1]} sütun")
            self.identify_column_types()
            self.print_basic_info()
        except FileNotFoundError:
            print(f"Hata, {self.data_path} dosyası bulunamadı")
            return False
        except Exception as e:
            print(f"Veri yükleme hatası: {str(e)}")
            return False
        return True
    
    def identify_column_types(self):
        for col in self.df.columns:
            if self.df[col].dtype in ['int64', 'float64']:
                self.numerical_cols.append(col)
            else:
                if col == "release_year" or col == "duration":
                    if col == "duration":
                        self.df[col + '_numeric'] = self.df[col].str.extract('(\d+)').astype(float)
                        self.numerical_cols.append(col + '_numeric')
                    else:
                        try:
                            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")
                            self.numerical_cols.append(col)
                        except:
                            self.categorical_cols.append(col)
                else:
                    self.categorical_cols.append(col)
    
    def print_basic_info(self):
        print("\n" + "="*50)
        print("Veri Seti hakkında temel bilgiler")
        print("="*50)

        print(f"Toplam Satır sayısı: {len(self.df)}")
        print(f"Toplam sütun sayısı: {len(self.df.columns)}")
        print(f"Sayısal sütun sayısı: {len(self.numerical_cols)}")
        print(f"Kategorik sütun sayısı: {len(self.categorical_cols)}")

        print("\n İlk 5 satır:")
        print(self.df.head())

        print("Veri türleri ve eksik değerler: ")
        info_df = pd.DataFrame({
            "Veri Türü": self.df.dtypes,
            "Eksik Veri": self.df.isnull().sum(),
            "Eksik Oran (%)": (self.df.isnull().sum() / len(self.df) * 100).round(2)
        })
        print(info_df)

    def calculate_basic_statistics(self):
        print("\n" + "="*50)
        print("Temel İstatistiksel Hesaplamalar")
        print("="*50)

        if not self.numerical_cols:
            print("Sayısal sütun bulunamadı!")
            return
        stats_data = []

        for col in self.numerical_cols:
            if col in self.df.columns:
                data = self.df[col].dropna()
                
                if len(data) > 0:
                    stats = {
                        "Değişken": col,
                        "Ortalama": round(data.mean(), 2),
                        "Median": round(data.median(), 2),
                        "Varyans": round(data.var(), 2),
                        "Standart Sapma": round(data.std(), 2),
                        "Minimum": round(data.min(), 2),
                        "Maksimum": round(data.max(), 2),
                        "Veri Sayısı": len(data)
                    }
                    stats_data.append(stats)

        self.stats_df = pd.DataFrame(stats_data)
        print(self.stats_df.to_string(index=False))

        self.stats_df.to_csv("data/basic_statistics.csv", index=False)
        print("\n İstatistik Tablosu data klasörünün içine basic_statistics ismi ile kaydedildi")
        self.result['basic_stats'] = self.stats_df

    def run_complete_analysis(self):
        print("Netflix EDA Analizi Başlatılıyor...")
        if self.load_csv():
            self.calculate_basic_statistics()
            print("\n Analiz tamamlandı! Şimdi report.pdf oluşturabilirsiniz.")

