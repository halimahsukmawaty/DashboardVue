# Mini Dashboard Perpustakaan Full-Stack (Vue 3 + FastAPI)

> **Ujian Tengah Semester (UTS) — Take-Home Individu**  
> **Mata Kuliah:** Pengembangan Aplikasi Web  
> **Soal:** Soal A — Dashboard Perpustakaan (NIM / Nomor Urut Ganjil)  
> **Entitas:** Buku (`id`, `judul`, `penulis`, `kategori`, `stok`)

---

## 📌 1. Deskripsi Proyek

Aplikasi **Mini Dashboard Perpustakaan** adalah aplikasi web full-stack modern yang dibangun untuk mengelola data koleksi buku perpustakaan secara interaktif. Proyek ini mengintegrasikan:
- **Backend (FastAPI)**: REST API dengan validasi skema Pydantic, penyimpanan *in-memory* yang di-seed dari file JSON, konfigurasi CORS, dan dokumentasi interaktif OpenAPI (Swagger).
- **Frontend (Vue 3 Composition API)**: Antarmuka reaktif menggunakan `<script setup>`, state management berbasis `ref`, *chained computed properties* untuk pencarian dan pengurutan, 4 tile statistik dinamis, penanganan status HTTP visual, modal CRUD, serta visualisasi distribusi kategori berbasis CSS murni.

---

## 🚀 2. Cara Menjalankan Aplikasi

Pastikan Anda telah menginstal **Python 3.10+** dan **Node.js 18+ (disarankan Node 20+)** pada perangkat Anda.

### A. Menjalankan Backend (FastAPI)

1. Buka terminal baru dan masuk ke direktori `backend/`:
   ```bash
   cd backend
   ```

2. Buat virtual environment Python (jika belum ada) dan aktifkan:
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instal dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan server FastAPI dengan Uvicorn:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. Backend aktif di:
   - **API Base URL:** `http://localhost:8000`
   - **Dokumentasi Interaktif (Swagger UI):** `http://localhost:8000/docs`
   - **Dokumentasi Alternatif (ReDoc):** `http://localhost:8000/redoc`

---

### B. Menjalankan Frontend (Vue 3 + Vite)

1. Buka terminal baru di folder utama frontend (`dashboard-vue/`):
   ```bash
   npm install
   ```

2. Jalankan server pengembangan Vite:
   ```bash
   npm run dev
   ```

3. Buka peramban (browser) dan akses:
   - **Frontend App:** `http://localhost:5173`

---

## 📊 3. Penjelasan Ambang Batas (Threshold) Status Stok

Sesuai ketentuan Soal A poin 3, ambang batas status stok ditentukan secara masuk akal untuk mencerminkan ketersediaan fisik buku di perpustakaan:

| Status Stok | Ambang Batas (*Stock Range*) | Tampilan Badge & Warna | Penjelasan Fungsional |
| :--- | :--- | :--- | :--- |
| **Stok Habis** | `stok === 0` | 🔴 **Merah** (`badge-habis`) | Semua eksemplar sedang dipinjam atau belum tersedia di rak. Mahasiswa/pengunjung tidak dapat meminjam saat ini. |
| **Menipis** | `1 <= stok <= 5` | 🟡 **Kuning/Oranye** (`badge-menipis`) | Jumlah eksemplar sangat terbatas (1 hingga 5 buku). Memerlukan perhatian petugas untuk pengadaan tambahan atau pembatasan peminjaman singkat. |
| **Tersedia** | `stok > 5` | 🟢 **Hijau** (`badge-tersedia`) | Eksemplar buku melimpah (lebih dari 5 buku) dan aman untuk dipinjam oleh banyak mahasiswa. |

Badge status stok diimplementasikan menggunakan **conditional class binding** di Vue 3:
```vue
<span class="badge" :class="statusInfo.cssClass">
  <span class="dot" :class="statusInfo.dotClass"></span>
  {{ statusInfo.label }}
</span>
```

---

## 📈 4. Penjelasan 4 Tile Statistik Ringkasan (Computed Murni)

Di bagian atas dashboard, terdapat 4 tile ringkasan yang dihitung murni menggunakan `computed` dari data buku yang diambil dari backend, menggunakan method array native ES6:

1. **Total Buku**  
   - Mengambil panjang array data buku:
     ```javascript
     const statTotalBuku = computed(() => books.value.length);
     ```
2. **Stok Menipis + Habis**  
   - Menghitung jumlah judul buku dengan status kritis (`stok <= 5`) menggunakan `.filter()`:
     ```javascript
     const statStokKritis = computed(() => {
       return books.value.filter((buku) => buku.stok <= 5).length;
     });
     ```
3. **Jumlah Kategori**  
   - Menghitung kategori genre unik menggunakan `.map()` dan native `Set`:
     ```javascript
     const statTotalKategori = computed(() => {
       const kategoriList = books.value.map((buku) => buku.kategori);
       return new Set(kategoriList).size;
     });
     ```
4. **Total Eksemplar**  
   - Menjumlahkan seluruh angka stok fisik buku menggunakan `.reduce()`:
     ```javascript
     const statTotalEksemplar = computed(() => {
       return books.value.reduce((total, buku) => total + (Number(buku.stok) || 0), 0);
     });
     ```

---

## 🔍 5. Filter Pencarian & Pengurutan Berantai (Chained Computed)

1. **Pencarian / Filter Tahap 1 (`filteredBooks`)**:  
   Menyaring buku berdasarkan kata kunci pada `judul` atau `penulis` (case-insensitive) dan opsi kategori:
   ```javascript
   const filteredBooks = computed(() => {
     const query = searchQuery.value.toLowerCase().trim();
     const kat = selectedCategory.value;
     return books.value.filter((buku) => {
       const matchQuery =
         !query ||
         (buku.judul && buku.judul.toLowerCase().includes(query)) ||
         (buku.penulis && buku.penulis.toLowerCase().includes(query));
       const matchCategory = kat === "semua" || buku.kategori === kat;
       return matchQuery && matchCategory;
     });
   });
   ```

2. **Pengurutan Berantai Tahap 2 (`sortedBooks`)**:  
   Mengurutkan salinan hasil `filteredBooks` berdasarkan judul buku (A-Z / Z-A) menggunakan `.sort()` dan `.localeCompare()`:
   ```javascript
   const sortedBooks = computed(() => {
     return [...filteredBooks.value].sort((a, b) => {
       if (sortOrder.value === "asc") {
         return a.judul.localeCompare(b.judul, "id");
       } else {
         return b.judul.localeCompare(a.judul, "id");
       }
     });
   });
   ```

---

## 🛠️ 6. Endpoint REST API (FastAPI)

Semua endpoint didefinisikan menggunakan validasi **Pydantic** (`BookBase`, `BookCreate`, `BookUpdate`, `BookOut`) dengan penanganan status HTTP yang tepat:

| Method | Endpoint | Status Code | Deskripsi |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | 200 OK | Health-check backend & total koleksi buku |
| `GET` | `/books` | 200 OK | Mengambil seluruh daftar buku (opsional filter query `q` & `kategori`) |
| `GET` | `/books/{id}` | 200 OK / 404 | Mengambil detail 1 buku berdasarkan ID |
| `POST` | `/books` | 201 Created / 422 | Menambahkan buku baru dengan validasi Pydantic |
| `PUT` | `/books/{id}` | 200 OK / 404 | *(Bonus)* Memperbarui data judul, penulis, kategori, atau stok |
| `DELETE` | `/books/{id}` | 200 OK / 404 | Menghapus buku dari koleksi |
| `POST` | `/books/reset` | 200 OK | Reset in-memory storage kembali ke 25 data seed awal |

---

## 🌟 7. Fitur Bonus (Nilai Tambah)

1. **Fitur Edit Buku (PUT /books/{id})**:
   - Terdapat tombol **Edit** pada setiap baris/kartu buku yang membuka modal interaktif pre-filled dengan data buku yang dipilih.
   - Perubahan langsung dikirim ke backend via `PUT` dan tampilan di-refresh secara otomatis.
2. **Dokumentasi OpenAPI yang Rapi (`/docs`)**:
   - Dokumentasi Swagger UI dilengkapi deskripsi modul, rincian tiap parameter, skema request/response, dan contoh data (*examples*).
3. **Visualisasi "Ringkasan Stok per Kategori" (CSS Bar)**:
   - Komponen `CategoryStockBars.vue` menghitung distribusi stok per kategori secara murni menggunakan native array method (`.reduce()`, `.map()`, `.sort()`).
   - Lebar bar ditampilkan dengan persentase CSS dinamis tanpa menggunakan library chart pihak ketiga apa pun.
4. **Fitur Reset Seed**:
   - Tombol **Reset Seed** di navbar atas memudahkan penguji/dosen untuk mengembalikan data awal kapan pun saat sesi pengujian.

---

## 📱 8. Desain Responsif (Breakpoints)

Aplikasi telah dioptimalkan secara fungsional di seluruh ukuran layar menggunakan CSS Flexbox, Grid, dan media query:
- **Desktop (≥ 1024px):** 4 tile statistik horizontal, toolbar lengkap, tabel buku komprehensif.
- **Tablet (768px – 1023px):** 2x2 grid tile statistik, tabel dapat digeser horizontal atau membungkus rapi.
- **Mobile (< 768px & 375px):** 1 atau 2 kolom tile statistik, tabel otomatis bertransformasi menjadi **kartu buku modern (`BookCard.vue`)** yang ramah sentuhan, tanpa scroll horizontal yang tidak disengaja.

---

## 📚 9. Data Awal (Seed Data)

Data awal disimpan di file `backend/books.json` berisi **25 buku** buatan sendiri yang mencakup beragam kategori (Teknologi, Sastra, Fiksi, Sains, Bisnis, Sejarah, Filsafat, Pendidikan, Pengembangan Diri) dengan variasi stok yang representatif (tersedia, menipis, dan stok habis).
