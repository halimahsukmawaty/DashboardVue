<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  value: {
    type: [Number, String],
    required: true,
  },
  description: {
    type: String,
    default: "",
  },
  type: {
    type: String,
    default: "primary", // 'primary' | 'danger' | 'purple' | 'emerald'
  },
  icon: {
    type: String,
    default: "book",
  },
});
</script>

<template>
  <div class="stat-tile" :class="`stat-${type}`">
    <div class="stat-content">
      <span class="stat-title">{{ title }}</span>
      <div class="stat-value-row">
        <span class="stat-value">{{ value }}</span>
      </div>
      <span v-if="description" class="stat-desc">{{ description }}</span>
    </div>

    <div class="stat-icon-wrapper">
      <!-- Icon Book Total -->
      <svg
        v-if="icon === 'book'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon"
      >
        <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path>
        <path d="M6 6h10"></path>
        <path d="M6 10h10"></path>
      </svg>

      <!-- Icon Warning / Low Stock -->
      <svg
        v-else-if="icon === 'alert'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon"
      >
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
        <line x1="12" y1="9" x2="12" y2="13"></line>
        <line x1="12" y1="17" x2="12.01" y2="17"></line>
      </svg>

      <!-- Icon Layers / Category -->
      <svg
        v-else-if="icon === 'category'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon"
      >
        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
        <polyline points="2 17 12 22 22 17"></polyline>
        <polyline points="2 12 12 17 22 12"></polyline>
      </svg>

      <!-- Icon Total Copies / Stock -->
      <svg
        v-else-if="icon === 'copies'"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="icon"
      >
        <rect width="8" height="18" x="3" y="3" rx="1"></rect>
        <rect width="8" height="18" x="13" y="3" rx="1"></rect>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.stat-tile {
  background: #ffffff;
  border-radius: 14px;
  padding: 1.25rem 1.35rem;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
  overflow: hidden;
}

.stat-tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  z-index: 1;
}

.stat-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.stat-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon {
  width: 24px;
  height: 24px;
}

/* Variant Primary (Ocean Blue) */
.stat-primary .stat-icon-wrapper {
  background: #e0f2fe;
  color: #0284c7;
}
.stat-primary:hover {
  border-color: #bae6fd;
}

/* Variant Danger / Warning (Amber/Rose) */
.stat-danger .stat-icon-wrapper {
  background: #fee2e2;
  color: #e11d48;
}
.stat-danger:hover {
  border-color: #fecaca;
}

/* Variant Purple (Indigo) */
.stat-purple .stat-icon-wrapper {
  background: #ede9fe;
  color: #6366f1;
}
.stat-purple:hover {
  border-color: #ddd6fe;
}

/* Variant Emerald (Green) */
.stat-emerald .stat-icon-wrapper {
  background: #dcfce7;
  color: #10b981;
}
.stat-emerald:hover {
  border-color: #bbf7d0;
}
</style>
