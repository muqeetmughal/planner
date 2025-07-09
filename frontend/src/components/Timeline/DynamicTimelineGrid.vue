<template>
  <div class="dynamic-timeline-grid">
    <!-- Enhanced Header with Search and Filters -->
    <div
      class="grid-header bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30"
    >
      <div class="p-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-4">
            <!-- Row Search -->
            <div class="relative">
              <FeatherIcon
                name="search"
                class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4"
              />
              <input
                v-model="rowSearch"
                type="text"
                placeholder="Search rows..."
                class="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <!-- View Mode Toggle -->
            <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
              <button
                v-for="mode in viewModes"
                :key="mode.value"
                @click="currentViewMode = mode.value"
                :class="[
                  'px-3 py-1 rounded-md text-sm font-medium transition-all duration-200',
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

          <div class="flex items-center gap-2">
            <!-- Legend -->
            <div
              class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400"
            >
              <div class="flex items-center gap-1">
                <div class="w-3 h-3 bg-blue-500 rounded"></div>
                <span>Active</span>
              </div>
              <div class="flex items-center gap-1">
                <div class="w-3 h-3 bg-amber-500 rounded"></div>
                <span>Pending</span>
              </div>
              <div class="flex items-center gap-1">
                <div class="w-3 h-3 bg-green-500 rounded"></div>
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
          <div class="flex items-center gap-3">
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="navigateDate(-1)"
            >
              <FeatherIcon name="chevron-left" class="w-4 h-4" />
            </Button>
            <div
              class="px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg font-medium text-sm"
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

    <!-- Main Grid Container -->
    <div class="grid-container" ref="gridContainer">
      <div class="grid-wrapper">
        <!-- Fixed Row Header -->
        <div
          class="row-header bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700"
        >
          <!-- Header Cell -->
          <div
            class="header-cell p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
          >
            <div class="font-semibold text-sm text-gray-900 dark:text-white">
              {{ config?.row_doctype || "Resources" }}
            </div>
          </div>

          <!-- Row Cells -->
          <div class="row-cells" :style="{ height: `${gridHeight}px` }">
            <div
              v-for="(row, index) in filteredRows"
              :key="row.id"
              :class="[
                'row-cell p-4 border-b border-gray-200 dark:border-gray-700 flex items-center gap-3',
                'hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer',
                selectedRow === row.id
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700'
                  : '',
              ]"
              :style="{ height: `${rowHeight}px` }"
              @click="selectRow(row.id)"
            >
              <!-- Row Avatar -->
              <div
                class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-sm font-bold shadow-sm"
              >
                {{ getRowInitials(row) }}
              </div>

              <!-- Row Info -->
              <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-900 dark:text-white truncate">
                  {{ getRowTitle(row) }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400 truncate">
                  {{ getRowSubtitle(row) }}
                </div>
                <div class="flex items-center gap-2 mt-1">
                  <div
                    class="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full"
                  >
                    {{ getRowBlockCount(row.id) }} items
                  </div>
                  <div
                    v-if="getRowWorkload(row.id)"
                    class="text-xs text-blue-600 dark:text-blue-400 font-medium"
                  >
                    {{ getRowWorkload(row.id) }}% capacity
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Scrollable Timeline Grid -->
        <div class="timeline-grid" ref="timelineGrid" @scroll="handleScroll">
          <!-- Date Header -->
          <div
            class="date-header bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-20"
          >
            <div class="date-columns flex">
              <div
                v-for="column in visibleDateColumns"
                :key="column.key"
                :class="[
                  'date-column border-r border-gray-200 dark:border-gray-700 p-3 text-center',
                  column.isToday
                    ? 'bg-blue-50 dark:bg-blue-900/20'
                    : 'bg-gray-50 dark:bg-gray-800',
                  column.isWeekend ? 'bg-amber-50 dark:bg-amber-900/20' : '',
                ]"
                :style="{
                  width: `${columnWidth}px`,
                  minWidth: `${columnWidth}px`,
                }"
              >
                <div
                  class="font-semibold text-sm text-gray-900 dark:text-white"
                >
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
            </div>
          </div>

          <!-- Timeline Rows -->
          <div class="timeline-rows" :style="{ height: `${gridHeight}px` }">
            <div
              v-for="(row, rowIndex) in filteredRows"
              :key="row.id"
              class="timeline-row border-b border-gray-200 dark:border-gray-700"
              :style="{ height: `${rowHeight}px` }"
            >
              <div class="timeline-cells flex">
                <div
                  v-for="column in visibleDateColumns"
                  :key="`${row.id}-${column.key}`"
                  :class="[
                    'timeline-cell border-r border-gray-200 dark:border-gray-700 relative',
                    'hover:bg-gray-50 dark:hover:bg-gray-800 transition-all duration-200',
                    column.isToday ? 'bg-blue-50/30 dark:bg-blue-900/10' : '',
                    column.isWeekend
                      ? 'bg-amber-50/30 dark:bg-amber-900/10'
                      : '',
                    dragOverCell === `${row.id}-${column.key}`
                      ? 'bg-green-100 dark:bg-green-900/20 ring-2 ring-green-500/50 ring-inset shadow-lg transform scale-105'
                      : '',
                  ]"
                  :style="{
                    width: `${columnWidth}px`,
                    minWidth: `${columnWidth}px`,
                  }"
                  @drop="handleDrop($event, row.id, column.key)"
                  @dragover.prevent="handleDragOver($event, row.id, column.key)"
                  @dragenter.prevent="
                    handleDragEnter($event, row.id, column.key)
                  "
                  @dragleave="handleDragLeave($event, row.id, column.key)"
                  @click="handleCellClick(row.id, column.key)"
                >
                  <!-- Today Indicator -->
                  <div
                    v-if="column.isToday"
                    class="absolute top-0 left-0 right-0 h-0.5 bg-blue-500 shadow-sm"
                  ></div>

                  <!-- Drop Zone Indicator -->
                  <div
                    v-if="dragOverCell === `${row.id}-${column.key}`"
                    class="absolute inset-0 border-2 border-dashed border-green-500 bg-green-50/50 dark:bg-green-900/20 flex items-center justify-center animate-pulse"
                  >
                    <div
                      class="bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg"
                    >
                      Drop here
                    </div>
                  </div>

                  <!-- Blocks Container -->
                  <div class="blocks-container p-1 h-full overflow-hidden">
                    <div class="space-y-1 h-full">
                      <TransitionGroup name="block" tag="div" class="space-y-1">
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
                    </div>
                  </div>

                  <!-- Add Block Button (only show in empty cells) -->
                  <div
                    v-if="getBlocksForCell(row.id, column.key).length === 0"
                    class="add-block-overlay absolute inset-0 opacity-0 hover:opacity-100 transition-all duration-200 bg-gray-100/50 dark:bg-gray-800/50 flex items-center justify-center backdrop-blur-sm"
                  >
                    <Button
                      variant="ghost"
                      theme="blue"
                      size="sm"
                      @click.stop="handleAddBlock(row.id, column.key)"
                      class="bg-white/90 dark:bg-gray-800/90 shadow-sm border border-blue-200 dark:border-blue-700 hover:shadow-md hover:scale-105 transition-all duration-200"
                    >
                      <FeatherIcon name="plus" class="w-3 h-3 mr-1" />
                      Add
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

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
const handleBlockDragStart = (event, block) => {
  draggedBlock.value = block;
  // Mark if this is an unassigned block
  const blockData = { ...block, unassigned: !block.row_id };
  event.dataTransfer.setData("application/json", JSON.stringify(blockData));
  event.dataTransfer.effectAllowed = "move";
};

const handleBlockDragEnd = (event) => {
  draggedBlock.value = null;
  dragOverCell.value = null;
};

const handleDragOver = (event, rowId, date) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
  dragOverCell.value = `${rowId}-${date}`;

  // Add visual feedback
  event.currentTarget.classList.add(
    "ring-2",
    "ring-green-500",
    "ring-opacity-50",
  );
};

const handleDragEnter = (event, rowId, date) => {
  event.preventDefault();
  dragOverCell.value = `${rowId}-${date}`;

  // Add hover effect
  event.currentTarget.style.transform = "scale(1.02)";
  event.currentTarget.style.transition = "transform 0.2s ease";
};

const handleDragLeave = (event, rowId, date) => {
  // Only clear if we're actually leaving the cell
  if (!event.currentTarget.contains(event.relatedTarget)) {
    dragOverCell.value = null;

    // Remove visual feedback
    event.currentTarget.classList.remove(
      "ring-2",
      "ring-green-500",
      "ring-opacity-50",
    );
    event.currentTarget.style.transform = "";
  }
};

const handleDrop = (event, rowId, date) => {
  event.preventDefault();
  dragOverCell.value = null;

  // Remove all visual feedback
  event.currentTarget.classList.remove(
    "ring-2",
    "ring-green-500",
    "ring-opacity-50",
  );
  event.currentTarget.style.transform = "";

  // Add success animation
  event.currentTarget.classList.add("animate-pulse");
  setTimeout(() => {
    event.currentTarget.classList.remove("animate-pulse");
  }, 500);

  // Try to get data from dataTransfer first (for backlog tasks)
  let taskData = null;
  try {
    const transferData = event.dataTransfer.getData("application/json");
    if (transferData) {
      taskData = JSON.parse(transferData);
    }
  } catch (e) {
    console.warn("Failed to parse drag data:", e);
  }

  // Handle dragged block (existing block being moved)
  if (draggedBlock.value) {
    const blockId = draggedBlock.value.id;
    const currentRowId = draggedBlock.value.row_id;
    const currentDate = draggedBlock.value.date;

    if (currentRowId === rowId && currentDate === date) {
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

    toast({
      title: "Block Moved",
      text: "Block has been moved successfully",
      icon: "check",
      iconClasses: "text-green-600",
    });

    draggedBlock.value = null;
    return;
  }

  // Handle backlog task (new task being assigned)
  if (taskData && taskData.unassigned) {
    emit("assignTask", {
      taskId: taskData.id,
      rowId,
      date,
      taskData,
    });

    toast({
      title: "Task Assigned",
      text: "Task has been assigned successfully",
      icon: "check",
      iconClasses: "text-green-600",
    });
    return;
  }

  // Handle regular task data
  if (taskData) {
    emit("blockMove", {
      blockId: taskData.id,
      newRowId: rowId,
      newDate: date,
      oldRowId: taskData.row_id,
      oldDate: taskData.date,
    });

    toast({
      title: "Task Moved",
      text: "Task has been moved successfully",
      icon: "check",
      iconClasses: "text-green-600",
    });
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

  toast({
    title: "Add Block",
    text: "Opening block creation dialog",
    icon: "plus",
    iconClasses: "text-blue-600",
  });
};

const handleCellClick = (rowId, date) => {
  emit("cellClick", { rowId, date });
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
.dynamic-timeline-grid {
  @apply h-full flex flex-col bg-gray-50 dark:bg-gray-900;
}

.grid-container {
  @apply flex-1 overflow-hidden;
}

.grid-wrapper {
  @apply flex h-full;
}

.row-header {
  @apply w-80 flex-shrink-0 overflow-hidden;
}

.timeline-grid {
  @apply flex-1 overflow-auto;
}

.header-cell {
  @apply h-20;
}

.row-cells {
  @apply overflow-y-auto;
}

.row-cell {
  transition: all 0.2s ease;
}

.row-cell:hover {
  transform: translateX(2px);
}

.date-header {
  @apply h-20;
}

.date-column {
  transition: all 0.2s ease;
}

.timeline-cell {
  @apply min-h-full;
  transition: all 0.2s ease;
}

.timeline-cell:hover .add-block-overlay {
  @apply opacity-100;
}

.blocks-container {
  @apply relative;
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

/* Block animations */
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

/* Unassigned animations */
.unassigned-enter-active,
.unassigned-leave-active {
  transition: all 0.3s ease;
}

.unassigned-enter-from,
.unassigned-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Scrollbar styling */
.timeline-grid::-webkit-scrollbar {
  @apply w-2 h-2;
}

.timeline-grid::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

.timeline-grid::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded;
}

.timeline-grid::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .row-header {
    @apply w-64;
  }

  .unassigned-panel {
    @apply w-72;
  }
}

@media (max-width: 768px) {
  .row-header {
    @apply w-48;
  }

  .unassigned-panel {
    @apply w-64 max-h-80;
  }
}
</style>
