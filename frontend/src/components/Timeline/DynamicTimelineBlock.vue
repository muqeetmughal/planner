<template>
  <div
    :class="[
      'timeline-block relative rounded-lg shadow-sm border cursor-pointer transition-all duration-200 group',
      blockClasses,
      {
        'hover:shadow-md hover:scale-105 hover:z-10': !unassigned,
        'opacity-75': unassigned
      }
    ]"
    :draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @click="$emit('click')"
    :title="blockTooltip"
  >
    <!-- Block Content -->
    <div class="p-2">
      <!-- Block Header -->
      <div class="flex items-center justify-between mb-1">
        <div class="flex items-center gap-1">
          <!-- Status Indicator -->
          <div 
            :class="[
              'w-2 h-2 rounded-full',
              statusColor
            ]"
          ></div>
          
          <!-- Block ID/Name -->
          <span class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">
            {{ blockTitle }}
          </span>
        </div>
        
        <!-- Priority/Urgency Indicator -->
        <div v-if="blockPriority" class="flex items-center">
          <FeatherIcon 
            :name="priorityIcon" 
            :class="[
              'w-3 h-3',
              priorityColor
            ]"
          />
        </div>
      </div>
      
      <!-- Block Description -->
      <div v-if="blockDescription" class="text-xs text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
        {{ blockDescription }}
      </div>
      
      <!-- Block Metadata -->
      <div class="flex items-center justify-between text-xs">
        <!-- Duration/Time -->
        <div v-if="blockDuration" class="flex items-center gap-1 text-gray-500 dark:text-gray-400">
          <FeatherIcon name="clock" class="w-3 h-3" />
          <span>{{ blockDuration }}</span>
        </div>
        
        <!-- Progress -->
        <div v-if="blockProgress !== null" class="flex items-center gap-1">
          <div class="w-8 h-1 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
            <div 
              :class="[
                'h-full transition-all duration-300',
                progressColor
              ]"
              :style="{ width: `${blockProgress}%` }"
            ></div>
          </div>
          <span class="text-gray-500 dark:text-gray-400 text-xs">{{ blockProgress }}%</span>
        </div>
      </div>
    </div>
    
    <!-- Drag Handle -->
    <div class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
      <FeatherIcon name="move" class="w-3 h-3 text-gray-400" />
    </div>
    
    <!-- Unassigned Badge -->
    <div v-if="unassigned" class="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full border-2 border-white dark:border-gray-800"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  block: {
    type: Object,
    required: true
  },
  config: {
    type: Object,
    required: true
  },
  unassigned: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click', 'dragstart', 'dragend'])

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

// Styling computed properties
const blockClasses = computed(() => {
  const status = blockStatus.value.toLowerCase()
  const baseClasses = 'min-h-[60px] max-w-full'
  
  switch (status) {
    case 'completed':
    case 'done':
      return `${baseClasses} bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700 text-green-900 dark:text-green-100`
    case 'in_progress':
    case 'working':
      return `${baseClasses} bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 text-blue-900 dark:text-blue-100`
    case 'pending':
    case 'waiting':
      return `${baseClasses} bg-amber-100 dark:bg-amber-900/30 border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-100`
    case 'cancelled':
    case 'rejected':
      return `${baseClasses} bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-700 text-red-900 dark:text-red-100`
    case 'draft':
      return `${baseClasses} bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100`
    default:
      return `${baseClasses} bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-600 text-gray-900 dark:text-white`
  }
})

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

const progressColor = computed(() => {
  const progress = blockProgress.value
  if (progress === null) return 'bg-gray-300'
  
  if (progress >= 80) return 'bg-green-500'
  if (progress >= 50) return 'bg-blue-500'
  if (progress >= 25) return 'bg-amber-500'
  return 'bg-red-500'
})

const blockTooltip = computed(() => {
  const parts = []
  
  parts.push(blockTitle.value)
  
  if (blockDescription.value) {
    parts.push(blockDescription.value)
  }
  
  if (blockStatus.value) {
    parts.push(`Status: ${blockStatus.value}`)
  }
  
  if (blockPriority.value) {
    parts.push(`Priority: ${blockPriority.value}`)
  }
  
  if (blockProgress.value !== null) {
    parts.push(`Progress: ${blockProgress.value}%`)
  }
  
  if (blockDuration.value) {
    parts.push(`Duration: ${blockDuration.value}`)
  }
  
  return parts.join('\n')
})

// Methods
const handleDragStart = (event) => {
  emit('dragstart', event, props.block)
}

const handleDragEnd = (event) => {
  emit('dragend', event, props.block)
}
</script>

<style scoped>
.timeline-block {
  min-width: 100px;
  max-width: 200px;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Drag feedback */
.timeline-block:active {
  transform: rotate(2deg);
}

/* Hover effects */
.timeline-block:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Focus styles for accessibility */
.timeline-block:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>