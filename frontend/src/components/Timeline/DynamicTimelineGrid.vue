<template>
  <div class="horizontal-timeline-grid">
    <!-- Timeline Header -->
    <div class="timeline-header sticky left-0 top-0 z-20 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-r border-gray-200/50 dark:border-gray-700/50 shadow-lg">
      <!-- Column Header + Row Labels -->
      <div class="grid grid-rows-[auto_1fr]" :style="gridTemplateRows">
        <!-- Column Header -->
        <div class="column-header-cell p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 border-b border-gray-200/50 dark:border-gray-700/50 flex items-center justify-center">
          <span class="text-sm font-bold text-gray-800 dark:text-gray-200 tracking-wide">
            {{ config?.row_doctype || 'Rows' }}
          </span>
        </div>
        
        <!-- Row Labels -->
        <div class="row-labels-container overflow-y-auto" :style="{ height: `${containerHeight}px` }">
          <div 
            v-for="(row, index) in visibleRows" 
            :key="row.id"
            :class="[
              'row-label-cell p-4 border-b border-gray-200/50 dark:border-gray-700/50 flex items-center transition-all duration-300',
              'hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-white dark:hover:from-blue-900/20 dark:hover:to-gray-800'
            ]"
            :style="{ height: `${rowHeight}px` }"
          >
            <div class="flex items-center gap-3 w-full">
              <!-- Row Avatar/Icon -->
              <div class="w-10 h-10 bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 rounded-xl flex items-center justify-center text-white text-sm font-bold shadow-lg transform transition-all duration-300 hover:scale-110 hover:rotate-3">
                {{ getRowInitials(row) }}
              </div>
              
              <!-- Row Info -->
              <div class="flex-1 min-w-0">
                <div class="text-sm font-bold text-gray-900 dark:text-white truncate mb-1">
                  {{ getRowTitle(row) }}
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400 truncate">
                  {{ getRowSubtitle(row) }}
                </div>
              </div>
              
              <!-- Row Stats -->
              <div class="flex items-center gap-2">
                <div class="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full font-medium">
                  {{ getRowBlockCount(row.id) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeline Body (Horizontal Scrolling) -->
    <div class="timeline-body flex-1 overflow-x-auto overflow-y-hidden" ref="timelineBody" @scroll="handleScroll">
      <div class="timeline-content" :style="{ width: `${totalWidth}px`, height: `${totalHeight}px` }">
        <!-- Date Headers -->
        <div class="date-headers-row sticky top-0 z-10 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 shadow-lg">
          <div class="flex" :style="{ transform: `translateX(${-scrollLeft}px)` }">
            <div 
              v-for="column in visibleDateColumns" 
              :key="column.key"
              :class="[
                'date-header-cell p-3 border-r border-gray-200/50 dark:border-gray-700/50 text-center relative transition-all duration-200 hover:scale-105',
                column.isToday ? 'bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/30' : 'bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800',
                column.isWeekend ? 'bg-gradient-to-br from-amber-50 to-orange-100 dark:from-amber-900/20 dark:to-orange-900/20' : ''
              ]"
              :style="{ width: `${columnWidth}px`, minWidth: `${columnWidth}px` }"
            >
              <div class="text-sm font-bold text-gray-900 dark:text-white">
                {{ column.label }}
              </div>
              <div class="text-xs text-gray-600 dark:text-gray-400 mt-1 font-medium">
                {{ column.sublabel }}
              </div>
              <div v-if="column.isToday" class="absolute top-2 right-2">
                <div class="w-3 h-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full animate-pulse shadow-lg"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Timeline Rows -->
        <div class="timeline-rows-container relative">
          <div 
            v-for="(row, rowIndex) in visibleRows" 
            :key="row.id"
            class="timeline-row group border-b border-gray-100/50 dark:border-gray-700/50 hover:bg-gradient-to-r hover:from-blue-50/30 hover:to-indigo-50/30 dark:hover:from-blue-900/10 dark:hover:to-indigo-900/10 transition-all duration-300"
            :style="{ 
              height: `${rowHeight}px`,
              transform: `translateY(${rowIndex * rowHeight}px)`
            }"
          >
            <!-- Virtual Date Cells -->
            <div class="flex absolute inset-0" :style="{ transform: `translateX(${-scrollLeft}px)` }">
              <div 
                v-for="column in visibleDateColumns" 
                :key="`${row.id}-${column.key}`"
                :class="[
                  'date-cell relative border-r border-gray-100/50 dark:border-gray-700/50 transition-all duration-300 hover:shadow-inner',
                  column.isToday ? 'bg-gradient-to-br from-blue-50/50 to-indigo-50/50 dark:from-blue-900/20 dark:to-indigo-900/20' : 'bg-white dark:bg-gray-800',
                  column.isWeekend ? 'bg-gradient-to-br from-amber-50/50 to-orange-50/50 dark:from-amber-900/20 dark:to-orange-900/20' : '',
                  dragOverCell === `${row.id}-${column.key}` ? 'bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-900/30 dark:to-teal-900/30 ring-2 ring-emerald-500/50 ring-inset' : ''
                ]"
                :style="{ width: `${columnWidth}px`, minWidth: `${columnWidth}px` }"
                @drop="handleDrop($event, row.id, column.key)"
                @dragover.prevent="handleDragOver($event, row.id, column.key)"
                @dragenter.prevent="handleDragEnter($event, row.id, column.key)"
                @dragleave="handleDragLeave($event, row.id, column.key)"
                :data-row-id="row.id"
                :data-date="column.key"
              >
                <!-- Today Indicator -->
                <div v-if="column.isToday" class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg"></div>
                
                <!-- Blocks in this cell -->
                <div class="p-2 space-y-1 relative z-10 h-full overflow-y-auto">
                  <TransitionGroup name="block-list" tag="div">
                    <DynamicTimelineBlock
                      v-for="block in getBlocksForCell(row.id, column.key)"
                      :key="block.id"
                      :block="block"
                      :config="config"
                      :dragging="draggedBlock?.id === block.id"
                      @click="$emit('blockClick', block.id)"
                      @dragstart="handleBlockDragStart"
                      @dragend="handleBlockDragEnd"
                    />
                  </TransitionGroup>
                </div>
                
                <!-- Add Block Button -->
                <div class="add-block-overlay absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center backdrop-blur-sm">
                  <Button 
                    variant="ghost" 
                    theme="blue" 
                    size="sm"
                    @click="$emit('addBlock', { rowId: row.id, date: column.key })"
                    class="text-xs font-medium transform transition-all duration-300 hover:scale-110 bg-white/90 dark:bg-gray-800/90 shadow-lg border border-blue-200 dark:border-blue-700"
                  >
                    <FeatherIcon name="plus" class="w-3 h-3 mr-1" />
                    Add
                  </Button>
                </div>
                
                <!-- Cell animation ripple effect -->
                <div v-if="cellAnimations[`${row.id}-${column.key}`]" class="absolute inset-0 pointer-events-none">
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/30 to-transparent animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unassigned Blocks Panel (Vertical Side Panel) -->
    <div v-if="unassignedBlocks.length > 0" class="unassigned-panel fixed right-4 top-1/2 transform -translate-y-1/2 z-30 w-80 max-h-96 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/40 dark:to-orange-900/40 rounded-2xl shadow-2xl border border-amber-200/50 dark:border-amber-700/50 backdrop-blur-lg">
      <!-- Panel Header -->
      <div class="panel-header p-4 border-b border-amber-200/50 dark:border-amber-700/50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-amber-500 via-orange-600 to-red-500 rounded-xl flex items-center justify-center text-white shadow-lg animate-bounce">
            <FeatherIcon name="inbox" class="w-5 h-5" />
          </div>
          <div class="flex-1">
            <div class="text-sm font-bold text-amber-900 dark:text-amber-100">
              Unassigned {{ config?.block_doctype || 'Blocks' }}
            </div>
            <div class="text-xs text-amber-800 dark:text-amber-300 font-medium">
              {{ unassignedBlocks.length }} items waiting
            </div>
          </div>
          <button @click="toggleUnassignedPanel" class="w-6 h-6 rounded-full bg-amber-200 dark:bg-amber-800 flex items-center justify-center hover:bg-amber-300 dark:hover:bg-amber-700 transition-colors">
            <FeatherIcon name="x" class="w-4 h-4 text-amber-800 dark:text-amber-200" />
          </button>
        </div>
      </div>
      
      <!-- Panel Content -->
      <div class="panel-content p-4 overflow-y-auto max-h-80">
        <div class="space-y-3">
          <TransitionGroup name="unassigned-blocks" tag="div" class="space-y-3">
            <DynamicTimelineBlock
              v-for="block in unassignedBlocks"
              :key="block.id"
              :block="block"
              :config="config"
              :unassigned="true"
              :dragging="draggedBlock?.id === block.id"
              @click="$emit('blockClick', block.id)"
              @dragstart="handleBlockDragStart"
              @dragend="handleBlockDragEnd"
            />
          </TransitionGroup>
        </div>
      </div>
    </div>

    <!-- Horizontal Scrollbar -->
    <div class="horizontal-scrollbar sticky bottom-0 left-0 right-0 z-20 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-t border-gray-200/50 dark:border-gray-700/50 p-2">
      <div class="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div 
          class="absolute h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-150"
          :style="{ 
            width: `${(viewportWidth / totalWidth) * 100}%`,
            left: `${(scrollLeft / totalWidth) * 100}%`
          }"
        ></div>
      </div>
    </div>

    <!-- Enhanced Loading Overlay -->
    <Transition name="loading-overlay">
      <div v-if="loading" class="absolute inset-0 bg-white/90 dark:bg-gray-800/90 backdrop-blur-lg flex items-center justify-center z-40">
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-2xl border border-gray-200/50 dark:border-gray-700/50 max-w-sm mx-4">
          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-8 h-8 border-3 border-blue-200 dark:border-blue-800 rounded-full"></div>
              <div class="absolute top-0 left-0 w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div>
              <div class="text-gray-900 dark:text-white font-bold text-lg">Updating timeline</div>
              <div class="text-gray-600 dark:text-gray-400 text-sm">Please wait a moment...</div>
            </div>
          </div>
          <div class="mt-4 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div class="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full animate-pulse" style="width: 60%"></div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onUnmounted, watch } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import DynamicTimelineBlock from './DynamicTimelineBlock.vue'

const props = defineProps({
  config: {
    type: Object,
    required: true
  },
  rows: {
    type: Array,
    default: () => []
  },
  blocks: {
    type: Array,
    default: () => []
  },
  dateColumns: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['blockMove', 'blockClick', 'addBlock'])

// Virtual scrolling configuration
const columnWidth = 160
const rowHeight = 120
const containerHeight = 600
const headerHeight = 80
const bufferSize = 5 // Number of extra columns to render for smooth scrolling

// Refs
const timelineBody = ref(null)

// Reactive state
const scrollLeft = ref(0)
const scrollTop = ref(0)
const viewportWidth = ref(0)
const viewportHeight = ref(0)
const draggedBlock = ref(null)
const dragOverCell = ref(null)
const cellAnimations = reactive({})
const showUnassignedPanel = ref(true)

// Computed properties
const totalWidth = computed(() => props.dateColumns.length * columnWidth)
const totalHeight = computed(() => headerHeight + (props.rows.length * rowHeight))

const gridTemplateRows = computed(() => `${headerHeight}px 1fr`)

const visibleColumnStart = computed(() => Math.max(0, Math.floor(scrollLeft.value / columnWidth) - bufferSize))
const visibleColumnEnd = computed(() => Math.min(props.dateColumns.length, Math.ceil((scrollLeft.value + viewportWidth.value) / columnWidth) + bufferSize))

const visibleRowStart = computed(() => Math.max(0, Math.floor(scrollTop.value / rowHeight) - bufferSize))
const visibleRowEnd = computed(() => Math.min(props.rows.length, Math.ceil((scrollTop.value + viewportHeight.value) / rowHeight) + bufferSize))

const visibleDateColumns = computed(() => {
  return props.dateColumns.slice(visibleColumnStart.value, visibleColumnEnd.value)
})

const visibleRows = computed(() => {
  return props.rows.slice(visibleRowStart.value, visibleRowEnd.value)
})

const unassignedBlocks = computed(() => {
  return props.blocks.filter(block => !block.row_id)
})

// Methods
const getRowTitle = (row) => {
  if (!props.config?.row_title_field) return row.name || row.id
  return row[props.config.row_title_field] || row.name || row.id
}

const getRowSubtitle = (row) => {
  if (!props.config?.row_subtitle_field) return ''
  return row[props.config.row_subtitle_field] || ''
}

const getRowInitials = (row) => {
  const title = getRowTitle(row)
  return title.split(' ').map(word => word[0]).join('').toUpperCase().slice(0, 2)
}

const getRowBlockCount = (rowId) => {
  const count = props.blocks.filter(block => block.row_id === rowId).length
  return count > 0 ? `${count}` : '0'
}

const getBlocksForCell = (rowId, date) => {
  return props.blocks.filter(block => {
    if (block.row_id !== rowId) return false
    
    const blockDate = block[props.config?.block_date_field || 'date']
    if (!blockDate) return false
    
    const blockDateStr = new Date(blockDate).toISOString().split('T')[0]
    return blockDateStr === date
  })
}

const handleScroll = (event) => {
  scrollLeft.value = event.target.scrollLeft
  scrollTop.value = event.target.scrollTop
}

const updateViewportSize = () => {
  if (timelineBody.value) {
    viewportWidth.value = timelineBody.value.clientWidth
    viewportHeight.value = timelineBody.value.clientHeight
  }
}

const toggleUnassignedPanel = () => {
  showUnassignedPanel.value = !showUnassignedPanel.value
}

// Enhanced drag and drop handlers
const handleBlockDragStart = (event, block) => {
  draggedBlock.value = block
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', block.id)
  
  event.target.style.opacity = '0.6'
  event.target.style.transform = 'scale(1.05) rotate(3deg)'
  event.target.style.zIndex = '1000'
}

const handleBlockDragEnd = (event) => {
  event.target.style.opacity = '1'
  event.target.style.transform = 'scale(1) rotate(0deg)'
  event.target.style.zIndex = 'auto'
  draggedBlock.value = null
  dragOverCell.value = null
}

const handleDragOver = (event, rowId, date) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
}

const handleDragEnter = (event, rowId, date) => {
  event.preventDefault()
  dragOverCell.value = `${rowId}-${date}`
}

const handleDragLeave = (event, rowId, date) => {
  if (!event.currentTarget.contains(event.relatedTarget)) {
    dragOverCell.value = null
  }
}

const handleDrop = (event, rowId, date) => {
  event.preventDefault()
  
  if (!draggedBlock.value) return
  
  const blockId = draggedBlock.value.id
  const currentRowId = draggedBlock.value.row_id
  const currentDate = draggedBlock.value[props.config?.block_date_field || 'date']
  
  if (currentRowId === rowId && currentDate === date) {
    dragOverCell.value = null
    return
  }
  
  const cellKey = `${rowId}-${date}`
  cellAnimations[cellKey] = true
  setTimeout(() => {
    delete cellAnimations[cellKey]
  }, 1000)
  
  emit('blockMove', {
    blockId,
    newRowId: rowId,
    newDate: date,
    oldRowId: currentRowId,
    oldDate: currentDate
  })
  
  draggedBlock.value = null
  dragOverCell.value = null
}

// Lifecycle
onMounted(() => {
  updateViewportSize()
  window.addEventListener('resize', updateViewportSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateViewportSize)
})

// Watch for viewport changes
watch(() => timelineBody.value, updateViewportSize)
</script>

<style scoped>
.horizontal-timeline-grid {
  @apply flex h-full bg-gray-50 dark:bg-gray-900 rounded-2xl overflow-hidden shadow-2xl border border-gray-200/50 dark:border-gray-700/50;
}

.timeline-header {
  @apply w-80 flex-shrink-0;
}

.timeline-body {
  @apply flex-1 relative;
}

.timeline-content {
  @apply relative;
}

.date-headers-row {
  @apply h-20;
}

.timeline-rows-container {
  @apply h-full;
}

.timeline-row {
  @apply absolute left-0 w-full;
}

.date-cell {
  @apply flex-shrink-0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.date-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px -8px rgba(59, 130, 246, 0.3);
}

.unassigned-panel {
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%) translateY(-50%);
    opacity: 0;
  }
  to {
    transform: translateX(0) translateY(-50%);
    opacity: 1;
  }
}

.row-labels-container::-webkit-scrollbar {
  width: 8px;
}

.row-labels-container::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

.row-labels-container::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

.timeline-body::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

.timeline-body::-webkit-scrollbar-track {
  @apply bg-gray-100/50 dark:bg-gray-800/50;
}

.timeline-body::-webkit-scrollbar-thumb {
  @apply bg-gradient-to-b from-gray-400 to-gray-500 dark:from-gray-600 dark:to-gray-700 rounded-full;
}

.timeline-body::-webkit-scrollbar-thumb:hover {
  @apply bg-gradient-to-b from-gray-500 to-gray-600 dark:from-gray-500 dark:to-gray-600;
}

/* Enhanced Transitions */
.block-list-move,
.block-list-enter-active,
.block-list-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.block-list-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.8);
}

.block-list-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.unassigned-blocks-move,
.unassigned-blocks-enter-active,
.unassigned-blocks-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.unassigned-blocks-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.8);
}

.unassigned-blocks-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.8);
}

.loading-overlay-enter-active,
.loading-overlay-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.loading-overlay-enter-from,
.loading-overlay-leave-to {
  opacity: 0;
  backdrop-filter: blur(0px);
}

.add-block-overlay {
  backdrop-filter: blur(8px);
}

.horizontal-scrollbar {
  height: 30px;
}
</style>