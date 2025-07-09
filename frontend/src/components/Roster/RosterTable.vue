<template>
  <div
    class="rounded-lg border overflow-auto max-h-[45rem] bg-white dark:bg-gray-900"
    :class="loading && 'animate-pulse pointer-events-none'"
  >
    <table class="border-separate border-spacing-0 w-full">
      <thead>
        <tr class="sticky top-0 bg-white dark:bg-gray-900 z-10">
          <!-- Employee Search -->
          <th class="p-2 border-b border-gray-200 dark:border-gray-700">
            <Autocomplete
              :options="employeeSearchOptions"
              v-model="employeeSearch"
              placeholder="Search Team Member"
              :multiple="true"
              class="min-w-64"
            />
          </th>

          <!-- Day/Date Row -->
          <th
            v-for="(day, idx) in daysOfPeriod"
            :key="idx"
            class="font-medium border-b border-gray-200 dark:border-gray-700 text-center min-w-36"
            :class="{
              'border-l border-gray-200 dark:border-gray-700': idx,
              'bg-blue-50 dark:bg-blue-900/20': day.isToday,
              'bg-gray-50 dark:bg-gray-800': day.isWeekend,
            }"
          >
            <div class="p-2">
              <div class="font-semibold text-sm">{{ day.dayName }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ dayjs(day.date).format("DD") }}
              </div>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(assignee, rowIdx) in filteredAssignees"
          :key="assignee.name"
        >
          <!-- Employee Column -->
          <td
            class="px-2 py-4 z-[5] sticky left-0 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700"
            :class="{ 'border-t border-gray-200 dark:border-gray-700': rowIdx }"
          >
            <div class="flex items-center gap-3">
              <Avatar
                :label="assignee.employee_name || assignee.name"
                :image="assignee.image"
                size="2xl"
              />
              <div class="flex flex-col min-w-0 flex-1">
                <div
                  class="truncate text-base font-medium text-gray-900 dark:text-white"
                >
                  {{ assignee.employee_name || assignee.name }}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {{ assignee.department || assignee.designation }}
                </div>
                <div v-if="assignee.workload_percentage" class="mt-1">
                  <div class="flex items-center gap-2">
                    <div
                      class="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
                    >
                      <div
                        class="h-full rounded-full transition-all duration-300"
                        :class="getWorkloadColor(assignee.workload_percentage)"
                        :style="{
                          width:
                            Math.min(assignee.workload_percentage, 100) + '%',
                        }"
                      ></div>
                    </div>
                    <span
                      class="text-xs font-medium"
                      :class="
                        getWorkloadTextColor(assignee.workload_percentage)
                      "
                    >
                      {{ Math.round(assignee.workload_percentage) }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </td>

          <!-- Task/Workload Cells -->
          <td
            v-for="(day, colIdx) in daysOfPeriod"
            :key="colIdx"
            class="p-1.5 align-top"
            :class="{
              'border-l border-gray-200 dark:border-gray-700': colIdx,
              'border-t border-gray-200 dark:border-gray-700': rowIdx,
              'bg-blue-50 dark:bg-blue-900/20': day.isToday,
              'bg-gray-50 dark:bg-gray-800': day.isWeekend,
              'bg-green-50 dark:bg-green-900/20':
                getAssignmentsForDay(assignee.name, day.date).length > 0,
              'bg-gray-50 dark:bg-gray-800':
                dropCell.assignee === assignee.name &&
                dropCell.date === day.date &&
                !isHolidayOrLeave(assignee.name, day.date),
            }"
            @mouseenter="
              hoveredCell.assignee = assignee.name;
              hoveredCell.date = day.date;
            "
            @mouseleave="
              hoveredCell.assignee = '';
              hoveredCell.date = '';
            "
            @dragover.prevent
            @dragenter="
              dropCell.assignee = assignee.name;
              dropCell.date = day.date;
            "
            @drop="handleAssignmentDrop(assignee.name, day.date)"
            @click="handleCellClick(assignee.name, day.date)"
          >
            <!-- Holiday/Leave Display -->
            <div
              v-if="isHolidayOrLeave(assignee.name, day.date)"
              class="blocked-cell text-center p-2 text-sm text-gray-500 dark:text-gray-400"
            >
              <div class="font-medium">
                {{ getHolidayOrLeaveText(assignee.name, day.date) }}
              </div>
            </div>

            <!-- Tasks -->
            <div v-else class="flex flex-col space-y-1.5">
              <div
                v-for="assignment in getAssignmentsForDay(
                  assignee.name,
                  day.date,
                )"
                :key="assignment.name"
                @mouseenter="
                  hoveredCell.task = assignment.name;
                  hoveredCell.taskData = assignment;
                "
                @mouseleave="
                  hoveredCell.task = '';
                  hoveredCell.taskData = null;
                "
                :draggable="true"
                @dragstart="handleAssignmentDragStart($event, assignment)"
                @dragend="handleAssignmentDragEnd"
                class="rounded border-2 p-2 cursor-pointer transition-all duration-200 hover:shadow-md"
                :class="[
                  getAssignmentStatusClass(assignment),
                  dropCell.assignee === assignee.name &&
                    dropCell.date === day.date &&
                    hoveredCell.task === assignment.name &&
                    'opacity-50',
                ]"
                :style="getAssignmentStyle(assignment)"
                @click.stop="handleAssignmentClick(assignment)"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1 min-w-0">
                    <div
                      class="truncate mb-1 text-sm font-medium text-gray-900 dark:text-white"
                    >
                      {{ assignment.task_name }}
                    </div>
                    <div
                      class="text-xs text-gray-600 dark:text-gray-300 space-y-1"
                    >
                      <div class="flex items-center gap-1">
                        <FeatherIcon name="clock" class="w-3 h-3" />
                        <span
                          >{{ assignment.start_time }} -
                          {{ assignment.end_time }}</span
                        >
                      </div>
                      <div
                        v-if="assignment.task_priority"
                        class="flex items-center gap-1"
                      >
                        <FeatherIcon name="flag" class="w-3 h-3" />
                        <span class="capitalize">{{
                          assignment.task_priority
                        }}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    v-if="hoveredCell.task === assignment.name"
                    @click.stop="handleDeleteAssignment(assignment)"
                    class="opacity-75 hover:opacity-100 text-red-500 hover:text-red-700 p-1 rounded transition-colors"
                    title="Delete assignment"
                  >
                    <FeatherIcon name="x" class="w-3 h-3" />
                  </button>
                </div>
              </div>

              <!-- Add Task Button -->
              <Button
                variant="outline"
                icon="plus"
                class="border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 w-full transition-all duration-200 opacity-60 hover:opacity-100"
                @click.stop="handleAddTask(assignee.name, day.date)"
                size="sm"
              >
                Add Task
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { Avatar, Autocomplete, FeatherIcon, Button } from "frappe-ui";
import { dayjs } from "@/utils/dateUtils";

const props = defineProps({
  assignees: {
    type: Array,
    default: () => [],
  },
  assignments: {
    type: Array,
    default: () => [],
  },
  dateRange: {
    type: Array,
    default: () => [],
  },
  viewMode: {
    type: String,
    default: "week",
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "cell-click",
  "assignment-click",
  "assignment-drag",
  "assignment-drop",
  "assignment-delete",
]);

// Reactive state
const employeeSearch = ref([]);
const hoveredCell = ref({
  assignee: "",
  date: "",
  task: "",
  taskData: null,
});
const dropCell = ref({ assignee: "", date: "", task: "" });

// Computed properties
const daysOfPeriod = computed(() => {
  const today = dayjs();
  return props.dateRange.map((date) => {
    const isToday = date.isSame(today, "day");
    const isWeekend = date.day() === 0 || date.day() === 6;

    return {
      date: date.format("YYYY-MM-DD"),
      dayName: date.format("ddd"),
      isToday,
      isWeekend,
    };
  });
});

const filteredAssignees = computed(() => {
  if (!employeeSearch.value?.length) {
    return props.assignees;
  }
  return props.assignees.filter((assignee) =>
    employeeSearch.value.some((item) => item.value === assignee.name),
  );
});

const employeeSearchOptions = computed(() => {
  return props.assignees.map((assignee) => ({
    value: assignee.name,
    label: `${assignee.name}: ${assignee.employee_name || assignee.name}`,
  }));
});

// Methods
const getAssignmentsForDay = (assigneeName, date) => {
  return props.assignments.filter((assignment) => {
    return assignment.assignee === assigneeName && assignment.date === date;
  });
};

const isHolidayOrLeave = (assigneeName, date) => {
  // Placeholder for holiday/leave logic
  // This would integrate with HRMS holiday and leave data
  return false;
};

const getHolidayOrLeaveText = (assigneeName, date) => {
  // Placeholder for holiday/leave text
  return "Holiday";
};

const getAssignmentStatusClass = (assignment) => {
  const statusClasses = {
    Assigned:
      "border-blue-200 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/20",
    Active:
      "border-yellow-200 bg-yellow-50 dark:border-yellow-700 dark:bg-yellow-900/20",
    Completed:
      "border-green-200 bg-green-50 dark:border-green-700 dark:bg-green-900/20",
    Cancelled:
      "border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900/20",
    Pending:
      "border-purple-200 bg-purple-50 dark:border-purple-700 dark:bg-purple-900/20",
  };
  return statusClasses[assignment.status] || statusClasses["Assigned"];
};

const getAssignmentStyle = (assignment) => {
  const priorityColors = {
    Low: "#10B981",
    Medium: "#F59E0B",
    High: "#EF4444",
    Urgent: "#DC2626",
  };
  return {
    borderColor: priorityColors[assignment.task_priority] || "#3B82F6",
  };
};

const getWorkloadColor = (percentage) => {
  if (percentage >= 100) return "bg-red-500";
  if (percentage >= 80) return "bg-yellow-500";
  if (percentage >= 60) return "bg-blue-500";
  return "bg-green-500";
};

const getWorkloadTextColor = (percentage) => {
  if (percentage >= 100) return "text-red-600 dark:text-red-400";
  if (percentage >= 80) return "text-yellow-600 dark:text-yellow-400";
  if (percentage >= 60) return "text-blue-600 dark:text-blue-400";
  return "text-green-600 dark:text-green-400";
};

const handleAssignmentClick = (assignment) => {
  emit("assignment-click", assignment);
};

const handleAssignmentDragStart = (event, assignment) => {
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData(
      "text/plain",
      JSON.stringify({
        assignment: assignment,
        sourceAssignee: assignment.assignee,
        sourceDate: assignment.date,
      }),
    );
  }
  emit("assignment-drag", assignment);
};

const handleAssignmentDragEnd = () => {
  if (!props.loading) {
    dropCell.value = { assignee: "", date: "", task: "" };
  }
};

const handleAssignmentDrop = (assigneeName, date) => {
  const event = window.event;
  if (event && event.dataTransfer) {
    const data = JSON.parse(event.dataTransfer.getData("text/plain"));
    if (
      data.assignment &&
      (data.sourceAssignee !== assigneeName || data.sourceDate !== date)
    ) {
      emit("assignment-drop", data.assignment, date, assigneeName);
    }
  }
};

const handleAddTask = (assigneeName, date) => {
  console.log("🔥 RosterTable handleAddTask called:", { assigneeName, date });
  const assignee = props.assignees.find((a) => a.name === assigneeName);
  console.log("🔥 Found assignee:", assignee);
  if (assignee) {
    console.log("🔥 Emitting cell-click event");
    emit("cell-click", date, assignee);
  }
};

const handleDeleteAssignment = (assignment) => {
  emit("assignment-delete", assignment);
};

const handleCellClick = (assigneeName, date) => {
  console.log("🔥 RosterTable handleCellClick called:", { assigneeName, date });
  const assignee = props.assignees.find((a) => a.name === assigneeName);
  if (assignee) {
    emit("cell-click", date, assignee);
  }
};

// Watch for changes
watch(
  () => props.loading,
  (val) => {
    if (!val) {
      dropCell.value = { assignee: "", date: "", task: "" };
    }
  },
);
</script>

<style scoped>
.blocked-cell {
  @apply text-sm text-gray-500 text-center p-2;
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
</style>
