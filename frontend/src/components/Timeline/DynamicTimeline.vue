<template>
  <div
    class="dynamic-timeline min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-blue-900/20 dark:to-indigo-900/20"
  >
    <!-- Animated Background Pattern -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div
        class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse"
      ></div>
      <div
        class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-indigo-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse delay-1000"
      ></div>
    </div>

    <!-- Enhanced Header -->
    <div
      class="relative z-10 timeline-header mb-8 p-8 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50 mx-6 mt-6"
    >
      <div
        class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8"
      >
        <!-- Left Section with Breadcrumb -->
        <div class="flex items-center gap-6">
          <Button
            variant="ghost"
            theme="gray"
            size="sm"
            @click="$emit('backToSelector')"
            class="group flex items-center gap-2 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-300 rounded-xl px-4 py-2"
          >
            <FeatherIcon
              name="arrow-left"
              class="w-4 h-4 group-hover:-translate-x-1 transition-transform"
            />
            <span class="font-medium">Back to Configurations</span>
          </Button>

          <div
            class="border-l-2 border-gradient-to-b from-blue-400 to-purple-400 pl-6"
          >
            <div class="flex items-center gap-3 mb-2">
              <div
                class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <FeatherIcon name="calendar" class="w-5 h-5 text-white" />
              </div>
              <h1
                class="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent"
              >
                {{ config?.configuration_name || "Dynamic Timeline" }}
              </h1>
            </div>
            <div
              class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
            >
              <span
                class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 rounded-md font-medium"
                >{{ config?.row_doctype }}</span
              >
              <FeatherIcon name="arrow-right" class="w-3 h-3" />
              <span
                class="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 rounded-md font-medium"
                >{{ config?.block_doctype }}</span
              >
            </div>
          </div>
        </div>

        <!-- Right Section - Enhanced Controls -->
        <div class="flex items-center gap-4">
          <!-- Date Navigation with Animation -->
          <div
            class="date-navigation flex items-center gap-2 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl p-3 shadow-lg border border-gray-200/50 dark:border-gray-700/50"
          >
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="navigateDate(-1)"
              class="group hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-xl transition-all duration-300"
            >
              <FeatherIcon
                name="chevron-left"
                class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform"
              />
            </Button>

            <div
              class="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white font-semibold min-w-[240px] text-center shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer group"
            >
              <div class="group-hover:scale-105 transition-transform">
                {{ formatDateRange() }}
              </div>
            </div>

            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="navigateDate(1)"
              class="group hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-xl transition-all duration-300"
            >
              <FeatherIcon
                name="chevron-right"
                class="w-4 h-4 group-hover:translate-x-0.5 transition-transform"
              />
            </Button>

            <div class="h-6 w-px bg-gray-300 dark:bg-gray-600 mx-2"></div>

            <Button
              variant="ghost"
              theme="blue"
              size="sm"
              @click="goToToday"
              class="hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-xl transition-all duration-300 px-4 py-2 font-medium"
            >
              <FeatherIcon name="calendar" class="w-4 h-4 mr-2" />
              Today
            </Button>
          </div>

          <!-- Enhanced View Mode Toggle -->
          <div
            class="view-toggle flex bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-2xl p-2 shadow-lg border border-gray-200/50 dark:border-gray-700/50"
          >
            <button
              v-for="mode in viewModes"
              :key="mode.value"
              @click="currentViewMode = mode.value"
              :class="[
                'px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 flex items-center gap-2 relative overflow-hidden',
                currentViewMode === mode.value
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg transform scale-105'
                  : 'text-gray-600 dark:text-gray-300 hover:text-white hover:bg-gradient-to-r hover:from-blue-400 hover:to-purple-500 hover:scale-102',
              ]"
            >
              <FeatherIcon :name="mode.icon" class="w-4 h-4 relative z-10" />
              <span class="relative z-10">{{ mode.label }}</span>
              <div
                v-if="currentViewMode === mode.value"
                class="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 animate-pulse"
              ></div>
            </button>
          </div>

          <!-- Enhanced Refresh Button -->
          <Button
            variant="ghost"
            theme="gray"
            size="sm"
            @click="refreshData"
            :loading="loading"
            class="group hover:bg-green-50 dark:hover:bg-green-900/30 rounded-xl transition-all duration-300 p-3"
          >
            <FeatherIcon
              name="refresh-cw"
              :class="[
                'w-4 h-4 transition-all duration-300',
                loading ? 'animate-spin' : 'group-hover:rotate-180',
              ]"
            />
          </Button>
        </div>
      </div>

      <!-- Enhanced Stats Bar with Animations -->
      <div
        class="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl border border-blue-200/50 dark:border-blue-700/50 backdrop-blur-sm"
      >
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-8">
            <div
              class="group flex items-center gap-3 hover:scale-105 transition-transform cursor-pointer"
            >
              <div class="relative">
                <div
                  class="w-4 h-4 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full shadow-lg"
                ></div>
                <div
                  class="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full animate-ping opacity-20"
                ></div>
              </div>
              <div>
                <div class="font-bold text-xl text-gray-800 dark:text-white">
                  {{ rows.length }}
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400">
                  {{ config?.row_doctype || "Rows" }}
                </div>
              </div>
            </div>

            <div
              class="group flex items-center gap-3 hover:scale-105 transition-transform cursor-pointer"
            >
              <div class="relative">
                <div
                  class="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full shadow-lg"
                ></div>
                <div
                  class="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full animate-ping opacity-20"
                ></div>
              </div>
              <div>
                <div class="font-bold text-xl text-gray-800 dark:text-white">
                  {{ blocks.length }}
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400">
                  {{ config?.block_doctype || "Blocks" }}
                </div>
              </div>
            </div>

            <div
              class="group flex items-center gap-3 hover:scale-105 transition-transform cursor-pointer"
            >
              <div class="relative">
                <div
                  class="w-4 h-4 bg-gradient-to-r from-amber-500 to-orange-600 rounded-full shadow-lg"
                ></div>
                <div
                  class="absolute inset-0 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full animate-ping opacity-20"
                ></div>
              </div>
              <div>
                <div class="font-bold text-xl text-gray-800 dark:text-white">
                  {{ unassignedBlocks.length }}
                </div>
                <div class="text-xs text-gray-600 dark:text-gray-400">
                  Unassigned
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <FeatherIcon name="clock" class="w-4 h-4" />
            <span class="font-medium">{{ formatDateRange() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Loading State -->
    <div
      v-if="loading"
      class="relative z-10 flex items-center justify-center py-20"
    >
      <div
        class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/20 dark:border-gray-700/50"
      >
        <div class="flex flex-col items-center gap-6">
          <div class="relative">
            <div
              class="w-12 h-12 border-4 border-blue-200 dark:border-blue-800 rounded-full"
            ></div>
            <div
              class="absolute inset-0 w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"
            ></div>
          </div>
          <div class="text-center">
            <div
              class="text-lg font-semibold text-gray-900 dark:text-white mb-2"
            >
              Loading Timeline Data
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Please wait while we fetch your data...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Error State -->
    <div v-else-if="error" class="relative z-10 mx-6">
      <div
        class="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 border border-red-200/50 dark:border-red-700/50 rounded-2xl p-8 backdrop-blur-sm shadow-lg"
      >
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">
            <div
              class="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-600 rounded-full flex items-center justify-center shadow-lg"
            >
              <FeatherIcon name="alert-triangle" class="w-6 h-6 text-white" />
            </div>
          </div>
          <div class="flex-1">
            <h3
              class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2"
            >
              Unable to Load Timeline Data
            </h3>
            <p class="text-red-700 dark:text-red-300 mb-4">{{ error }}</p>
            <Button
              variant="outline"
              theme="red"
              size="sm"
              @click="refreshData"
              class="hover:bg-red-50 dark:hover:bg-red-900/30 transition-all duration-300"
            >
              <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Timeline Grid -->
    <div v-else class="relative z-10 timeline-grid mx-6 mb-6">
      <div
        class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl border border-white/20 dark:border-gray-700/50 overflow-hidden shadow-2xl"
      >
        <DynamicTimelineGrid
          :config="config"
          :rows="rows"
          :blocks="blocks"
          :dateColumns="dateColumns"
          :loading="loading"
          @blockMove="handleBlockMove"
          @blockClick="handleBlockClick"
          @addBlock="handleAddBlock"
          class="enhanced-grid"
        />
      </div>
    </div>

    <!-- Enhanced Block Details Modal -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="selectedBlock"
        class="fixed inset-0 bg-black/60 backdrop-blur-lg flex items-center justify-center z-50 p-4"
        @click.self="closeBlockDetails"
      >
        <div
          class="bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50 w-full max-w-2xl max-h-[90vh] overflow-hidden"
        >
          <div
            class="flex items-center justify-between p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg"
              >
                <FeatherIcon name="file-text" class="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ config?.block_doctype }} Details
                </h2>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  View and edit block information
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click="closeBlockDetails"
              class="hover:bg-red-50 dark:hover:bg-red-900/30 rounded-xl transition-all duration-300 p-2"
            >
              <FeatherIcon name="x" class="w-5 h-5" />
            </Button>
          </div>

          <div class="p-6 overflow-y-auto">
            <DynamicBlockDetails
              :block="selectedBlock"
              :config="config"
              @close="closeBlockDetails"
              @update="handleBlockUpdate"
            />
          </div>
        </div>
      </div>
    </Transition>

    <!-- Floating Action Button -->
    <div class="fixed bottom-6 right-6 z-40">
      <div class="relative group">
        <Button
          variant="ghost"
          theme="blue"
          size="lg"
          @click="showQuickActions = !showQuickActions"
          class="w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-110"
        >
          <FeatherIcon name="plus" class="w-6 h-6 text-white" />
        </Button>

        <!-- Quick Actions Menu -->
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 translate-y-4 scale-95"
          enter-to-class="opacity-100 translate-y-0 scale-100"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0 scale-100"
          leave-to-class="opacity-0 translate-y-4 scale-95"
        >
          <div
            v-if="showQuickActions"
            class="absolute bottom-16 right-0 bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50 p-4 min-w-[200px]"
          >
            <div class="space-y-2">
              <button
                class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-200 text-left"
              >
                <FeatherIcon name="plus-circle" class="w-5 h-5 text-blue-500" />
                <span class="font-medium">Add Block</span>
              </button>
              <button
                class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-green-50 dark:hover:bg-green-900/30 transition-all duration-200 text-left"
              >
                <FeatherIcon name="download" class="w-5 h-5 text-green-500" />
                <span class="font-medium">Export</span>
              </button>
              <button
                class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-purple-50 dark:hover:bg-purple-900/30 transition-all duration-200 text-left"
              >
                <FeatherIcon name="settings" class="w-5 h-5 text-purple-500" />
                <span class="font-medium">Settings</span>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { Button, FeatherIcon } from "frappe-ui";
import { call } from "frappe-ui";
import DynamicTimelineGrid from "./DynamicTimelineGrid.vue";
import DynamicBlockDetails from "./DynamicBlockDetails.vue";
import { toast } from "../../composables/useToast";

const props = defineProps({
  configuration: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["backToSelector"]);

// Reactive state
const config = ref(null);
const rows = ref([]);
const blocks = ref([]);
const loading = ref(false);
const error = ref(null);
const selectedBlock = ref(null);
const showQuickActions = ref(false);

// View state
const currentViewMode = ref("week");
const currentDate = ref(new Date());

// Constants
const viewModes = [
  { label: "Week", value: "week", icon: "calendar" },
  { label: "Month", value: "month", icon: "calendar" },
  { label: "2 Weeks", value: "biweek", icon: "calendar" },
];

// Computed properties
const dateColumns = computed(() => {
  const columns = [];
  const today = new Date();
  let startDate, daysToShow;

  switch (currentViewMode.value) {
    case "week":
      startDate = getWeekStart(currentDate.value);
      daysToShow = 7;
      break;
    case "biweek":
      startDate = getWeekStart(currentDate.value);
      daysToShow = 14;
      break;
    case "month":
      startDate = new Date(
        currentDate.value.getFullYear(),
        currentDate.value.getMonth(),
        1,
      );
      daysToShow = getDaysInMonth(currentDate.value);
      break;
    default:
      startDate = getWeekStart(currentDate.value);
      daysToShow = 7;
  }

  for (let i = 0; i < daysToShow; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);

    const isToday = date.toDateString() === today.toDateString();
    const isWeekend = date.getDay() === 0 || date.getDay() === 6;

    columns.push({
      key: date.toISOString().split("T")[0],
      date: date,
      label: date.getDate().toString(),
      sublabel: date.toLocaleDateString("en-US", { weekday: "short" }),
      isToday,
      isWeekend,
    });
  }

  return columns;
});

const unassignedBlocks = computed(() => {
  return blocks.value.filter((block) => !block.row_id);
});

// Methods
const loadTimelineData = async () => {
  if (!props.configuration) return;

  loading.value = true;
  error.value = null;

  try {
    const startDate = dateColumns.value[0]?.date.toISOString().split("T")[0];
    const endDate = dateColumns.value[dateColumns.value.length - 1]?.date
      .toISOString()
      .split("T")[0];

    const response = await call("planner.api.get_timeline_data", {
      configuration_name: props.configuration.name,
      start_date: startDate,
      end_date: endDate,
      filters: {},
    });

    if (response.success) {
      config.value = response.config;
      rows.value = response.rows || [];
      blocks.value = response.blocks || [];
    } else {
      throw new Error(response.error || "Failed to load timeline data");
    }
  } catch (err) {
    error.value = err.message || "Failed to load timeline data";
    console.error("Error loading timeline data:", err);
  } finally {
    loading.value = false;
  }
};

const refreshData = () => {
  loadTimelineData();
};

const navigateDate = (direction) => {
  const newDate = new Date(currentDate.value);
  let daysToMove;

  switch (currentViewMode.value) {
    case "week":
      daysToMove = 7;
      break;
    case "biweek":
      daysToMove = 14;
      break;
    case "month":
      newDate.setMonth(newDate.getMonth() + direction);
      currentDate.value = newDate;
      return;
    default:
      daysToMove = 7;
  }

  newDate.setDate(newDate.getDate() + direction * daysToMove);
  currentDate.value = newDate;
};

const goToToday = () => {
  currentDate.value = new Date();
};

const formatDateRange = () => {
  if (!dateColumns.value.length) return "";

  switch (currentViewMode.value) {
    case "week":
    case "biweek":
      const start = dateColumns.value[0].date;
      const end = dateColumns.value[dateColumns.value.length - 1].date;
      return `${start.toLocaleDateString("en-US", { month: "short", day: "numeric" })} - ${end.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`;
    case "month":
      return currentDate.value.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
      });
    default:
      return "";
  }
};

const getWeekStart = (date) => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(d.setDate(diff));
};

const getDaysInMonth = (date) => {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
};

const handleBlockMove = async (data) => {
  try {
    const response = await call("planner.api.update_block_assignment", {
      block_doctype: config.value.block_doctype,
      block_name: data.blockId,
      new_row_assignment: data.newRowId,
      new_date: data.newDate,
      config_name: config.value.name,
    });

    if (response.success) {
      await loadTimelineData();

      toast.success("Block moved successfully");
    } else {
      throw new Error(response.error || "Failed to move block");
    }
  } catch (err) {
    console.error("Error moving block:", err);
    toast.error("Failed to move block: " + err.message);
  }
};

const handleBlockClick = (blockId) => {
  const block = blocks.value.find((b) => b.id === blockId);
  selectedBlock.value = block;
};

const handleAddBlock = (data) => {
  console.log("Add block:", data);
};

const handleBlockUpdate = async (data) => {
  try {
    console.log("Update block:", data);
    closeBlockDetails();
    await loadTimelineData();
  } catch (err) {
    console.error("Error updating block:", err);
  }
};

const closeBlockDetails = () => {
  selectedBlock.value = null;
};

// Watch for configuration changes
watch(
  () => props.configuration,
  () => {
    if (props.configuration) {
      loadTimelineData();
    }
  },
  { immediate: true },
);

// Watch for date/view changes
watch([currentDate, currentViewMode], () => {
  loadTimelineData();
});

// Initialize
onMounted(() => {
  if (props.configuration) {
    loadTimelineData();
  }
});
</script>

<style scoped>
.dynamic-timeline {
  @apply w-full min-h-screen relative;
}

.timeline-grid {
  min-height: 600px;
}

/* Enhanced animations */
.enhanced-grid {
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Smooth transitions for all interactive elements */
* {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}

/* Backdrop blur support */
@supports (backdrop-filter: blur(20px)) {
  .backdrop-blur-xl {
    backdrop-filter: blur(20px);
  }

  .backdrop-blur-sm {
    backdrop-filter: blur(8px);
  }

  .backdrop-blur-lg {
    backdrop-filter: blur(16px);
  }
}

/* Enhanced button hover effects */
.group:hover .group-hover\:scale-105 {
  transform: scale(1.05);
}

.group:hover .group-hover\:scale-102 {
  transform: scale(1.02);
}

/* Gradient text support */
.bg-clip-text {
  -webkit-background-clip: text;
  background-clip: text;
}

/* Animation delays */
.delay-1000 {
  animation-delay: 1000ms;
}

/* Enhanced shadows */
.shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* Floating action button pulse */
.fixed .group:hover > button {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1.1);
  }
  50% {
    transform: scale(1.15);
  }
}
</style>
