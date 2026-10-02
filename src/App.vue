<script setup>
import { ref, computed, onMounted } from "vue";
import StatTile from "./components/StatTile.vue";
import BookBadge from "./components/BookBadge.vue";
import BookCard from "./components/BookCard.vue";
import BookModal from "./components/BookModal.vue";
import CategoryStockBars from "./components/CategoryStockBars.vue";

// Konfigurasi endpoint API backend FastAPI
const API_BASE_URL = "http://localhost:8000";

// ==========================================
// 1. STATE REAKTIF (Composition API ref)
// ==========================================
// Data buku dari backend disimpan sebagai ref (Spesifikasi 3.1)
const books = ref([]);
const keadaan = ref("idle"); // 'idle' | 'loading' | 'sukses' | 'kosong' | 'error'
const pesanError = ref("");

// State filter pencarian teks (judul / penulis)
const searchQuery = ref("");

// State filter kategori
const selectedCategory = ref("semua");

// State arah pengurutan ('asc' = A-Z, 'desc' = Z-A berdasarkan judul)
const sortOrder = ref("asc");

// State Modal Tambah & Edit Buku
const isModalOpen = ref(false);
const isEditMode = ref(false);
const bookToEdit = ref(null);
const isSubmitting = ref(false);

// State Feedback Toast
const toast = ref({
  show: false,
  message: "",
  type: "success", // 'success' | 'error' | 'info'
});

let toastTimeout = null;
function showToast(message, type = "success") {
  toast.value = { show: true, message, type };
  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.value.show = false;
  }, 3500);
}

// ==========================================
// 2. FETCH API ASINKRON (async/await + try/catch)
// ==========================================
async function fetchBooks() {
  keadaan.value = "loading";
  pesanError.value = "";
  try {
    const response = await fetch(`${API_BASE_URL}/books`);
    if (!response.ok) {
      throw new Error(`Gagal memuat data (HTTP ${response.status}: ${response.statusText})`);
    }
    const data = await response.json();
    books.value = data;
    if (data.length === 0) {
      keadaan.value = "kosong";
    } else {
      keadaan.value = "sukses";
    }
  } catch (err) {
    keadaan.value = "error";
    pesanError.value =
      err.message ||
      "Tidak dapat terhubung ke backend FastAPI. Pastikan server backend berjalan di port 8000.";
  }
}

// Ambil data saat komponen pertama kali dipasang
onMounted(() => {
  fetchBooks();
});

// ==========================================
// 3. COMPUTED TAHAP 1: PENCARIAN & FILTER
// ==========================================
// Menyaring berdasarkan judul atau penulis dan kategori menggunakan method array .filter()
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

// ==========================================
// 4. COMPUTED TAHAP 2: PENGURUTAN BERANTAI (Chained Computed)
// ==========================================
// Mengurutkan SALINAN hasil dari filteredBooks berdasarkan judul buku A-Z / Z-A
const sortedBooks = computed(() => {
  return [...filteredBooks.value].sort((a, b) => {
    if (sortOrder.value === "asc") {
      return a.judul.localeCompare(b.judul, "id");
    } else {
      return b.judul.localeCompare(a.judul, "id");
    }
  });
});

// ==========================================
// 5. 4 TILE RINGKASAN (Computed Murni via Array Methods)
// ==========================================
// 1. Total Buku (jumlah seluruh judul buku dalam daftar)
const statTotalBuku = computed(() => {
  return books.value.length;
});

// 2. Stok Menipis + Habis (jumlah buku dengan stok <= 5)
// Menggunakan .filter() native
const statStokKritis = computed(() => {
  return books.value.filter((buku) => buku.stok <= 5).length;
});

// 3. Jumlah Kategori Unik
// Menggunakan .map() dan Set native
const statTotalKategori = computed(() => {
  const kategoriList = books.value.map((buku) => buku.kategori);
  return new Set(kategoriList).size;
});

// 4. Total Eksemplar (seluruh angka stok dijumlahkan)
// Menggunakan .reduce() native
const statTotalEksemplar = computed(() => {
  return books.value.reduce((total, buku) => total + (Number(buku.stok) || 0), 0);
});

// Daftar kategori unik untuk opsi filter dropdown
const kategoriOptions = computed(() => {
  const list = books.value.map((b) => b.kategori);
  return Array.from(new Set(list)).sort((a, b) => a.localeCompare(b, "id"));
});

// ==========================================
// 6. OPERASI CRUD (Tambah, Edit, Hapus, Reset)
// ==========================================
// Buka modal untuk tambah baru
function bukaModalTambah() {
  isEditMode.value = false;
  bookToEdit.value = null;
  isModalOpen.value = true;
}

// Buka modal untuk edit buku (Fitur Bonus)
function bukaModalEdit(buku) {
  isEditMode.value = true;
  bookToEdit.value = { ...buku };
  isModalOpen.value = true;
}

// Tutup modal
function tutupModal() {
  isModalOpen.value = false;
  bookToEdit.value = null;
}

// Submit data dari modal (POST atau PUT)
async function handleSimpanBuku(formData) {
  isSubmitting.value = true;
  try {
    if (isEditMode.value && bookToEdit.value) {
      // FITUR BONUS: Update buku via PUT /books/{id}
      const res = await fetch(`${API_BASE_URL}/books/${bookToEdit.value.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Gagal memperbarui buku.");
      }

      showToast(`Buku "${formData.judul}" berhasil diperbarui!`, "success");
    } else {
      // TAMBAH BUKU: POST /books
      const res = await fetch(`${API_BASE_URL}/books`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Gagal menambahkan buku baru.");
      }

      showToast(`Buku "${formData.judul}" berhasil ditambahkan!`, "success");
    }

    tutupModal();
    // Me-refresh daftar secara asinkron (Spesifikasi 3.1)
    await fetchBooks();
  } catch (err) {
    showToast(err.message || "Terjadi kesalahan saat menyimpan data.", "error");
  } finally {
    isSubmitting.value = false;
  }
}

// Hapus buku via DELETE /books/{id} (Spesifikasi 3.1)
async function handleHapusBuku(id, judulBuku) {
  const konfirmasi = window.confirm(
    `Apakah Anda yakin ingin menghapus buku "${judulBuku}" (ID: ${id}) dari perpustakaan?`
  );
  if (!konfirmasi) return;

  try {
    const res = await fetch(`${API_BASE_URL}/books/${id}`, {
      method: "DELETE",
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || "Gagal menghapus buku dari server.");
    }

    showToast(`Buku "${judulBuku}" berhasil dihapus.`, "info");
    // Me-refresh daftar setelah penghapusan
    await fetchBooks();
  } catch (err) {
    showToast(err.message || "Terjadi kesalahan saat menghapus buku.", "error");
  }
}

// Reset database kembali ke seed awal 25 buku
async function handleResetDatabase() {
  const konfirmasi = window.confirm(
    "Kembalikan seluruh koleksi buku ke 25 data seed awal dari books.json?"
  );
  if (!konfirmasi) return;

  try {
    const res = await fetch(`${API_BASE_URL}/books/reset`, {
      method: "POST",
    });
    if (!res.ok) throw new Error("Gagal mereset data.");
    showToast("Koleksi buku berhasil direset ke 25 data awal!", "success");
    await fetchBooks();
  } catch (err) {
    showToast(err.message || "Gagal mereset database.", "error");
  }
}
</script>

<template>
  <div class="app-layout">
    <!-- Toast Feedback Notification -->
    <transition name="toast-fade">
      <div v-if="toast.show" class="toast-popup" :class="`toast-${toast.type}`">
        <span class="toast-icon">
          <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="t-icon"><polyline points="20 6 9 17 4 12"></polyline></svg>
          <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="t-icon"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="t-icon"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        </span>
        <span class="toast-text">{{ toast.message }}</span>
      </div>
    </transition>

    <!-- Top Navigation Header -->
    <header class="app-header">
      <div class="container header-container">
        <div class="brand-group">
          <div class="brand-logo">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="logo-icon">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path>
              <path d="M6 6h10"></path>
              <path d="M6 10h10"></path>
            </svg>
          </div>
          <div>
            <h1 class="app-title">Dashboard Perpustakaan</h1>
            <p class="app-subtitle">UTS Pemrograman Aplikasi Web • Vue 3 & FastAPI</p>
          </div>
        </div>

        <div class="header-actions">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-api-docs"
            title="Buka Dokumentasi Swagger /docs"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon-sm">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            OpenAPI Docs
          </a>

          <button
            class="btn-reset"
            title="Reset data ke 25 seed awal"
            @click="handleResetDatabase"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon-sm">
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
              <path d="M21 3v5h-5"></path>
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
              <path d="M8 16H3v5"></path>
            </svg>
            Reset Seed
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="app-main">
      <div class="container main-content-flow">
        <!-- 4 TILE RINGKASAN STATISTIK (Dihitung Murni dengan Computed dari data buku) -->
        <section class="stats-section">
          <StatTile
            title="Total Buku"
            :value="statTotalBuku"
            description="Judul buku terdaftar"
            type="primary"
            icon="book"
          />

          <StatTile
            title="Stok Menipis + Habis"
            :value="statStokKritis"
            description="Stok ≤ 5 eksemplar"
            type="danger"
            icon="alert"
          />

          <StatTile
            title="Jumlah Kategori"
            :value="statTotalKategori"
            description="Kategori genre unik"
            type="purple"
            icon="category"
          />

          <StatTile
            title="Total Eksemplar"
            :value="statTotalEksemplar"
            description="Seluruh stok fisik"
            type="emerald"
            icon="copies"
          />
        </section>

        <!-- TOOLBAR KONTROL: Pencarian, Filter Kategori, Pengurutan A-Z/Z-A, dan Tambah Buku -->
        <section class="toolbar-section">
          <div class="search-filter-group">
            <!-- Input Pencarian (Spesifikasi 3.1 & 4: judul atau penulis) -->
            <div class="search-box">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Cari judul atau penulis buku..."
                class="input-search"
              />
              <button
                v-if="searchQuery"
                class="btn-clear-search"
                title="Hapus pencarian"
                @click="searchQuery = ''"
              >
                ✕
              </button>
            </div>

            <!-- Filter Kategori -->
            <select v-model="selectedCategory" class="select-category">
              <option value="semua">Semua Kategori</option>
              <option
                v-for="kategori in kategoriOptions"
                :key="kategori"
                :value="kategori"
              >
                {{ kategori }}
              </option>
            </select>
          </div>

          <div class="sort-action-group">
            <!-- Tombol Pengurutan Chained Computed (Spesifikasi 3.1: Urutkan A-Z / Z-A) -->
            <div class="sort-toggle-group">
              <button
                class="btn-sort"
                :class="{ active: sortOrder === 'asc' }"
                title="Urutkan judul A ke Z"
                @click="sortOrder = 'asc'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sort-icon">
                  <path d="m3 8 4-4 4 4"></path>
                  <path d="M7 4v16"></path>
                  <path d="M15 4h5l-5 6h5"></path>
                  <path d="M15 20v-6h5v6"></path>
                </svg>
                A-Z
              </button>

              <button
                class="btn-sort"
                :class="{ active: sortOrder === 'desc' }"
                title="Urutkan judul Z ke A"
                @click="sortOrder = 'desc'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sort-icon">
                  <path d="m3 16 4 4 4-4"></path>
                  <path d="M7 20V4"></path>
                  <path d="M15 4h5l-5 6h5"></path>
                  <path d="M15 20v-6h5v6"></path>
                </svg>
                Z-A
              </button>
            </div>

            <!-- Tombol Tambah Buku Baru (Spesifikasi 3.1) -->
            <button class="btn-add-book" @click="bukaModalTambah">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon-sm">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Tambah Buku
            </button>
          </div>
        </section>

        <!-- Keterangan Ambang Batas & Urutan Aktif -->
        <div class="info-bar">
          <span class="info-left">
            Menampilkan <strong>{{ sortedBooks.length }}</strong> dari total <strong>{{ statTotalBuku }}</strong> buku
            <span v-if="searchQuery"> (disaring: "{{ searchQuery }}")</span>
            <span v-if="selectedCategory !== 'semua'"> [Kategori: {{ selectedCategory }}]</span>
            • Diurutkan: <strong>{{ sortOrder === 'asc' ? 'A ke Z' : 'Z ke A' }}</strong>
          </span>
          <span class="info-right">
            Ambang Batas Stok: <span class="badge-dot dot-g"></span> >5 Tersedia • <span class="badge-dot dot-y"></span> 1-5 Menipis • <span class="badge-dot dot-r"></span> 0 Habis
          </span>
        </div>

        <!-- ==========================================
             7. PENANGANAN STATUS (Spesifikasi 3.3)
             - loading
             - error
             - kosong
             - sukses
        ========================================== -->
        <!-- STATE LOADING -->
        <div v-if="keadaan === 'loading'" class="state-card loading-state">
          <div class="loading-spinner"></div>
          <h3 class="state-title">Memuat Koleksi Buku...</h3>
          <p class="state-desc">Menghubungkan ke API FastAPI (http://localhost:8000/books)</p>
        </div>

        <!-- STATE ERROR -->
        <div v-else-if="keadaan === 'error'" class="state-card error-state">
          <div class="error-icon-circle">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="e-icon">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <h3 class="state-title error-text">Gagal Menghubungi Backend</h3>
          <p class="state-desc">{{ pesanError }}</p>
          <div class="error-guidance">
            <span>Petunjuk: Jalankan perintah berikut di terminal backend:</span>
            <code>uvicorn main:app --reload</code>
          </div>
          <button class="btn-retry" @click="fetchBooks">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon-sm">
              <path d="M21 2v6h-6"></path>
              <path d="M3 12a9 9 0 0 1 15-6.7L21 8"></path>
              <path d="M3 22v-6h6"></path>
              <path d="M21 12a9 9 0 0 1-15 6.7L3 16"></path>
            </svg>
            Coba Lagi
          </button>
        </div>

        <!-- STATE KOSONG / SUKSES -->
        <div v-else-if="keadaan === 'sukses' || keadaan === 'kosong'">
          <!-- HASIL PENCARIAN KOSONG -->
          <div v-if="sortedBooks.length === 0" class="state-card empty-state">
            <div class="empty-icon-circle">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="empty-icon">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg>
            </div>
            <h3 class="state-title">Buku Tidak Ditemukan</h3>
            <p class="state-desc">
              Tidak ada buku yang cocok dengan kata kunci
              <span v-if="searchQuery">"<strong>{{ searchQuery }}</strong>"</span>
              <span v-if="selectedCategory !== 'semua'"> pada kategori "<strong>{{ selectedCategory }}</strong>"</span>.
            </p>
            <button
              v-if="searchQuery || selectedCategory !== 'semua'"
              class="btn-reset-filters"
              @click="searchQuery = ''; selectedCategory = 'semua'"
            >
              Reset Filter Pencarian
            </button>
          </div>

          <!-- DAFTAR BUKU: TABLE DI DESKTOP / TABLET, CARDS DI MOBILE -->
          <div v-else class="catalog-wrapper">
            <!-- Tampilan Tabel (Desktop >= 768px) -->
            <div class="table-container desktop-table-view">
              <table class="books-table">
                <thead>
                  <tr>
                    <th class="th-id">ID</th>
                    <th class="th-title">Judul Buku</th>
                    <th class="th-author">Penulis</th>
                    <th class="th-category">Kategori</th>
                    <th class="th-stock">Stok</th>
                    <th class="th-status">Status Stok</th>
                    <th class="th-actions">Aksi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="buku in sortedBooks"
                    :key="buku.id"
                    class="book-row"
                  >
                    <td class="td-id">#{{ buku.id }}</td>
                    <td class="td-title">
                      <div class="book-title-cell">
                        <span class="cell-title">{{ buku.judul }}</span>
                      </div>
                    </td>
                    <td class="td-author">{{ buku.penulis }}</td>
                    <td class="td-category">
                      <span class="category-badge">{{ buku.kategori }}</span>
                    </td>
                    <td class="td-stock">
                      <span class="stock-num" :class="{ 'zero-stock': buku.stok === 0 }">
                        {{ buku.stok }}
                      </span>
                    </td>
                    <td class="td-status">
                      <BookBadge :stok="buku.stok" />
                    </td>
                    <td class="td-actions">
                      <div class="row-actions">
                        <button
                          class="btn-row-edit"
                          title="Edit buku ini (Fitur Bonus)"
                          @click="bukaModalEdit(buku)"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="act-icon">
                            <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"></path>
                          </svg>
                          Edit
                        </button>
                        <button
                          class="btn-row-delete"
                          title="Hapus buku dari perpustakaan"
                          @click="handleHapusBuku(buku.id, buku.judul)"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="act-icon">
                            <path d="M3 6h18"></path>
                            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                          </svg>
                          Hapus
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Tampilan Cards (Mobile < 768px dan 375px) -->
            <div class="mobile-cards-view">
              <BookCard
                v-for="buku in sortedBooks"
                :key="buku.id"
                :book="buku"
                @edit="bukaModalEdit"
                @delete="handleHapusBuku"
              />
            </div>
          </div>
        </div>

        <!-- FITUR BONUS: VISUALISASI RINGKASAN STOK PER KATEGORI (CSS BAR) -->
        <section class="bonus-section">
          <CategoryStockBars :books="books" />
        </section>
      </div>
    </main>

    <!-- Modal Tambah / Edit Buku -->
    <BookModal
      :is-open="isModalOpen"
      :edit-mode="isEditMode"
      :book-to-edit="bookToEdit"
      :is-submitting="isSubmitting"
      @close="tutupModal"
      @submit="handleSimpanBuku"
    />

    <!-- Footer -->
    <footer class="app-footer">
      <div class="container footer-content">
        <p>
          UTS Pemrograman Aplikasi Web • Mini Dashboard Full-Stack (Vue 3 + FastAPI)
        </p>
        <p class="sub-credit">
          Soal A: Perpustakaan (NIM Ganjil) • REST API & In-Memory Seed Storage
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* ==========================================
   LAYOUT & CONTAINER
========================================== */
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8fafc;
  color: #0f172a;
  font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.25rem;
  width: 100%;
  box-sizing: border-box;
}

/* ==========================================
   TOAST NOTIFICATION
========================================== */
.toast-popup {
  position: fixed;
  top: 1.25rem;
  right: 1.25rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 1.15rem;
  border-radius: 10px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.12), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
  font-size: 0.875rem;
  font-weight: 600;
  max-width: 90vw;
}

.toast-success {
  background-color: #065f46;
  color: #ffffff;
}

.toast-error {
  background-color: #991b1b;
  color: #ffffff;
}

.toast-info {
  background-color: #0c4a6e;
  color: #ffffff;
}

.t-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ==========================================
   HEADER
========================================== */
.app-header {
  background: linear-gradient(135deg, #0b4f6c 0%, #032b3a 100%);
  color: #ffffff;
  padding: 1.15rem 0;
  box-shadow: 0 4px 12px rgba(11, 79, 108, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.brand-logo {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex-shrink: 0;
}

.logo-icon {
  width: 24px;
  height: 24px;
  color: #ffffff;
}

.app-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.app-subtitle {
  margin: 0.15rem 0 0 0;
  font-size: 0.75rem;
  color: #94d3e8;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.btn-api-docs,
.btn-reset {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.btn-api-docs:hover,
.btn-reset:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
}

.btn-icon-sm {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

/* ==========================================
   MAIN CONTENT FLOW
========================================== */
.app-main {
  flex: 1;
  padding: 1.75rem 0 3rem 0;
}

.main-content-flow {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ==========================================
   4 STAT TILES SECTION
========================================== */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

/* ==========================================
   TOOLBAR SECTION
========================================== */
.toolbar-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  background: #ffffff;
  padding: 1rem 1.25rem;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.search-filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  min-width: 280px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 220px;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.85rem;
  width: 17px;
  height: 17px;
  color: #94a3b8;
  pointer-events: none;
}

.input-search {
  width: 100%;
  padding: 0.55rem 2.2rem 0.55rem 2.4rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  font-size: 0.875rem;
  color: #0f172a;
  background-color: #f8fafc;
  outline: none;
  font-family: inherit;
  transition: all 0.15s ease;
}

.input-search:focus {
  background-color: #ffffff;
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}

.btn-clear-search {
  position: absolute;
  right: 0.65rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 4px;
}

.btn-clear-search:hover {
  color: #0f172a;
}

.select-category {
  padding: 0.55rem 0.85rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: #f8fafc;
  color: #334155;
  font-size: 0.875rem;
  font-weight: 500;
  outline: none;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}

.select-category:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
  background-color: #ffffff;
}

.sort-action-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.sort-toggle-group {
  display: flex;
  align-items: center;
  background-color: #f1f5f9;
  padding: 0.25rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.btn-sort {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #475569;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-sort.active {
  background-color: #0b4f6c;
  color: #ffffff;
  box-shadow: 0 1px 3px rgba(11, 79, 108, 0.25);
}

.sort-icon {
  width: 14px;
  height: 14px;
}

.btn-add-book {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  border: 1px solid #0284c7;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(2, 132, 199, 0.3);
  transition: all 0.15s ease;
}

.btn-add-book:hover {
  opacity: 0.95;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
}

/* ==========================================
   INFO BAR
========================================== */
.info-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8125rem;
  color: #64748b;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0 0.25rem;
}

.info-right {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
}

.badge-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
  margin-left: 0.2rem;
}

.dot-g { background-color: #10b981; }
.dot-y { background-color: #f59e0b; }
.dot-r { background-color: #ef4444; }

/* ==========================================
   STATE CARDS (Loading, Error, Empty)
========================================== */
.state-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  padding: 3rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}

.state-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #0f172a;
}

.state-desc {
  margin: 0;
  font-size: 0.875rem;
  color: #64748b;
  max-width: 500px;
}

/* Loading */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e0f2fe;
  border-top-color: #0284c7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.5rem;
}

/* Error */
.error-state {
  border-color: #fecaca;
  background-color: #fef2f2;
}

.error-icon-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #fee2e2;
  color: #dc2626;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.e-icon {
  width: 26px;
  height: 26px;
}

.error-text {
  color: #991b1b;
}

.error-guidance {
  background-color: #ffffff;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  border: 1px solid #fecaca;
  font-size: 0.8125rem;
  color: #475569;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 0.5rem;
}

.error-guidance code {
  background-color: #f1f5f9;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 700;
  color: #0f172a;
}

.btn-retry {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.75rem;
  padding: 0.55rem 1.25rem;
  border-radius: 8px;
  border: 1px solid #dc2626;
  background-color: #dc2626;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-retry:hover {
  background-color: #b91c1c;
}

/* Empty */
.empty-icon-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #f1f5f9;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.empty-icon {
  width: 26px;
  height: 26px;
}

.btn-reset-filters {
  margin-top: 0.75rem;
  padding: 0.45rem 1rem;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #0b4f6c;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-reset-filters:hover {
  background-color: #f8fafc;
}

/* ==========================================
   CATALOG TABLE (DESKTOP & TABLET)
========================================== */
.catalog-wrapper {
  display: flex;
  flex-direction: column;
}

.table-container {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  overflow-x: auto;
}

.books-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.books-table th {
  background-color: #f8fafc;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.95rem 1.15rem;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.books-table td {
  padding: 1rem 1.15rem;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #1e293b;
  vertical-align: middle;
}

.book-row:last-child td {
  border-bottom: none;
}

.book-row:hover {
  background-color: #f8fafc;
}

.td-id {
  font-family: monospace;
  font-weight: 600;
  color: #64748b;
  font-size: 0.8125rem;
}

.cell-title {
  font-weight: 700;
  color: #0f172a;
}

.td-author {
  color: #475569;
}

.category-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #0369a1;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
  white-space: nowrap;
}

.stock-num {
  font-weight: 700;
}

.stock-num.zero-stock {
  color: #e11d48;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.btn-row-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #0284c7;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-row-edit:hover {
  background-color: #e0f2fe;
}

.btn-row-delete {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #dc2626;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-row-delete:hover {
  background-color: #fee2e2;
}

.act-icon {
  width: 13px;
  height: 13px;
}

/* ==========================================
   MOBILE CARDS VIEW (Disembunyikan di Desktop)
========================================== */
.mobile-cards-view {
  display: none;
  flex-direction: column;
  gap: 0.85rem;
}

/* ==========================================
   BONUS SECTION
========================================== */
.bonus-section {
  margin-top: 0.5rem;
}

/* ==========================================
   FOOTER
========================================== */
.app-footer {
  margin-top: auto;
  background-color: #ffffff;
  border-top: 1px solid #e2e8f0;
  padding: 1.5rem 0;
  text-align: center;
  font-size: 0.8125rem;
  color: #64748b;
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sub-credit {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

/* ==========================================
   RESPONSIVE DESIGN (Desktop / Tablet / Mobile)
   - Desktop >= 1024px
   - Tablet 768px - 1023px
   - Mobile < 768px (termasuk 375px)
========================================== */
@media (max-width: 1023px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .header-container {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .stats-section {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .toolbar-section {
    flex-direction: column;
    align-items: stretch;
    padding: 1rem;
  }

  .search-filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }

  .select-category {
    width: 100%;
  }

  .sort-action-group {
    justify-content: space-between;
  }

  .btn-add-book {
    flex: 1;
    justify-content: center;
  }

  .info-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  /* Sembunyikan tabel di layar sempit, ganti dengan Card list */
  .desktop-table-view {
    display: none;
  }

  .mobile-cards-view {
    display: flex;
  }
}

@media (max-width: 480px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .sort-action-group {
    flex-direction: column;
    align-items: stretch;
  }

  .sort-toggle-group {
    width: 100%;
    justify-content: center;
  }

  .btn-sort {
    flex: 1;
    justify-content: center;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
