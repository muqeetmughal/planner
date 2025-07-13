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
                  <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                    {{ getRowInitials(row) }}
                  </div>
                  
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
                  v-for="(row, colIndex) in filteredRows"
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
import { Button, FeatherIcon } from "frappe-ui";
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
    const startDate = parseDateTime(block.start_date || block[props.config?.block_to_date_field] || block.date);
    const endDate = parseDateTime(block.end_date || block[props.config?.date_range_end_field]);
    
    if (!startDate) return false;
    
    // Check if block overlaps with the current day
    if (endDate) {
      return startDate <= dayEnd && endDate >= dayStart;
    } else {
      // Single datetime block
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

// Helper functions
const parseDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return null;
  
  // Handle different datetime formats
  let dateObj;
  if (typeof dateTimeStr === 'string') {
    if (dateTimeStr.includes(' ')) {
      // "2025-07-09 14:30:00" format
      dateObj = new Date(dateTimeStr.replace(' ', 'T'));
    } else if (dateTimeStr.includes('T')) {
      // ISO format
      dateObj = new Date(dateTimeStr);
    } else {
      // Date only - assume start of day
      dateObj = new Date(dateTimeStr + 'T00:00:00');
    }
  } else if (dateTimeStr instanceof Date) {
    dateObj = dateTimeStr;
  } else {
    return null;
  }
  
  return isNaN(dateObj.getTime()) ? null : dateObj;
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

const getRowInitials = (row) => {
  const title = getRowTitle(row);
  return title
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
};

const getRowBlockCount = (rowId) => {
  return visibleBlocks.value.filter((block) => block.row_id === rowId).length;
};

const getBlocksForResource = (rowId) => {
  return visibleBlocks.value.filter((block) => block.row_id === rowId);
};

const getBlockStyle = (block) => {
  const startDateTime = parseDateTime(block.start_date || block[props.config?.block_to_date_field] || block.date);
  const endDateTime = parseDateTime(block.end_date || block[props.config?.date_range_end_field]);
  
  if (!startDateTime) return {};
  
  const hourHeight = getHourHeight();
  
  // Calculate start position
  const startHours = startDateTime.getHours() + (startDateTime.getMinutes() / 60);
  const top = Math.max(0, (startHours - startHour.value) * hourHeight);
  
  // Calculate height
  let height = hourHeight; // Default 1 hour
  if (endDateTime && endDateTime > startDateTime) {
    const durationHours = (endDateTime - startDateTime) / (1000 * 60 * 60);
    height = Math.max(20, durationHours * hourHeight); // Minimum 20px height
  }
  
  return {
    top: `${top}px`,
    height: `${height}px`,
    left: '4px',
    right: '4px',
    width: 'calc(100% - 8px)',
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