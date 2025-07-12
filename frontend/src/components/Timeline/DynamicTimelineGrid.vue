<template>
  <div
    class="dynamic-timeline-grid rounded-lg border overflow-auto max-h-[45rem]"
    :class="loading && 'animate-pulse pointer-events-none'"
  >
    <!-- Enhanced Header with Search and Filters -->
    <div
      class="grid-header bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30"
    >
      <div class="p-3">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <!-- Row Search -->
            <div class="relative">
              <FeatherIcon
                name="search"
                class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4"
              />
              <input
                v-model="rowSearch"
                type="text"
                placeholder="Search resources..."
                class="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>

            <!-- View Mode Toggle -->
            <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                v-for="mode in viewModes"
                :key="mode.value"
                @click="currentViewMode = mode.value"
                :class="[
                  'px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 flex items-center',
                  currentViewMode === mode.value
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white',
                ]"
              >
                <FeatherIcon :name="mode.icon" class="w-4 h-4 mr-1" />
                {{ mode.label }}
              </button>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Legend -->
            <div
              class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400 mr-2"
            >
              <div class="flex items-center gap-1.5">
                <div class="w-3 h-3 bg-blue-500 rounded shadow-sm"></div>
                <span>Active</span>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="w-3 h-3 bg-amber-500 rounded shadow-sm"></div>
                <span>Pending</span>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="w-3 h-3 bg-green-500 rounded shadow-sm"></div>
                <span>Completed</span>
              </div>
            </div>

            <!-- Auto-refresh toggle -->
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="toggleAutoRefresh"
              :class="autoRefresh ? 'text-blue-600' : ''"
            >
              <FeatherIcon
                name="refresh-cw"
                :class="['w-4 h-4', autoRefresh ? 'animate-spin' : '']"
              />
            </Button>
          </div>
        </div>

        <!-- Timeline Navigation -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="navigateDate(-1)"
            >
              <FeatherIcon name="chevron-left" class="w-4 h-4" />
            </Button>
            <div
              class="px-3 py-1.5 bg-gray-50 dark:bg-gray-800 rounded-lg font-medium text-sm"
            >
              {{ formatDateRange() }}
            </div>
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="navigateDate(1)"
            >
              <FeatherIcon name="chevron-right" class="w-4 h-4" />
            </Button>
            <Button variant="ghost" theme="blue" size="sm" @click="goToToday">
              Today
            </Button>
          </div>

          <div class="text-sm text-gray-500 dark:text-gray-400">
            {{ filteredRows.length }} rows • {{ visibleBlocks.length }} blocks
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Table Structure -->
    <table class="border-separate border-spacing-0 w-full">
      <thead>
        <tr class="sticky top-0 bg-white dark:bg-gray-900 z-20">
          <!-- Resource Header -->
          <th class="resource-header-cell p-3 border-b border-gray-200 dark:border-gray-700 text-left bg-gray-50 dark:bg-gray-800">
            <div class="font-semibold text-sm text-gray-900 dark:text-white">
              {{ config?.row_doctype || "Resources" }}
            </div>
          </th>

          <!-- Date Header Columns -->
          <th
            v-for="(column, idx) in visibleDateColumns"
            :key="column.key"
            :class="[
              'date-header-cell font-medium border-b border-gray-200 dark:border-gray-700 text-center',
              { 'border-l border-gray-200 dark:border-gray-700': idx > 0 },
              column.isToday ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-gray-50 dark:bg-gray-800',
              column.isWeekend ? 'bg-amber-50 dark:bg-amber-900/20' : ''
            ]"
          >
            <div class="p-2">
              <div class="font-semibold text-sm text-gray-900 dark:text-white">
                {{ column.label }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ column.sublabel }}
              </div>
              <div
                v-if="column.isToday"
                class="w-2 h-2 bg-blue-500 rounded-full mx-auto mt-1"
              ></div>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="(row, rowIdx) in filteredRows" 
          :key="row.id"
          :class="[
            'hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group',
            selectedRow === row.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''
          ]"
        >
          <!-- Resource Column -->
          <td
            :class="[
              'resource-cell px-3 py-4 z-[5] cursor-pointer',
              { 'border-t border-gray-200 dark:border-gray-700': rowIdx > 0 }
            ]"
            @click="selectRow(row.id)"
          >
            <div class="flex items-center gap-3">
              <!-- Enhanced Avatar with better design -->
              <div class="relative">
                <div
                  class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-sm font-bold shadow-lg group-hover:shadow-xl transition-shadow duration-200"
                >
                  {{ getRowInitials(row) }}
                </div>
                <!-- Status indicator -->
                <div 
                  v-if="getRowBlockCount(row.id) > 0"
                  class="absolute -top-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full flex items-center justify-center"
                >
                  <div class="w-1.5 h-1.5 bg-white rounded-full"></div>
                </div>
              </div>

              <!-- Enhanced Row Info -->
              <div class="flex-1 min-w-0">
                <div class="font-semibold text-base text-gray-900 dark:text-white truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {{ getRowTitle(row) }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400 truncate mt-0.5">
                  {{ getRowSubtitle(row) }}
                </div>
                <div class="flex items-center gap-2 mt-2">
                  <div
                    class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded-full font-medium"
                  >
                    {{ getRowBlockCount(row.id) }} items
                  </div>
                  <div
                    v-if="getRowWorkload(row.id) > 0"
                    :class="[
                      'text-xs px-2 py-1 rounded-full font-medium',
                      getRowWorkload(row.id) > 80 
                        ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400' 
                        : getRowWorkload(row.id) > 60 
                        ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400' 
                        : 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400'
                    ]"
                  >
                    {{ getRowWorkload(row.id) }}% capacity
                  </div>
                </div>
              </div>
            </div>
          </td>

          <!-- Timeline Cells -->
          <td
            v-for="(column, colIdx) in visibleDateColumns"
            :key="`${row.id}-${column.key}`"
            :class="[
              'timeline-cell p-1.5 relative align-top',
              { 'border-l border-gray-200 dark:border-gray-700': colIdx > 0 },
              { 'border-t border-gray-200 dark:border-gray-700': rowIdx > 0 },
              'hover:bg-gray-50 dark:hover:bg-gray-800 transition-all duration-200',
              column.isToday ? 'bg-blue-50/30 dark:bg-blue-900/10' : '',
              column.isWeekend ? 'bg-amber-50/30 dark:bg-amber-900/10' : '',
              dragOverCell === `${row.id}-${column.key}` 
                ? 'bg-green-100 dark:bg-green-900/20 ring-2 ring-green-500/50 ring-inset shadow-lg transform scale-105' 
                : '',
              hoveredCell.row === row.id && hoveredCell.date === column.key 
                ? 'bg-gray-100 dark:bg-gray-800/50' 
                : ''
            ]"
            @mouseenter="handleCellHover(row.id, column.key, true)"
            @mouseleave="handleCellHover(row.id, column.key, false)"
            @drop="handleDrop($event, row.id, column.key)"
            @dragover.prevent="handleDragOver($event, row.id, column.key)"
            @dragenter.prevent="handleDragEnter($event, row.id, column.key)"
            @dragleave="handleDragLeave($event)"
            @click="handleCellClick(row.id, column.key)"
          >
            <!-- Today Indicator -->
            <div
              v-if="column.isToday"
              class="absolute top-0 left-0 right-0 h-0.5 bg-blue-500 shadow-sm z-10"
            ></div>

            <!-- Enhanced Drop Zone with better visual feedback -->
            <div
              v-if="dragOverCell === `${row.id}-${column.key}`"
              class="absolute inset-0 border-2 border-dashed border-green-500 bg-green-50/80 dark:bg-green-900/30 flex items-center justify-center animate-pulse z-20 rounded"
            >
              <div
                class="bg-green-500 text-white px-3 py-1.5 rounded-full text-sm font-medium shadow-lg flex items-center gap-2"
              >
                <FeatherIcon name="arrow-down" class="w-4 h-4" />
                Drop here
              </div>
            </div>

            <!-- Blocks Container with improved spacing -->
            <div class="blocks-container min-h-[80px] space-y-1.5">
              <TransitionGroup name="block" tag="div" class="space-y-1.5">
                <DynamicTimelineBlock
                  v-for="block in getBlocksForCell(row.id, column.key)"
                  :key="block.id"
                  :block="block"
                  :config="config"
                  :selected="selectedBlock?.id === block.id"
                  :resizable="hasDateRange"
                  @click="handleBlockClick"
                  @dragstart="handleBlockDragStart"
                  @dragend="handleBlockDragEnd"
                  @resize="handleBlockResize"
                  @contextmenu="handleBlockContextMenu"
                />
              </TransitionGroup>

              <!-- Enhanced Add Block Button -->
              <Button
                v-if="hoveredCell.row === row.id && hoveredCell.date === column.key && getBlocksForCell(row.id, column.key).length === 0"
                variant="outline"
                theme="blue"
                size="sm"
                @click.stop="handleAddBlock(row.id, column.key)"
                class="w-full border-2 border-dashed border-blue-300 dark:border-blue-600 hover:border-blue-500 dark:hover:border-blue-400 bg-blue-50/50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-all duration-200"
              >
                <FeatherIcon name="plus" class="w-4 h-4 mr-1" />
                Add Block
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>


    <!-- Unassigned Blocks Panel -->
    <div
      v-if="unassignedBlocks.length > 0 && showUnassignedPanel"
      class="unassigned-panel fixed z-40"
      :style="{
        right: '24px',
        top: '50%',
        transform: 'translateY(-50%)',
      }"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
        :class="[
          'w-80 max-w-[90vw] max-h-[70vh]',
          'sm:w-80 sm:max-w-[400px]',
          'md:w-96 md:max-w-[450px]',
          'lg:w-96 lg:max-w-[500px]',
        ]"
      >
        <!-- Panel Header -->
        <div
          class="p-4 border-b border-gray-200 dark:border-gray-700 bg-amber-50 dark:bg-amber-900/20"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                class="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center"
              >
                <FeatherIcon name="inbox" class="w-4 h-4 text-white" />
              </div>
              <div>
                <div class="font-semibold text-amber-900 dark:text-amber-100">
                  Unassigned {{ config?.block_doctype || "Items" }}
                </div>
                <div class="text-sm text-amber-700 dark:text-amber-300">
                  {{ unassignedBlocks.length }} items
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click.stop="$emit('toggleUnassignedPanel')"
            >
              <FeatherIcon name="x" class="w-4 h-4" />
            </Button>
          </div>
        </div>

        <!-- Panel Content -->
        <div class="p-4 space-y-2 overflow-y-auto max-h-[50vh]">
          <TransitionGroup name="unassigned" tag="div" class="space-y-2">
            <DynamicTimelineBlock
              v-for="block in unassignedBlocks"
              :key="block.id"
              :block="block"
              :config="config"
              :unassigned="true"
              @click="handleBlockClick"
              @dragstart="handleBlockDragStart"
              @dragend="handleBlockDragEnd"
            />
          </TransitionGroup>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 bg-white/50 dark:bg-gray-900/50 flex items-center justify-center z-50"
    >
      <div
        class="bg-white dark:bg-gray-900 rounded-lg p-6 shadow-xl border border-gray-200 dark:border-gray-700"
      >
        <div class="flex items-center gap-3">
          <div
            class="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full"
          ></div>
          <span class="text-gray-700 dark:text-gray-300"
            >Updating timeline...</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue";
import { Button, FeatherIcon } from "frappe-ui";
import DynamicTimelineBlock from "./DynamicTimelineBlock.vue";
import { toast } from "../../composables/useToast";

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
  dateColumns: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  showUnassignedPanel: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits([
  "blockMove",
  "blockClick",
  "addBlock",
  "blockResize",
  "cellClick",
  "assignTask",
  "toggleUnassignedPanel",
]);

// Refs
const gridContainer = ref(null);
const timelineGrid = ref(null);

// Reactive state
const rowSearch = ref("");
const currentViewMode = ref("week");
const selectedRow = ref(null);
const selectedBlock = ref(null);
const draggedBlock = ref(null);
const dragOverCell = ref(null);
const hoveredCell = ref({
  row: "",
  date: "",
});
const showUnassignedPanel = computed(() => props.showUnassignedPanel);
const autoRefresh = ref(false);
const scrollLeft = ref(0);
const scrollTop = ref(0);

// Unassigned panel state
const unassignedPanelPosition = ref({
  x: window.innerWidth - 250,
  y: window.innerHeight / 2,
});

// Grid configuration
const rowHeight = 120;
const columnWidth = 160;
const headerHeight = 100;

// View modes
const viewModes = [
  { label: "Day", value: "day", icon: "calendar" },
  { label: "Week", value: "week", icon: "calendar" },
  { label: "Month", value: "month", icon: "calendar" },
];

// Computed properties
const filteredRows = computed(() => {
  if (!rowSearch.value) return props.rows;
  const search = rowSearch.value.toLowerCase();
  return props.rows.filter(
    (row) =>
      getRowTitle(row).toLowerCase().includes(search) ||
      getRowSubtitle(row).toLowerCase().includes(search),
  );
});

const visibleDateColumns = computed(() => {
  return props.dateColumns;
});

const visibleBlocks = computed(() => {
  return props.blocks.filter((block) =>
    filteredRows.value.some((row) => row.id === block.row_id),
  );
});

const unassignedBlocks = computed(() => {
  return props.blocks.filter(
    (block) =>
      !block.row_id || block.row_id === null || block.row_id === undefined,
  );
});

const gridHeight = computed(() => {
  return filteredRows.value.length * rowHeight;
});

const hasDateRange = computed(() => {
  return (
    props.config?.date_range_start_field && props.config?.date_range_end_field
  );
});

// Methods
const getRowTitle = (row) => {
  return row.label || row.name || row.id;
};

const getRowSubtitle = (row) => {
  return row.department || row.description || "";
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
  return props.blocks.filter((block) => block.row_id === rowId).length;
};

const getRowWorkload = (rowId) => {
  const blocks = props.blocks.filter((block) => block.row_id === rowId);
  if (blocks.length === 0) return 0;

  // Calculate workload based on block durations or count
  const totalDuration = blocks.reduce((sum, block) => {
    return sum + (block.duration || 1);
  }, 0);

  // Assuming 8 hours per day capacity
  const capacity = visibleDateColumns.value.length * 8;
  return Math.round((totalDuration / capacity) * 100);
};

const getBlocksForCell = (rowId, date) => {
  return props.blocks.filter((block) => {
    if (block.row_id !== rowId) return false;

    const blockDate = block.date || block[props.config?.block_to_date_field];
    if (!blockDate) return false;

    // Handle date ranges
    if (hasDateRange.value && block.start_date && block.end_date) {
      const cellDate = new Date(date);
      const startDate = new Date(block.start_date);
      const endDate = new Date(block.end_date);
      return cellDate >= startDate && cellDate <= endDate;
    }

    // Handle single dates
    const blockDateStr = new Date(blockDate).toISOString().split("T")[0];
    return blockDateStr === date;
  });
};

const selectRow = (rowId) => {
  selectedRow.value = selectedRow.value === rowId ? null : rowId;
};

const formatDateRange = () => {
  if (!visibleDateColumns.value.length) return "";

  const start = visibleDateColumns.value[0].date;
  const end =
    visibleDateColumns.value[visibleDateColumns.value.length - 1].date;

  if (currentViewMode.value === "day") {
    return start.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
    });
  }

  return `${start.toLocaleDateString("en-US", { month: "short", day: "numeric" })} - ${end.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`;
};

const navigateDate = (direction) => {
  // This would be handled by parent component
  emit("dateNavigate", direction);
};

const goToToday = () => {
  emit("goToToday");
};

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value;
  if (autoRefresh.value) {
    startAutoRefresh();
  } else {
    stopAutoRefresh();
  }
};

let autoRefreshInterval = null;

const startAutoRefresh = () => {
  autoRefreshInterval = setInterval(() => {
    emit("refresh");
  }, 30000); // Refresh every 30 seconds
};

const stopAutoRefresh = () => {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
};

// Drag and drop handlers
const handleBlockDragStart = (block) => {
  console.log("Block drag start:", block);
  draggedBlock.value = block;
  // The block component already sets the dataTransfer data
};

const handleBlockDragEnd = () => {
  console.log("Block drag end");
  draggedBlock.value = null;
  dragOverCell.value = null;
};

const handleDragOver = (event, rowId, date) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
  dragOverCell.value = `${rowId}-${date}`;

  // Add visual feedback
  if (event.currentTarget && event.currentTarget.classList) {
    event.currentTarget.classList.add(
      "ring-2",
      "ring-green-500",
      "ring-opacity-50",
    );
  }
};

const handleDragEnter = (event, rowId, date) => {
  event.preventDefault();
  dragOverCell.value = `${rowId}-${date}`;

  // Add hover effect
  if (event.currentTarget && event.currentTarget.style) {
    event.currentTarget.style.transform = "scale(1.02)";
    event.currentTarget.style.transition = "transform 0.2s ease";
  }
};

const handleDragLeave = (event) => {
  // Only clear if we're actually leaving the cell
  if (event.currentTarget && !event.currentTarget.contains(event.relatedTarget)) {
    dragOverCell.value = null;

    // Remove visual feedback
    if (event.currentTarget.classList) {
      event.currentTarget.classList.remove(
        "ring-2",
        "ring-green-500",
        "ring-opacity-50",
      );
    }
    if (event.currentTarget.style) {
      event.currentTarget.style.transform = "";
    }
  }
};

const handleDrop = (event, rowId, date) => {
  event.preventDefault();
  dragOverCell.value = null;

  // Remove all visual feedback
  if (event.currentTarget && event.currentTarget.classList) {
    event.currentTarget.classList.remove(
      "ring-2",
      "ring-green-500",
      "ring-opacity-50",
    );
    
    // Add success animation
    event.currentTarget.classList.add("animate-pulse");
    setTimeout(() => {
      if (event.currentTarget && event.currentTarget.classList) {
        event.currentTarget.classList.remove("animate-pulse");
      }
    }, 500);
  }
  
  if (event.currentTarget && event.currentTarget.style) {
    event.currentTarget.style.transform = "";
  }

  console.log("Drop event triggered", { rowId, date, draggedBlock: draggedBlock.value });

  // Try to get data from dataTransfer
  let taskData = null;
  try {
    const transferData = event.dataTransfer.getData("application/json");
    if (transferData) {
      taskData = JSON.parse(transferData);
      console.log("Task data from dataTransfer:", taskData);
    }
  } catch (e) {
    console.warn("Failed to parse drag data:", e);
  }

  // Handle dragged block (existing block being moved via draggedBlock ref)
  if (draggedBlock.value) {
    const blockId = draggedBlock.value.id;
    const currentRowId = draggedBlock.value.row_id;
    let currentDate = draggedBlock.value.date || draggedBlock.value[props.config?.block_to_date_field];
    
    // Ensure date format consistency - extract just the date part if it's a datetime
    if (currentDate && typeof currentDate === 'string' && currentDate.includes(' ')) {
      currentDate = currentDate.split(' ')[0];
    }
    if (currentDate && currentDate instanceof Date) {
      currentDate = currentDate.toISOString().split('T')[0];
    }

    console.log("Moving block:", { blockId, currentRowId, currentDate, newRowId: rowId, newDate: date });

    // Check if we're dropping in the same place
    if (currentRowId === rowId && currentDate === date) {
      console.log("Same location, no move needed");
      draggedBlock.value = null;
      return;
    }

    emit("blockMove", {
      blockId,
      newRowId: rowId,
      newDate: date,
      oldRowId: currentRowId,
      oldDate: currentDate,
    });

    toast.success("Block has been moved successfully");

    draggedBlock.value = null;
    return;
  }

  // Handle data from dataTransfer (for blocks dragged from outside or backlog)
  if (taskData) {
    console.log("Handling task data:", taskData);
    
    // Check if this is an unassigned task being assigned
    if (taskData.unassigned || !taskData.row_id) {
      emit("assignTask", {
        taskId: taskData.id,
        rowId,
        date,
        taskData,
      });

      toast.success("Task has been assigned successfully");
      return;
    }

    // Handle moving existing task
    const currentRowId = taskData.row_id;
    let currentDate = taskData.date || taskData[props.config?.block_to_date_field];
    
    // Ensure date format consistency - extract just the date part if it's a datetime
    if (currentDate && typeof currentDate === 'string' && currentDate.includes(' ')) {
      currentDate = currentDate.split(' ')[0];
    }
    if (currentDate && currentDate instanceof Date) {
      currentDate = currentDate.toISOString().split('T')[0];
    }

    if (currentRowId === rowId && currentDate === date) {
      console.log("Same location, no move needed");
      return;
    }

    emit("blockMove", {
      blockId: taskData.id,
      newRowId: rowId,
      newDate: date,
      oldRowId: currentRowId,
      oldDate: currentDate,
    });

    toast.success("Task has been moved successfully");
  }
};

// Block interaction handlers
const handleBlockClick = (block, event) => {
  event?.stopPropagation();
  selectedBlock.value = block;
  emit("blockClick", block.id);
};

const handleBlockResize = (block, newDuration) => {
  emit("blockResize", {
    blockId: block.id,
    newDuration,
  });
};

const handleBlockContextMenu = (block, event) => {
  event.preventDefault();
  // Show context menu
  selectedBlock.value = block;
};

const handleAddBlock = (rowId, date) => {
  emit("addBlock", { rowId, date });

  toast.info("Opening block creation dialog");
};

const handleCellClick = (rowId, date) => {
  emit("cellClick", { rowId, date });
};

const handleCellHover = (rowId, date, isEntering) => {
  if (isEntering) {
    hoveredCell.value.row = rowId;
    hoveredCell.value.date = date;
  } else {
    hoveredCell.value.row = "";
    hoveredCell.value.date = "";
  }
};

// Scroll handling
const handleScroll = (event) => {
  scrollLeft.value = event.target.scrollLeft;
  scrollTop.value = event.target.scrollTop;
};

// Lifecycle
// Panel management methods
const toggleUnassignedPanel = () => {
  showUnassignedPanel.value = !showUnassignedPanel.value;
};

onMounted(() => {
  // Set up resize observer for responsive behavior
  if (gridContainer.value) {
    const resizeObserver = new ResizeObserver(() => {
      nextTick(() => {
        // Handle responsive adjustments
        // Adjust unassigned panel position on window resize
        const maxX = window.innerWidth - 150;
        const maxY = window.innerHeight - 150;
        if (unassignedPanelPosition.value.x > maxX) {
          unassignedPanelPosition.value.x = maxX;
        }
        if (unassignedPanelPosition.value.y > maxY) {
          unassignedPanelPosition.value.y = maxY;
        }
      });
    });
    resizeObserver.observe(gridContainer.value);
  }

  // Initialize unassigned panel visibility
  showUnassignedPanel.value = true;
});

onUnmounted(() => {
  stopAutoRefresh();
});

// Watch for auto-refresh
watch(
  () => props.blocks,
  () => {
    if (autoRefresh.value) {
      // Emit refresh signal periodically
    }
  },
);
</script>

<style scoped>
/* Table structure inspired by MonthViewTable.vue */
.resource-header-cell,
.date-header-cell {
  max-width: 9rem;
  min-width: 9rem;
  font-size: 0.875rem;
}

.resource-cell {
  position: sticky;
  left: 0;
  max-width: 16rem;
  min-width: 16rem;
  background: white;
  border-right: 1px solid rgb(229 231 235);
}

@media (prefers-color-scheme: dark) {
  .resource-cell {
    background: rgb(17 24 39);
    border-right-color: rgb(75 85 99);
  }
}

.timeline-cell {
  min-height: 120px;
  transition: all 0.2s ease;
  vertical-align: top;
}

.timeline-cell:hover {
  background-color: rgb(249 250 251);
}

@media (prefers-color-scheme: dark) {
  .timeline-cell:hover {
    background-color: rgb(31 41 55);
  }
}

.blocks-container {
  position: relative;
  min-height: 80px;
}

.unassigned-panel {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%) translateY(-50%);
    opacity: 0;
  }
  to {
    transform: translateX(0) translateY(-50%);
    opacity: 1;
  }
}

/* Enhanced animations from MonthViewTable.vue */
.block-enter-active,
.block-leave-active {
  transition: all 0.3s ease;
}

.block-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.block-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.block-move {
  transition: transform 0.3s ease;
}

.unassigned-enter-active,
.unassigned-leave-active {
  transition: all 0.3s ease;
}

.unassigned-enter-from,
.unassigned-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Enhanced hover effects */
.group:hover .resource-cell {
  transform: translateX(2px);
}

/* Improved scrollbar styling */
.dynamic-timeline-grid::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.dynamic-timeline-grid::-webkit-scrollbar-track {
  background: rgb(243 244 246);
}

.dynamic-timeline-grid::-webkit-scrollbar-thumb {
  background: rgb(209 213 219);
  border-radius: 4px;
}

.dynamic-timeline-grid::-webkit-scrollbar-thumb:hover {
  background: rgb(156 163 175);
}

@media (prefers-color-scheme: dark) {
  .dynamic-timeline-grid::-webkit-scrollbar-track {
    background: rgb(31 41 55);
  }
  
  .dynamic-timeline-grid::-webkit-scrollbar-thumb {
    background: rgb(75 85 99);
  }
  
  .dynamic-timeline-grid::-webkit-scrollbar-thumb:hover {
    background: rgb(107 114 128);
  }
}

/* Better responsive design */
@media (max-width: 1024px) {
  .resource-cell {
    max-width: 12rem;
    min-width: 12rem;
  }
  
  .resource-header-cell,
  .date-header-cell {
    max-width: 7rem;
    min-width: 7rem;
  }
}

@media (max-width: 768px) {
  .resource-cell {
    max-width: 10rem;
    min-width: 10rem;
  }
  
  .resource-header-cell,
  .date-header-cell {
    max-width: 6rem;
    min-width: 6rem;
  }
  
  .timeline-cell {
    min-height: 100px;
  }
}
</style>
