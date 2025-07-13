<template>
  <div class="dynamic-timeline-day-view flex flex-col h-full bg-white dark:bg-gray-900">
    <!-- Day View Header -->
    <div class="day-view-header sticky top-0 z-20 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-4">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white">
              {{ formatDayTitle() }}
            </h2>
            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <span>{{ visibleBlocks.length }} blocks scheduled</span>
              <div class="w-1 h-1 bg-gray-400 rounded-full"></div>
              <span>{{ filteredRows.length }} resources</span>
            </div>
          </div>
          
          <div class="flex items-center gap-3">
            <!-- Time Range Display -->
            <div class="px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-sm font-medium text-blue-700 dark:text-blue-300">
              {{ startHour }}:00 - {{ endHour }}:00
            </div>
            
            <!-- View Controls -->
            <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                v-for="granularity in timeGranularities"
                :key="granularity.value"
                @click="timeGranularity = granularity.value"
                :class="[
                  'px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200',
                  timeGranularity === granularity.value
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white',
                ]"
              >
                {{ granularity.label }}
              </button>
            </div>
            
            <!-- Today Button -->
            <Button
              variant="ghost"
              theme="blue"
              size="sm"
              @click="goToToday"
            >
              <FeatherIcon name="calendar" class="w-4 h-4 mr-1" />
              Today
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Day View Grid -->
    <div class="day-view-content flex-1 overflow-hidden">
      <div class="h-full flex">
        <!-- Time Column (Fixed) -->
        <div class="time-column w-20 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0 overflow-hidden">
          <!-- Header Spacer -->
          <div class="h-16 border-b border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
            <FeatherIcon name="clock" class="w-4 h-4 text-gray-500" />
          </div>
          
          <!-- Time Slots Container -->
          <div class="time-slots-container overflow-y-auto h-[calc(100%-4rem)]">
            <div
              v-for="hour in timeSlots"
              :key="hour"
              :class="[
                'time-slot flex items-start justify-end pr-3 py-2 border-b border-gray-200 dark:border-gray-700',
                getSlotHeight()
              ]"
            >
              <span class="text-xs font-medium text-gray-600 dark:text-gray-400">
                {{ formatHour(hour) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Resources Grid (Scrollable) -->
        <div class="resources-grid flex-1 overflow-hidden flex flex-col">
          <!-- Resources Header (Fixed) -->
          <div class="resources-header h-16 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex-shrink-0 overflow-x-auto">
            <div class="flex min-w-max">
              <div
                v-for="(row, index) in filteredRows"
                :key="row.id"
                :class="[
                  'resource-header-cell w-[200px] flex-shrink-0 p-3 border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900',
                  { 'border-l': index === 0 }
                ]"
              >
                <div class="flex items-center gap-3">
                  <!-- Resource Avatar -->
                  <Avatar
                    :label="getRowTitle(row)"
                    :image="row.image"
                    size="lg"
                  />
                  
                  <!-- Resource Info -->
                  <div class="flex-1 min-w-0">
                    <div class="font-semibold text-sm text-gray-900 dark:text-white truncate">
                      {{ getRowTitle(row) }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {{ getRowBlockCount(row.id) }} blocks
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Time Grid (Scrollable) -->
          <div class="time-grid-container flex-1 overflow-auto">
            <div class="time-grid relative min-w-max" :style="{ height: getTotalGridHeight() + 'px', width: (filteredRows.length * 200) + 'px' }">
              <!-- Background Grid Lines -->
              <div class="grid-lines absolute inset-0 pointer-events-none">
                <!-- Horizontal Lines -->
                <div
                  v-for="hour in timeSlots"
                  :key="`line-${hour}`"
                  class="absolute left-0 right-0 border-t border-gray-100 dark:border-gray-800"
                  :style="{ top: getTimePosition(hour) + 'px' }"
                ></div>
                
                <!-- Vertical Lines -->
                <div
                  v-for="(row, index) in filteredRows"
                  :key="`vline-${row.id}`"
                  :class="[
                    'absolute top-0 bottom-0 border-l border-gray-200 dark:border-gray-700',
                    { 'border-r': index === filteredRows.length - 1 }
                  ]"
                  :style="{ left: (index * 200) + 'px', width: '200px' }"
                ></div>
              </div>

              <!-- Current Time Indicator -->
              <div
                v-if="isToday"
                class="current-time-line absolute left-0 right-0 z-10 pointer-events-none"
                :style="{ top: getCurrentTimePosition() + 'px' }"
              >
                <div class="h-0.5 bg-red-500 shadow-lg">
                  <div class="absolute -left-2 -top-1 w-4 h-3 bg-red-500 rounded-sm"></div>
                </div>
              </div>

              <!-- Resource Columns -->
              <div class="resource-columns flex">
                <div
                  v-for="row in filteredRows"
                  :key="row.id"
                  class="resource-column relative flex-shrink-0 border-r border-gray-200 dark:border-gray-700"
                  :style="{ width: '200px', height: getTotalGridHeight() + 'px' }"
                  @drop="handleDrop($event, row.id)"
                  @dragover.prevent="handleDragOver($event, row.id)"
                  @dragenter.prevent
                  @dragleave="handleDragLeave($event)"
                >
                  <!-- Drop Zone Overlay -->
                  <div
                    v-if="dragOverResource === row.id"
                    class="absolute inset-0 bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-blue-500 flex items-center justify-center z-20"
                  >
                    <div class="bg-blue-500 text-white px-3 py-1.5 rounded-full text-sm font-medium shadow-lg flex items-center gap-2">
                      <FeatherIcon name="arrow-down" class="w-4 h-4" />
                      Drop here
                    </div>
                  </div>

                  <!-- Time Blocks -->
                  <DynamicTimelineBlock
                    v-for="block in getBlocksForResource(row.id)"
                    :key="block.id"
                    :block="block"
                    :config="config"
                    :selected="selectedBlock?.id === block.id"
                    :dayView="true"
                    :style="getBlockStyle(block)"
                    class="absolute z-10"
                    @click="handleBlockClick"
                    @dragstart="handleBlockDragStart"
                    @dragend="handleBlockDragEnd"
                    @resize="handleBlockResize"
                    @contextmenu="handleBlockContextMenu"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { Button, FeatherIcon, Avatar } from "frappe-ui";
import DynamicTimelineBlock from "./DynamicTimelineBlock.vue";

const props = defineProps({
  config: {
    type: Object,
    required: true,
  },
  rows: {
    type: Array,
    default: () => [],
  },
  blocks: {
    type: Array,
    default: () => [],
  },
  currentDate: {
    type: Date,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "blockMove",
  "blockClick", 
  "addBlock",
  "blockResize",
  "dateNavigate",
  "goToToday",
]);

// Reactive state
const timeGranularity = ref(60); // minutes: 15, 30, 60
const startHour = ref(8); // 8 AM
const endHour = ref(18); // 6 PM
const selectedBlock = ref(null);
const draggedBlock = ref(null);
const dragOverResource = ref(null);

// Time granularity options
const timeGranularities = [
  { label: "15min", value: 15 },
  { label: "30min", value: 30 },
  { label: "1hour", value: 60 },
];

// Computed properties
const filteredRows = computed(() => {
  return Array.isArray(props.rows) ? props.rows : [];
});

const visibleBlocks = computed(() => {
  if (!Array.isArray(props.blocks)) return [];
  
  const dayStart = new Date(props.currentDate);
  dayStart.setHours(0, 0, 0, 0);
  
  const dayEnd = new Date(props.currentDate);
  dayEnd.setHours(23, 59, 59, 999);
  
  return props.blocks.filter(block => {
    // Use improved datetime field detection
    const startField = props.config?.block_to_date_field || 'start_date';
    const endField = props.config?.date_range_end_field || 'end_date';
    
    const startDate = parseDateTime(
      getDateTimeFieldValue(block, startField) || 
      block.start_date || 
      block.date
    );
    
    const endDate = parseDateTime(
      getDateTimeFieldValue(block, endField) || 
      block.end_date
    );
    
    if (!startDate) {
      console.warn('Block missing start date:', block);
      return false;
    }
    
    // Check if block overlaps with the current day
    if (endDate && endDate > startDate) {
      // Multi-day or timed event
      return startDate <= dayEnd && endDate >= dayStart;
    } else {
      // Single datetime block - check if it falls within the day
      return startDate >= dayStart && startDate <= dayEnd;
    }
  });
});

const timeSlots = computed(() => {
  const slots = [];
  for (let hour = startHour.value; hour <= endHour.value; hour++) {
    slots.push(hour);
  }
  return slots;
});

const isToday = computed(() => {
  const today = new Date();
  return props.currentDate.toDateString() === today.toDateString();
});

// Enhanced datetime parsing function with proper format detection
const parseDateTime = (dateTimeInput, preserveTime = true) => {
  if (!dateTimeInput) return null;
  
  let dateObj;
  
  if (typeof dateTimeInput === 'string') {
    const trimmed = dateTimeInput.trim();
    
    // Handle datetime with space separator
    if (trimmed.includes(' ') && !trimmed.includes('T')) {
      const [datePart, timePart] = trimmed.split(' ');
      
      // Detect date format and convert to ISO
      let isoDatePart;
      
      // Check if it's DD-MM-YYYY or DD/MM/YYYY format
      if (datePart.includes('-') && datePart.split('-').length === 3) {
        const parts = datePart.split('-');
        if (parts[0].length <= 2 && parts[2].length === 4) {
          // DD-MM-YYYY format - convert to YYYY-MM-DD
          const [day, month, year] = parts;
          isoDatePart = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        } else {
          // Assume YYYY-MM-DD format
          isoDatePart = datePart;
        }
      } else if (datePart.includes('/') && datePart.split('/').length === 3) {
        const parts = datePart.split('/');
        if (parts[0].length <= 2 && parts[2].length === 4) {
          // DD/MM/YYYY format - convert to YYYY-MM-DD
          const [day, month, year] = parts;
          isoDatePart = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        } else {
          // Assume MM/DD/YYYY format - convert to YYYY-MM-DD
          const [month, day, year] = parts;
          isoDatePart = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
      } else {
        isoDatePart = datePart;
      }
      
      // Create ISO datetime string
      const isoString = preserveTime ? `${isoDatePart}T${timePart}` : `${isoDatePart}T00:00:00`;
      dateObj = new Date(isoString);
    }
    // Handle ISO format: "2025-07-09T14:30:00"
    else if (trimmed.includes('T')) {
      if (preserveTime) {
        dateObj = new Date(trimmed);
      } else {
        const datePart = trimmed.split('T')[0];
        dateObj = new Date(datePart + 'T00:00:00');
      }
    }
    // Handle date-only formats
    else {
      let isoDatePart;
      
      // Check for DD-MM-YYYY format
      if (trimmed.includes('-') && trimmed.split('-').length === 3) {
        const parts = trimmed.split('-');
        if (parts[0].length <= 2 && parts[2].length === 4) {
          // DD-MM-YYYY format - convert to YYYY-MM-DD
          const [day, month, year] = parts;
          isoDatePart = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        } else {
          // Assume YYYY-MM-DD format
          isoDatePart = trimmed;
        }
      } else {
        isoDatePart = trimmed;
      }
      
      dateObj = new Date(isoDatePart + 'T00:00:00');
    }
  } 
  else if (dateTimeInput instanceof Date) {
    dateObj = new Date(dateTimeInput);
    if (!preserveTime) {
      dateObj.setHours(0, 0, 0, 0);
    }
  } 
  else {
    return null;
  }
  
  // Validate the parsed date
  if (isNaN(dateObj.getTime())) {
    console.warn('Invalid date parsed:', dateTimeInput, '- trying manual parsing');
    
    // Fallback: try manual parsing for DD-MM-YYYY HH:mm:ss format
    if (typeof dateTimeInput === 'string' && dateTimeInput.includes(' ')) {
      try {
        const [datePart, timePart] = dateTimeInput.split(' ');
        const [day, month, year] = datePart.split(/[-\/]/).map(Number);
        const [hours, minutes, seconds] = timePart.split(':').map(Number);
        
        // Create date with explicit components (month is 0-indexed)
        dateObj = new Date(year, month - 1, day, hours || 0, minutes || 0, seconds || 0);
        
        if (!isNaN(dateObj.getTime())) {
          return dateObj;
        }
      } catch (e) {
        console.warn('Manual parsing also failed:', e.message);
      }
    }
    
    return null;
  }
  
  return dateObj;
};

// Helper function for improved datetime field detection
const getDateTimeFieldValue = (block, fieldName) => {
  if (!block || !fieldName) return null;
  
  // Try the configured field name first
  if (block[fieldName]) return block[fieldName];
  
  // Fall back to common field names
  const commonFields = ['date', 'start_date', 'end_date', 'datetime', 'scheduled_date'];
  for (const field of commonFields) {
    if (block[field]) return block[field];
  }
  
  return null;
};

const formatDayTitle = () => {
  return props.currentDate.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric", 
    month: "long",
    day: "numeric",
  });
};

const formatHour = (hour) => {
  const period = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${displayHour} ${period}`;
};

const getTimePosition = (hour) => {
  const hourHeight = getHourHeight();
  return (hour - startHour.value) * hourHeight;
};

const getCurrentTimePosition = () => {
  if (!isToday.value) return 0;
  
  const now = new Date();
  const currentHour = now.getHours();
  const currentMinutes = now.getMinutes();
  
  if (currentHour < startHour.value || currentHour > endHour.value) return 0;
  
  const hourHeight = getHourHeight();
  const position = (currentHour - startHour.value) * hourHeight + (currentMinutes / 60) * hourHeight;
  
  return position;
};

const getHourHeight = () => {
  return timeGranularity.value === 15 ? 64 : timeGranularity.value === 30 ? 48 : 80;
};

const getSlotHeight = () => {
  return timeGranularity.value === 15 ? 'h-16' : timeGranularity.value === 30 ? 'h-12' : 'h-20';
};

const getTotalGridHeight = () => {
  return timeSlots.value.length * getHourHeight();
};

const getRowTitle = (row) => {
  return row.label || row.name || row.id;
};


const getRowBlockCount = (rowId) => {
  return visibleBlocks.value.filter((block) => block.row_id === rowId).length;
};

const getBlocksForResource = (rowId) => {
  return visibleBlocks.value.filter((block) => block.row_id === rowId);
};

const getBlockStyle = (block) => {
  // Use improved datetime field detection
  const startField = props.config?.block_to_date_field || 'start_date';
  const endField = props.config?.date_range_end_field || 'end_date';
  
  const startDateTime = parseDateTime(
    getDateTimeFieldValue(block, startField) || 
    block.start_date || 
    block.date
  );
  
  const endDateTime = parseDateTime(
    getDateTimeFieldValue(block, endField) || 
    block.end_date
  );
  
  if (!startDateTime) {
    console.warn('Cannot calculate block style without start time:', block);
    return { display: 'none' };
  }
  
  const hourHeight = getHourHeight();
  
  // Calculate start position with bounds checking
  const startHours = startDateTime.getHours() + (startDateTime.getMinutes() / 60);
  const top = Math.max(0, (startHours - startHour.value) * hourHeight);
  
  // Calculate height with smart defaults
  let height = hourHeight * 0.8; // Default to 80% of hour height for better spacing
  
  if (endDateTime && endDateTime > startDateTime) {
    const durationMs = endDateTime - startDateTime;
    const durationHours = durationMs / (1000 * 60 * 60);
    
    // Ensure minimum height for readability
    height = Math.max(24, durationHours * hourHeight);
    
    // Cap maximum height to prevent blocks from extending beyond visible area
    const maxHeight = (endHour.value - startHour.value + 1) * hourHeight - top;
    height = Math.min(height, maxHeight);
  } else {
    // For blocks without end time, use a reasonable default
    const blockDuration = block.duration || 1; // Default 1 hour
    height = Math.max(24, blockDuration * hourHeight * 0.8);
  }
  
  return {
    top: `${top}px`,
    height: `${height}px`,
    left: '4px',
    right: '4px',
    width: 'calc(100% - 8px)',
    minHeight: '24px', // Ensure blocks are always visible
  };
};

// Event handlers
const goToToday = () => {
  emit("goToToday");
};

const handleBlockClick = (block, event) => {
  selectedBlock.value = selectedBlock.value?.id === block.id ? null : block;
  emit("blockClick", block, event);
};

const handleBlockDragStart = (block) => {
  draggedBlock.value = block;
};

const handleBlockDragEnd = () => {
  draggedBlock.value = null;
  dragOverResource.value = null;
};

const handleDragOver = (event, rowId) => {
  event.preventDefault();
  dragOverResource.value = rowId;
};

const handleDragLeave = (event) => {
  // Only clear if leaving the resource column entirely
  if (!event.currentTarget.contains(event.relatedTarget)) {
    dragOverResource.value = null;
  }
};

const handleDrop = (event, rowId) => {
  event.preventDefault();
  dragOverResource.value = null;
  
  if (!draggedBlock.value) return;
  
  // Calculate the time based on drop position
  const rect = event.currentTarget.getBoundingClientRect();
  const y = event.clientY - rect.top;
  const hourHeight = getHourHeight();
  const droppedHour = Math.floor(y / hourHeight) + startHour.value;
  const droppedMinutes = Math.floor(((y % hourHeight) / hourHeight) * 60);
  
  // Create new datetime for the dropped position
  const newDateTime = new Date(props.currentDate);
  newDateTime.setHours(droppedHour, droppedMinutes, 0, 0);
  
  // Emit the move event with the new datetime
  emit("blockMove", {
    blockId: draggedBlock.value.id,
    newRowId: rowId,
    newDateTime: newDateTime.toISOString(),
    originalBlock: draggedBlock.value
  });
  
  draggedBlock.value = null;
};

const handleBlockResize = (resizeData) => {
  emit("blockResize", resizeData);
};

const handleBlockContextMenu = (block, event) => {
  // Handle right-click context menu
  event.preventDefault();
};
</script>

<style scoped>
.dynamic-timeline-day-view {
  min-height: 600px;
}

.time-column {
  min-width: 80px;
}

.resource-column {
  transition: background-color 0.2s ease;
}

.resource-column:hover {
  background-color: rgb(249 250 251);
}

.dark .resource-column:hover {
  background-color: rgb(31 41 55);
}

.current-time-line {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Improved scrolling */
.time-slots-container {
  scrollbar-width: thin;
  scrollbar-color: rgb(156 163 175) rgb(243 244 246);
}

.time-grid-container {
  scrollbar-width: thin;
  scrollbar-color: rgb(156 163 175) rgb(243 244 246);
}

/* Grid styling */
.grid-lines {
  background-image: 
    linear-gradient(to right, rgb(229 231 235) 1px, transparent 1px),
    linear-gradient(to bottom, rgb(229 231 235) 1px, transparent 1px);
  background-size: 200px 80px;
}

.dark .grid-lines {
  background-image: 
    linear-gradient(to right, rgb(75 85 99) 1px, transparent 1px),
    linear-gradient(to bottom, rgb(75 85 99) 1px, transparent 1px);
}

/* Scrollbar styling */
.time-grid-container::-webkit-scrollbar,
.time-slots-container::-webkit-scrollbar,
.resources-header::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.time-grid-container::-webkit-scrollbar-track,
.time-slots-container::-webkit-scrollbar-track,
.resources-header::-webkit-scrollbar-track {
  background: rgb(243 244 246);
  border-radius: 4px;
}

.time-grid-container::-webkit-scrollbar-thumb,
.time-slots-container::-webkit-scrollbar-thumb,
.resources-header::-webkit-scrollbar-thumb {
  background: rgb(156 163 175);
  border-radius: 4px;
}

.time-grid-container::-webkit-scrollbar-thumb:hover,
.time-slots-container::-webkit-scrollbar-thumb:hover,
.resources-header::-webkit-scrollbar-thumb:hover {
  background: rgb(107 114 128);
}

.dark .time-grid-container::-webkit-scrollbar-track,
.dark .time-slots-container::-webkit-scrollbar-track,
.dark .resources-header::-webkit-scrollbar-track {
  background: rgb(31 41 55);
}

.dark .time-grid-container::-webkit-scrollbar-thumb,
.dark .time-slots-container::-webkit-scrollbar-thumb,
.dark .resources-header::-webkit-scrollbar-thumb {
  background: rgb(75 85 99);
}

.dark .time-grid-container::-webkit-scrollbar-thumb:hover,
.dark .time-slots-container::-webkit-scrollbar-thumb:hover,
.dark .resources-header::-webkit-scrollbar-thumb:hover {
  background: rgb(107 114 128);
}
</style>