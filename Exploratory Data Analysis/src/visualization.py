import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import config
from statistical_analysis import NetflixEda
print("\n" + "="*50)
print("Veri Görselleştirmeleri")
print("="*50)

def create_visualizations(self):
    """Veri görselleştirmelerini oluştur"""
    print("\n" + "="*50)
    print("📊 VERİ GÖRSELLEŞTİRMELERİ")
    print("="*50)
    
    self.create_histograms()
    self.create_boxplots()
    self.create_scatterplots()
    self.create_netflix_specific_plots()

def create_histograms(self):
    if not self.numerical_cols:
        return
    
    n_cols = min(3, len(self.numerical_cols))
    n_rows = (len(self.numerical_cols) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_rows == 1:
        axes = [axes] if n_cols == 1 else axes
    else:
        axes = axes.flatten()

    for i, col in enumerate(self.numerical_cols):
        if col in self.df.columns:
            data = self.df[col].dropna()
        if len(data) > 0:
            axes[i].hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            axes[i].set_title(f'{col} Dağılımı', fontsize=12)
            axes[i].set_xlabel(col)
            axes[i].set_ylabel("Frekans")
            axes[i].grid(True, alpha=0.3)

    for j in range(len(self.numerical_cols), len(axes)):
        axes[j].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("data/histograms.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("Histogram grafikleri histograms.png olarak kaydedildi")

def create_boxplots(self):
    if not self.numerical_cols:
        return
    
    n_cols = min(3, len(self.numerical_cols))
    n_rows = (len(self.numerical_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_rows == 1:
        axes = [axes] if n_cols == 1 else axes
    else:
        axes = axes.flatten()
    for i, col in enumerate(self.numerical_cols):
        if col in self.df.columns:
            data = self.df[col].dropna()
            if len(data) > 0:
                axes[i].boxplot(data)
                axes[i].set_title(f'{col} Boxplot', fontsize=12)
                axes[i].set_ylabel(col)
                axes[i].grid(True, alpha=0.3)
    for j in range(len(self.numerical_cols), len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    plt.savefig("data/boxplots.png", dpi=300, bbox_inches='tight')
    plt.show()
    print("Boxplot grafikleri boxplots.png olarak kaydedildi.")

def create_scatterplots(self):
    if len(self.numerical_cols) < 2:
        return
    if hasattr(self, 'correlation_matrix'):
        plt.figure(figsize=(15,5))
        plot_count = 0
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i + 1, len(self.correlation_matrix.columns)):
                if plot_count >= 3:
                    break
                var1 = self.correlation_matrix.columns[i]
                var2 = self.correlation_matrix.columns[j]
                corr_val = self.correlation_matrix.iloc[i, j]

                if not pd.isna(corr_val) and abs(corr_val) > 0.1:
                    plt.subplot(1, 3, plot_count + 1)
                    x_data = self.df[var1].dropna()
                    y_data = self.df[var2].dropna()
                    common_idx = x_data.index.intersection(y_data.index)
                    plt.scatter(self.df.loc[common_idx, var1],
                                self.df.loc[common_idx, var2],
                                alpha=0.6, color='coral')
                    plt.xlabel(var1)
                    plt.ylabel(var2)
                    plt.title(f'{var1} vs {var2}\nKorelasyon: {corr_val:.3f}')
                    plt.grid(True, alpha=0.3)
                    plot_count += 1
            if plot_count >= 3:
                break
        plt.tight_layout()
        plt.savefig("data/scatterplots.png", dpi=300, bbox_inches = 'tight')
        plt.show()
        print("Scatterplot grafikleri scatterplots.png olarak kaydedildi")

def create_netflix_spesific_plots(self):
    if 'type' in self.df.columns:
        plt.figure(figsize=(12,4))
        plt.subplot(1,2,1)
        type_counts = self.df['type'].value_counts()
        plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        plt.title("Netflix İçerik Türü Dağılımı")

        plt.subplot(1,2,2)
        if 'release_year' in self.df.columns:
            year_counts = self.df['release_year'].value_counts().sort_index()
            plt.plot(year_counts.index, year_counts.values, marker='o', linewidth=2)
            plt.title("Yıllara Göre Netflix İçerik Sayısı")
            plt.xlabel("Yıl")
            plt.ylabel("İçerik Sayısı")
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("data/netflix_specific_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        print("Netflix özel analiz grafikleri netflix_specific_analysis.png olarak kaydedildi")

def generate_summary(self):
    print("\n" + '='*50)
    print("Analiz Özeti Ve Çıkarımlar")
    print("="*50)

    summary = []
    summary.append(f'Toplam {len(self.df)} Netflix içeriği analiz edildi.')
    summary.append(f"{len(self.numerical_cols)} Sayısal değişken inceledi")

    if hasattr(self, 'stats_df'):
        summary.append("Temel istatistikler hesaplandı ve kaydedildi.")
    if hasattr(self, 'correlation_matrix'):
        summary.append("Korelasyon analizi tamamlandı")

    summary.append("Histogram, boxplot ve scatterplot grafikleri oluşturuldu")
    summary.append("Netflix özel analizleri yapıldı.")
    
    for item in summary:
        print(item)
    print(f"\n Tüm Çıktılar data klasöründe saklandı")
    print("Rapor için bu sonuçları kullanabilirsiniz.")

def run_complete_analysis(self):
    print("Netflix EDA Analizi Başlatılıyor...")
    if not self.load_data():
        return
    self.calculate_basic_statistics()
    self.correlation_analysis()
    self.create_visualizations()
    self.generate_summary()
    print("\n Analiz tamamlandı! Şimdi report.pdf oluşturabilirsiniz.")
