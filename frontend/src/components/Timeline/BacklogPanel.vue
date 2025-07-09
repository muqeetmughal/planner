<template>
  <Card class="backlog-panel h-full flex flex-col">
    <!-- Header -->
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Avatar size="lg" :image="false" :label="'B'" />
          <div>
            <h3 class="text-lg font-semibold">Backlog</h3>
            <p class="text-sm text-gray-500">
              {{ tasks.length }} unscheduled tasks
            </p>
          </div>
        </div>
        <Button variant="ghost" @click="$emit('close')">
          <FeatherIcon name="x" class="w-4 h-4" />
        </Button>
      </div>
    </template>

    <!-- Search and Filters -->
    <div class="p-4 border-b space-y-3">
      <Input
        v-model="searchQuery"
        type="text"
        placeholder="Search tasks..."
        :prefix-icon="'search'"
      />

      <div class="flex gap-2">
        <FormControl
          v-model="selectedPriority"
          type="select"
          :options="priorityOptions"
          placeholder="All Priorities"
          class="flex-1"
        />

        <FormControl
          v-model="selectedProject"
          type="select"
          :options="projectOptions"
          placeholder="All Projects"
          class="flex-1"
        />
      </div>
    </div>

    <!-- Task List -->
    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="loading" class="space-y-3">
        <LoadingIndicator v-for="i in 5" :key="i" />
      </div>

      <div v-else-if="filteredTasks.length === 0" class="text-center py-12">
        <div
          class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
        >
          <FeatherIcon name="check-circle" class="w-8 h-8 text-gray-400" />
        </div>
        <h4 class="text-lg font-medium mb-2">All caught up!</h4>
        <p class="text-gray-500">No unscheduled tasks found.</p>
      </div>

      <div v-else class="space-y-3">
        <Card
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-card group cursor-move hover:shadow-md transition-all duration-200 hover:scale-[1.02]"
          :class="getTaskBorderClass(task.priority)"
          draggable="true"
          @dragstart="handleDragStart($event, task)"
          @click="$emit('taskClick', task.id)"
        >
          <!-- Task Header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1 min-w-0">
              <h4
                class="font-semibold text-sm truncate group-hover:text-blue-600 transition-colors"
              >
                {{ task.title }}
              </h4>
              <p
                v-if="task.project"
                class="text-xs text-gray-500 mt-1 truncate"
              >
                {{ task.project }}
              </p>
            </div>
            <div class="flex items-center gap-2 ml-3">
              <Badge
                :label="task.priority"
                :color="getPriorityColor(task.priority)"
              />
            </div>
          </div>

          <!-- Task Details -->
          <div class="flex items-center justify-between text-xs text-gray-500">
            <div class="flex items-center gap-3">
              <div class="flex items-center gap-1">
                <FeatherIcon name="clock" class="w-3 h-3" />
                <span>{{ task.duration }}h</span>
              </div>
              <div
                v-if="task.assignee && task.assignee !== 'unassigned'"
                class="flex items-center gap-1"
              >
                <FeatherIcon name="user" class="w-3 h-3" />
                <span>{{ getAssigneeName(task.assignee) }}</span>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <FeatherIcon name="calendar" class="w-3 h-3" />
              <span>{{ formatCreatedDate(task.created) }}</span>
            </div>
          </div>

          <!-- Task Description -->
          <div v-if="task.description" class="mt-3 pt-3 border-t">
            <p class="text-xs text-gray-600 line-clamp-2">
              {{ task.description }}
            </p>
          </div>

          <!-- Drag Indicator -->
          <div
            class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <FeatherIcon name="move" class="w-4 h-4 text-gray-400" />
          </div>
        </Card>
      </div>
    </div>

    <!-- Footer Actions -->
    <template #footer>
      <Button variant="solid" class="w-full" @click="$emit('addTask')">
        <FeatherIcon name="plus" class="w-4 h-4 mr-2" />
        Add New Task
      </Button>
    </template>
  </Card>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Button,
  FeatherIcon,
  Card,
  Avatar,
  Input,
  FormControl,
  Badge,
  LoadingIndicator,
} from "frappe-ui";

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  assignees: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["taskDragStart", "taskClick", "addTask", "close"]);

// Filter state
const searchQuery = ref("");
const selectedPriority = ref("");
const selectedProject = ref("");

// Filter options
const priorityOptions = [
  { label: "All Priorities", value: "" },
  { label: "High", value: "High" },
  { label: "Medium", value: "Medium" },
  { label: "Low", value: "Low" },
];

// Computed properties
const uniqueProjects = computed(() => {
  const projects = props.tasks
    .map((task) => task.project)
    .filter((project) => project && project.trim() !== "");
  return [...new Set(projects)].sort();
});

const projectOptions = computed(() => {
  return [
    { label: "All Projects", value: "" },
    ...uniqueProjects.value.map((project) => ({
      label: project,
      value: project,
    })),
  ];
});

const filteredTasks = computed(() => {
  let filtered = props.tasks;

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(
      (task) =>
        task.title.toLowerCase().includes(query) ||
        (task.project && task.project.toLowerCase().includes(query)) ||
        (task.description && task.description.toLowerCase().includes(query)),
    );
  }

  // Priority filter
  if (selectedPriority.value) {
    filtered = filtered.filter(
      (task) => task.priority === selectedPriority.value,
    );
  }

  // Project filter
  if (selectedProject.value) {
    filtered = filtered.filter(
      (task) => task.project === selectedProject.value,
    );
  }

  // Sort by priority and creation date
  return filtered.sort((a, b) => {
    const priorityOrder = { High: 3, Medium: 2, Low: 1 };
    const aPriority = priorityOrder[a.priority] || 0;
    const bPriority = priorityOrder[b.priority] || 0;

    if (aPriority !== bPriority) {
      return bPriority - aPriority; // High priority first
    }

    return new Date(b.created) - new Date(a.created); // Newer first
  });
});

// Methods
const handleDragStart = (event, task) => {
  event.dataTransfer.setData("application/json", JSON.stringify(task));
  event.dataTransfer.effectAllowed = "move";
  emit("taskDragStart", event, task);
};

const getTaskBorderClass = (priority) => {
  switch (priority) {
    case "High":
      return "border-l-4 border-l-red-500 hover:border-l-red-600";
    case "Medium":
      return "border-l-4 border-l-blue-500 hover:border-l-blue-600";
    case "Low":
      return "border-l-4 border-l-green-500 hover:border-l-green-600";
    default:
      return "border-l-4 border-l-gray-500 hover:border-l-gray-600";
  }
};

const getPriorityColor = (priority) => {
  switch (priority) {
    case "High":
      return "red";
    case "Medium":
      return "blue";
    case "Low":
      return "green";
    default:
      return "gray";
  }
};

const getAssigneeName = (assigneeId) => {
  const assignee = props.assignees.find((a) => a.id === assigneeId);
  return assignee ? assignee.name : assigneeId;
};

const formatCreatedDate = (dateStr) => {
  if (!dateStr) return "";

  const date = new Date(dateStr);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 1) return "Today";
  if (diffDays === 2) return "Yesterday";
  if (diffDays <= 7) return `${diffDays} days ago`;

  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};
</script>

<style scoped>
.backlog-panel {
  max-height: 70vh;
}

.task-card {
  position: relative;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
