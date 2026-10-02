<script setup>
import { computed } from "vue";

const props = defineProps({
  books: {
    type: Array,
    required: true,
  },
});

// Palet warna yang harmonis untuk tiap bar kategori
const categoryColors = [
  "#0284c7", // Sky/Blue
  "#059669", // Emerald
  "#d97706", // Amber
  "#7c3aed", // Violet
  "#e11d48", // Rose
  "#0891b2", // Cyan
  "#4f46e5", // Indigo
  "#65a30d", // Lime
];

// Computed murni menggunakan method array native ES6: .reduce(), .map(), .sort()
// Menghitung ringkasan stok per kategori dan persentase lebar bar CSS
const categorySummary = computed(() => {
  if (!props.books || props.books.length === 0) return [];

  // 1. Kelompokkan dan jumlahkan stok per kategori menggunakan .reduce()
  const grouped = props.books.reduce((acc, book) => {
    const kat = book.kategori || "Lainnya";
    if (!acc[kat]) {
      acc[kat] = { kategori: kat, totalStok: 0, jumlahBuku: 0 };
    }
    acc[kat].totalStok += book.stok;
    acc[kat].jumlahBuku += 1;
    return acc;
  }, {});

  // 2. Ubah objek grup menjadi array
  const list = Object.values(grouped);

  // 3. Cari stok tertinggi untuk patokan skala 100% lebar bar
  const maxStok = list.reduce(
    (max, item) => (item.totalStok > max ? item.totalStok : max),
    1
  );

  // 4. Urutkan berdasarkan total stok terbanyak menggunakan .sort()
  // dan hitung persentase lebar CSS menggunakan .map()
  return list
    .sort((a, b) => b.totalStok - a.totalStok)
    .map((item, index) => ({
      ...item,
      color: categoryColors[index % categoryColors.length],
      percentage: Math.max(8, Math.round((item.totalStok / maxStok) * 100)),
    }));
});
</script>

<template>
  <div class="category-bars-card">
    <div class="card-header">
      <div class="header-left">
        <h3 class="card-title">Ringkasan Stok per Kategori</h3>
        <span class="bonus-badge">Fitur Bonus</span>
      </div>
      <p class="card-subtitle">
        Visualisasi distribusi eksemplar buku dihitung dengan computed murni & bar CSS native.
      </p>
    </div>

    <div v-if="categorySummary.length === 0" class="empty-state">
      Tidak ada data kategori untuk ditampilkan.
    </div>

    <div v-else class="bars-container">
      <div
        v-for="cat in categorySummary"
        :key="cat.kategori"
        class="bar-item"
      >
        <div class="bar-header">
          <div class="category-label-group">
            <span
              class="color-dot"
              :style="{ backgroundColor: cat.color }"
            ></span>
            <span class="category-name">{{ cat.kategori }}</span>
            <span class="book-count-pill">{{ cat.jumlahBuku }} judul</span>
          </div>
          <div class="stock-figures">
            <span class="stock-number">{{ cat.totalStok }}</span>
            <span class="stock-unit">eksemplar</span>
          </div>
        </div>

        <!-- Track & Fill CSS Bar -->
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{
              width: cat.percentage + '%',
              backgroundColor: cat.color,
            }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.category-bars-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.35rem 1.5rem;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}

.card-header {
  margin-bottom: 1.25rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.bonus-badge {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  background-color: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.card-subtitle {
  margin: 0.25rem 0 0 0;
  font-size: 0.8125rem;
  color: #64748b;
}

.bars-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bar-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.bar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8125rem;
}

.category-label-group {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.category-name {
  font-weight: 600;
  color: #1e293b;
}

.book-count-pill {
  font-size: 0.6875rem;
  color: #64748b;
  background-color: #f1f5f9;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.stock-figures {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.stock-number {
  font-weight: 700;
  color: #0f172a;
}

.stock-unit {
  font-size: 0.75rem;
  color: #64748b;
}

.bar-track {
  width: 100%;
  height: 8px;
  background-color: #f1f5f9;
  border-radius: 9999px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.empty-state {
  text-align: center;
  padding: 1.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}
</style>
