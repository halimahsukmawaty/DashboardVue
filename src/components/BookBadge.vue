<script setup>
import { computed } from "vue";

const props = defineProps({
  stok: {
    type: Number,
    required: true,
  },
});

// Computed untuk menentukan status teks dan class berdasarkan ambang batas stok
// Ambang Batas:
// - stok === 0      => "Stok Habis" (Merah / Danger)
// - 1 <= stok <= 5  => "Menipis"    (Kuning/Oranye / Warning)
// - stok > 5        => "Tersedia"   (Hijau / Success)
const statusInfo = computed(() => {
  if (props.stok === 0) {
    return {
      label: "Stok Habis",
      cssClass: "badge-habis",
      dotClass: "dot-habis",
    };
  } else if (props.stok <= 5) {
    return {
      label: "Menipis",
      cssClass: "badge-menipis",
      dotClass: "dot-menipis",
    };
  } else {
    return {
      label: "Tersedia",
      cssClass: "badge-tersedia",
      dotClass: "dot-tersedia",
    };
  }
});
</script>

<template>
  <span class="badge" :class="statusInfo.cssClass">
    <span class="dot" :class="statusInfo.dotClass"></span>
    {{ statusInfo.label }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

/* Badge Tersedia (Stok > 5) */
.badge-tersedia {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}
.dot-tersedia {
  background-color: #10b981;
}

/* Badge Menipis (1 <= Stok <= 5) */
.badge-menipis {
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
}
.dot-menipis {
  background-color: #f59e0b;
}

/* Badge Stok Habis (Stok === 0) */
.badge-habis {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}
.dot-habis {
  background-color: #ef4444;
}
</style>
