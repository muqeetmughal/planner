<template>
  <div
    class="dynamic-timeline-grid rounded-lg border overflow-auto"
    :class="[
      loading && 'animate-pulse pointer-events-none',
      getGridHeightClass()
    ]"
    :data-row-count="filteredRows.length > 20 ? 'large' : 'normal'"
  >
    <!-- Header with Search and Filters -->
    <div class="grid-header bg-white border-b border-gray-200 sticky top-0 z-30">
      <div class="p-3">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-3">
            <!-- Row Search -->
            <FormControl
              type="text"
              placeholder="Search resources..."
              v-model="rowSearch"
              class="w-64"
            />

            <!-- View Mode Toggle -->
            <div class="flex bg-gray-100 rounded-lg p-1">
              <button
                v-for="mode in viewModes"
                :key="mode.value"
                @click="currentViewMode = mode.value"
                :class="[
                  'px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center',
                  currentViewMode === mode.value
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900',
                ]"
              >
                <FeatherIcon :name="mode.icon" class="w-4 h-4 mr-1" />
                {{ mode.label }}
              </button>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <!-- Legend -->
            <div class="flex items-center gap-4 text-xs text-gray-500 mr-2">
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
              size="sm"
              @click="navigateDate(-1)"
            >
              <FeatherIcon name="chevron-left" class="w-4 h-4" />
            </Button>
            <div class="px-3 py-1.5 bg-gray-50 rounded-lg font-medium text-sm">
              {{ formatDateRange() }}
            </div>
            <Button
              variant="ghost"
              size="sm"
              @click="navigateDate(1)"
            >
              <FeatherIcon name="chevron-right" class="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" @click="goToToday">
              Today
            </Button>
          </div>

          <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span>{{ filteredRows.length }} rows • {{ visibleBlocks.length }} blocks</span>
            <div class="flex items-center gap-2" v-if="filteredRows.length > 8">
              <FeatherIcon name="layers" class="w-4 h-4" />
              <span class="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
                Showing {{ paginatedRows.length }} of {{ filteredRows.length }}
              </span>
            </div>
            <!-- Pagination Controls -->
            <div v-if="totalPages > 1" class="flex items-center gap-2">
              <Button
                variant="ghost"
                theme="gray"
                size="sm"
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage <= 1"
              >
                <FeatherIcon name="chevron-left" class="w-4 h-4" />
              </Button>
              <span class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded">
                {{ currentPage }} / {{ totalPages }}
              </span>
              <Button
                variant="ghost"
                theme="gray"
                size="sm"
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage >= totalPages"
              >
                <FeatherIcon name="chevron-right" class="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Table Structure with Virtual Scrolling for Large Datasets -->
    <div class="table-container relative">
      <table class="border-separate border-spacing-0 w-full table-fixed">
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
          v-for="(row, rowIdx) in paginatedRows" 
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

            <!-- Enhanced Blocks Container with Multiple Block Support -->
            <div 
              :class="[
                'blocks-container relative transition-all duration-300',
                getCellContainerClasses(row.id, column.key)
              ]"
            >
              <!-- Block Count Indicator for Multiple Blocks -->
              <div 
                v-if="getBlocksForCell(row.id, column.key).length > 1"
                class="absolute top-1 right-1 z-30 flex items-center gap-1"
              >
                <div 
                  :class="[
                    'px-1.5 py-0.5 rounded-full text-xs font-bold shadow-sm transition-all duration-200',
                    getBlocksForCell(row.id, column.key).length > 3 
                      ? 'bg-red-500 text-white animate-pulse' 
                      : 'bg-blue-500 text-white'
                  ]"
                >
                  {{ getBlocksForCell(row.id, column.key).length }}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="toggleCellExpansion(row.id, column.key)"
                  class="w-5 h-5 p-0 hover:bg-white/80 dark:hover:bg-gray-700/80 rounded-full transition-all duration-200"
                >
                  <FeatherIcon 
                    :name="isCellExpanded(row.id, column.key) ? 'chevron-up' : 'chevron-down'" 
                    class="w-3 h-3" 
                  />
                </Button>
              </div>

              <!-- Blocks Display with Multiple Layout Options -->
              <div :class="getBlocksDisplayClasses(row.id, column.key)">
                <TransitionGroup 
                  name="block" 
                  tag="div" 
                  :class="getTransitionGroupClasses(row.id, column.key)"
                >
                  <DynamicTimelineBlock
                    v-for="(block, index) in getVisibleBlocksForCell(row.id, column.key)"
                    :key="`${block.id}-${column.key}`"
                    :block="block"
                    :config="config"
                    :selected="selectedBlock?.id === block.id"
                    :resizable="hasDateRange && isBlockStartCell(block, column.key)"
                    :spanning="isBlockSpanning(block)"
                    :spanWidth="getBlockSpanWidth(block)"
                    :isStartCell="isBlockStartCell(block, column.key)"
                    :isEndCell="isBlockEndCell(block, column.key)"
                    :cellPosition="getBlockCellPosition(block, column.key)"
                    :compact="getCellViewMode(row.id, column.key) === 'compact'"
                    :index="index"
                    :total="getBlocksForCell(row.id, column.key).length"
                    @click="handleBlockClick"
                    @dragstart="handleBlockDragStart"
                    @dragend="handleBlockDragEnd"
                    @resize="handleBlockResize"
                    @contextmenu="handleBlockContextMenu"
                  />
                </TransitionGroup>
              </div>

              <!-- Overflow Indicator -->
              <div 
                v-if="hasOverflowBlocks(row.id, column.key)"
                class="mt-1 text-center"
              >
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="toggleCellExpansion(row.id, column.key)"
                  class="text-xs px-2 py-1 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-md transition-all duration-200"
                >
                  <FeatherIcon name="more-horizontal" class="w-3 h-3 mr-1" />
                  +{{ getOverflowCount(row.id, column.key) }} more
                </Button>
              </div>

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

              <!-- Quick Add Button for Cells with Existing Blocks -->
              <Button
                v-else-if="hoveredCell.row === row.id && hoveredCell.date === column.key && getBlocksForCell(row.id, column.key).length > 0"
                variant="ghost"
                size="sm"
                @click.stop="handleAddBlock(row.id, column.key)"
                class="absolute bottom-1 right-1 w-6 h-6 p-0 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 opacity-80 hover:opacity-100 z-20"
              >
                <FeatherIcon name="plus" class="w-3 h-3" />
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
      </table>
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
import { Button, FeatherIcon, FormControl } from "frappe-ui";
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
  "dateNavigate",
  "goToToday",
  "refresh",
]);

// Refs
const gridContainer = ref(null);

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

// Multiple blocks management
const expandedCells = ref(new Set());
const cellViewMode = ref(new Map()); // 'stacked', 'compact', 'list'

// Unassigned panel state
const unassignedPanelPosition = ref({
  x: window.innerWidth - 250,
  y: window.innerHeight / 2,
});


// View modes
const viewModes = [
  { label: "Day", value: "day", icon: "calendar" },
  { label: "Week", value: "week", icon: "calendar" },
  { label: "Month", value: "month", icon: "calendar" },
];

// Computed properties
const filteredRows = computed(() => {
  if (!Array.isArray(props.rows)) return [];
  if (!rowSearch.value) return props.rows;
  const search = rowSearch.value.toLowerCase();
  return props.rows.filter(
    (row) =>
      getRowTitle(row).toLowerCase().includes(search) ||
      getRowSubtitle(row).toLowerCase().includes(search),
  );
});

// Pagination for large datasets
const currentPage = ref(1);
const itemsPerPage = computed(() => {
  const rowCount = filteredRows.value.length;
  if (rowCount <= 8) return rowCount; // Show all for small datasets
  if (rowCount <= 20) return 10; // Moderate pagination
  return 15; // Aggressive pagination for large datasets
});

const totalPages = computed(() => {
  return Math.ceil(filteredRows.value.length / itemsPerPage.value);
});

const paginatedRows = computed(() => {
  if (filteredRows.value.length <= 8) {
    return filteredRows.value; // No pagination for small datasets
  }
  
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredRows.value.slice(start, end);
});

const visibleDateColumns = computed(() => {
  return Array.isArray(props.dateColumns) ? props.dateColumns : [];
});

const visibleBlocks = computed(() => {
  if (!Array.isArray(props.blocks) || !Array.isArray(paginatedRows.value)) return [];
  return props.blocks.filter((block) =>
    paginatedRows.value.some((row) => row.id === block.row_id),
  );
});

// Watch for pagination changes and reset to first page when search changes
watch(rowSearch, () => {
  currentPage.value = 1;
});

// Watch for block changes to update cell view modes
watch(() => props.blocks, () => {
  // Auto-expand cells with many blocks on initial load
  props.blocks.forEach(block => {
    if (block.row_id) {
      const date = block.date || block[props.config?.block_to_date_field];
      if (date) {
        const dateStr = new Date(date).toISOString().split('T')[0];
        const blocksInCell = getBlocksForCell(block.row_id, dateStr);
        if (blocksInCell.length > 4) {
          expandedCells.value.add(getCellId(block.row_id, dateStr));
        }
      }
    }
  });
}, { deep: true });

const unassignedBlocks = computed(() => {
  if (!Array.isArray(props.blocks)) return [];
  return props.blocks.filter(
    (block) =>
      !block.row_id || block.row_id === null || block.row_id === undefined,
  );
});


const hasDateRange = computed(() => {
  const hasFields = props.config?.block_to_date_field && props.config?.date_range_end_field;
  return hasFields;
});

// Helper function to format dates without timezone issues
const formatDateForComparison = (dateInput) => {
  if (!dateInput) return null;
  
  // Handle different date input formats
  let dateObj;
  if (typeof dateInput === 'string') {
    // For datetime strings like "2025-07-09 00:00:00", parse without timezone conversion
    if (dateInput.includes(' ')) {
      // Split datetime and take only the date part
      const datePart = dateInput.split(' ')[0];
      dateObj = new Date(datePart + 'T00:00:00'); // Add time to prevent timezone issues
    } else if (dateInput.includes('T')) {
      // ISO format - use the date part
      dateObj = new Date(dateInput.split('T')[0] + 'T00:00:00');
    } else {
      // Date only format
      dateObj = new Date(dateInput + 'T00:00:00');
    }
  } else if (dateInput instanceof Date) {
    dateObj = dateInput;
  } else {
    return null;
  }
  
  // Return YYYY-MM-DD format using local date to avoid timezone shifts
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0');
  const day = String(dateObj.getDate()).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
};

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
  if (!Array.isArray(props.blocks)) return 0;
  return props.blocks.filter((block) => block.row_id === rowId).length;
};

const getRowWorkload = (rowId) => {
  if (!Array.isArray(props.blocks)) return 0;
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
  if (!Array.isArray(props.blocks)) return [];
  const filteredBlocks = props.blocks.filter((block) => {
    if (block.row_id !== rowId) return false;

    const blockDate = block.date || block[props.config?.block_to_date_field];
    if (!blockDate) return false;


    // Handle date ranges - show blocks across their full date span
    if (hasDateRange.value) {
      // Use standardized fields from backend mapping first, fallback to config field names
      const startDate = block.start_date || block[props.config?.block_to_date_field] || block.date;
      const endDate = block.end_date || block[props.config?.date_range_end_field];
      
      if (startDate && endDate) {
        // Normalize dates for comparison - fix timezone issue by using local date parsing
        const blockStartDateStr = formatDateForComparison(startDate);
        const blockEndDateStr = formatDateForComparison(endDate);
        
        // Show block if the cell date falls within the date range (inclusive)
        const shouldShow = date >= blockStartDateStr && date <= blockEndDateStr;
        return shouldShow;
      }
    }

    // Handle single dates - fix timezone issue
    const blockDateStr = formatDateForComparison(blockDate);
    const shouldShow = blockDateStr === date;
    return shouldShow;
  });
  
  return filteredBlocks;
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
  draggedBlock.value = block;
  // The block component already sets the dataTransfer data
};

const handleBlockDragEnd = () => {
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

  // console.log("Drop event triggered", { rowId, date, draggedBlock: draggedBlock.value });

  // Try to get data from dataTransfer
  let taskData = null;
  try {
    const transferData = event.dataTransfer.getData("application/json");
    if (transferData) {
      taskData = JSON.parse(transferData);
      // console.log("Task data from dataTransfer:", taskData);
    }
  } catch (e) {
    console.warn("Failed to parse drag data:", e);
  }

  // Handle dragged block (existing block being moved via draggedBlock ref)
  if (draggedBlock.value) {
    const blockId = draggedBlock.value.id;
    const currentRowId = draggedBlock.value.row_id;
    let currentDate = draggedBlock.value.date || draggedBlock.value[props.config?.block_to_date_field];
    
    // Ensure date format consistency - handle both date and datetime fields
    if (currentDate) {
      if (typeof currentDate === 'string') {
        // Handle datetime strings (YYYY-MM-DD HH:MM:SS) and date strings (YYYY-MM-DD)
        if (currentDate.includes(' ')) {
          currentDate = currentDate.split(' ')[0];
        } else if (currentDate.includes('T')) {
          currentDate = currentDate.split('T')[0];
        }
      } else if (currentDate instanceof Date) {
        currentDate = currentDate.toISOString().split('T')[0];
      }
    }

    // console.log("Moving block:", { blockId, currentRowId, currentDate, newRowId: rowId, newDate: date });

    // Check if we're dropping in the same place
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

    toast.success("Block has been moved successfully");

    draggedBlock.value = null;
    return;
  }

  // Handle data from dataTransfer (for blocks dragged from outside or backlog)
  if (taskData) {
    // console.log("Handling task data:", taskData);
    
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
    
    // Ensure date format consistency - handle both date and datetime fields
    if (currentDate) {
      if (typeof currentDate === 'string') {
        // Handle datetime strings (YYYY-MM-DD HH:MM:SS) and date strings (YYYY-MM-DD)
        if (currentDate.includes(' ')) {
          currentDate = currentDate.split(' ')[0];
        } else if (currentDate.includes('T')) {
          currentDate = currentDate.split('T')[0];
        }
      } else if (currentDate instanceof Date) {
        currentDate = currentDate.toISOString().split('T')[0];
      }
    }

    if (currentRowId === rowId && currentDate === date) {
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

const handleBlockResize = (resizeData) => {
  // Enhanced resize handling for date range blocks
  // console.log('📏 Handling block resize:', resizeData);
  
  const { block, newDuration, direction, newStartDate, newEndDate } = resizeData;
  
  // Prepare the resize event data
  const eventData = {
    blockId: block.id,
    newDuration,
    direction
  };
  
  // Add date fields based on configuration
  if (hasDateRange.value) {
    if (newStartDate) {
      eventData.newStartDate = newStartDate;
      eventData[props.config?.block_to_date_field] = newStartDate;
    }
    if (newEndDate) {
      eventData.newEndDate = newEndDate;
      eventData[props.config?.date_range_end_field] = newEndDate;
    }
  } else {
    // For non-date-range blocks, just update the main date field
    const startDate = new Date(block[props.config?.block_to_date_field] || block.date);
    if (direction === 'right') {
      const newEnd = new Date(startDate);
      newEnd.setDate(startDate.getDate() + Math.floor(newDuration));
      eventData.newEndDate = newEnd.toISOString().split('T')[0];
    }
  }
  
  emit("blockResize", eventData);
  toast.success("Block has been resized successfully");
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

const getGridHeightClass = () => {
  const rowCount = filteredRows.value.length;
  
  if (rowCount <= 4) {
    return 'max-h-[32rem]'; // ~512px for up to 4 rows
  } else if (rowCount <= 8) {
    return 'max-h-[48rem]'; // ~768px for 5-8 rows
  } else if (rowCount <= 12) {
    return 'max-h-[64rem]'; // ~1024px for 9-12 rows
  } else {
    return 'max-h-[80vh]'; // Use viewport height for large datasets
  }
};

// Multiple blocks management methods
const getCellId = (rowId, date) => `${rowId}-${date}`;

const toggleCellExpansion = (rowId, date) => {
  const cellId = getCellId(rowId, date);
  const currentlyExpanded = expandedCells.value.has(cellId);
  
  if (currentlyExpanded) {
    expandedCells.value.delete(cellId);
  } else {
    expandedCells.value.add(cellId);
  }
};

const isCellExpanded = (rowId, date) => {
  return expandedCells.value.has(getCellId(rowId, date));
};

const getCellViewMode = (rowId, date) => {
  const blocks = getBlocksForCell(rowId, date);
  if (blocks.length <= 1) return 'single';
  if (blocks.length <= 3) return 'stacked';
  return isCellExpanded(rowId, date) ? 'expanded' : 'compact';
};

const getVisibleBlocksForCell = (rowId, date) => {
  const blocks = getBlocksForCell(rowId, date);
  if (!Array.isArray(blocks)) return [];
  const viewMode = getCellViewMode(rowId, date);
  
  switch (viewMode) {
    case 'single':
    case 'stacked':
    case 'expanded':
      return blocks;
    case 'compact':
      return blocks.slice(0, 2); // Show first 2 blocks in compact mode
    default:
      return blocks;
  }
};

const hasOverflowBlocks = (rowId, date) => {
  const blocks = getBlocksForCell(rowId, date);
  const visibleBlocks = getVisibleBlocksForCell(rowId, date);
  if (!Array.isArray(blocks) || !Array.isArray(visibleBlocks)) return false;
  return blocks.length > visibleBlocks.length;
};

const getOverflowCount = (rowId, date) => {
  const blocks = getBlocksForCell(rowId, date);
  const visibleBlocks = getVisibleBlocksForCell(rowId, date);
  if (!Array.isArray(blocks) || !Array.isArray(visibleBlocks)) return 0;
  return blocks.length - visibleBlocks.length;
};

const getCellContainerClasses = (rowId, date) => {
  const blocks = getBlocksForCell(rowId, date);
  const viewMode = getCellViewMode(rowId, date);
  
  const classes = ['min-h-[80px]'];
  
  if (Array.isArray(blocks) && blocks.length > 1) {
    classes.push('multiple-blocks');
  }
  
  switch (viewMode) {
    case 'expanded':
      classes.push('max-h-[300px]', 'overflow-y-auto', 'cell-expanded');
      break;
    case 'compact':
      classes.push('max-h-[120px]', 'cell-compact');
      break;
    default:
      classes.push('max-h-[200px]');
  }
  
  return classes;
};

const getBlocksDisplayClasses = (rowId, date) => {
  const viewMode = getCellViewMode(rowId, date);
  
  const classes = ['relative', 'w-full'];
  
  switch (viewMode) {
    case 'expanded':
      classes.push('space-y-1');
      break;
    case 'compact':
      classes.push('space-y-0.5');
      break;
    default:
      classes.push('space-y-1.5');
  }
  
  return classes.join(' ');
};

const getTransitionGroupClasses = (rowId, date) => {
  const viewMode = getCellViewMode(rowId, date);
  
  switch (viewMode) {
    case 'expanded':
      return 'space-y-1';
    case 'compact':
      return 'space-y-0.5';
    default:
      return 'space-y-1.5';
  }
};

// Block positioning helper functions
const isBlockStartCell = (block, dateKey) => {
  if (!hasDateRange.value || !block) return true;
  
  // Use standardized start_date from backend mapping
  const blockStartDate = block.start_date || block[props.config?.block_to_date_field];
  if (!blockStartDate) return false;
  
  const startDateStr = formatDateForComparison(blockStartDate);
  return startDateStr === dateKey;
};

const isBlockEndCell = (block, dateKey) => {
  if (!hasDateRange.value || !block) return true;
  
  // Use standardized end_date from backend mapping
  const blockEndDate = block.end_date || block[props.config?.date_range_end_field];
  if (!blockEndDate) return false;
  
  const endDateStr = formatDateForComparison(blockEndDate);
  return endDateStr === dateKey;
};

const getBlockCellPosition = (block, dateKey) => {
  if (!hasDateRange.value || !block) return 'single';
  
  const isStart = isBlockStartCell(block, dateKey);
  const isEnd = isBlockEndCell(block, dateKey);
  
  if (isStart && isEnd) return 'single';
  if (isStart) return 'start';
  if (isEnd) return 'end';
  return 'middle';
};

const isBlockSpanning = (block) => {
  if (!hasDateRange.value || !block) return false;
  
  // Use standardized fields from backend mapping
  const startDate = block.start_date || block[props.config?.block_to_date_field];
  const endDate = block.end_date || block[props.config?.date_range_end_field];
  
  if (!startDate || !endDate) return false;
  
  const startDateStr = formatDateForComparison(startDate);
  const endDateStr = formatDateForComparison(endDate);
  
  // Check if block spans more than one day
  return startDateStr !== endDateStr;
};

const getBlockSpanWidth = (block) => {
  if (!isBlockSpanning(block)) return 1;
  
  // Use standardized fields from backend mapping
  const startDate = block.start_date || block[props.config?.block_to_date_field];
  const endDate = block.end_date || block[props.config?.date_range_end_field];
  
  if (!startDate || !endDate) return 1;
  
  const startDateStr = formatDateForComparison(startDate);
  const endDateStr = formatDateForComparison(endDate);
  
  // Find the span in visible columns to ensure it matches the visible range
  const visibleColumns = visibleDateColumns.value;
  const startIdx = visibleColumns.findIndex(col => col.key === startDateStr);
  const endIdx = visibleColumns.findIndex(col => col.key === endDateStr);
  
  if (startIdx === -1) return 1; // Start date not visible
  if (endIdx === -1) {
    // Block extends beyond visible range
    return visibleColumns.length - startIdx;
  }
  
  return Math.max(1, endIdx - startIdx + 1);
};

// Lifecycle

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

.table-container {
  contain: layout;
}

.dynamic-timeline-grid {
  contain: layout style;
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


/* Enhanced responsive design with better scaling */
@media (max-width: 1024px) {
  .resource-cell {
    max-width: 12rem;
    min-width: 12rem;
  }
  
  .resource-header-cell,
  .date-header-cell {
    max-width: 7rem;
    min-width: 7rem;
    font-size: 0.8125rem;
  }
  
  .timeline-cell {
    min-height: 110px;
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
    font-size: 0.75rem;
  }
  
  .timeline-cell {
    min-height: 100px;
  }
  
  .blocks-container {
    min-height: 70px;
  }
}

@media (max-width: 640px) {
  .resource-cell {
    max-width: 8rem;
    min-width: 8rem;
  }
  
  .resource-header-cell,
  .date-header-cell {
    max-width: 5rem;
    min-width: 5rem;
  }
  
  .timeline-cell {
    min-height: 90px;
  }
  
  .grid-header {
    padding: 0.75rem;
  }
  
  .grid-header .flex {
    flex-direction: column;
    gap: 0.75rem;
  }
}

/* Improved scrolling behavior for large datasets */
.dynamic-timeline-grid {
  scroll-behavior: smooth;
}

.dynamic-timeline-grid::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.dynamic-timeline-grid::-webkit-scrollbar-track {
  background: rgb(248 250 252);
  border-radius: 6px;
}

.dynamic-timeline-grid::-webkit-scrollbar-thumb {
  background: rgb(203 213 225);
  border-radius: 6px;
  border: 2px solid rgb(248 250 252);
}

.dynamic-timeline-grid::-webkit-scrollbar-thumb:hover {
  background: rgb(148 163 184);
}

@media (prefers-color-scheme: dark) {
  .dynamic-timeline-grid::-webkit-scrollbar-track {
    background: rgb(31 41 55);
  }
  
  .dynamic-timeline-grid::-webkit-scrollbar-thumb {
    background: rgb(75 85 99);
    border-color: rgb(31 41 55);
  }
  
  .dynamic-timeline-grid::-webkit-scrollbar-thumb:hover {
    background: rgb(107 114 128);
  }
}

/* Performance optimizations for large datasets */
.timeline-cell {
  contain: layout style;
  will-change: background-color;
}

.blocks-container {
  contain: layout;
  position: relative;
}

.blocks-container.multiple-blocks {
  contain: layout style;
}

/* Virtual scrolling hint for very large datasets */
@media (min-width: 1024px) {
  .dynamic-timeline-grid[data-row-count="large"] {
    contain: strict;
  }
}

/* Multiple blocks handling styles */
.blocks-container.multiple-blocks {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.02) 0%, rgba(59, 130, 246, 0.05) 100%);
  border-radius: 8px;
  padding: 4px;
}

.blocks-container.multiple-blocks::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent);
  border-radius: 1px;
  z-index: 1;
}

/* Cell expansion styles */
.cell-expanded {
  animation: expandCell 0.3s ease-out;
}

.cell-compact {
  animation: compactCell 0.3s ease-out;
}

@keyframes expandCell {
  from {
    max-height: 120px;
  }
  to {
    max-height: 300px;
  }
}

@keyframes compactCell {
  from {
    max-height: 300px;
  }
  to {
    max-height: 120px;
  }
}

/* Enhanced block count indicator */
.blocks-container .absolute.top-1.right-1 {
  backdrop-filter: blur(4px);
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  padding: 2px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (prefers-color-scheme: dark) {
  .blocks-container .absolute.top-1.right-1 {
    background: rgba(17, 24, 39, 0.9);
  }
}

/* Overflow indicator styling */
.blocks-container .mt-1.text-center {
  border-top: 1px solid rgba(229, 231, 235, 0.5);
  padding-top: 4px;
  margin-top: 4px;
}

@media (prefers-color-scheme: dark) {
  .blocks-container .mt-1.text-center {
    border-top-color: rgba(75, 85, 99, 0.5);
  }
}

/* Quick add button enhancement */
.blocks-container .absolute.bottom-1.right-1 {
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.blocks-container .absolute.bottom-1.right-1:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}
</style>
