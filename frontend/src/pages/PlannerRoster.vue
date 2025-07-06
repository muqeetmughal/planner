<template>
  <Layout :breadcrumbs="breadcrumbs">
    <div class="mx-auto px-4 lg:px-8 max-w-[2000px]">
      <!-- Minimal Header -->
      <div class="planner-header mb-6 sticky top-0 z-50 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm pb-4">
        <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <!-- Title and Info -->
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <FeatherIcon name="calendar" class="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">Team Planner</h1>
              <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mt-1">
                <span>{{ department.value || 'All Departments' }}</span>
                <span class="w-1 h-1 bg-gray-400 rounded-full"></span>
                <span>{{ formatCurrentPeriod() }}</span>
              </div>
            </div>
          </div>

          <!-- Compact Stats -->
          <div class="grid grid-cols-4 gap-3">
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center min-w-[60px]">
              <div class="text-lg font-semibold text-gray-900 dark:text-white">{{ workloadStats.totalAssignees }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Team</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center min-w-[60px]">
              <div class="text-lg font-semibold text-green-600 dark:text-green-400">{{ workloadStats.scheduledTasks }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Active</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center min-w-[60px]">
              <div class="text-lg font-semibold text-amber-600 dark:text-amber-400">{{ workloadStats.unscheduledTasks }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Queue</div>
            </div>
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center min-w-[60px]">
              <div class="text-lg font-semibold text-blue-600 dark:text-blue-400">{{ Math.round(workloadStats.overallUtilization) }}%</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Usage</div>
            </div>
          </div>
        </div>

        <!-- Compact Action Bar -->
        <div class="flex items-center justify-between mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div class="flex items-center gap-3">
            <!-- Department Filter -->
            <select 
              v-model="department.value"
              class="px-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              @change="handleDepartmentChange"
            >
              <option value="">All Departments</option>
              <option v-for="dept in availableDepartments" :key="dept" :value="dept">
                {{ dept }}
              </option>
            </select>

            <!-- View Toggle -->
            <div class="flex bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-700">
              <button
                @click="viewMode = 'week'"
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-l-md',
                  viewMode === 'week' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                ]"
              >
                Week
              </button>
              <button
                @click="viewMode = 'month'"
                :class="[
                  'px-3 py-1.5 text-sm font-medium rounded-r-md border-l border-gray-200 dark:border-gray-700',
                  viewMode === 'month' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                ]"
              >
                Month
              </button>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Refresh Button -->
            <Button 
              variant="ghost" 
              theme="gray" 
              size="sm" 
              :loading="loading"
              @click="refreshData"
              class="px-3 py-1.5"
            >
              <FeatherIcon name="refresh-cw" class="w-4 h-4" />
            </Button>

            <!-- Add Task Button -->
            <Button 
              variant="solid" 
              theme="blue" 
              size="sm"
              @click="handleAddTask"
              class="px-3 py-1.5"
            >
              <FeatherIcon name="plus" class="w-4 h-4 mr-1" />
              Add Task
            </Button>
          </div>
        </div>
      </div>

      <!-- Timeline Container -->
      <div class="timeline-container bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <TimelineViewRoster 
          :assignees="assignees"
          :tasks="tasks"
          :loading="loading"
          @taskClick="handleTaskClick"
          @taskMove="handleTaskMove"
          @addTask="handleAddTask"
        />
      </div>

      <!-- Task Modal -->
      <div 
        v-if="isTaskFormActive" 
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        @click.self="closeTaskDetails"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-lg max-h-[90vh] overflow-hidden">
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ activeTask ? 'Edit Task' : 'Create Task' }}
            </h2>
            <Button variant="ghost" theme="gray" size="sm" @click="closeTaskDetails">
              <FeatherIcon name="x" class="w-4 h-4" />
            </Button>
          </div>
          
          <div class="p-4 overflow-y-auto">
            <TaskForm 
              :task="activeTask" 
              :department="department.value"
              :assignees="assignees"
              @close="closeTaskDetails"
              @update="handleTaskUpdate"
              @create="handleTaskCreate"
            />
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="fixed inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm flex items-center justify-center z-40">
        <div class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-lg border border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-gray-900 dark:text-white text-sm">Loading...</span>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import Layout from "@/pages/shared/Layout.vue"
import { ref, computed, onMounted, watch } from "vue"
import { useRoute } from 'vue-router'
import { Button, FeatherIcon } from 'frappe-ui'
import TimelineViewRoster from "@/components/Timeline/TimelineViewRoster.vue"
import TaskForm from "@/components/Task/TaskForm.vue"
import { useWorkloadManager } from "@/composables/useWorkloadManager"

const route = useRoute()

// Reactive state
const department = ref(route.params.department || '')
const dashboardName = ref(route.params.dashboardName || 'Team Planner')
const viewMode = ref('week')
const isTaskFormActive = ref(false)
const activeTask = ref(null)

// Breadcrumbs
const breadcrumbs = computed(() => [
  {
    label: 'Dashboard',
    route: { name: 'Dashboard' }
  },
  {
    label: dashboardName.value,
    route: { name: 'PlannerRoster' }
  }
])

// Initialize workload manager
const {
  assignees,
  tasks,
  loading,
  workloadStats,
  overallocatedAssignees,
  underutilizedAssignees,
  loadWorkloadData,
  moveTask,
  updateTask,
  createTask
} = useWorkloadManager(department.value)

// Computed properties
const availableDepartments = computed(() => {
  const departments = new Set()
  assignees.value.forEach(assignee => {
    if (assignee.department) {
      departments.add(assignee.department)
    }
  })
  return Array.from(departments).sort()
})

// Methods
const refreshData = async () => {
  await loadWorkloadData(null, null, true)
}

const handleDepartmentChange = () => {
  loadWorkloadData(null, null, true)
}

const handleTaskClick = (taskId) => {
  const task = tasks.value.find(t => t.id === taskId)
  activeTask.value = task || null
  isTaskFormActive.value = true
}

const handleTaskMove = async (data) => {
  try {
    await moveTask(data.taskId, data.assigneeId, data.startDate, data.endDate)
  } catch (error) {
    console.error('Error moving task:', error)
  }
}

const handleTaskUpdate = async (data) => {
  try {
    await updateTask(data.taskId, data.updates)
    closeTaskDetails()
  } catch (error) {
    console.error('Error updating task:', error)
  }
}

const handleTaskCreate = async (taskData) => {
  try {
    await createTask(taskData)
    closeTaskDetails()
  } catch (error) {
    console.error('Error creating task:', error)
  }
}

const handleAddTask = (data = {}) => {
  activeTask.value = null // New task
  isTaskFormActive.value = true
}

const closeTaskDetails = () => {
  activeTask.value = null
  isTaskFormActive.value = false
}

const formatCurrentPeriod = () => {
  const now = new Date()
  if (viewMode.value === 'week') {
    const startOfWeek = new Date(now)
    const day = startOfWeek.getDay()
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1)
    startOfWeek.setDate(diff)
    
    const endOfWeek = new Date(startOfWeek)
    endOfWeek.setDate(startOfWeek.getDate() + 6)
    
    return `${startOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endOfWeek.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  } else {
    return now.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
  }
}

// Watch for route changes
watch(() => route.params.department, (newDepartment) => {
  if (newDepartment !== department.value) {
    department.value = newDepartment || ''
    loadWorkloadData(null, null, true)
  }
}, { immediate: true })

// Initialize
onMounted(() => {
  loadWorkloadData()
})
</script>

<style scoped>
.planner-header {
  transition: all 0.2s ease;
}

.timeline-container {
  min-height: 500px;
}

/* Subtle focus states */
select:focus,
button:focus {
  outline: none;
}

/* Smooth transitions */
* {
  transition: all 0.15s ease;
}

/* Modal animation */
.fixed.inset-0 {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .planner-header {
    position: relative;
    top: auto;
  }
  
  .timeline-container {
    min-height: 400px;
  }
}
</style>