<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  editMode: {
    type: Boolean,
    default: false,
  },
  bookToEdit: {
    type: Object,
    default: null,
  },
  isSubmitting: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["close", "submit"]);

// State lokal form menggunakan ref sesuai spesifikasi 3.1
const judul = ref("");
const penulis = ref("");
const kategori = ref("");
const stok = ref(1);
const formError = ref("");

// Kategori umum untuk kemudahan input
const daftarKategori = [
  "Teknologi",
  "Sains",
  "Fiksi",
  "Sastra",
  "Bisnis",
  "Sejarah",
  "Filsafat",
  "Pengembangan Diri",
  "Pendidikan",
  "Lainnya",
];

// Sinkronisasi data form saat modal dibuka atau saat mode edit berubah
watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      formError.value = "";
      if (props.editMode && props.bookToEdit) {
        judul.value = props.bookToEdit.judul || "";
        penulis.value = props.bookToEdit.penulis || "";
        kategori.value = props.bookToEdit.kategori || "";
        stok.value = props.bookToEdit.stok ?? 0;
      } else {
        // Reset form untuk mode tambah baru
        judul.value = "";
        penulis.value = "";
        kategori.value = "Teknologi";
        stok.value = 5;
      }
    }
  }
);

function handleSubmit() {
  formError.value = "";

  // Validasi lokal field wajib
  if (!judul.value.trim()) {
    formError.value = "Judul buku wajib diisi.";
    return;
  }
  if (!penulis.value.trim()) {
    formError.value = "Nama penulis wajib diisi.";
    return;
  }
  if (!kategori.value.trim()) {
    formError.value = "Kategori buku wajib dipilih atau diisi.";
    return;
  }
  if (stok.value === null || stok.value === undefined || Number(stok.value) < 0) {
    formError.value = "Jumlah stok harus berupa angka minimal 0.";
    return;
  }

  // Kirim data yang sudah divalidasi ke parent component
  emit("submit", {
    judul: judul.value.trim(),
    penulis: penulis.value.trim(),
    kategori: kategori.value.trim(),
    stok: parseInt(stok.value, 10),
  });
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-dialog" role="dialog" aria-modal="true">
      <div class="modal-header">
        <div class="header-text">
          <h2 class="modal-title">
            {{ editMode ? "Edit Data Buku" : "Tambah Koleksi Buku Baru" }}
          </h2>
          <p class="modal-subtitle">
            {{
              editMode
                ? "Perbarui informasi atau stok buku perpustakaan."
                : "Masukkan detail informasi buku baru ke dalam katalog perpustakaan."
            }}
          </p>
        </div>
        <button class="btn-close" aria-label="Tutup modal" @click="$emit('close')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="close-icon">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="modal-form">
        <!-- Notifikasi Error Form -->
        <div v-if="formError" class="alert-error">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="alert-icon">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{{ formError }}</span>
        </div>

        <!-- Field Judul Buku -->
        <div class="form-group">
          <label for="input-judul" class="form-label">
            Judul Buku <span class="required">*</span>
          </label>
          <input
            id="input-judul"
            v-model="judul"
            type="text"
            class="form-input"
            placeholder="Contoh: Belajar Vue 3 & FastAPI"
            required
            :disabled="isSubmitting"
          />
        </div>

        <!-- Field Penulis -->
        <div class="form-group">
          <label for="input-penulis" class="form-label">
            Penulis / Pengarang <span class="required">*</span>
          </label>
          <input
            id="input-penulis"
            v-model="penulis"
            type="text"
            class="form-input"
            placeholder="Contoh: Robert C. Martin"
            required
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-row">
          <!-- Field Kategori -->
          <div class="form-group form-col">
            <label for="input-kategori" class="form-label">
              Kategori <span class="required">*</span>
            </label>
            <select
              id="input-kategori"
              v-model="kategori"
              class="form-select"
              required
              :disabled="isSubmitting"
            >
              <option value="" disabled>Pilih Kategori</option>
              <option
                v-for="kat in daftarKategori"
                :key="kat"
                :value="kat"
              >
                {{ kat }}
              </option>
            </select>
          </div>

          <!-- Field Stok -->
          <div class="form-group form-col">
            <label for="input-stok" class="form-label">
              Jumlah Stok Fisik <span class="required">*</span>
            </label>
            <input
              id="input-stok"
              v-model.number="stok"
              type="number"
              min="0"
              class="form-input"
              placeholder="0"
              required
              :disabled="isSubmitting"
            />
          </div>
        </div>

        <!-- Ambang Batas Info -->
        <div class="threshold-hint">
          <span class="hint-title">Aturan Status Stok Otomatis:</span>
          <span>0 = Stok Habis (Merah) | 1-5 = Menipis (Kuning) | > 5 = Tersedia (Hijau)</span>
        </div>

        <!-- Modal Actions -->
        <div class="modal-footer">
          <button
            type="button"
            class="btn-secondary"
            :disabled="isSubmitting"
            @click="$emit('close')"
          >
            Batal
          </button>
          <button
            type="submit"
            class="btn-submit"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting" class="spinner-small"></span>
            <span v-else>{{ editMode ? "Simpan Perubahan" : "Tambah Buku" }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}

.modal-dialog {
  background: #ffffff;
  border-radius: 16px;
  max-width: 520px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid #e2e8f0;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.modal-subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.8125rem;
  color: #64748b;
}

.btn-close {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 0.35rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.btn-close:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}

.close-icon {
  width: 20px;
  height: 20px;
}

.modal-form {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.alert-error {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.65rem 0.85rem;
  border-radius: 8px;
  font-size: 0.8125rem;
}

.alert-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-col {
  flex: 1;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
}

.required {
  color: #ef4444;
}

.form-input,
.form-select {
  width: 100%;
  box-sizing: border-box;
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: #ffffff;
  color: #0f172a;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
}

.form-input:disabled,
.form-select:disabled {
  background-color: #f8fafc;
  cursor: not-allowed;
  opacity: 0.7;
}

.threshold-hint {
  background-color: #f8fafc;
  border: 1px dashed #cbd5e1;
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  font-size: 0.75rem;
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.hint-title {
  font-weight: 600;
  color: #334155;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.btn-secondary {
  padding: 0.6rem 1.15rem;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background-color: #ffffff;
  color: #475569;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f1f5f9;
  color: #0f172a;
}

.btn-submit {
  padding: 0.6rem 1.35rem;
  border-radius: 8px;
  border: 1px solid #0284c7;
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(2, 132, 199, 0.3);
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-submit:hover:not(:disabled) {
  opacity: 0.95;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
}

.btn-submit:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 640px) {
  .form-row {
    flex-direction: column;
    gap: 1.15rem;
  }
}
</style>
