<template>
  <div class="dynamic-block-details">
    <!-- Block Header -->
    <div class="block-header mb-6">
      <div class="flex items-start gap-4">
        <!-- Status Indicator -->
        <div 
          :class="[
            'w-4 h-4 rounded-full mt-1 flex-shrink-0',
            statusColor
          ]"
        ></div>
        
        <!-- Block Info -->
        <div class="flex-1 min-w-0">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            {{ blockTitle }}
          </h3>
          <div class="text-sm text-gray-600 dark:text-gray-400">
            {{ config?.block_doctype }} • {{ block.name }}
          </div>
        </div>
        
        <!-- Priority Badge -->
        <div v-if="blockPriority" :class="[
          'px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1',
          priorityBadgeClass
        ]">
          <FeatherIcon :name="priorityIcon" class="w-3 h-3" />
          {{ blockPriority }}
        </div>
      </div>
    </div>

    <!-- Block Details Grid -->
    <div class="details-grid space-y-6">
      <!-- Basic Information -->
      <div class="detail-section">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <FeatherIcon name="info" class="w-4 h-4" />
          Basic Information
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Status -->
          <div class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Status</label>
            <div class="mt-1 flex items-center gap-2">
              <div :class="['w-2 h-2 rounded-full', statusColor]"></div>
              <span class="text-sm text-gray-900 dark:text-white capitalize">{{ blockStatus }}</span>
            </div>
          </div>
          
          <!-- Priority -->
          <div v-if="blockPriority" class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Priority</label>
            <div class="mt-1 flex items-center gap-2">
              <FeatherIcon :name="priorityIcon" :class="['w-4 h-4', priorityColor]" />
              <span class="text-sm text-gray-900 dark:text-white capitalize">{{ blockPriority }}</span>
            </div>
          </div>
          
          <!-- Progress -->
          <div v-if="blockProgress !== null" class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Progress</label>
            <div class="mt-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm text-gray-900 dark:text-white">{{ blockProgress }}%</span>
              </div>
              <div class="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                <div 
                  :class="['h-full transition-all duration-300', progressColor]"
                  :style="{ width: `${blockProgress}%` }"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- Duration -->
          <div v-if="blockDuration" class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Duration</label>
            <div class="mt-1 flex items-center gap-2">
              <FeatherIcon name="clock" class="w-4 h-4 text-gray-400" />
              <span class="text-sm text-gray-900 dark:text-white">{{ blockDuration }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Description -->
      <div v-if="blockDescription" class="detail-section">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <FeatherIcon name="file-text" class="w-4 h-4" />
          Description
        </h4>
        <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
          <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ blockDescription }}</p>
        </div>
      </div>

      <!-- Assignment Information -->
      <div class="detail-section">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <FeatherIcon name="user" class="w-4 h-4" />
          Assignment
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Assigned To -->
          <div class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Assigned To</label>
            <div class="mt-1">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ assignedRowTitle || 'Unassigned' }}
              </span>
            </div>
          </div>
          
          <!-- Date -->
          <div class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Date</label>
            <div class="mt-1 flex items-center gap-2">
              <FeatherIcon name="calendar" class="w-4 h-4 text-gray-400" />
              <span class="text-sm text-gray-900 dark:text-white">
                {{ formatBlockDate() }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Custom Fields -->
      <div v-if="customFields.length > 0" class="detail-section">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <FeatherIcon name="settings" class="w-4 h-4" />
          Additional Details
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="field in customFields" :key="field.key" class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              {{ field.label }}
            </label>
            <div class="mt-1">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ field.value || '-' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Timestamps -->
      <div class="detail-section">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <FeatherIcon name="clock" class="w-4 h-4" />
          Timestamps
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Created</label>
            <div class="mt-1">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ formatTimestamp(block.creation) }}
              </span>
            </div>
          </div>
          
          <div class="detail-item">
            <label class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Modified</label>
            <div class="mt-1">
              <span class="text-sm text-gray-900 dark:text-white">
                {{ formatTimestamp(block.modified) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions-section mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Button variant="solid" theme="blue" size="sm" @click="editBlock">
            <FeatherIcon name="edit" class="w-4 h-4 mr-2" />
            Edit {{ config?.block_doctype }}
          </Button>
          
          <Button variant="outline" theme="gray" size="sm" @click="viewInSystem">
            <FeatherIcon name="external-link" class="w-4 h-4 mr-2" />
            View in System
          </Button>
        </div>
        
        <Button variant="ghost" theme="gray" size="sm" @click="$emit('close')">
          Close
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  block: {
    type: Object,
    required: true
  },
  config: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'update'])

// Computed properties for block data
const blockTitle = computed(() => {
  if (!props.config?.block_title_field) return props.block.name || props.block.id
  return props.block[props.config.block_title_field] || props.block.name || props.block.id
})

const blockDescription = computed(() => {
  if (!props.config?.block_description_field) return ''
  return props.block[props.config.block_description_field] || ''
})

const blockStatus = computed(() => {
  if (!props.config?.block_status_field) return 'default'
  return props.block[props.config.block_status_field] || 'default'
})

const blockPriority = computed(() => {
  if (!props.config?.block_priority_field) return null
  return props.block[props.config.block_priority_field] || null
})

const blockProgress = computed(() => {
  if (!props.config?.block_progress_field) return null
  const progress = props.block[props.config.block_progress_field]
  return progress !== null && progress !== undefined ? Number(progress) : null
})

const blockDuration = computed(() => {
  if (!props.config?.block_duration_field) return null
  const duration = props.block[props.config.block_duration_field]
  if (!duration) return null
  
  // Format duration (assuming it's in hours or minutes)
  if (typeof duration === 'number') {
    return duration >= 1 ? `${duration}h` : `${Math.round(duration * 60)}m`
  }
  return duration
})

const assignedRowTitle = computed(() => {
  // This would need to be passed from parent or fetched
  return props.block.assigned_row_title || null
})

const customFields = computed(() => {
  const fields = []
  
  // Add any additional fields that aren't covered by the main fields
  Object.keys(props.block).forEach(key => {
    if (!['name', 'id', 'creation', 'modified', 'row_id'].includes(key) &&
        key !== props.config?.block_title_field &&
        key !== props.config?.block_description_field &&
        key !== props.config?.block_status_field &&
        key !== props.config?.block_priority_field &&
        key !== props.config?.block_progress_field &&
        key !== props.config?.block_duration_field &&
        key !== props.config?.block_date_field) {
      
      const value = props.block[key]
      if (value !== null && value !== undefined && value !== '') {
        fields.push({
          key,
          label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          value: typeof value === 'object' ? JSON.stringify(value) : String(value)
        })
      }
    }
  })
  
  return fields
})

// Styling computed properties
const statusColor = computed(() => {
  const status = blockStatus.value.toLowerCase()
  
  switch (status) {
    case 'completed':
    case 'done':
      return 'bg-green-500'
    case 'in_progress':
    case 'working':
      return 'bg-blue-500'
    case 'pending':
    case 'waiting':
      return 'bg-amber-500'
    case 'cancelled':
    case 'rejected':
      return 'bg-red-500'
    case 'draft':
      return 'bg-gray-400'
    default:
      return 'bg-gray-300'
  }
})

const priorityIcon = computed(() => {
  const priority = blockPriority.value?.toLowerCase()
  
  switch (priority) {
    case 'high':
    case 'urgent':
      return 'alert-triangle'
    case 'medium':
      return 'minus'
    case 'low':
      return 'arrow-down'
    default:
      return 'circle'
  }
})

const priorityColor = computed(() => {
  const priority = blockPriority.value?.toLowerCase()
  
  switch (priority) {
    case 'high':
    case 'urgent':
      return 'text-red-500'
    case 'medium':
      return 'text-amber-500'
    case 'low':
      return 'text-green-500'
    default:
      return 'text-gray-400'
  }
})

const priorityBadgeClass = computed(() => {
  const priority = blockPriority.value?.toLowerCase()
  
  switch (priority) {
    case 'high':
    case 'urgent':
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    case 'medium':
      return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300'
    case 'low':
      return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  }
})

const progressColor = computed(() => {
  const progress = blockProgress.value
  if (progress === null) return 'bg-gray-300'
  
  if (progress >= 80) return 'bg-green-500'
  if (progress >= 50) return 'bg-blue-500'
  if (progress >= 25) return 'bg-amber-500'
  return 'bg-red-500'
})

// Methods
const formatBlockDate = () => {
  const dateField = props.config?.block_date_field || 'date'
  const date = props.block[dateField]
  
  if (!date) return 'No date set'
  
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const editBlock = () => {
  // TODO: Implement edit functionality
  console.log('Edit block:', props.block)
  emit('update', { action: 'edit', block: props.block })
}

const viewInSystem = () => {
  // Open the block in Frappe's form view
  const url = `/app/${props.config.block_doctype.toLowerCase().replace(' ', '-')}/${props.block.name}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.dynamic-block-details {
  @apply max-w-full;
}

.detail-item {
  @apply space-y-1;
}

.detail-section {
  @apply border-b border-gray-100 dark:border-gray-700 pb-6 last:border-b-0 last:pb-0;
}

/* Smooth transitions */
* {
  transition: all 0.15s ease;
}
</style>