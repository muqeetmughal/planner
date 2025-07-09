<template>
  <div class="toast-container fixed top-4 right-4 z-50 space-y-2 max-w-sm">
    <TransitionGroup name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'toast-item p-4 rounded-lg shadow-lg border backdrop-blur-sm transition-all duration-300',
          toast.bgColor,
          toast.borderColor,
          'bg-opacity-95 dark:bg-opacity-95'
        ]"
        role="alert"
        @click="removeToast(toast.id)"
      >
        <div class="flex items-start gap-3">
          <!-- Icon -->
          <div class="flex-shrink-0 pt-0.5">
            <FeatherIcon
              :name="toast.icon"
              :class="['w-5 h-5', toast.color]"
            />
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div :class="['text-sm font-medium', toast.color]">
              {{ toast.message }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ formatTime(toast.timestamp) }}
            </div>
          </div>

          <!-- Close Button -->
          <button
            @click.stop="removeToast(toast.id)"
            class="flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            aria-label="Close notification"
          >
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>

        <!-- Progress bar for timed toasts -->
        <div
          v-if="toast.duration > 0"
          class="mt-3 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
        >
          <div
            class="h-full bg-current opacity-50 rounded-full transition-all ease-linear"
            :class="toast.color"
            :style="{
              width: '100%',
              animation: `toast-progress ${toast.duration}ms linear forwards`
            }"
          ></div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { toast } from '../../composables/useToast'

// Get toasts from the global toast instance
const toasts = computed(() => toast.toasts.value)

// Methods
const removeToast = (id) => {
  toast.removeToast(id)
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}
</script>

<style scoped>
/* Toast animations */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-leave-active {
  transition: all 0.2s ease-in;
}

.toast-enter-from {
  transform: translateX(100%) scale(0.9);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%) scale(0.9);
  opacity: 0;
}

.toast-move {
  transition: transform 0.3s ease;
}

/* Progress bar animation */
@keyframes toast-progress {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

/* Toast item styling */
.toast-item {
  max-width: 400px;
  min-width: 300px;
  cursor: pointer;
  transform-origin: right center;
}

.toast-item:hover {
  transform: translateX(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Dark mode adjustments */
.dark .toast-item {
  backdrop-filter: blur(12px);
}

.dark .toast-item:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
}

/* Responsive design */
@media (max-width: 640px) {
  .toast-container {
    @apply left-4 right-4;
  }

  .toast-item {
    @apply min-w-0 max-w-none;
  }
}
</style>
