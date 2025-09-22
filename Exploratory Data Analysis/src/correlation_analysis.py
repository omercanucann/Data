import statistical_analysis
import config
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def correlacion_analysis(self):
    print("\n" + "="*50)
    print("Kolerasyon Analizi")
    print("="*50)

    if len(self.numerical_cols) < 2:
        print("Kolerasyon analizi için en az iki sayısal sütun gerekli!")
        return
    
    numeric_data = self.df[self.numerical_cols].select_dtypes(include=[np.number])
    self.correlation_matrix = numeric_data.corr()

    print("Kolerasyon Matrisi:")
    print(self.correlation.matrix.round(5))

    self.find_extreme_correlations()
    self.create_correlation_heatmap()
    self.results["correlation_matrix"] = self.correlation_matrix

def find_extreme_correlations(self):
    corr_values= []
    for i in range(len(self.correlation_matrix_columns)):
        for j in range(i+1, len(self.correlation_matrix.columns)):
            var1 = self.correlation_matrix.columns[i]
            var2 = self.correlation_matrix_columns[j]
            corr_val = self.correlation_matrix.iloc[i, j]
            if not pd.isna(corr_val):
                corr_values.append((var1, var2, corr_val))
    
    if corr_values:
        corr_values.sort(key=lambda x : abs(x[2]), reverse=True)
        print("\n En Yüksek Korelasyonlar:")
        for i, (var1, var2, corr) in enumerate(corr_values[:5]):
            if corr > 0:
                print(f"{i+1}. {var1} ↔ {var2}: {corr:.3f} (Pozitif)")
            else:
                print(f"{i+1}. {var1} ↔ {var2}: {corr:.3f} (Negatif)")
            
def create_correlation_heatmap(self):
    plt.figure(figsize=(10,8))
    mask = np.triu(np.ones_like(self.correlation_matrix, dtype=bool))

    sns.heatmap(self.correlation_matrix,
                mask=mask,
                annot=True,
                cmap="RdYlBu_r",
                center=0,
                square=True,
                fmt=".2f",
                cbar_kws={"shrink": .8})
    plt.title("Netflix Veri Seti - Kolerasyon Matrisi", fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig("data/correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("Kolerasyon heatmap'i correalation_heatmap olarak kaydedildi.")