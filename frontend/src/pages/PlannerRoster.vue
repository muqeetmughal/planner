<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Enhanced Header -->
    <RosterHeader
      :title="pageTitle"
      :view-mode="viewMode"
      :current-date="currentDate"
      :current-department="selectedDepartment"
      :current-company="selectedCompany"
      :departments="departments"
      :companies="companies"
      :stats="workloadStats"
      :loading="loading"
      @view-mode-change="handleViewModeChange"
      @date-change="handleDateChange"
      @department-change="handleDepartmentChange"
      @company-change="handleCompanyChange"
      @refresh="handleRefresh"
      @add-task="handleAddTask"
    />

    <!-- Main Content -->
    <div class="px-6 pb-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="flex items-center gap-3 text-gray-500 dark:text-gray-400">
          <div
            class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"
          ></div>
          <span>Loading team planner...</span>
        </div>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-6"
      >
        <div class="flex items-center gap-3">
          <FeatherIcon name="alert-circle" class="w-6 h-6 text-red-500" />
          <div>
            <h3 class="font-semibold text-red-800 dark:text-red-200">
              Error Loading Data
            </h3>
            <p class="text-sm text-red-600 dark:text-red-300 mt-1">
              {{ error }}
            </p>
            <Button
              variant="solid"
              theme="red"
              size="sm"
              @click="handleRefresh"
              class="mt-3"
            >
              <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!assignees.length"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center"
      >
        <div
          class="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <FeatherIcon name="users" class="w-8 h-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No Team Members Found
        </h3>
        <p class="text-gray-500 dark:text-gray-400 mb-6">
          {{
            selectedDepartment
              ? `No team members found in ${selectedDepartment} department.`
              : "No team members available for planning."
          }}
        </p>
        <div class="flex justify-center gap-3">
          <Button variant="ghost" theme="gray" @click="handleRefresh">
            <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="solid" theme="blue" @click="handleAddTask">
            <FeatherIcon name="plus" class="w-4 h-4 mr-2" />
            Add Task
          </Button>
        </div>
      </div>

      <!-- Roster Table -->
      <RosterTable
        v-else
        :assignees="assignees"
        :assignments="assignments"
        :date-range="dateRange"
        :view-mode="viewMode"
        :loading="loading"
        @cell-click="handleCellClick"
        @assignment-click="handleAssignmentClick"
        @assignment-drag="handleAssignmentDrag"
        @assignment-drop="handleAssignmentDrop"
        @assignment-delete="handleAssignmentDelete"
      />
    </div>

    <!-- Task Assignment Dialog -->
    <TaskAssignmentDialog
      v-model="showAssignmentDialog"
      :selected-date="selectedDate"
      :selected-assignee="selectedAssignee"
      :existing-assignment="selectedAssignment"
      :existing-assignments="assignments"
      @submit="handleAssignmentSubmit"
      @cancel="handleAssignmentCancel"
    />

    <!-- Confirmation Dialog -->
    <Dialog
      v-model="showConfirmDialog"
      :options="{
        title: confirmDialog.title,
        size: 'md',
        actions: [
          {
            label: 'Cancel',
            theme: 'gray',
            variant: 'ghost',
            onClick: () => (showConfirmDialog = false),
          },
          {
            label: confirmDialog.confirmLabel,
            theme: confirmDialog.theme,
            variant: 'solid',
            loading: confirmDialog.loading,
            onClick: confirmDialog.onConfirm,
          },
        ],
      }"
    >
      <div class="flex items-start gap-3">
        <FeatherIcon
          :name="confirmDialog.icon"
          :class="[
            'w-6 h-6 mt-1',
            confirmDialog.theme === 'red' ? 'text-red-500' : 'text-amber-500',
          ]"
        />
        <div>
          <p class="text-gray-700 dark:text-gray-300">
            {{ confirmDialog.message }}
          </p>
          <p
            v-if="confirmDialog.details"
            class="text-sm text-gray-500 dark:text-gray-400 mt-2"
          >
            {{ confirmDialog.details }}
          </p>
        </div>
      </div>
    </Dialog>

    <!-- Toast Notifications -->
    <div class="fixed bottom-4 right-4 z-50 space-y-2">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border max-w-sm transform transition-all duration-300',
          toast.type === 'success'
            ? 'bg-green-50 border-green-200 text-green-800'
            : '',
          toast.type === 'error' ? 'bg-red-50 border-red-200 text-red-800' : '',
          toast.type === 'warning'
            ? 'bg-amber-50 border-amber-200 text-amber-800'
            : '',
          toast.type === 'info'
            ? 'bg-blue-50 border-blue-200 text-blue-800'
            : '',
        ]"
      >
        <FeatherIcon
          :name="getToastIcon(toast.type)"
          class="w-5 h-5 flex-shrink-0"
        />
        <div class="flex-1">
          <p class="font-medium">{{ toast.title }}</p>
          <p v-if="toast.message" class="text-sm opacity-90">
            {{ toast.message }}
          </p>
        </div>
        <button
          @click="removeToast(toast.id)"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <FeatherIcon name="x" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { Button, Dialog, FeatherIcon } from "frappe-ui";
import { call } from "frappe-ui";
import { dayjs } from "@/utils/dateUtils";
import RosterHeader from "@/components/Roster/RosterHeader.vue";
import RosterTable from "@/components/Roster/RosterTable.vue";
import TaskAssignmentDialog from "@/components/Roster/TaskAssignmentDialog.vue";

// Reactive state
const loading = ref(false);
const error = ref(null);
const viewMode = ref("week");
const currentDate = ref(dayjs());
const selectedDepartment = ref("");
const selectedCompany = ref("");

// Data
const assignees = ref([]);
const assignments = ref([]);
const departments = ref([]);
const companies = ref([]);

// Dialog state
const showAssignmentDialog = ref(false);

const selectedDate = ref(null);
const selectedAssignee = ref(null);
const selectedAssignment = ref(null);

// Confirmation dialog
const showConfirmDialog = ref(false);
const confirmDialog = ref({
  title: "",
  message: "",
  details: "",
  confirmLabel: "Confirm",
  theme: "red",
  icon: "alert-triangle",
  loading: false,
  onConfirm: () => {},
});

// Toast notifications
const toasts = ref([]);
let toastId = 0;

// Computed properties
const pageTitle = computed(() => {
  if (selectedDepartment.value) {
    return `${selectedDepartment.value} Planner`;
  }
  return "Team Planner";
});

const dateRange = computed(() => {
  if (viewMode.value === "week") {
    const startOfWeek = getWeekStart(currentDate.value);
    return Array.from({ length: 7 }, (_, i) => startOfWeek.add(i, "day"));
  } else {
    const startOfMonth = currentDate.value.startOf("month");
    const endOfMonth = currentDate.value.endOf("month");
    const daysInMonth = endOfMonth.date();
    return Array.from({ length: daysInMonth }, (_, i) =>
      startOfMonth.add(i, "day"),
    );
  }
});

const workloadStats = computed(() => {
  const totalAssignees = assignees.value.length;
  const activeTasks = assignments.value.filter(
    (a) => a.status === "Active",
  ).length;
  const pendingTasks = assignments.value.filter(
    (a) => a.status === "Pending",
  ).length;

  let totalUtilization = 0;
  if (totalAssignees > 0) {
    const utilizationSum = assignees.value.reduce((sum, assignee) => {
      const assigneeAssignments = assignments.value.filter(
        (a) => a.assignee === assignee.name,
      );
      const totalHours = assigneeAssignments.reduce((hours, assignment) => {
        const start = dayjs(`2023-01-01 ${assignment.start_time}`);
        const end = dayjs(`2023-01-01 ${assignment.end_time}`);
        return hours + end.diff(start, "hour", true);
      }, 0);
      return sum + Math.min((totalHours / 8) * 100, 100); // Cap at 100%
    }, 0);
    totalUtilization = utilizationSum / totalAssignees;
  }

  return {
    totalAssignees,
    activeTasks,
    pendingTasks,
    avgUtilization: totalUtilization,
  };
});

// Methods
const getWeekStart = (date) => {
  const d = dayjs(date);
  const day = d.day();
  const diff = d.date() - day + (day === 0 ? -6 : 1);
  return d.date(diff);
};

const loadData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const [assigneesData, assignmentsData, filtersData] = await Promise.all([
      call("planner.api.roster.get_assignees", {
        department: selectedDepartment.value,
        company: selectedCompany.value,
      }),
      call("planner.api.roster.get_assignments", {
        start_date: dateRange.value[0].format("YYYY-MM-DD"),
        end_date:
          dateRange.value[dateRange.value.length - 1].format("YYYY-MM-DD"),
        department: selectedDepartment.value,
        company: selectedCompany.value,
      }),
      call("planner.api.roster.get_filters"),
    ]);

    assignees.value = assigneesData || [];
    assignments.value = assignmentsData || [];
    departments.value = filtersData?.departments || [];
    companies.value = filtersData?.companies || [];
  } catch (err) {
    console.error("Error loading data:", err);
    error.value = err.message || "Failed to load planner data";
  } finally {
    loading.value = false;
  }
};

const handleViewModeChange = (mode) => {
  viewMode.value = mode;
  loadData();
};

const handleDateChange = (date) => {
  currentDate.value = date;
  loadData();
};

const handleDepartmentChange = (department) => {
  selectedDepartment.value = department;
  loadData();
};

const handleCompanyChange = (company) => {
  selectedCompany.value = company;
  loadData();
};

const handleRefresh = () => {
  loadData();
};

const handleAddTask = () => {
  console.log("🔥 PlannerRoster handleAddTask called (header button)");
  selectedDate.value = dayjs().format("YYYY-MM-DD");
  selectedAssignee.value = null;
  selectedAssignment.value = null;
  showAssignmentDialog.value = true;
  console.log("🔥 showAssignmentDialog set to true from header");
};

const handleCellClick = (date, assignee) => {
  console.log("🔥 PlannerRoster handleCellClick received:", { date, assignee });
  selectedDate.value = date;
  selectedAssignee.value = assignee;
  selectedAssignment.value = null;
  showAssignmentDialog.value = true;
  console.log("🔥 showAssignmentDialog set to true");
};

const handleAssignmentClick = (assignment) => {
  selectedDate.value = assignment.date;
  selectedAssignee.value = assignees.value.find(
    (a) => a.name === assignment.assignee,
  );
  selectedAssignment.value = assignment;
  showAssignmentDialog.value = true;
};

const handleAssignmentDrag = (assignment) => {
  // Handle drag start
  console.log("Drag started:", assignment);
};

const handleAssignmentDrop = async (assignment, newDate, newAssignee) => {
  try {
    await call("planner.api.roster.move_assignment", {
      assignment_id: assignment.name,
      new_date: newDate,
      new_assignee: newAssignee,
    });

    showToast(
      "success",
      "Assignment Moved",
      "Task assignment has been successfully moved.",
    );
    loadData();
  } catch (err) {
    console.error("Error moving assignment:", err);
    showToast(
      "error",
      "Move Failed",
      err.message || "Failed to move assignment",
    );
  }
};

const handleAssignmentDelete = (assignment) => {
  confirmDialog.value = {
    title: "Delete Assignment",
    message: "Are you sure you want to delete this task assignment?",
    details: `This will remove "${assignment.task_name}" from ${assignment.assignee_name} on ${dayjs(assignment.date).format("MMM D, YYYY")}.`,
    confirmLabel: "Delete Assignment",
    theme: "red",
    icon: "trash-2",
    loading: false,
    onConfirm: async () => {
      confirmDialog.value.loading = true;
      try {
        await call("planner.api.roster.delete_assignment", {
          assignment_id: assignment.name,
        });

        showConfirmDialog.value = false;
        showToast(
          "success",
          "Assignment Deleted",
          "Task assignment has been successfully deleted.",
        );
        loadData();
      } catch (err) {
        console.error("Error deleting assignment:", err);
        showToast(
          "error",
          "Delete Failed",
          err.message || "Failed to delete assignment",
        );
      } finally {
        confirmDialog.value.loading = false;
      }
    },
  };
  showConfirmDialog.value = true;
};

const handleAssignmentSubmit = async (assignmentData) => {
  try {
    if (selectedAssignment.value) {
      await call("planner.api.roster.update_assignment", assignmentData);
      showToast(
        "success",
        "Assignment Updated",
        "Task assignment has been successfully updated.",
      );
    } else {
      await call("planner.api.roster.create_assignment", assignmentData);
      showToast(
        "success",
        "Assignment Created",
        "Task assignment has been successfully created.",
      );
    }

    showAssignmentDialog.value = false;
    loadData();
  } catch (err) {
    console.error("Error saving assignment:", err);
    showToast(
      "error",
      "Save Failed",
      err.message || "Failed to save assignment",
    );
  }
};

const handleAssignmentCancel = () => {
  showAssignmentDialog.value = false;
  selectedDate.value = null;
  selectedAssignee.value = null;
  selectedAssignment.value = null;
};

// Toast methods
const showToast = (type, title, message = "") => {
  const toast = {
    id: ++toastId,
    type,
    title,
    message,
  };
  toasts.value.push(toast);

  // Auto remove after 5 seconds
  setTimeout(() => {
    removeToast(toast.id);
  }, 5000);
};

const removeToast = (id) => {
  const index = toasts.value.findIndex((t) => t.id === id);
  if (index > -1) {
    toasts.value.splice(index, 1);
  }
};

const getToastIcon = (type) => {
  const icons = {
    success: "check-circle",
    error: "alert-circle",
    warning: "alert-triangle",
    info: "info",
  };
  return icons[type] || "info";
};

// Lifecycle
onMounted(() => {
  loadData();
});

// Watchers
watch(
  [viewMode, currentDate, selectedDepartment, selectedCompany],
  () => {
    loadData();
  },
  { deep: true },
);
</script>

<style scoped>
/* Smooth transitions */
* {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Toast animations */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
