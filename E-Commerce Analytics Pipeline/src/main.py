import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

scripts = [
    ("data_cleaning.py",          "Data Cleaning"),
    ("weekly_sales_analysis.py",  "Weekly Sales Analysis"),
]

for script, label in scripts:
    print("=" * 60)
    print(f"▶ {label}  ({script})")
    print("=" * 60)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ {script} hata ile sonlandı (return code: {result.returncode})")
        print("Sonraki scriptler çalıştırılmayacak.")
        sys.exit(result.returncode)
    print()

print("=" * 60)
print("✅ Tüm scriptler başarıyla tamamlandı.")
print("=" * 60)