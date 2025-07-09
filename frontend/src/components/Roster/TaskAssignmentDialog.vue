<template>
  <Dialog
    v-model="show"
    :options="{
      title: dialogTitle,
      size: 'xl',
      actions: [
        {
          label: 'Cancel',
          theme: 'gray',
          variant: 'ghost',
          onClick: handleCancel,
        },
        {
          label: isEditing ? 'Update Assignment' : 'Create Assignment',
          theme: 'blue',
          variant: 'solid',
          loading: loading,
          onClick: handleSubmit,
        },
      ],
    }"
  >
    <div class="space-y-6">
      <!-- Debug Info -->
      <div class="bg-yellow-100 p-2 text-sm">
        <p>Debug Info:</p>
        <p>taskMode: {{ taskMode }}</p>
        <p>isEditing: {{ isEditing }}</p>
        <p>selectedDate: {{ props.selectedDate }}</p>
        <p>selectedAssignee: {{ props.selectedAssignee?.name }}</p>
      </div>

      <!-- Task Selection Mode -->
      <div class="space-y-4">
        <div class="flex items-center gap-4">
          <label class="flex items-center gap-2">
            <input
              type="radio"
              v-model="taskMode"
              value="existing"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300"
              >Select Existing Task</span
            >
          </label>
          <label class="flex items-center gap-2">
            <input
              type="radio"
              v-model="taskMode"
              value="create"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300"
              >Create New Task</span
            >
          </label>
        </div>

        <!-- Existing Task Selection -->
        <div v-if="taskMode === 'existing'" class="space-y-3">
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Select Task <span class="text-red-500">*</span>
          </label>
          <Autocomplete
            v-model="formData.task"
            :options="taskOptions"
            placeholder="Search and select a task..."
            :loading="loadingTasks"
            @input-change="searchTasks"
            class="w-full"
          >
            <template #item-label="{ option }">
              <div class="flex items-center gap-3">
                <div class="w-3 h-3 rounded-full bg-blue-500"></div>
                <div>
                  <div class="font-medium text-gray-900 dark:text-white">
                    {{ option.subject }}
                  </div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ option.status }}
                  </div>
                </div>
              </div>
            </template>
          </Autocomplete>
          <!-- Debug info -->
          <div class="mt-2 text-xs text-gray-500">
            Debug: {{ taskOptions.length }} tasks loaded, loadingTasks:
            {{ loadingTasks }}
            <div v-if="taskOptions.length > 0" class="mt-1">
              First task: {{ taskOptions[0].subject }} ({{
                taskOptions[0].name
              }})
            </div>
            <div v-else class="mt-1 text-red-500">No tasks available</div>
            <div class="mt-1">formData.task: {{ formData.task }}</div>
            <div class="mt-1">taskMode: {{ taskMode }}</div>
          </div>
        </div>

        <!-- New Task Creation -->
        <div v-if="taskMode === 'create'" class="space-y-4">
          <div class="space-y-3">
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Task Subject <span class="text-red-500">*</span>
            </label>
            <FormControl
              v-model="newTaskData.subject"
              placeholder="Enter task subject..."
            />
          </div>

          <div class="space-y-3">
            <label
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Description
            </label>
            <FormControl
              type="textarea"
              v-model="newTaskData.description"
              placeholder="Describe the task..."
              :rows="3"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="space-y-3">
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Priority
              </label>
              <FormControl
                type="select"
                v-model="newTaskData.priority"
                :options="priorityOptions"
              />
            </div>
            <div class="space-y-3">
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Expected Time (hours)
              </label>
              <FormControl
                type="number"
                v-model="newTaskData.expected_time"
                placeholder="0"
                :min="0"
                :step="0.5"
              />
            </div>
            <div class="space-y-3">
              <label
                class="block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Project
              </label>
              <Autocomplete
                v-model="newTaskData.project"
                :options="projectOptions"
                placeholder="Select project..."
                :loading="loadingProjects"
                @input-change="searchProjects"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Time Allocation -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-3">
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Start Time <span class="text-red-500">*</span>
          </label>
          <FormControl
            type="time"
            v-model="formData.start_time"
            placeholder="09:00"
          />
        </div>
        <div class="space-y-3">
          <label
            class="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            End Time <span class="text-red-500">*</span>
          </label>
          <FormControl
            type="time"
            v-model="formData.end_time"
            placeholder="17:00"
          />
        </div>
      </div>

      <!-- Duration Display -->
      <div
        v-if="calculatedDuration"
        class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300"
            >Duration:</span
          >
          <span class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ calculatedDuration }} hours
          </span>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { Dialog, Autocomplete, FormControl, FeatherIcon } from "frappe-ui";
import { dayjs } from "@/utils/dateUtils";
import { call } from "frappe-ui";

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  selectedDate: {
    type: String,
    default: null,
  },
  selectedAssignee: {
    type: Object,
    default: null,
  },
  existingAssignment: {
    type: Object,
    default: null,
  },
  existingAssignments: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue", "submit", "cancel"]);

// Reactive state
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
});

const loading = ref(false);
const loadingTasks = ref(false);
const loadingProjects = ref(false);
const taskOptions = ref([]);
const projectOptions = ref([]);
const taskMode = ref("existing");

// Debug: Watch taskOptions changes
watch(
  taskOptions,
  (newOptions) => {
    console.log("🔥 taskOptions changed:", newOptions.length, "options");
    console.log("🔥 taskOptions content:", newOptions);
  },
  { deep: true },
);

const formData = ref({
  task: null,
  start_time: "09:00",
  end_time: "17:00",
  notes: "",
});

const newTaskData = ref({
  subject: "",
  description: "",
  priority: "Medium",
  expected_time: 0,
  project: null,
});

// Computed properties
const isEditing = computed(() => !!props.existingAssignment);

const dialogTitle = computed(() => {
  if (isEditing.value) {
    return "Edit Task Assignment";
  }
  return taskMode.value === "create" ? "Create Task & Assign" : "Assign Task";
});

const priorityOptions = computed(() => [
  { label: "Low", value: "Low" },
  { label: "Medium", value: "Medium" },
  { label: "High", value: "High" },
  { label: "Urgent", value: "Urgent" },
]);

const calculatedDuration = computed(() => {
  if (!formData.value.start_time || !formData.value.end_time) return null;

  const start = dayjs(`2023-01-01 ${formData.value.start_time}`);
  const end = dayjs(`2023-01-01 ${formData.value.end_time}`);

  if (end.isBefore(start)) return null;

  return end.diff(start, "hour", true).toFixed(1);
});

// Methods
const formatDate = (dateStr) => {
  return dayjs(dateStr).format("dddd, MMMM D, YYYY");
};

const getTaskPriorityColor = (priority) => {
  const colors = {
    Low: "bg-green-400",
    Medium: "bg-yellow-400",
    High: "bg-orange-400",
    Urgent: "bg-red-400",
  };
  return colors[priority] || colors["Medium"];
};

const searchTasks = async (query) => {
  if (!query || query.length < 2) {
    taskOptions.value = [];
    return;
  }

  loadingTasks.value = true;
  try {
    const response = await call("planner.api.roster.search_tasks", {
      query: query,
      assignee: props.selectedAssignee?.name,
      date: props.selectedDate,
      include_unassigned: true,
    });

    console.log("🔥 Raw API response:", response);

    // Use raw data format like TaskCreationDialog
    taskOptions.value = response || [];
    console.log("🔥 Tasks loaded:", taskOptions.value.length, "tasks");
    console.log("🔥 Sample task:", taskOptions.value[0]);
    console.log("🔥 All taskOptions:", taskOptions.value);
  } catch (error) {
    console.error("Error searching tasks:", error);
    taskOptions.value = [];
  } finally {
    loadingTasks.value = false;
  }
};

const searchProjects = async (query) => {
  if (!query || query.length < 2) {
    projectOptions.value = [];
    return;
  }

  loadingProjects.value = true;
  try {
    const response = await call("planner.api.roster.get_projects");
    const filteredProjects = (response || []).filter(
      (project) =>
        project.project_name.toLowerCase().includes(query.toLowerCase()) ||
        project.name.toLowerCase().includes(query.toLowerCase()),
    );

    // Use raw data format like TaskCreationDialog
    projectOptions.value = filteredProjects;
  } catch (error) {
    console.error("Error searching projects:", error);
    projectOptions.value = [];
  } finally {
    loadingProjects.value = false;
  }
};

const workloadWarning = computed(() => {
  if (!props.selectedAssignee || !calculatedDuration.value) return null;

  const currentWorkload = getCurrentDayWorkload();
  const newWorkload = currentWorkload + parseFloat(calculatedDuration.value);

  if (newWorkload > 8) {
    return `This assignment will bring the total workload to ${newWorkload.toFixed(1)} hours, exceeding the standard 8-hour workday.`;
  }

  return null;
});

const conflictWarning = computed(() => {
  if (
    !props.selectedDate ||
    !props.selectedAssignee ||
    !formData.value.start_time ||
    !formData.value.end_time
  ) {
    return null;
  }

  const conflicts = checkTimeConflicts();
  if (conflicts.length > 0) {
    return `Time conflict with existing assignment: ${conflicts[0].task_name} (${conflicts[0].start_time} - ${conflicts[0].end_time})`;
  }

  return null;
});

const getCurrentDayWorkload = () => {
  if (
    !props.existingAssignments ||
    !props.selectedDate ||
    !props.selectedAssignee
  ) {
    return 0;
  }

  return props.existingAssignments
    .filter(
      (assignment) =>
        assignment.date === props.selectedDate &&
        assignment.assignee === props.selectedAssignee.name &&
        assignment.name !== props.existingAssignment?.name,
    )
    .reduce((total, assignment) => {
      const start = dayjs(`2023-01-01 ${assignment.start_time}`);
      const end = dayjs(`2023-01-01 ${assignment.end_time}`);
      return total + end.diff(start, "hour", true);
    }, 0);
};

const checkTimeConflicts = () => {
  if (
    !props.existingAssignments ||
    !props.selectedDate ||
    !props.selectedAssignee ||
    !formData.value.start_time ||
    !formData.value.end_time
  ) {
    return [];
  }

  const newStart = dayjs(`2023-01-01 ${formData.value.start_time}`);
  const newEnd = dayjs(`2023-01-01 ${formData.value.end_time}`);

  return props.existingAssignments.filter((assignment) => {
    if (
      assignment.date !== props.selectedDate ||
      assignment.assignee !== props.selectedAssignee.name ||
      assignment.name === props.existingAssignment?.name
    ) {
      return false;
    }

    const existingStart = dayjs(`2023-01-01 ${assignment.start_time}`);
    const existingEnd = dayjs(`2023-01-01 ${assignment.end_time}`);

    return newStart.isBefore(existingEnd) && newEnd.isAfter(existingStart);
  });
};

const handleSubmit = async () => {
  console.log("🔥 TaskAssignmentDialog handleSubmit called");
  console.log("🔥 taskMode:", taskMode.value);
  console.log("🔥 formData:", JSON.stringify(formData.value, null, 2));
  console.log("🔥 newTaskData:", JSON.stringify(newTaskData.value, null, 2));
  console.log("🔥 selectedDate:", props.selectedDate);
  console.log("🔥 selectedAssignee:", props.selectedAssignee);

  if (!formData.value.start_time || !formData.value.end_time) {
    console.log("🔥 Missing start_time or end_time");
    return;
  }

  // Validate based on mode
  if (taskMode.value === "existing" && !formData.value.task) {
    console.log("🔥 Existing mode but no task selected");
    return;
  }

  if (taskMode.value === "create" && !newTaskData.value.subject) {
    console.log("🔥 Create mode but no subject");
    return;
  }

  console.log("🔥 Starting task submission...");
  loading.value = true;
  try {
    let taskId = null;

    // Create new task if needed
    if (taskMode.value === "create") {
      const taskResponse = await call("planner.api.roster.create_task", {
        subject: newTaskData.value.subject,
        description: newTaskData.value.description,
        priority: newTaskData.value.priority,
        expected_time: newTaskData.value.expected_time,
        project: newTaskData.value.project?.name || null,
      });

      if (taskResponse.success) {
        taskId = taskResponse.task.name;
      } else {
        throw new Error("Failed to create task");
      }
    } else {
      taskId = formData.value.task.name;
    }

    // Create assignment
    const assignmentData = {
      task: taskId,
      assignee: props.selectedAssignee.name,
      date: props.selectedDate,
      start_time: formData.value.start_time,
      end_time: formData.value.end_time,
      notes: formData.value.notes,
      duration: calculatedDuration.value,
    };

    if (isEditing.value) {
      assignmentData.name = props.existingAssignment.name;
    }

    emit("submit", assignmentData);
  } catch (error) {
    console.error("Error submitting assignment:", error);
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  emit("cancel");
};

const resetForm = () => {
  console.log("🔥 Resetting form");
  formData.value = {
    task: null,
    start_time: "09:00",
    end_time: "17:00",
    notes: "",
  };

  newTaskData.value = {
    subject: "",
    description: "",
    priority: "Medium",
    expected_time: 0,
    project: null,
  };

  taskOptions.value = [];
  projectOptions.value = [];
  taskMode.value = "existing";
  console.log("🔥 Form reset complete, taskMode:", taskMode.value);

  // Force reactivity update
  nextTick(() => {
    console.log("🔥 After nextTick, taskMode:", taskMode.value);
  });
};

// Watchers
watch(
  () => props.modelValue,
  (newVal) => {
    console.log("🔥 Dialog modelValue changed:", newVal);
    console.log("🔥 existingAssignment:", props.existingAssignment);
    if (newVal) {
      if (props.existingAssignment) {
        // Populate form with existing data
        formData.value = {
          task: props.existingAssignment.task_doc || null,
          start_time: props.existingAssignment.start_time || "09:00",
          end_time: props.existingAssignment.end_time || "17:00",
          notes: props.existingAssignment.notes || "",
        };
        taskMode.value = "existing";
        console.log("🔥 Editing mode - form populated");
      } else {
        // For new assignments, don't reset but set defaults
        taskMode.value = "existing";
        formData.value = {
          task: null,
          start_time: "09:00",
          end_time: "17:00",
          notes: "",
        };

        // Load initial tasks when dialog opens in existing mode
        if (taskMode.value === "existing") {
          searchTasks("ta");
        }

        console.log(
          "🔥 New assignment mode - defaults set, taskMode:",
          taskMode.value,
        );
      }

      // Force reactivity and load tasks
      nextTick(() => {
        console.log(
          "🔥 Dialog opened - taskMode after nextTick:",
          taskMode.value,
        );
        // Load tasks when dialog opens in existing mode
        if (taskMode.value === "existing") {
          console.log("🔥 Loading tasks in nextTick");
          searchTasks("ta");
        }
      });
    }
  },
);

watch(
  () => props.existingAssignment,
  (newVal) => {
    if (newVal && props.modelValue) {
      formData.value = {
        task: newVal.task_doc || null,
        start_time: newVal.start_time || "09:00",
        end_time: newVal.end_time || "17:00",
        notes: newVal.notes || "",
      };
      taskMode.value = "existing";
    }
  },
);

// Watch taskMode changes to load tasks when switching to existing mode
watch(
  () => taskMode.value,
  (newMode) => {
    console.log("🔥 taskMode changed to:", newMode);
    if (newMode === "existing" && show.value) {
      searchTasks("ta");
    }
  },
);
</script>

<style scoped>
/* Custom scrollbar for dialog content */
:deep(.dialog-content) {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

:deep(.dialog-content::-webkit-scrollbar) {
  width: 6px;
}

:deep(.dialog-content::-webkit-scrollbar-track) {
  background: #f7fafc;
}

:deep(.dialog-content::-webkit-scrollbar-thumb) {
  background-color: #cbd5e0;
  border-radius: 3px;
}

/* Enhanced form styling */
:deep(.form-control) {
  transition: all 0.2s ease;
}

:deep(.form-control:focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Ensure autocomplete dropdown is visible */
:deep(.autocomplete-dropdown) {
  z-index: 9999 !important;
  position: relative !important;
}

:deep(.autocomplete-options) {
  z-index: 9999 !important;
  background: white !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 0.375rem !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
  max-height: 200px !important;
  overflow-y: auto !important;
}

:deep(.autocomplete-option) {
  padding: 0.5rem !important;
  cursor: pointer !important;
  border-bottom: 1px solid #f3f4f6 !important;
}

:deep(.autocomplete-option:hover) {
  background-color: #f9fafb !important;
}

:deep(.autocomplete-option.selected) {
  background-color: #dbeafe !important;
  color: #1e40af !important;
}
</style>
