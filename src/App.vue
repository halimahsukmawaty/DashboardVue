<script setup>
import { ref, computed } from "vue";
import UserCard from "./components/UserCard.vue";

const judul = "Dashboard Vue — Pertemuan 5";

// State data pengguna dan status HTTP/aplikasi (Sesi 5)
const pengguna = ref([]);
const keadaan = ref("idle"); // 'idle' | 'loading' | 'sukses' | 'kosong' | 'error'
const pesanError = ref("");

// State pencarian (Step 8 modul praktikum)
const queryPencarian = ref("");

// State arah pengurutan (Problem 2: 'asc' atau 'desc')
const arahUrutan = ref("asc");

// Fungsi untuk mengambil data dari JSONPlaceholder
async function fetchData() {
  keadaan.value = "loading";
  pesanError.value = "";
  try {
    const res = await fetch("https://jsonplaceholder.typicode.com/users");
    if (!res.ok) {
      throw new Error("Status HTTP: " + res.status);
    }
    const data = await res.json();
    if (data.length === 0) {
      keadaan.value = "kosong";
    } else {
      pengguna.value = data;
      keadaan.value = "sukses";
    }
  } catch (err) {
    keadaan.value = "error";
    pesanError.value = err.message || "Gagal memuat data pengguna";
  }
}

// Computed tahap 1: menyaring pengguna berdasarkan query pencarian username (Step 8)
const penggunaTersaring = computed(() => {
  const q = queryPencarian.value.toLowerCase().trim();
  if (!q) {
    return pengguna.value;
  }
  return pengguna.value.filter((user) =>
    user.username && user.username.toLowerCase().includes(q)
  );
});

// Computed tahap 2 (Problem 2 - Chained Computed):
// Mengurutkan SALINAN hasil dari penggunaTersaring menggunakan spread operator [...]
const penggunaTerurut = computed(() => {
  return [...penggunaTersaring.value].sort((a, b) => {
    if (arahUrutan.value === "asc") {
      return a.name.localeCompare(b.name);
    } else {
      return b.name.localeCompare(a.name);
    }
  });
});
</script>

<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="container">
        <h1>{{ judul }}</h1>
      </div>
    </header>

    <main class="app-main">
      <div class="container">
        <!-- Kontrol Toolbar: Tombol Muat, Input Pencarian, dan Tombol Pengurutan (Problem 2) -->
        <section class="toolbar">
          <button
            class="btn-primary"
            :disabled="keadaan === 'loading'"
            @click="fetchData"
          >
            Muat Pengguna
          </button>

          <input
            v-model="queryPencarian"
            type="text"
            placeholder="Cari username..."
            class="input-search"
          />

          <button
            class="btn-sort"
            :class="{ active: arahUrutan === 'asc' }"
            @click="arahUrutan = 'asc'"
          >
            Urutkan A-Z
          </button>

          <button
            class="btn-sort"
            :class="{ active: arahUrutan === 'desc' }"
            @click="arahUrutan = 'desc'"
          >
            Urutkan Z-A
          </button>
        </section>

        <!-- Keterangan visual arah urutan yang aktif -->
        <p v-if="keadaan === 'sukses' && arahUrutan" class="keterangan-urutan">
          Tombol "Urutkan {{ arahUrutan === 'asc' ? 'A-Z' : 'Z-A' }}" sedang aktif (disorot) — daftar di bawah tampil terurut alfabet {{ arahUrutan === 'asc' ? 'A ke Z' : 'Z ke A' }} berdasarkan nama.
        </p>

        <!-- Kondisi v-if / v-else-if untuk menampilkan berbagai state aplikasi (Sesi 5) -->
        <div v-if="keadaan === 'loading'" class="status-card">
          <p class="status-msg">Memuat data pengguna...</p>
        </div>

        <div v-else-if="keadaan === 'error'" class="status-card error-card">
          <p class="status-msg error-msg">Terjadi kesalahan: {{ pesanError }}</p>
        </div>

        <div v-else-if="keadaan === 'kosong'" class="status-card">
          <p class="status-msg">Tidak ada data pengguna yang tersedia.</p>
        </div>

        <div v-else-if="keadaan === 'sukses'">
          <div v-if="penggunaTerurut.length === 0" class="status-card">
            <p class="status-msg">
              Tidak ada pengguna dengan username yang cocok dengan "{{ queryPencarian }}".
            </p>
          </div>

          <!-- Daftar Pengguna terurut (Problem 1 & Problem 2) -->
          <div v-else class="user-list">
            <UserCard
              v-for="user in penggunaTerurut"
              :key="user.id"
              :user="user"
              :name="user.name"
              :email="user.email"
              :phone="user.phone"
              :company="user.company?.name"
              :city="user.address?.city"
            />
          </div>
        </div>

        <div v-else-if="keadaan === 'idle'" class="status-card">
          <p class="status-msg">
            Silakan klik tombol <strong>"Muat Pengguna"</strong> di atas untuk memuat data pengguna.
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background-color: #f8fafc;
  color: #1e293b;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}

.app-header {
  background-color: #0b4f6c;
  color: #ffffff;
  padding: 1.25rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.container {
  max-width: 820px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.app-header h1 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.app-main {
  padding: 2rem 0;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.btn-primary {
  background-color: #0b4f6c;
  color: #ffffff;
  border: 1px solid #0b4f6c;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background-color: #083b51;
  border-color: #083b51;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-search {
  padding: 0.5rem 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1e293b;
  outline: none;
  width: 200px;
  background-color: #ffffff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-search:focus {
  border-color: #0b4f6c;
  box-shadow: 0 0 0 2px rgba(11, 79, 108, 0.15);
}

.btn-sort {
  background-color: #ffffff;
  color: #0b4f6c;
  border: 1px solid #0b4f6c;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-sort:hover {
  background-color: #f0f7fa;
}

.btn-sort.active {
  background-color: #0b4f6c;
  color: #ffffff;
  border-color: #0b4f6c;
}

.btn-sort.active:hover {
  background-color: #083b51;
}

.keterangan-urutan {
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0 0 1.25rem 0;
  line-height: 1.4;
}

.status-card {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.status-msg {
  margin: 0;
  color: #475569;
  font-size: 0.95rem;
}

.error-card {
  border-color: #fecaca;
  background-color: #fef2f2;
}

.error-msg {
  color: #dc2626;
  font-weight: 500;
}

.user-list {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
</style>
