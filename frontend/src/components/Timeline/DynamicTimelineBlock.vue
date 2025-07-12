<template>
  <div
    :class="[
      'timeline-block relative rounded-lg border cursor-pointer select-none transition-all duration-200 group',
      blockClasses,
      {
        'hover:shadow-md hover:scale-105 hover:z-10': !unassigned,
        'opacity-75 border-dashed': unassigned,
        'ring-2 ring-blue-500 ring-opacity-50': selected,
        'transform scale-95 opacity-60': dragging,
      },
    ]"
    :style="blockStyle"
    :draggable="!resizing"
    @click="handleClick"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
    @contextmenu="handleContextMenu"
    @mouseenter="showControls = true"
    @mouseleave="showControls = false"
  >
    <!-- Resize Handle (Left) -->
    <div
      v-if="resizable && hasDateRange && !unassigned"
      class="resize-handle resize-left absolute left-0 top-0 bottom-0 w-2 cursor-w-resize opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity z-10"
      @mousedown="startResize('left', $event)"
    >
      <div
        class="w-full h-full bg-blue-500 hover:bg-blue-600 rounded-l-lg shadow-sm"
      ></div>
    </div>

    <!-- Main Block Content -->
    <div class="block-content p-3 min-h-full flex flex-col">
      <!-- Header Row -->
      <div class="flex items-start justify-between mb-2">
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <!-- Status Indicator -->
          <div
            :class="['w-2 h-2 rounded-full flex-shrink-0', statusColor]"
          ></div>

          <!-- Block Title -->
          <div class="flex-1 min-w-0">
            <div
              class="text-sm font-semibold text-gray-900 dark:text-white truncate"
            >
              {{ blockTitle }}
            </div>
            <div
              v-if="blockSubtitle"
              class="text-xs text-gray-500 dark:text-gray-400 truncate"
            >
              {{ blockSubtitle }}
            </div>
          </div>
        </div>

        <!-- Priority/Actions -->
        <div class="flex items-center gap-1 flex-shrink-0">
          <!-- Priority Badge -->
          <div
            v-if="blockPriority"
            :class="[
              'px-1.5 py-0.5 rounded text-xs font-medium',
              priorityBadgeClass,
            ]"
          >
            {{ blockPriority }}
          </div>

          <!-- Quick Actions (show on hover) -->
          <div
            v-if="showControls && !unassigned"
            class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <Button
              variant="ghost"
              theme="gray"
              size="sm"
              @click.stop="handleEdit"
              class="w-6 h-6 p-0"
            >
              <FeatherIcon name="edit" class="w-3 h-3" />
            </Button>
            <Button
              variant="ghost"
              theme="red"
              size="sm"
              @click.stop="handleDelete"
              class="w-6 h-6 p-0"
            >
              <FeatherIcon name="trash-2" class="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>

      <!-- Content Area -->
      <div class="flex-1 space-y-2">
        <!-- Description -->
        <div
          v-if="blockDescription"
          class="text-xs text-gray-600 dark:text-gray-400 line-clamp-2"
        >
          {{ blockDescription }}
        </div>

        <!-- Metadata Row -->
        <div class="flex items-center justify-between text-xs">
          <!-- Duration/Time -->
          <div
            v-if="blockDuration"
            class="flex items-center gap-1 text-gray-500 dark:text-gray-400"
          >
            <FeatherIcon name="clock" class="w-3 h-3" />
            <span>{{ formatDuration(blockDuration) }}</span>
          </div>

          <!-- Progress Bar -->
          <div
            v-if="blockProgress !== null"
            class="flex items-center gap-2 flex-1 min-w-0 ml-2"
          >
            <div
              class="flex-1 h-1.5 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden"
            >
              <div
                :class="['h-full transition-all duration-300', progressColor]"
                :style="{ width: `${blockProgress}%` }"
              ></div>
            </div>
            <span class="text-gray-500 dark:text-gray-400 text-xs min-w-max"
              >{{ blockProgress }}%</span
            >
          </div>
        </div>

        <!-- Date Range (for spanning blocks) -->
        <div
          v-if="hasDateRange && (block.start_date || block.end_date)"
          class="text-xs text-gray-500 dark:text-gray-400"
        >
          <div class="flex items-center gap-1">
            <FeatherIcon name="calendar" class="w-3 h-3" />
            <span>{{ formatDateRange() }}</span>
          </div>
        </div>

        <!-- Assignment Info -->
        <div
          v-if="assignmentInfo"
          class="text-xs text-gray-500 dark:text-gray-400"
        >
          <div class="flex items-center gap-1">
            <FeatherIcon name="user" class="w-3 h-3" />
            <span>{{ assignmentInfo }}</span>
          </div>
        </div>
      </div>

      <!-- Footer with Tags/Labels -->
      <div
        v-if="blockTags.length > 0"
        class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700"
      >
        <div class="flex flex-wrap gap-1">
          <span
            v-for="tag in blockTags.slice(0, 3)"
            :key="tag"
            class="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded"
          >
            {{ tag }}
          </span>
          <span
            v-if="blockTags.length > 3"
            class="px-1.5 py-0.5 text-xs text-gray-400 dark:text-gray-500"
          >
            +{{ blockTags.length - 3 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Resize Handle (Right) -->
    <div
      v-if="resizable && hasDateRange && !unassigned"
      class="resize-handle resize-right absolute right-0 top-0 bottom-0 w-2 cursor-e-resize opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity z-10"
      @mousedown="startResize('right', $event)"
    >
      <div
        class="w-full h-full bg-blue-500 hover:bg-blue-600 rounded-r-lg shadow-sm"
      ></div>
    </div>

    <!-- Drag Handle (for mobile/touch) -->
    <div
      v-if="!unassigned"
      class="drag-handle absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
    >
      <FeatherIcon name="move" class="w-3 h-3 text-gray-400" />
    </div>

    <!-- Unassigned Badge -->
    <div
      v-if="unassigned"
      class="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full border-2 border-white dark:border-gray-800 animate-pulse"
    ></div>

    <!-- Loading Overlay -->
    <div
      v-if="updating"
      class="absolute inset-0 bg-white/80 dark:bg-gray-800/80 rounded-lg flex items-center justify-center"
    >
      <div
        class="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { Button, FeatherIcon } from "frappe-ui";

const props = defineProps({
  block: {
    type: Object,
    required: true,
  },
  config: {
    type: Object,
    required: true,
  },
  unassigned: {
    type: Boolean,
    default: false,
  },
  selected: {
    type: Boolean,
    default: false,
  },
  dragging: {
    type: Boolean,
    default: false,
  },
  resizable: {
    type: Boolean,
    default: false,
  },
  updating: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "click",
  "dragstart",
  "dragend",
  "resize",
  "edit",
  "delete",
  "contextmenu",
]);

// Local state
const showControls = ref(false);
const resizing = ref(false);
const resizeDirection = ref(null);
const originalDuration = ref(null);
const dragging = ref(false);

// Computed properties for block data
const blockTitle = computed(() => {
  return props.block.label || props.block.name || props.block.id;
});

const blockSubtitle = computed(() => {
  return (
    props.block.subtitle || props.block.description?.substring(0, 50) || ""
  );
});

const blockDescription = computed(() => {
  if (!props.config?.block_description_field)
    return props.block.description || "";
  return (
    props.block[props.config.block_description_field] ||
    props.block.description ||
    ""
  );
});

const blockStatus = computed(() => {
  if (!props.config?.block_status_field) return props.block.status || "default";
  return (
    props.block[props.config.block_status_field] ||
    props.block.status ||
    "default"
  );
});

const blockPriority = computed(() => {
  if (!props.config?.block_priority_field) return props.block.priority || null;
  return (
    props.block[props.config.block_priority_field] ||
    props.block.priority ||
    null
  );
});

const blockProgress = computed(() => {
  if (!props.config?.block_progress_field) return props.block.progress || null;
  const progress =
    props.block[props.config.block_progress_field] || props.block.progress;
  return progress !== null && progress !== undefined ? Number(progress) : null;
});

const blockDuration = computed(() => {
  if (!props.config?.block_duration_field) return props.block.duration || null;
  return (
    props.block[props.config.block_duration_field] ||
    props.block.duration ||
    null
  );
});

const hasDateRange = computed(() => {
  // Check if configuration has date range fields
  const hasDateFields =
    props.config?.date_range_start_field && props.config?.date_range_end_field;

  // Check if block has date range data
  const hasBlockDates = props.block?.start_date && props.block?.end_date;

  // Also check config-based field names
  const hasConfigDates =
    props.config?.date_range_start_field &&
    props.config?.date_range_end_field &&
    props.block?.[props.config.date_range_start_field] &&
    props.block?.[props.config.date_range_end_field];

  return hasDateFields && (hasBlockDates || hasConfigDates);
});

const assignmentInfo = computed(() => {
  if (props.unassigned) return "Unassigned";
  return props.block.assigned_to || props.block.assignee || null;
});

const blockTags = computed(() => {
  const tags = [];

  // Add status as tag
  if (blockStatus.value && blockStatus.value !== "default") {
    tags.push(blockStatus.value);
  }

  // Add department/category
  if (props.block.department) tags.push(props.block.department);
  if (props.block.category) tags.push(props.block.category);
  if (props.block.project) tags.push(props.block.project);

  return tags;
});

// Styling computed properties
const statusColor = computed(() => {
  const status = blockStatus.value.toLowerCase();

  const statusColors = {
    completed: "bg-green-500",
    done: "bg-green-500",
    in_progress: "bg-blue-500",
    working: "bg-blue-500",
    pending: "bg-amber-500",
    waiting: "bg-amber-500",
    cancelled: "bg-red-500",
    rejected: "bg-red-500",
    draft: "bg-gray-400",
    open: "bg-indigo-500",
    new: "bg-cyan-500",
  };

  return statusColors[status] || "bg-gray-300";
});

const priorityBadgeClass = computed(() => {
  const priority = blockPriority.value?.toLowerCase();

  const priorityClasses = {
    high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    urgent: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    medium:
      "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    low: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  };

  return (
    priorityClasses[priority] ||
    "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300"
  );
});

const progressColor = computed(() => {
  const progress = blockProgress.value;
  if (progress === null) return "bg-gray-300";

  if (progress >= 80) return "bg-green-500";
  if (progress >= 50) return "bg-blue-500";
  if (progress >= 25) return "bg-amber-500";
  return "bg-red-500";
});

const blockClasses = computed(() => {
  const classes = ["group"];

  // Status-based styling
  const status = blockStatus.value.toLowerCase();
  if (status === "completed" || status === "done") {
    classes.push(
      "bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-700",
    );
  } else if (status === "in_progress" || status === "working") {
    classes.push(
      "bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700",
    );
  } else if (status === "pending" || status === "waiting") {
    classes.push(
      "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-700",
    );
  } else if (status === "cancelled" || status === "rejected") {
    classes.push(
      "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-700",
    );
  } else {
    classes.push(
      "bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700",
    );
  }

  // Priority accent
  const priority = blockPriority.value?.toLowerCase();
  if (priority === "high" || priority === "urgent") {
    classes.push("border-l-4 border-l-red-500");
  } else if (priority === "medium") {
    classes.push("border-l-4 border-l-amber-500");
  } else if (priority === "low") {
    classes.push("border-l-4 border-l-green-500");
  }

  return classes;
});

const blockStyle = computed(() => {
  const style = {};

  // Set minimum height based on content
  style.minHeight = "80px";

  // Spanning blocks (date ranges)
  if (hasDateRange.value) {
    style.minWidth = "120px";
  }

  return style;
});

// Methods
const formatDuration = (duration) => {
  if (typeof duration === "number") {
    if (duration >= 1) {
      return duration === 1 ? "1 hour" : `${duration} hours`;
    } else {
      const minutes = Math.round(duration * 60);
      return minutes === 1 ? "1 minute" : `${minutes} minutes`;
    }
  }
  return duration;
};

const formatDateRange = () => {
  if (!props.block.start_date || !props.block.end_date) return "";

  const start = new Date(props.block.start_date);
  const end = new Date(props.block.end_date);

  if (start.toDateString() === end.toDateString()) {
    return start.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  }

  return `${start.toLocaleDateString("en-US", { month: "short", day: "numeric" })} - ${end.toLocaleDateString("en-US", { month: "short", day: "numeric" })}`;
};

// Event handlers
const handleClick = (event) => {
  event.stopPropagation();
  emit("click", props.block, event);
};

const handleDragStart = (event) => {
  if (resizing.value) {
    event.preventDefault();
    return;
  }

  dragging.value = true;
  event.dataTransfer.effectAllowed = "move";
  
  // Set both formats for compatibility
  event.dataTransfer.setData("text/plain", props.block.id);
  event.dataTransfer.setData("application/json", JSON.stringify(props.block));
  
  emit("dragstart", props.block, event);
};

const handleDragEnd = (event) => {
  dragging.value = false;
  emit("dragend", props.block, event);
};

const handleContextMenu = (event) => {
  event.preventDefault();
  emit("contextmenu", props.block, event);
};

const handleEdit = () => {
  emit("edit", props.block);
};

const handleDelete = () => {
  emit("delete", props.block);
};

// Resize functionality
const startResize = (direction, event) => {
  if (!props.resizable || props.unassigned) return;

  event.preventDefault();
  event.stopPropagation();

  resizing.value = true;
  resizeDirection.value = direction;
  originalDuration.value = blockDuration.value || 1;

  const startX = event.clientX;
  const startDuration = originalDuration.value;

  const handleMouseMove = (e) => {
    const deltaX = e.clientX - startX;
    const hourChange = Math.round(deltaX / 40); // 40px per hour adjustment

    let newDuration = startDuration;
    if (direction === "right") {
      newDuration = Math.max(0.5, startDuration + hourChange);
    } else {
      newDuration = Math.max(0.5, startDuration - hourChange);
    }

    emit("resize", props.block, newDuration);
  };

  const handleMouseUp = () => {
    resizing.value = false;
    resizeDirection.value = null;
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
  };

  document.addEventListener("mousemove", handleMouseMove);
  document.addEventListener("mouseup", handleMouseUp);
};

// Watchers
watch(
  () => props.selected,
  (selected) => {
    if (selected) {
      showControls.value = true;
    }
  },
);
</script>

<style scoped>
.timeline-block {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

.timeline-block:hover {
  transform: translateY(-1px);
  box-shadow:
    0 4px 12px -2px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.resize-handle {
  transition: all 0.2s ease;
}

.resize-handle:hover {
  width: 4px;
}

.resize-handle:active {
  width: 6px;
}

.timeline-block:active {
  transform: translateY(0);
}

.resize-handle {
  z-index: 10;
}

.resize-handle:hover {
  background: linear-gradient(
    to bottom,
    rgba(59, 130, 246, 0.1),
    rgba(59, 130, 246, 0.2)
  );
}

.resize-handle:active {
  background: linear-gradient(
    to bottom,
    rgba(59, 130, 246, 0.2),
    rgba(59, 130, 246, 0.3)
  );
}

.block-content {
  position: relative;
  z-index: 1;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Dragging state */
.timeline-block.dragging {
  transform: rotate(2deg) scale(1.05);
  z-index: 1000;
  box-shadow:
    0 10px 25px -5px rgba(0, 0, 0, 0.2),
    0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

/* Selection highlight */
.timeline-block.selected {
  box-shadow:
    0 0 0 2px rgba(59, 130, 246, 0.5),
    0 4px 12px -2px rgba(0, 0, 0, 0.1);
}

/* Unassigned state */
.timeline-block.unassigned {
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 2px,
    rgba(245, 158, 11, 0.1) 2px,
    rgba(245, 158, 11, 0.1) 4px
  );
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .timeline-block {
    min-height: 60px;
  }

  .block-content {
    @apply p-2;
  }

  .resize-handle {
    @apply w-2;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .timeline-block:hover {
    box-shadow:
      0 4px 12px -2px rgba(0, 0, 0, 0.3),
      0 2px 4px -1px rgba(0, 0, 0, 0.2);
  }
}

/* Focus states for accessibility */
.timeline-block:focus {
  outline: 2px solid rgba(59, 130, 246, 0.6);
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .timeline-block {
    border-width: 2px;
  }
}

/* Animation for updates */
@keyframes pulse-update {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

.timeline-block.updating {
  animation: pulse-update 1s ease-in-out infinite;
}
</style>
