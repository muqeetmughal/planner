import { ref, reactive } from 'vue'
import { createToast } from 'frappe-ui'

// Global toast state
const toasts = ref([])
let toastId = 0

// Toast types configuration
const toastTypes = {
  success: {
    icon: 'check-circle',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  error: {
    icon: 'alert-circle',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200'
  },
  warning: {
    icon: 'alert-triangle',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200'
  },
  info: {
    icon: 'info',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
  }
}

export function useToast() {
  // Create a toast notification
  const showToast = (message, type = 'info', duration = 5000) => {
    const id = ++toastId

    const toast = {
      id,
      message,
      type,
      duration,
      ...toastTypes[type],
      timestamp: Date.now()
    }

    toasts.value.push(toast)

    // Auto-remove toast after duration
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }

    return id
  }

  // Remove a specific toast
  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  // Clear all toasts
  const clearAllToasts = () => {
    toasts.value = []
  }

  // Convenience methods for different toast types
  const success = (message, duration = 3000) => {
    return showToast(message, 'success', duration)
  }

  const error = (message, duration = 5000) => {
    return showToast(message, 'error', duration)
  }

  const warning = (message, duration = 4000) => {
    return showToast(message, 'warning', duration)
  }

  const info = (message, duration = 3000) => {
    return showToast(message, 'info', duration)
  }

  // Create persistent toast (must be manually dismissed)
  const persistent = (message, type = 'info') => {
    return showToast(message, type, 0)
  }

  return {
    toasts,
    showToast,
    removeToast,
    clearAllToasts,
    success,
    error,
    warning,
    info,
    persistent
  }
}

// Global toast instance for use across the application
export const toast = useToast()
