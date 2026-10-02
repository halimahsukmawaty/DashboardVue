<script setup>
import BookBadge from "./BookBadge.vue";

defineProps({
  book: {
    type: Object,
    required: true,
  },
});

defineEmits(["edit", "delete"]);
</script>

<template>
  <div class="book-card">
    <div class="card-header">
      <span class="category-pill">{{ book.kategori }}</span>
      <BookBadge :stok="book.stok" />
    </div>

    <div class="card-body">
      <h3 class="book-title">{{ book.judul }}</h3>
      <p class="book-author">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="inline-icon">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        {{ book.penulis }}
      </p>

      <div class="stock-info">
        <span class="stock-label">Jumlah Stok:</span>
        <span class="stock-count" :class="{ 'zero-stock': book.stok === 0 }">
          {{ book.stok }} eksemplar
        </span>
      </div>
    </div>

    <div class="card-actions">
      <button
        class="btn-action btn-edit"
        title="Edit Buku"
        @click="$emit('edit', book)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon">
          <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"></path>
        </svg>
        Edit
      </button>

      <button
        class="btn-action btn-delete"
        title="Hapus Buku"
        @click="$emit('delete', book.id, book.judul)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="btn-icon">
          <path d="M3 6h18"></path>
          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
        Hapus
      </button>
    </div>
  </div>
</template>

<style scoped>
.book-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.book-card:hover {
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.category-pill {
  font-size: 0.75rem;
  font-weight: 600;
  color: #0369a1;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  padding: 0.2rem 0.55rem;
  border-radius: 6px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.book-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.35;
}

.book-author {
  margin: 0;
  font-size: 0.8125rem;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.inline-icon {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.25rem;
  font-size: 0.8125rem;
}

.stock-label {
  color: #64748b;
}

.stock-count {
  font-weight: 700;
  color: #0f172a;
}

.stock-count.zero-stock {
  color: #e11d48;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.6rem;
  border-top: 1px solid #f1f5f9;
  margin-top: auto;
}

.btn-action {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-icon {
  width: 14px;
  height: 14px;
}

.btn-edit {
  background-color: #f8fafc;
  color: #0284c7;
  border: 1px solid #cbd5e1;
}

.btn-edit:hover {
  background-color: #f0f9ff;
  border-color: #7dd3fc;
}

.btn-delete {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.btn-delete:hover {
  background-color: #fee2e2;
  border-color: #fca5a5;
}
</style>
