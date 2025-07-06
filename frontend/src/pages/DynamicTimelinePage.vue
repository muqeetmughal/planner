<template>
  <div class="dynamic-timeline-page min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Page Header -->
    <div class="page-header bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Left Section -->
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <FeatherIcon name="calendar" class="w-4 h-4 text-white" />
              </div>
              <div>
                <h1 class="text-xl font-semibold text-gray-900 dark:text-white">
                  Dynamic Timeline
                </h1>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Flexible timeline views for any DocType combination
                </p>
              </div>
            </div>
          </div>

          <!-- Right Section -->
          <div class="flex items-center gap-3">
            <!-- Help Button -->
            <Button variant="ghost" theme="gray" size="sm" @click="showHelp = true">
              <FeatherIcon name="help-circle" class="w-4 h-4 mr-2" />
              Help
            </Button>

            <!-- Settings Button -->
            <Button variant="ghost" theme="gray" size="sm" @click="showSettings = true">
              <FeatherIcon name="settings" class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Configuration Selection View -->
        <div v-if="currentView === 'selector'" class="configuration-view">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Choose Timeline Configuration
            </h2>
            <p class="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Select a timeline configuration to view your data in a dynamic, interactive timeline. 
              Each configuration defines how different DocTypes are mapped to timeline rows, blocks, and dates.
            </p>
          </div>

          <ConfigurationSelector 
            @configurationSelected="handleConfigurationSelected"
            @error="handleError"
          />
        </div>

        <!-- Dynamic Timeline View -->
        <div v-else-if="currentView === 'timeline'" class="timeline-view">
          <DynamicTimeline 
            :configuration="selectedConfiguration"
            @backToSelector="handleBackToSelector"
          />
        </div>

        <!-- Loading State -->
        <div v-else-if="currentView === 'loading'" class="loading-view flex items-center justify-center py-20">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-xl border border-gray-200 dark:border-gray-700">
            <div class="flex flex-col items-center gap-4">
              <div class="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <div class="text-center">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  Loading Timeline
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Preparing your dynamic timeline view...
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="currentView === 'error'" class="error-view">
          <div class="max-w-md mx-auto">
            <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
              <FeatherIcon name="alert-circle" class="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
                Something went wrong
              </h3>
              <p class="text-red-700 dark:text-red-300 text-sm mb-4">
                {{ errorMessage }}
              </p>
              <div class="flex items-center justify-center gap-3">
                <Button variant="solid" theme="red" size="sm" @click="handleRetry">
                  <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
                  Retry
                </Button>
                <Button variant="outline" theme="gray" size="sm" @click="handleBackToSelector">
                  Back to Configurations
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Help Modal -->
    <div 
      v-if="showHelp" 
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showHelp = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-hidden">
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Dynamic Timeline Help
          </h2>
          <Button variant="ghost" theme="gray" size="sm" @click="showHelp = false">
            <FeatherIcon name="x" class="w-4 h-4" />
          </Button>
        </div>
        
        <div class="p-6 overflow-y-auto">
          <div class="space-y-6">
            <div>
              <h3 class="text-md font-semibold text-gray-900 dark:text-white mb-2">
                What is Dynamic Timeline?
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Dynamic Timeline allows you to create flexible timeline views using any combination of DocTypes. 
                You can map different DocTypes to timeline rows, blocks, and dates to visualize your data in new ways.
              </p>
            </div>

            <div>
              <h3 class="text-md font-semibold text-gray-900 dark:text-white mb-2">
                How to Use
              </h3>
              <ol class="list-decimal list-inside space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>Select a timeline configuration from the available options</li>
                <li>The timeline will load with your configured DocType mapping</li>
                <li>Drag and drop blocks between rows and dates to reassign them</li>
                <li>Click on blocks to view detailed information</li>
                <li>Use the date navigation to move through different time periods</li>
              </ol>
            </div>

            <div>
              <h3 class="text-md font-semibold text-gray-900 dark:text-white mb-2">
                Example Configurations
              </h3>
              <div class="space-y-3">
                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                  <div class="font-medium text-blue-900 dark:text-blue-100 text-sm">
                    Workstation Planning
                  </div>
                  <div class="text-xs text-blue-700 dark:text-blue-300 mt-1">
                    Workstations (rows) → Work Orders (blocks) → Dates (columns)
                  </div>
                </div>
                <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3">
                  <div class="font-medium text-green-900 dark:text-green-100 text-sm">
                    Resource Scheduling
                  </div>
                  <div class="text-xs text-green-700 dark:text-green-300 mt-1">
                    Resources (rows) → Bookings (blocks) → Dates (columns)
                  </div>
                </div>
                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
                  <div class="font-medium text-purple-900 dark:text-purple-100 text-sm">
                    Team Planning
                  </div>
                  <div class="text-xs text-purple-700 dark:text-purple-300 mt-1">
                    Users (rows) → Tasks (blocks) → Dates (columns)
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div 
      v-if="showSettings" 
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      @click.self="showSettings = false"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 w-full max-w-md">
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Settings
          </h2>
          <Button variant="ghost" theme="gray" size="sm" @click="showSettings = false">
            <FeatherIcon name="x" class="w-4 h-4" />
          </Button>
        </div>
        
        <div class="p-6">
          <div class="space-y-4">
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                Default View Mode
              </label>
              <select class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="week">Week View</option>
                <option value="month">Month View</option>
                <option value="biweek">2 Week View</option>
              </select>
            </div>
            
            <div>
              <label class="flex items-center gap-2">
                <input type="checkbox" class="rounded border-gray-300 dark:border-gray-600" />
                <span class="text-sm text-gray-700 dark:text-gray-300">Auto-refresh timeline data</span>
              </label>
            </div>
            
            <div>
              <label class="flex items-center gap-2">
                <input type="checkbox" class="rounded border-gray-300 dark:border-gray-600" />
                <span class="text-sm text-gray-700 dark:text-gray-300">Show weekend columns</span>
              </label>
            </div>
          </div>
          
          <div class="mt-6 flex justify-end">
            <Button variant="solid" theme="blue" size="sm" @click="showSettings = false">
              Save Settings
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'
import ConfigurationSelector from '../components/Timeline/ConfigurationSelector.vue'
import DynamicTimeline from '../components/Timeline/DynamicTimeline.vue'

// Reactive state
const currentView = ref('selector') // 'selector', 'timeline', 'loading', 'error'
const selectedConfiguration = ref(null)
const errorMessage = ref('')
const showHelp = ref(false)
const showSettings = ref(false)

// Methods
const handleConfigurationSelected = (configuration) => {
  selectedConfiguration.value = configuration
  currentView.value = 'loading'
  
  // Simulate loading delay
  setTimeout(() => {
    currentView.value = 'timeline'
  }, 1000)
}

const handleBackToSelector = () => {
  currentView.value = 'selector'
  selectedConfiguration.value = null
  errorMessage.value = ''
}

const handleError = (error) => {
  errorMessage.value = error
  currentView.value = 'error'
}

const handleRetry = () => {
  if (selectedConfiguration.value) {
    currentView.value = 'loading'
    setTimeout(() => {
      currentView.value = 'timeline'
    }, 1000)
  } else {
    handleBackToSelector()
  }
}

// Initialize
onMounted(() => {
  // Check if there's a configuration in URL params
  const urlParams = new URLSearchParams(window.location.search)
  const configName = urlParams.get('config')
  
  if (configName) {
    // TODO: Load specific configuration
    console.log('Loading configuration from URL:', configName)
  }
})
</script>

<style scoped>
.dynamic-timeline-page {
  min-height: 100vh;
}

/* Smooth transitions */
.configuration-view,
.timeline-view,
.loading-view,
.error-view {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

/* Modal animations */
.fixed.inset-0 {
  animation: modalFadeIn 0.2s ease-out;
}

@keyframes modalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>