<script setup>
import { ref } from 'vue';

defineProps({
  user: {
    type: Object,
    default: () => ({})
  },
  name: {
    type: String,
    default: ''
  },
  email: {
    type: String,
    default: ''
  },
  phone: {
    type: String,
    default: ''
  },
  company: {
    type: [Object, String],
    default: ''
  },
  city: {
    type: String,
    default: ''
  }
});

// State lokal khusus untuk UserCard ini (Problem 1)
const isDetailOpen = ref(false);

function toggleDetail() {
  isDetailOpen.value = !isDetailOpen.value;
}
</script>

<template>
  <div class="user-card">
    <div class="user-card-header">
      <div class="user-info">
        <h3 class="user-name">{{ name || user.name }}</h3>
        <p class="user-email">{{ email || user.email }}</p>
      </div>
      <button
        class="btn-detail"
        :class="{ active: isDetailOpen }"
        @click="toggleDetail"
      >
        {{ isDetailOpen ? 'Sembunyikan' : 'Lihat Detail' }}
      </button>
    </div>

    <!-- Detail pengguna yang ditampilkan saat isDetailOpen bernilai true -->
    <div v-if="isDetailOpen" class="user-detail">
      <p class="detail-item">
        <span class="detail-label">Telepon:</span>
        {{ phone || user.phone }}
      </p>
      <p class="detail-item">
        <span class="detail-label">Perusahaan:</span>
        {{ (typeof company === 'object' ? company?.name : company) || user.company?.name || '-' }}
      </p>
      <p class="detail-item">
        <span class="detail-label">Kota:</span>
        {{ city || user.address?.city || '-' }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.user-card {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #ffffff;
  transition: background-color 0.15s ease;
}

.user-card:last-child {
  border-bottom: none;
}

.user-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
}

.user-email {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.btn-detail {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  background-color: #ffffff;
  color: #0b4f6c;
  border: 1px solid #0b4f6c;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-detail:hover {
  background-color: #f0f7fa;
}

.btn-detail.active {
  background-color: #0b4f6c;
  color: #ffffff;
  border-color: #0b4f6c;
}

.btn-detail.active:hover {
  background-color: #083c52;
}

.user-detail {
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  background-color: #f8fafc;
  border-radius: 6px;
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.detail-item {
  margin: 0;
  font-size: 0.875rem;
  color: #334155;
  line-height: 1.5;
}

.detail-label {
  font-weight: 600;
  color: #1e293b;
  margin-right: 0.25rem;
}
</style>
