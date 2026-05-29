# NutriBalance

Sistem Rekomendasi Diet Berdasarkan Komposisi Makromolekul.

NutriBalance adalah aplikasi CLI berbasis Python untuk menghitung kebutuhan
kalori, menentukan target makromolekul harian, lalu memberi rekomendasi menu
berdasarkan komposisi karbohidrat, protein, dan lemak.

## Fitur

- Input data personal: umur, berat badan, tinggi badan, jenis kelamin.
- Pilihan tujuan diet: weight loss, maintain weight, dan muscle gain.
- Pilihan aktivitas harian: rendah, sedang, dan tinggi.
- Perhitungan BMR memakai rumus Mifflin-St Jeor.
- Perhitungan target makromolekul berdasarkan rasio diet.
- Rekomendasi makanan dari dataset CSV.
- Visualisasi CLI berupa diagram batang ASCII.
- Grafik PNG opsional jika `matplotlib` tersedia.
- Monitoring sederhana untuk mencatat makanan yang sudah dimakan.

## Struktur Repositori

```text
NutriBalance/
+-- data/
|   +-- makanan.csv
+-- src/
|   +-- nutribalance/
|       +-- __init__.py
|       +-- __main__.py
|       +-- cli.py
|       +-- nutrition_calculator.py
|       +-- recommendation.py
|       +-- visualization.py
+-- main.py
+-- pyproject.toml
+-- README.md
+-- LICENSE
```

Keterangan file:

- `data/makanan.csv`: dataset makanan dan kandungan makromolekul.
- `src/nutribalance/cli.py`: alur utama input-output CLI.
- `src/nutribalance/nutrition_calculator.py`: perhitungan BMR, kalori, dan target makro.
- `src/nutribalance/recommendation.py`: algoritma rekomendasi menu.
- `src/nutribalance/visualization.py`: visualisasi ASCII dan grafik PNG opsional.
- `main.py`: launcher agar program mudah dijalankan dari root repo.
- `pyproject.toml`: metadata package Python dan konfigurasi install.

## Pembagian Tugas Tim



| Nama | NIM | Pembagian | 
| --- | --- | --- | 
| Aryo Bama Wiratama | 13523088 | Perhitungan nutrisi dan visualisasi hasil |
| Muhammad Edo Raduputu Aprima | 13523096 | Dataset makanan dan algoritma rekomendasi | 
| Fityatul Haq Rosyidi | 13523116 | Integrasi CLI, struktur package, dan dokumentasi | `src/nutribalance/cli.py`, `main.py`, `src/nutribalance/__main__.py`, `src/nutribalance/__init__.py`, `pyproject.toml`, `.gitignore`, `README.md` | Menghubungkan semua modul ke antarmuka CLI, membuat alur input-output, menampilkan hasil program, menyediakan launcher, menyiapkan konfigurasi package, dan menulis dokumentasi penggunaan. |

## Requirement

Pastikan Python 3.10 atau lebih baru sudah terpasang.

Program inti tidak membutuhkan library tambahan. Untuk membuat grafik PNG,
install dependency opsional `matplotlib`.

## How to Use

Jalankan dari root repositori:

```bash
python main.py
```

Program akan meminta input secara interaktif:

```text
Umur (tahun): 21
Berat badan (kg): 65
Tinggi badan (cm): 170
Jenis kelamin [1/2]: 1
Tujuan [1/2/3]: 2
Aktivitas [1/2/3]: 2
Apakah ingin mencatat makanan yang sudah dimakan? [y/n]: n
```

Pilihan jenis kelamin:

```text
1. Laki-laki
2. Perempuan
```

Pilihan tujuan diet:

```text
1. Weight loss (diet)
2. Maintain weight
3. Muscle gain (bulking)
```

Pilihan aktivitas harian:

```text
1. Rendah
2. Sedang
3. Tinggi
```

Validasi input:

- Umur harus 1 sampai 120 tahun.
- Berat badan harus 20 sampai 300 kg.
- Tinggi badan harus 80 sampai 250 cm.
- Jenis kelamin hanya menerima pilihan `1` atau `2`.
- Tujuan diet dan aktivitas hanya menerima nomor pilihan yang tersedia.

## Cara Menjalankan Tanpa Grafik PNG

Gunakan opsi ini jika hanya ingin output terminal atau belum memasang
`matplotlib`:

```bash
python main.py --no-png
```

Output tetap menampilkan visualisasi ASCII di terminal.

## Cara Menjalankan Dengan Grafik PNG

Install dependency opsional:

```bash
python -m pip install -e ".[charts]"
```

Lalu jalankan:

```bash
python main.py
```

Jika `matplotlib` tersedia, program akan menyimpan:

```text
output/pie_makromolekul.png
output/target_vs_aktual.png
```

Folder `output/` diabaikan oleh Git karena berisi file hasil generate.

## Cara Install Sebagai Package

Jika ingin menjalankan program sebagai command:

```bash
python -m pip install -e .
nutribalance
```

Alternatif setelah package ter-install:

```bash
python -m nutribalance
```

Untuk install sekaligus dukungan grafik PNG:

```bash
python -m pip install -e ".[charts]"
```

## Cara Memakai Dataset CSV Lain

Gunakan opsi `--csv`:

```bash
python main.py --csv path/ke/makanan.csv
```

Format CSV harus memiliki kolom berikut:

```csv
name,category,carbs_g,protein_g,fat_g,calories_kcal
Nasi putih,karbohidrat,40,4,1,180
Dada ayam,protein,0,31,4,165
Alpukat,lemak,12,2,15,180
```

Satuan yang dipakai:

- `carbs_g`: gram karbohidrat per porsi.
- `protein_g`: gram protein per porsi.
- `fat_g`: gram lemak per porsi.
- `calories_kcal`: kalori per porsi dalam kcal.

## Output Program

Program menampilkan:

- BMR pengguna.
- Kebutuhan kalori pemeliharaan.
- Target kalori sesuai tujuan diet.
- Target gram karbohidrat, protein, dan lemak.
- Daftar makanan prioritas sesuai tujuan.
- Menu rekomendasi harian.
- Total nutrisi menu rekomendasi.
- Visualisasi target vs aktual di terminal.
- Monitoring asupan jika pengguna memilih mencatat makanan.

## Ringkasan Algoritma

1. Program menerima data pengguna.
2. BMR dihitung dengan rumus Mifflin-St Jeor.
3. BMR dikalikan faktor aktivitas untuk mendapat kalori pemeliharaan.
4. Kalori disesuaikan dengan tujuan diet.
5. Target gram makro dihitung dari rasio:
   - Weight loss: 40% karbohidrat, 35% protein, 25% lemak.
   - Maintain weight: 45% karbohidrat, 25% protein, 30% lemak.
   - Muscle gain: 50% karbohidrat, 30% protein, 20% lemak.
6. Sistem memilih makanan dengan greedy search agar total menu mendekati target
   kalori dan makromolekul.

## Konsep Biologi

Karbohidrat berperan sebagai sumber energi utama, protein mendukung pembentukan
dan perbaikan jaringan tubuh, sedangkan lipid atau lemak berperan sebagai
cadangan energi, komponen membran sel, dan bahan pembentukan hormon.
