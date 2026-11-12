# Aplikasi Ekstraksi Fitur Warna dan Segmentasi Citra Digital Menggunakan Metode HSV

Aplikasi web interaktif untuk praktikum **Pengolahan Citra Digital (Digital Image Processing)** yang berfokus pada ekstraksi fitur warna (RGB & HSV) serta segmentasi citra digital berbasis ruang warna HSV (*Hue, Saturation, Value*) menggunakan Python, OpenCV, dan Flask.

Aplikasi ini mengacu pada konsep dan metodologi materi:
[Pemrograman MATLAB - Pengenalan Pola Citra Digital: Pola Warna](https://pemrogramanmatlab.com/pengenalan-pola-citra-digital-menggunakan-matlab/pola-warna/) yang diimplementasikan secara nyata dan mandiri menggunakan Python dan OpenCV.

---

## 1. Tujuan Aplikasi

1. Mengimplementasikan konversi ruang warna dari RGB (Red, Green, Blue) ke HSV (Hue, Saturation, Value) pada citra digital.
2. Memvisualisasikan komponen kanal Hue, Saturation, dan Value dalam citra terpisah.
3. Melakukan ekstraksi fitur statistik warna secara nyata (nilai rata-rata Red, Green, Blue, Hue, Saturation, dan Value) menggunakan komputasi matriks NumPy.
4. Melakukan segmentasi citra digital untuk 9 kelompok warna (Merah, Jingga, Kuning, Hijau, Cyan, Biru, Ungu, Magenta, Merah Muda) menggunakan fungsi thresholding biner `cv2.inRange()` dan operasi logika `cv2.bitwise_and()`.
5. Menyediakan kontrol rentang threshold HSV manual interaktif (Hue Min/Max, Saturation Min/Max, Value Min/Max) secara *real-time*.
6. Menyajikan laporan kuantitatif analisis piksel berupa jumlah piksel terdeteksi dan persentase ketercakupan warna pada citra.
7. Menyediakan fitur pengunduhan citra hasil segmentasi dan mask biner berformat PNG.

---

## 2. Dasar Teori

### A. Keterbatasan Ruang Warna RGB
Ruang warna RGB (*Red, Green, Blue*) merepresentasikan warna melalui kombinasi intensitas cahaya ketiga warna primer aditif. Kelemahan mendasar ruang warna RGB dalam segmentasi citra adalah tingginya korelasi antara komponen warna (kromatisitas) dengan intensitas pencahayaan (luminansi). Perubahan intensitas cahaya atau bayangan pada suatu objek akan mengubah nilai R, G, dan B secara serempak, sehingga penentuan batas ambang (*thresholding*) menjadi tidak stabil.

### B. Ruang Warna HSV (*Hue, Saturation, Value*)
Ruang warna HSV memisahkan informasi warna murni dari tingkat kecerahan:
- **Hue (H):** Menyatakan corak warna murni berdasarkan panjang gelombang cahaya dalam spektrum lingkaran warna (0°–360°). Pada OpenCV, karena tipe data piksel citra 8-bit memiliki rentang 0–255, nilai derajat sudut Hue dibagi 2 sehingga bernilai **0–179**.
- **Saturation (S):** Menyatakan tingkat kejenuhan atau kemurnian warna dengan rentang **0–255**. Nilai 0 menunjukkan warna abu-abu (tidak ada warna murni), sedangkan 255 menunjukkan warna murni pekat.
- **Value (V):** Menyatakan intensitas kecerahan (*brightness*) cahaya dengan rentang **0–255**. Nilai 0 menunjukkan hitam pekat, sedangkan 255 menunjukkan kecerahan tertinggi.

### C. Karakteristik Khusus Warna Merah (Hue Wrap-around)
Pada roda warna 360 derajat, warna merah berada di sekitar sudut 0° sekaligus 360°. Dalam skala OpenCV (0–179), corak merah berada pada rentang **0–10** dan **170–179**. Oleh karena itu, segmentasi warna merah membutuhkan dua operasi thresholding biner yang kemudian digabungkan dengan operasi logika OR bitwise (`cv2.bitwise_or`).

### D. Tahapan Segmentasi Citra
1. **Pembacaan Citra:** OpenCV membaca berkas citra dalam urutan kanal BGR (*Blue, Green, Red*).
2. **Konversi Ruang Warna:** Citra BGR dikonversi ke HSV menggunakan `cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)`.
3. **Thresholding Biner (`cv2.inRange`):**
   $$\text{Mask}(x,y) = \begin{cases} 255, & \text{jika } \text{Lower} \le \text{HSV}(x,y) \le \text{Upper} \\ 0, & \text{lainnya} \end{cases}$$
4. **Ekstraksi Objek (`cv2.bitwise_and`):**
   $$\text{Citra Hasil}(x,y) = \text{Citra Asli}(x,y) \text{ AND } \text{Mask}(x,y)$$
5. **Kalkulasi Kuantitatif:**
   $$\text{Persentase Deteksi} = \left( \frac{\sum \text{Piksel Mask} > 0}{\text{Total Piksel Citra}} \right) \times 100\%$$

---

## 3. Spesifikasi Rentang 9 Kelompok Warna (OpenCV HSV)

| Kelompok Warna | Rentang Hue (H) | Rentang Saturation (S) | Rentang Value (V) | Keterangan Spektrum |
| :--- | :---: | :---: | :---: | :--- |
| **Merah** | [0–10] & [170–179] | 70–255 | 50–255 | Spektrum melingkar di awal & akhir roda warna |
| **Jingga (Orange)** | 11–25 | 70–255 | 50–255 | Corak peralihan merah ke kuning (~20°–50°) |
| **Kuning** | 26–35 | 70–255 | 50–255 | Corak kuning (~50°–70°) |
| **Hijau** | 36–85 | 50–255 | 50–255 | Spektrum hijau lebar (~70°–170°) |
| **Cyan** | 86–100 | 50–255 | 50–255 | Peralihan hijau ke biru (~170°–200°) |
| **Biru** | 101–130 | 50–255 | 50–255 | Spektrum biru primer (~200°–260°) |
| **Ungu** | 131–145 | 50–255 | 50–255 | Peralihan biru ke magenta (~260°–290°) |
| **Magenta** | 146–160 | 50–255 | 50–255 | Campuran jenuh merah-biru (~290°–320°) |
| **Merah Muda (Pink)** | 161–172 | 30–255 | 100–255 | Dekat merah dengan saturasi pastel/sedang |

---

## 4. Teknologi yang Digunakan

- **Bahasa Pemrograman:** Python 3.10+ (Diuji pada Python 3.15 di Windows 11)
- **Web Framework:** Flask 3.1.3
- **Computer Vision:** OpenCV (opencv-python 5.0.0.93)
- **Komputasi Matriks & Numerik:** NumPy 2.5.4
- **Manipulasi Citra & Format:** Pillow 13.0.0
- **Frontend:** HTML5 Semantik, CSS3 Modern (Konsep White Minimalist dengan aksen biru dan burgundi), Vanilla JavaScript (Async/Await Fetch API)

---

## 5. Struktur Folder Proyek

```text
color_segmentation/
├── app.py                      # Server Flask & routing API
├── image_processor.py          # Modul algoritma OpenCV, ekstraksi fitur & segmentasi
├── requirements.txt            # Daftar pustaka dependensi teruji
├── README.md                   # Dokumentasi lengkap teori dan cara pakai
├── .gitignore                  # Berkas pengabaian Git
├── uploads/                    # Direktori penyimpanan citra yang diunggah
├── static/
│   ├── css/
│   │   └── style.css           # Desain White Minimalist, tipografi & layout responsif
│   ├── js/
│   │   └── script.js           # Logika interaksi frontend, slider debounce & AJAX
│   ├── samples/                # Citra contoh siap uji praktikum
│   └── results/                # Direktori luaran mask biner dan citra tersegmentasi
└── templates/
    └── index.html              # Antarmuka web utama

## 6. Panduan Penggunaan Aplikasi

1. **Memuat Citra:**
   - Unggah berkas gambar pribadi (JPG, JPEG, atau PNG) melalui area *drag-and-drop* atau klik tombol **"Pilih File dari Komputer"**.
   - Atau langsung klik salah satu tombol citra sampel praktikum: **"Palet 9 Warna Lengkap"** atau **"Komposisi Bentuk Geometri"**.
2. **Melihat Hasil Ekstraksi Fitur:**
   - Pada bagian **Dashboard Utama**, periksa nama berkas, dimensi piksel, dan total jumlah piksel.
   - Pada bagian **Ekstraksi Fitur Warna**, amati rata-rata nilai Red, Green, Blue serta Hue, Saturation, dan Value yang dihitung secara nyata dari matriks citra.
3. **Melihat Komponen HSV:**
   - Pada bagian **Visualisasi Komponen Ruang Warna HSV**, amati representasi citra kanal Hue, Saturation, dan Value dalam skala grayscale.
4. **Melakukan Segmentasi Warna:**
   - Pada bagian **Segmentasi Warna Berbasis HSV**, klik salah satu dari 9 tombol kelompok warna (Merah s.d. Merah Muda).
   - Citra akan langsung diproses tanpa perlu memuat ulang halaman.
5. **Pengaturan Threshold Slider Manual:**
   - Geser slider Hue Min/Max, Saturation Min/Max, atau Value Min/Max untuk mencari batas warna yang presisi.
   - Jika slider digeser, sistem secara otomatis beralih ke mode kustom dengan debouncing cepat.
   - Klik tombol **"Reset Threshold"** untuk mengembalikan slider ke nilai bawaan warna terpilih.
6. **Melihat Visualisasi & Analisis Kuantitatif:**
   - Amati 4 kuadran tampilan: (1) Citra Asli, (2) Komponen Hue Citra, (3) Mask Segmentasi Hitam Putih, (4) Hasil Segmentasi Warna.
   - Lihat rincian total piksel, jumlah piksel terdeteksi, dan persentase ketercakupan warna pada meter bar.
7. **Mengunduh Hasil:**
   - Klik tombol **"Unduh Hasil Segmentasi (PNG)"** untuk menyimpan gambar hasil isolasi warna.
   - Klik tombol **"Unduh Mask Biner (PNG)"** untuk menyimpan gambar mask hitam-putih.

---

## 7. Menjalankan Pengujian Otomatis

Aplikasi telah dilengkapi dengan berkas pengujian otomatis untuk memverifikasi 20 skenario fungsional:
```powershell
python run_comprehensive_tests.py
```
Hasil pengujian akan menampilkan status `[BERHASIL (PASS)]` untuk seluruh 20 aspek pengujian.
