<template>
    <Layout :breadcrumbs="breadcrumbs">
        <div class="mx-auto px-4 lg:px-8 max-w-[2000px] min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
            <!-- Enhanced Header with Workload Stats -->
            <div 
                class="workload-header mb-8 sticky top-0 z-50 backdrop-blur-lg bg-white/80 dark:bg-gray-900/80 pb-6 border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm" 
                ref="headerRef"
                :class="{ 'scrolled': isScrolled }"
            >
                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
                    <!-- Enhanced Title Section -->
                    <div class="flex items-center gap-6">
                        <div class="relative">
                            <div class="absolute -inset-1 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg blur opacity-25 animate-pulse"></div>
                            <div class="relative bg-white dark:bg-gray-800 rounded-lg p-1">
                                <FeatherIcon name="calendar" class="w-8 h-8 text-blue-600 dark:text-blue-400" />
                            </div>
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                                Workload Planner
                            </h1>
                            <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400 mt-1">
                                <div class="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1">
                                    <FeatherIcon name="users" class="w-4 h-4" />
                                    <span class="font-medium">{{ department.value }}</span>
                                </div>
                                <div class="flex items-center gap-2 bg-blue-50 dark:bg-blue-900/30 rounded-full px-3 py-1">
                                    <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                                    <span>{{ workloadStats.totalAssignees }} active members</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Enhanced Quick Stats with Cards -->
                    <div class="flex items-center gap-4">
                        <div class="stats-grid flex items-center gap-3">
                            <!-- Scheduled Tasks -->
                            <div class="stat-card group hover:scale-105 transition-all duration-300 cursor-pointer">
                                <div class="bg-white dark:bg-gray-800 rounded-lg px-4 py-3 shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600 flex items-center gap-3 min-w-[120px]">
                                    <div class="flex-shrink-0">
                                        <FeatherIcon name="check-circle" class="w-5 h-5 text-blue-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <div class="text-xl font-bold text-blue-600 dark:text-blue-400 leading-tight">{{ workloadStats.scheduledTasks }}</div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400 font-medium truncate">Scheduled</div>
                                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 mt-1.5">
                                            <div class="bg-blue-500 h-1 rounded-full transition-all duration-500" :style="{ width: `${(workloadStats.scheduledTasks / (workloadStats.scheduledTasks + workloadStats.unscheduledTasks)) * 100}%` }"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Pending Tasks -->
                            <div class="stat-card group hover:scale-105 transition-all duration-300 cursor-pointer">
                                <div class="bg-white dark:bg-gray-800 rounded-lg px-4 py-3 shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-yellow-300 dark:hover:border-yellow-600 flex items-center gap-3 min-w-[120px]">
                                    <div class="flex-shrink-0">
                                        <FeatherIcon name="clock" class="w-5 h-5 text-yellow-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <div class="text-xl font-bold text-yellow-600 dark:text-yellow-400 leading-tight">{{ workloadStats.unscheduledTasks }}</div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400 font-medium truncate">Pending</div>
                                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 mt-1.5">
                                            <div class="bg-yellow-500 h-1 rounded-full transition-all duration-500" :style="{ width: `${(workloadStats.unscheduledTasks / (workloadStats.scheduledTasks + workloadStats.unscheduledTasks)) * 100}%` }"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Utilization -->
                            <div class="stat-card group hover:scale-105 transition-all duration-300 cursor-pointer">
                                <div class="bg-white dark:bg-gray-800 rounded-lg px-4 py-3 shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-green-300 dark:hover:border-green-600 flex items-center gap-3 min-w-[120px]">
                                    <div class="flex-shrink-0">
                                        <FeatherIcon name="trending-up" class="w-5 h-5 text-green-500 opacity-70 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <div class="text-xl font-bold text-green-600 dark:text-green-400 leading-tight">{{ workloadStats.overallUtilization }}%</div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400 font-medium truncate">Utilization</div>
                                        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 mt-1.5">
                                            <div class="bg-green-500 h-1 rounded-full transition-all duration-500" :style="{ width: `${workloadStats.overallUtilization}%` }"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Overloaded -->
                            <div class="stat-card group hover:scale-105 transition-all duration-300 cursor-pointer">
                                <div class="bg-white dark:bg-gray-800 rounded-lg px-4 py-3 shadow-md border border-gray-200 dark:border-gray-700 hover:shadow-lg flex items-center gap-3 min-w-[120px]" 
                                     :class="overallocatedAssignees.length > 0 ? 'hover:border-red-300 dark:hover:border-red-600' : 'hover:border-gray-300 dark:hover:border-gray-600'">
                                    <div class="flex-shrink-0">
                                        <FeatherIcon 
                                            :name="overallocatedAssignees.length > 0 ? 'alert-triangle' : 'shield-check'" 
                                            class="w-5 h-5 opacity-70 group-hover:opacity-100 transition-opacity"
                                            :class="overallocatedAssignees.length > 0 ? 'text-red-500' : 'text-gray-500'"
                                        />
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <div class="text-xl font-bold leading-tight" :class="overallocatedAssignees.length > 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'">
                                            {{ overallocatedAssignees.length }}
                                        </div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400 font-medium truncate">Overloaded</div>
                                        <div v-if="overallocatedAssignees.length > 0" class="flex items-center gap-1 mt-1">
                                            <div class="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></div>
                                            <span class="text-xs text-red-600 dark:text-red-400 font-medium truncate">Attention needed</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Enhanced Action Buttons -->
                        <div class="flex items-center gap-2 ml-4">
                            <Button 
                                :variant="'ghost'" 
                                theme="gray" 
                                size="sm" 
                                :loading="loading"
                                @click="refreshWorkloadData"
                                class="group hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-200 flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600"
                            >
                                <FeatherIcon name="refresh-cw" class="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                                <span class="text-sm font-medium">Refresh</span>
                            </Button>
                            
                            <Button 
                                :variant="showCapacityAnalysis ? 'solid' : 'ghost'" 
                                :theme="showCapacityAnalysis ? 'blue' : 'gray'"
                                size="sm"
                                @click="showCapacityAnalysis = !showCapacityAnalysis"
                                class="group transition-all duration-200 flex items-center gap-2 px-3 py-2 rounded-lg border"
                                :class="showCapacityAnalysis ? 'border-blue-500 bg-blue-600 text-white shadow-md' : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30'"
                            >
                                <FeatherIcon name="bar-chart-2" class="w-4 h-4 group-hover:scale-110 transition-transform" />
                                <span class="text-sm font-medium">Analytics</span>
                                <div v-if="showCapacityAnalysis" class="ml-1 w-1.5 h-1.5 bg-blue-300 rounded-full animate-pulse"></div>
                            </Button>

                            <Button 
                                variant="solid" 
                                theme="blue" 
                                size="sm"
                                @click="handleAddTask"
                                class="group hover:scale-105 transition-all duration-200 shadow-md hover:shadow-lg flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white border-0"
                            >
                                <FeatherIcon name="plus" class="w-4 h-4 group-hover:rotate-90 transition-transform duration-300" />
                                <span class="text-sm font-medium">New Task</span>
                            </Button>
                        </div>
                    </div>
                </div>

                <!-- Capacity Analysis Banner -->
                <Transition
                    enter-active-class="transition-all duration-300 ease-out"
                    enter-from-class="opacity-0 transform -translate-y-4"
                    enter-to-class="opacity-100 transform translate-y-0"
                    leave-active-class="transition-all duration-200 ease-in"
                    leave-from-class="opacity-100 transform translate-y-0"
                    leave-to-class="opacity-0 transform -translate-y-4"
                >
                    <div v-if="showCapacityAnalysis" class="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
                        <div class="flex items-center justify-between mb-4">
                            <div class="flex items-center gap-3">
                                <div class="w-8 h-8 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
                                    <FeatherIcon name="trending-up" class="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                </div>
                                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Team Capacity Analysis</h3>
                            </div>
                            <Button variant="ghost" theme="gray" size="sm" @click="showCapacityAnalysis = false">
                                <FeatherIcon name="x" class="w-4 h-4" />
                            </Button>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Well Balanced</span>
                                </div>
                                <div class="text-2xl font-bold text-green-600 dark:text-green-400">
                                    {{ workloadStats.totalAssignees - overallocatedAssignees.length - underutilizedAssignees.length }}
                                </div>
                                <p class="text-xs text-gray-500 dark:text-gray-400">Team members with optimal workload</p>
                            </div>
                            
                            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Underutilized</span>
                                </div>
                                <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{{ underutilizedAssignees.length }}</div>
                                <p class="text-xs text-gray-500 dark:text-gray-400">Can take on more work</p>
                            </div>
                            
                            <div class="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                                <div class="flex items-center gap-2 mb-2">
                                    <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Overloaded</span>
                                </div>
                                <div class="text-2xl font-bold text-red-600 dark:text-red-400">{{ overallocatedAssignees.length }}</div>
                                <p class="text-xs text-gray-500 dark:text-gray-400">Need workload redistribution</p>
                            </div>
                        </div>
                    </div>
                </Transition>
            </div>

            <!-- Main Workload View with Enhanced Layout -->
            <div class="flex flex-col xl:flex-row gap-8">
                <!-- Timeline View with Enhanced Container -->
                <div class="flex-1">
                    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
                        <div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-900">
                            <div class="flex items-center justify-between">
                                <h2 class="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-3">
                                    <FeatherIcon name="layout" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                    Team Timeline
                                </h2>
                                <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
                                        <span>Scheduled</span>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-yellow-500 rounded-full"></div>
                                        <span>Pending</span>
                                    </div>
                                    <div class="flex items-center gap-1">
                                        <div class="w-2 h-2 bg-red-500 rounded-full"></div>
                                        <span>Overdue</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="p-6">
                            <TimelineViewRoster 
                                :assignees="assignees"
                                :tasks="tasks"
                                :loading="loading"
                                @taskClick="handleTaskClick"
                                @taskMove="handleTaskMove"
                                @taskUpdate="handleTaskUpdate"
                                @addTask="handleAddTask"
                                class="enhanced-timeline"
                            />
                        </div>
                    </div>
                </div>

                <!-- Enhanced Task Details Panel -->
                <Transition
                    enter-active-class="transition-all duration-300 ease-out"
                    enter-from-class="opacity-0 transform translate-x-8"
                    enter-to-class="opacity-100 transform translate-x-0"
                    leave-active-class="transition-all duration-200 ease-in"
                    leave-from-class="opacity-100 transform translate-x-0"
                    leave-to-class="opacity-0 transform translate-x-8"
                >
                    <div v-if="isTaskFormActive" class="w-full xl:w-96">
                        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden sticky top-32">
                            <div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
                                <div class="flex items-center justify-between">
                                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                                        <FeatherIcon name="edit-3" class="w-5 h-5 text-blue-600 dark:text-blue-400" />
                                        {{ activeTask ? 'Edit Task' : 'New Task' }}
                                    </h3>
                                    <Button variant="ghost" theme="gray" size="sm" @click="closeTaskDetails" class="hover:bg-white/50 dark:hover:bg-gray-800/50">
                                        <FeatherIcon name="x" class="w-4 h-4" />
                                    </Button>
                                </div>
                            </div>
                            
                            <div class="p-6">
                                <TaskForm 
                                    :task="activeTask" 
                                    :department="department.value"
                                    :assignees="assignees"
                                    @close="closeTaskDetails"
                                    @update="handleTaskUpdate"
                                    class="enhanced-task-form"
                                />
                            </div>
                        </div>
                    </div>
                </Transition>
            </div>

            <!-- Quick Action Floating Button -->
            <div class="fixed bottom-6 right-6 z-40">
                <div class="relative group">
                    <Button 
                        variant="solid" 
                        theme="blue" 
                        size="lg"
                        @click="quickActionMenuOpen = !quickActionMenuOpen"
                        class="rounded-full w-14 h-14 shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-110"
                    >
                        <FeatherIcon :name="quickActionMenuOpen ? 'x' : 'zap'" class="w-6 h-6 transition-transform duration-300" :class="{ 'rotate-90': quickActionMenuOpen }" />
                    </Button>
                    
                    <!-- Quick Action Menu -->
                    <Transition
                        enter-active-class="transition-all duration-200 ease-out"
                        enter-from-class="opacity-0 transform scale-95 translate-y-2"
                        enter-to-class="opacity-100 transform scale-100 translate-y-0"
                        leave-active-class="transition-all duration-150 ease-in"
                        leave-from-class="opacity-100 transform scale-100 translate-y-0"
                        leave-to-class="opacity-0 transform scale-95 translate-y-2"
                    >
                        <div v-if="quickActionMenuOpen" class="absolute bottom-16 right-0 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 py-2 min-w-48">
                            <button @click="handleAddTask(); quickActionMenuOpen = false" class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-3 transition-colors">
                                <FeatherIcon name="plus" class="w-4 h-4 text-blue-600 dark:text-blue-400" />
                                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Add Task</span>
                            </button>
                            <button @click="refreshWorkloadData(); quickActionMenuOpen = false" class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-3 transition-colors">
                                <FeatherIcon name="refresh-cw" class="w-4 h-4 text-green-600 dark:text-green-400" />
                                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Refresh Data</span>
                            </button>
                            <button @click="showCapacityAnalysis = true; quickActionMenuOpen = false" class="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center gap-3 transition-colors">
                                <FeatherIcon name="bar-chart-2" class="w-4 h-4 text-purple-600 dark:text-purple-400" />
                                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">View Analytics</span>
                            </button>
                        </div>
                    </Transition>
                </div>
            </div>
        </div>
    </Layout>
</template>

<script setup>
import Layout from "@/pages/shared/Layout.vue"
import { ref, computed, onMounted, watch, onUnmounted } from "vue"
import { useRoute } from 'vue-router'
import { Button, TextInput } from 'frappe-ui'
import TimelineViewRoster from "@/components/Timeline/TimelineViewRoster.vue"
import TaskForm from "@/components/Task/TaskForm.vue"
import { useWorkloadManager } from "@/composables/useWorkloadManager"

const route = useRoute()

const department = ref(route.params.department)
const dashboardName = ref(route.params.dashboardName)

// Breadcrumbs
const breadcrumbs = [
    {
        label: 'Dashboard',
        route: { name: 'Dashboard' }
    },
    {
        label: dashboardName.value,
        route: { name: 'PlannerEnhanced' }
    }
]

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
    calculateUtilization
} = useWorkloadManager(department.value)

// Watch for department changes
watch(() => route.params.department, (newDepartment) => {
    if (newDepartment) {
        department.value = newDepartment
        loadWorkloadData(null, null, true)
    }
}, { immediate: true })

// Enhanced UI State
const showCapacityAnalysis = ref(false)
const isTaskFormActive = ref(false)
const activeTask = ref(null)
const quickActionMenuOpen = ref(false)
const isScrolled = ref(false)
const headerRef = ref(null)

// Scroll detection for sticky header
const handleScroll = () => {
    if (headerRef.value) {
        isScrolled.value = window.scrollY > 20
    }
}

// Methods
const refreshWorkloadData = async () => {
    await loadWorkloadData(null, null, true)
}

const handleTaskClick = (taskId) => {
    activeTask.value = taskId
    isTaskFormActive.value = true
    quickActionMenuOpen.value = false
}

const handleTaskMove = async (data) => {
    await moveTask(data.taskId, data.assigneeId, data.startDate, data.endDate)
}

const handleTaskUpdate = async (data) => {
    await updateTask(data.taskId, data.updates)
}

const handleAddTask = (data) => {
    activeTask.value = null // New task
    isTaskFormActive.value = true
    quickActionMenuOpen.value = false
}

const closeTaskDetails = () => {
    activeTask.value = null
    isTaskFormActive.value = false
}

// Click outside to close menus
const handleClickOutside = (event) => {
    if (quickActionMenuOpen.value && !event.target.closest('.group')) {
        quickActionMenuOpen.value = false
    }
}

// Initialize
onMounted(() => {
    loadWorkloadData()
    window.addEventListener('scroll', handleScroll)
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
    document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.workload-header {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.workload-header.scrolled {
    @apply shadow-lg;
    backdrop-filter: blur(20px);
}

.task-item {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.task-item:hover {
    transform: translateX(4px) translateY(-2px);
    @apply shadow-lg;
}

.stat-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
    transform: translateY(-4px);
}

.enhanced-timeline {
    @apply rounded-lg overflow-hidden;
}

.enhanced-task-form {
    @apply space-y-4;
}

/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    @apply bg-gray-100 dark:bg-gray-800 rounded-full;
}

::-webkit-scrollbar-thumb {
    @apply bg-gray-300 dark:bg-gray-600 rounded-full hover:bg-gray-400 dark:hover:bg-gray-500;
}

/* Smooth animations */
.v-enter-active, .v-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-enter-from, .v-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* Loading animation */
@keyframes shimmer {
    0% {
        background-position: -200px 0;
    }
    100% {
        background-position: calc(200px + 100%) 0;
    }
}

.loading-shimmer {
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    background-size: 200px 100%;
    animation: shimmer 1.5s infinite;
}
</style>