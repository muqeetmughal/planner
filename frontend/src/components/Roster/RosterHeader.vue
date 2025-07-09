<template>
  <div class="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
    <!-- Main Header -->
    <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 mb-6">
      <!-- Title Section -->
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
          <FeatherIcon name="calendar" class="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ title }}
          </h1>
          <div class="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400 mt-1">
            <span>{{ currentDepartment || 'All Departments' }}</span>
            <span class="w-1 h-1 bg-gray-400 rounded-full"></span>
            <span>{{ formatCurrentPeriod() }}</span>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4 text-center border border-blue-200 dark:border-blue-700">
          <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ stats.totalAssignees }}</div>
          <div class="text-xs text-blue-600/70 dark:text-blue-400/70 font-medium">Team Members</div>
        </div>
        <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4 text-center border border-green-200 dark:border-green-700">
          <div class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.activeTasks }}</div>
          <div class="text-xs text-green-600/70 dark:text-green-400/70 font-medium">Active Tasks</div>
        </div>
        <div class="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 rounded-lg p-4 text-center border border-amber-200 dark:border-amber-700">
          <div class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ stats.pendingTasks }}</div>
          <div class="text-xs text-amber-600/70 dark:text-amber-400/70 font-medium">Pending</div>
        </div>
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-4 text-center border border-purple-200 dark:border-purple-700">
          <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{{ Math.round(stats.avgUtilization) }}%</div>
          <div class="text-xs text-purple-600/70 dark:text-purple-400/70 font-medium">Utilization</div>
        </div>
      </div>
    </div>

    <!-- Controls Section -->
    <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <!-- Left Controls -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Department Filter -->
        <div class="flex items-center gap-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Department:</label>
          <Select
            v-model="selectedDepartment"
            :options="departmentOptions"
            placeholder="All Departments"
            @change="handleDepartmentChange"
            class="min-w-48"
          />
        </div>

        <!-- Company Filter -->
        <div class="flex items-center gap-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">Company:</label>
          <Select
            v-model="selectedCompany"
            :options="companyOptions"
            placeholder="Select Company"
            @change="handleCompanyChange"
            class="min-w-48"
          />
        </div>

        <!-- View Mode Toggle -->
        <div class="flex bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-1">
          <button
            v-for="mode in viewModes"
            :key="mode.value"
            @click="handleViewModeChange(mode.value)"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex items-center gap-2',
              viewMode === mode.value 
                ? 'bg-blue-500 text-white shadow-sm' 
                : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800'
            ]"
          >
            <FeatherIcon :name="mode.icon" class="w-4 h-4" />
            <span>{{ mode.label }}</span>
          </button>
        </div>
      </div>

      <!-- Right Controls -->
      <div class="flex items-center gap-3">
        <!-- Date Navigation -->
        <div class="flex items-center gap-2 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-1">
          <Button
            variant="ghost"
            theme="gray"
            size="sm"
            @click="navigateDate(-1)"
            class="hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <FeatherIcon name="chevron-left" class="w-4 h-4" />
          </Button>
          
          <div class="px-4 py-2 text-sm font-medium text-gray-900 dark:text-white min-w-48 text-center">
            {{ formatCurrentPeriod() }}
          </div>
          
          <Button
            variant="ghost"
            theme="gray"
            size="sm"
            @click="navigateDate(1)"
            class="hover:bg-gray-50 dark:hover:bg-gray-800"
          >
            <FeatherIcon name="chevron-right" class="w-4 h-4" />
          </Button>
          
          <div class="h-6 w-px bg-gray-300 dark:bg-gray-600 mx-1"></div>
          
          <Button
            variant="ghost"
            theme="blue"
            size="sm"
            @click="goToToday"
            class="hover:bg-blue-50 dark:hover:bg-blue-900/30"
          >
            <FeatherIcon name="calendar" class="w-4 h-4 mr-1" />
            Today
          </Button>
        </div>

        <!-- Action Buttons -->
        <Button
          variant="ghost"
          theme="gray"
          size="sm"
          :loading="loading"
          @click="handleRefresh"
          class="hover:bg-green-50 dark:hover:bg-green-900/30"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4" />
        </Button>

        <Button
          variant="solid"
          theme="blue"
          size="sm"
          @click="handleAddTask"
        >
          <FeatherIcon name="plus" class="w-4 h-4 mr-2" />
          Add Task
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button, FeatherIcon, Select } from 'frappe-ui'
import { dayjs } from '@/utils/dateUtils'

const props = defineProps({
  title: {
    type: String,
    default: 'Team Planner'
  },
  viewMode: {
    type: String,
    default: 'week'
  },
  currentDate: {
    type: Object,
    default: () => dayjs()
  },
  currentDepartment: {
    type: String,
    default: ''
  },
  currentCompany: {
    type: String,
    default: ''
  },
  departments: {
    type: Array,
    default: () => []
  },
  companies: {
    type: Array,
    default: () => []
  },
  stats: {
    type: Object,
    default: () => ({
      totalAssignees: 0,
      activeTasks: 0,
      pendingTasks: 0,
      avgUtilization: 0
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'viewModeChange',
  'dateChange',
  'departmentChange', 
  'companyChange',
  'refresh',
  'addTask'
])

// Reactive state
const selectedDepartment = ref(props.currentDepartment)
const selectedCompany = ref(props.currentCompany)

// Constants
const viewModes = [
  { label: 'Week', value: 'week', icon: 'calendar' },
  { label: 'Month', value: 'month', icon: 'calendar' }
]

// Computed properties
const departmentOptions = computed(() => [
  { label: 'All Departments', value: '' },
  ...props.departments.map(dept => ({ label: dept, value: dept }))
])

const companyOptions = computed(() => [
  { label: 'Select Company', value: '' },
  ...props.companies.map(company => ({ label: company, value: company }))
])

// Methods
const formatCurrentPeriod = () => {
  if (props.viewMode === 'week') {
    const startOfWeek = getWeekStart(props.currentDate)
    const endOfWeek = startOfWeek.add(6, 'day')
    return `${startOfWeek.format('MMM D')} - ${endOfWeek.format('MMM D, YYYY')}`
  } else {
    return props.currentDate.format('MMMM YYYY')
  }
}

const getWeekStart = (date) => {
  const d = dayjs(date)
  const day = d.day()
  const diff = d.date() - day + (day === 0 ? -6 : 1)
  return d.date(diff)
}

const navigateDate = (direction) => {
  let newDate
  if (props.viewMode === 'week') {
    newDate = props.currentDate.add(direction * 7, 'day')
  } else {
    newDate = props.currentDate.add(direction, 'month')
  }
  emit('dateChange', newDate)
}

const goToToday = () => {
  emit('dateChange', dayjs())
}

const handleViewModeChange = (mode) => {
  emit('viewModeChange', mode)
}

const handleDepartmentChange = () => {
  emit('departmentChange', selectedDepartment.value)
}

const handleCompanyChange = () => {
  emit('companyChange', selectedCompany.value)
}

const handleRefresh = () => {
  emit('refresh')
}

const handleAddTask = () => {
  emit('addTask')
}

// Watch for prop changes
watch(() => props.currentDepartment, (newVal) => {
  selectedDepartment.value = newVal
})

watch(() => props.currentCompany, (newVal) => {
  selectedCompany.value = newVal
})
</script>

<style scoped>
/* Smooth transitions */
* {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced button hover effects */
.group:hover .group-hover\:scale-105 {
  transform: scale(1.05);
}

/* Gradient backgrounds */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}
</style>