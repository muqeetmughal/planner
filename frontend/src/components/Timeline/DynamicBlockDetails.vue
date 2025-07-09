<template>
  <div class="dynamic-block-details">
    <!-- Enhanced Header with Document Link -->
    <div
      class="block-header mb-6 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-700"
    >
      <div class="flex items-start justify-between mb-4">
        <!-- Block Info -->
        <div class="flex items-start gap-4 flex-1">
          <!-- Status Indicator -->
          <div
            :class="[
              'w-12 h-12 rounded-xl flex items-center justify-center text-white text-lg font-bold shadow-lg',
              statusBgColor,
            ]"
          >
            <FeatherIcon :name="statusIcon" class="w-6 h-6" />
          </div>

          <!-- Title and Meta -->
          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
              {{ blockTitle }}
            </h3>
            <div
              class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400 mb-3"
            >
              <div class="flex items-center gap-1">
                <FeatherIcon name="file-text" class="w-4 h-4" />
                <span>{{ config?.block_doctype }}</span>
              </div>
              <div class="text-gray-300 dark:text-gray-600">•</div>
              <div class="flex items-center gap-1">
                <FeatherIcon name="hash" class="w-4 h-4" />
                <span class="font-mono">{{ block.name }}</span>
              </div>
            </div>

            <!-- Quick Stats Row -->
            <div class="flex items-center gap-4">
              <div
                v-if="blockProgress !== null"
                class="flex items-center gap-2"
              >
                <div
                  class="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
                >
                  <div
                    :class="[
                      'h-full transition-all duration-500',
                      progressColor,
                    ]"
                    :style="{ width: `${blockProgress}%` }"
                  ></div>
                </div>
                <span
                  class="text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  {{ blockProgress }}%
                </span>
              </div>

              <div
                v-if="blockDuration"
                class="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400"
              >
                <FeatherIcon name="clock" class="w-4 h-4" />
                <span>{{ formatDuration(blockDuration) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Priority Badge -->
        <div
          v-if="blockPriority"
          :class="[
            'px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2',
            priorityBadgeClass,
          ]"
        >
          <FeatherIcon :name="priorityIcon" class="w-4 h-4" />
          {{ blockPriority }}
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-3">
        <Button
          variant="solid"
          theme="blue"
          size="md"
          @click="openDocumentInDesk"
          class="shadow-sm"
        >
          <FeatherIcon name="external-link" class="w-4 h-4 mr-2" />
          Open in {{ config?.block_doctype }}
        </Button>

        <Button variant="outline" theme="gray" size="md" @click="editBlock">
          <FeatherIcon name="edit" class="w-4 h-4 mr-2" />
          Edit
        </Button>

        <Button variant="ghost" theme="gray" size="md" @click="duplicateBlock">
          <FeatherIcon name="copy" class="w-4 h-4 mr-2" />
          Duplicate
        </Button>
      </div>
    </div>

    <!-- Enhanced Details Grid -->
    <div class="details-grid space-y-6">
      <!-- Basic Information Card -->
      <div
        class="detail-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <div
            class="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center"
          >
            <FeatherIcon
              name="info"
              class="w-4 h-4 text-blue-600 dark:text-blue-400"
            />
          </div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
            Basic Information
          </h4>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Status -->
          <div class="detail-item">
            <label class="detail-label">Status</label>
            <div class="flex items-center gap-2 mt-1">
              <div :class="['w-3 h-3 rounded-full', statusColor]"></div>
              <span class="detail-value capitalize">{{ blockStatus }}</span>
              <Badge v-if="isOverdue" theme="red" size="sm">Overdue</Badge>
            </div>
          </div>

          <!-- Priority -->
          <div v-if="blockPriority" class="detail-item">
            <label class="detail-label">Priority</label>
            <div class="flex items-center gap-2 mt-1">
              <FeatherIcon
                :name="priorityIcon"
                :class="['w-4 h-4', priorityColor]"
              />
              <span class="detail-value capitalize">{{ blockPriority }}</span>
            </div>
          </div>

          <!-- Progress -->
          <div v-if="blockProgress !== null" class="detail-item">
            <label class="detail-label">Progress</label>
            <div class="mt-2">
              <div class="flex items-center justify-between mb-1">
                <span class="detail-value">{{ blockProgress }}%</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ getProgressStatus() }}
                </span>
              </div>
              <div
                class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden"
              >
                <div
                  :class="['h-full transition-all duration-500', progressColor]"
                  :style="{ width: `${blockProgress}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Duration -->
          <div v-if="blockDuration" class="detail-item">
            <label class="detail-label">Duration</label>
            <div class="flex items-center gap-2 mt-1">
              <FeatherIcon name="clock" class="w-4 h-4 text-gray-400" />
              <span class="detail-value">{{
                formatDuration(blockDuration)
              }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Assignment & Scheduling Card -->
      <div
        class="detail-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <div
            class="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center"
          >
            <FeatherIcon
              name="calendar"
              class="w-4 h-4 text-green-600 dark:text-green-400"
            />
          </div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
            Assignment & Scheduling
          </h4>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Assigned To -->
          <div class="detail-item">
            <label class="detail-label">Assigned To</label>
            <div class="mt-2">
              <div
                v-if="assignedRowTitle"
                class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <Avatar :label="assignedRowTitle" size="sm" />
                <div>
                  <div class="detail-value">{{ assignedRowTitle }}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ config?.row_doctype }}
                  </div>
                </div>
              </div>
              <div
                v-else
                class="flex items-center gap-2 text-amber-600 dark:text-amber-400"
              >
                <FeatherIcon name="alert-triangle" class="w-4 h-4" />
                <span class="text-sm font-medium">Unassigned</span>
              </div>
            </div>
          </div>

          <!-- Date Range -->
          <div class="detail-item">
            <label class="detail-label">Schedule</label>
            <div class="mt-2 space-y-2">
              <div class="flex items-center gap-2">
                <FeatherIcon name="calendar" class="w-4 h-4 text-gray-400" />
                <span class="detail-value">{{ formatBlockDate() }}</span>
              </div>

              <div
                v-if="hasDateRange"
                class="text-sm text-gray-600 dark:text-gray-400"
              >
                <div class="flex items-center gap-4">
                  <div class="flex items-center gap-1">
                    <FeatherIcon name="play" class="w-3 h-3" />
                    <span>{{ formatDate(block.start_date) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <FeatherIcon name="stop" class="w-3 h-3" />
                    <span>{{ formatDate(block.end_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Description Card -->
      <div
        v-if="blockDescription"
        class="detail-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <div
            class="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center"
          >
            <FeatherIcon
              name="file-text"
              class="w-4 h-4 text-purple-600 dark:text-purple-400"
            />
          </div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
            Description
          </h4>
        </div>

        <div class="prose prose-sm dark:prose-invert max-w-none">
          <div
            class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed"
          >
            {{ blockDescription }}
          </div>
        </div>
      </div>

      <!-- Custom Fields Card -->
      <div
        v-if="customFields.length > 0"
        class="detail-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <div
            class="w-8 h-8 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center"
          >
            <FeatherIcon
              name="settings"
              class="w-4 h-4 text-indigo-600 dark:text-indigo-400"
            />
          </div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
            Additional Details
          </h4>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div
            v-for="field in customFields"
            :key="field.key"
            class="detail-item"
          >
            <label class="detail-label">{{ field.label }}</label>
            <div class="mt-1">
              <span class="detail-value">{{ field.value || "—" }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity & Metadata Card -->
      <div
        class="detail-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <div
            class="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center"
          >
            <FeatherIcon
              name="activity"
              class="w-4 h-4 text-gray-600 dark:text-gray-400"
            />
          </div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
            Activity & Metadata
          </h4>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="detail-item">
            <label class="detail-label">Created</label>
            <div class="mt-1 space-y-1">
              <div class="detail-value">
                {{ formatTimestamp(block.creation) }}
              </div>
              <div
                v-if="block.owner"
                class="text-sm text-gray-500 dark:text-gray-400"
              >
                by {{ block.owner }}
              </div>
            </div>
          </div>

          <div class="detail-item">
            <label class="detail-label">Last Modified</label>
            <div class="mt-1 space-y-1">
              <div class="detail-value">
                {{ formatTimestamp(block.modified) }}
              </div>
              <div
                v-if="block.modified_by"
                class="text-sm text-gray-500 dark:text-gray-400"
              >
                by {{ block.modified_by }}
              </div>
            </div>
          </div>

          <div v-if="block.docstatus !== undefined" class="detail-item">
            <label class="detail-label">Document Status</label>
            <div class="mt-1">
              <Badge :theme="getDocStatusTheme(block.docstatus)" size="sm">
                {{ getDocStatusLabel(block.docstatus) }}
              </Badge>
            </div>
          </div>

          <div v-if="block.version" class="detail-item">
            <label class="detail-label">Version</label>
            <div class="mt-1">
              <span class="detail-value font-mono">{{ block.version }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Related Documents Card (if applicable) -->
      <div
        v-if="relatedDocuments.length > 0"
        class="detail-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
      >
        <div class="flex items-center gap-2 mb-4">
          <div
            class="w-8 h-8 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center"
          >
            <FeatherIcon
              name="link"
              class="w-4 h-4 text-amber-600 dark:text-amber-400"
            />
          </div>
          <h4 class="text-lg font-semibold text-gray-900 dark:text-white">
            Related Documents
          </h4>
        </div>

        <div class="space-y-3">
          <div
            v-for="doc in relatedDocuments"
            :key="`${doc.doctype}-${doc.name}`"
            class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <div class="flex items-center gap-3">
              <FeatherIcon name="file" class="w-4 h-4 text-gray-500" />
              <div>
                <div class="font-medium text-gray-900 dark:text-white">
                  {{ doc.name }}
                </div>
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {{ doc.doctype }}
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              theme="blue"
              size="sm"
              @click="openRelatedDocument(doc)"
            >
              <FeatherIcon name="external-link" class="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Enhanced Footer Actions -->
    <div
      class="footer-actions mt-8 pt-6 border-t border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <Button
            variant="solid"
            theme="blue"
            size="md"
            @click="openDocumentInDesk"
          >
            <FeatherIcon name="external-link" class="w-4 h-4 mr-2" />
            Open in Desk
          </Button>

          <Button variant="outline" theme="gray" size="md" @click="editBlock">
            <FeatherIcon name="edit" class="w-4 h-4 mr-2" />
            Quick Edit
          </Button>

          <Dropdown :items="moreActions" placement="top">
            <template v-slot="{ toggleDropdown }">
              <Button
                variant="ghost"
                theme="gray"
                size="md"
                @click="toggleDropdown()"
              >
                <FeatherIcon name="more-horizontal" class="w-4 h-4 mr-2" />
                More
                <FeatherIcon name="chevron-down" class="w-4 h-4 ml-1" />
              </Button>
            </template>
          </Dropdown>
        </div>

        <Button variant="ghost" theme="gray" size="md" @click="$emit('close')">
          <FeatherIcon name="x" class="w-4 h-4 mr-2" />
          Close
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { Button, FeatherIcon, Avatar, Badge, Dropdown } from "frappe-ui";
import { toast } from "../../composables/useToast";

const props = defineProps({
  block: {
    type: Object,
    required: true,
  },
  config: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "update", "edit", "delete"]);

// Computed properties for block data
const blockTitle = computed(() => {
  return props.block.label || props.block.name || props.block.id;
});

const blockDescription = computed(() => {
  return (
    props.block.description ||
    props.block[props.config?.block_description_field] ||
    ""
  );
});

const blockStatus = computed(() => {
  return (
    props.block.status ||
    props.block[props.config?.block_status_field] ||
    "draft"
  );
});

const blockPriority = computed(() => {
  return (
    props.block.priority ||
    props.block[props.config?.block_priority_field] ||
    null
  );
});

const blockProgress = computed(() => {
  const progress =
    props.block.progress || props.block[props.config?.block_progress_field];
  return progress !== null && progress !== undefined ? Number(progress) : null;
});

const blockDuration = computed(() => {
  return (
    props.block.duration ||
    props.block[props.config?.block_duration_field] ||
    null
  );
});

const assignedRowTitle = computed(() => {
  return props.block.assigned_row_title || props.block.assigned_to || null;
});

const hasDateRange = computed(() => {
  return props.block.start_date && props.block.end_date;
});

const isOverdue = computed(() => {
  if (!props.block.end_date && !props.block.due_date) return false;
  const dueDate = new Date(props.block.end_date || props.block.due_date);
  const today = new Date();
  return dueDate < today && blockStatus.value !== "completed";
});

const customFields = computed(() => {
  const fields = [];
  const excludeFields = [
    "name",
    "id",
    "creation",
    "modified",
    "row_id",
    "owner",
    "modified_by",
    "status",
    "priority",
    "progress",
    "description",
    "duration",
    "docstatus",
    "version",
  ];

  Object.keys(props.block).forEach((key) => {
    if (
      !excludeFields.includes(key) &&
      key !== props.config?.block_title_field &&
      key !== props.config?.block_description_field &&
      key !== props.config?.block_status_field &&
      key !== props.config?.block_priority_field &&
      key !== props.config?.block_progress_field &&
      key !== props.config?.block_duration_field
    ) {
      const value = props.block[key];
      if (value !== null && value !== undefined && value !== "") {
        fields.push({
          key,
          label: key
            .replace(/_/g, " ")
            .replace(/\b\w/g, (l) => l.toUpperCase()),
          value:
            typeof value === "object" ? JSON.stringify(value) : String(value),
        });
      }
    }
  });

  return fields;
});

const relatedDocuments = computed(() => {
  // Mock related documents - in real implementation, this would be fetched from API
  const docs = [];

  if (props.block.project) {
    docs.push({ doctype: "Project", name: props.block.project });
  }

  if (props.block.customer) {
    docs.push({ doctype: "Customer", name: props.block.customer });
  }

  if (props.block.item_code) {
    docs.push({ doctype: "Item", name: props.block.item_code });
  }

  return docs;
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
  };
  return statusColors[status] || "bg-gray-300";
});

const statusBgColor = computed(() => {
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
    draft: "bg-gray-500",
    open: "bg-indigo-500",
  };
  return statusColors[status] || "bg-gray-500";
});

const statusIcon = computed(() => {
  const status = blockStatus.value.toLowerCase();
  const statusIcons = {
    completed: "check-circle",
    done: "check-circle",
    in_progress: "play-circle",
    working: "play-circle",
    pending: "clock",
    waiting: "clock",
    cancelled: "x-circle",
    rejected: "x-circle",
    draft: "edit",
    open: "circle",
  };
  return statusIcons[status] || "circle";
});

const priorityIcon = computed(() => {
  const priority = blockPriority.value?.toLowerCase();
  const priorityIcons = {
    high: "arrow-up",
    urgent: "alert-triangle",
    medium: "minus",
    low: "arrow-down",
  };
  return priorityIcons[priority] || "circle";
});

const priorityColor = computed(() => {
  const priority = blockPriority.value?.toLowerCase();
  const priorityColors = {
    high: "text-red-500",
    urgent: "text-red-600",
    medium: "text-amber-500",
    low: "text-green-500",
  };
  return priorityColors[priority] || "text-gray-400";
});

const priorityBadgeClass = computed(() => {
  const priority = blockPriority.value?.toLowerCase();
  const priorityClasses = {
    high: "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-700",
    urgent:
      "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-700",
    medium:
      "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-700",
    low: "bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-300 dark:border-green-700",
  };
  return (
    priorityClasses[priority] ||
    "bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600"
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

// More actions dropdown
const moreActions = [
  {
    label: "Duplicate",
    icon: "copy",
    handler: () => duplicateBlock(),
  },
  {
    label: "Export",
    icon: "download",
    handler: () => exportBlock(),
  },
  {
    label: "Print",
    icon: "printer",
    handler: () => printBlock(),
  },
  { type: "divider" },
  {
    label: "Delete",
    icon: "trash-2",
    theme: "red",
    handler: () => deleteBlock(),
  },
];

// Methods
const formatDuration = (duration) => {
  if (typeof duration === "number") {
    if (duration >= 24) {
      const days = Math.floor(duration / 24);
      const hours = duration % 24;
      return hours > 0 ? `${days}d ${hours}h` : `${days}d`;
    } else if (duration >= 1) {
      return duration === 1 ? "1 hour" : `${duration} hours`;
    } else {
      const minutes = Math.round(duration * 60);
      return minutes === 1 ? "1 minute" : `${minutes} minutes`;
    }
  }
  return duration;
};

const formatBlockDate = () => {
  const dateField = props.config?.block_to_date_field || "date";
  const date = props.block[dateField] || props.block.date;

  if (!date) return "No date set";

  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "short",
  });
};

const formatDate = (dateString) => {
  if (!dateString) return "Not set";

  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
};

const formatTimestamp = (timestamp) => {
  if (!timestamp) return "—";

  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return (
      date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }) + " (today)"
    );
  } else if (diffDays === 1) {
    return (
      date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      }) + " (yesterday)"
    );
  } else if (diffDays < 7) {
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } else {
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }
};

const getProgressStatus = () => {
  const progress = blockProgress.value;
  if (progress === null) return "";

  if (progress === 100) return "Complete";
  if (progress >= 75) return "Nearly done";
  if (progress >= 50) return "In progress";
  if (progress >= 25) return "Getting started";
  return "Just started";
};

const getDocStatusTheme = (docstatus) => {
  const statusThemes = {
    0: "gray",
    1: "blue",
    2: "red",
  };
  return statusThemes[docstatus] || "gray";
};

const getDocStatusLabel = (docstatus) => {
  const statusLabels = {
    0: "Draft",
    1: "Submitted",
    2: "Cancelled",
  };
  return statusLabels[docstatus] || "Draft";
};

// Action handlers
const openDocumentInDesk = () => {
  const doctype = props.config.block_doctype.toLowerCase().replace(/ /g, "-");
  const url = `/app/${doctype}/${props.block.name}`;
  window.open(url, "_blank");
  toast.success(`Opening ${props.config.block_doctype} in new tab`);
};

const editBlock = () => {
  emit("edit", props.block);
};

const duplicateBlock = () => {
  emit("update", { action: "duplicate", block: props.block });
  toast.info("Duplicating block...");
};

const exportBlock = () => {
  const dataStr = JSON.stringify(props.block, null, 2);
  const dataUri =
    "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

  const exportFileDefaultName = `${props.config.block_doctype.toLowerCase()}_${props.block.name}.json`;

  const linkElement = document.createElement("a");
  linkElement.setAttribute("href", dataUri);
  linkElement.setAttribute("download", exportFileDefaultName);
  linkElement.click();

  toast.success("Block data exported");
};

const printBlock = () => {
  window.print();
};

const deleteBlock = () => {
  if (confirm(`Are you sure you want to delete ${props.block.name}?`)) {
    emit("update", { action: "delete", block: props.block });
    emit("close");
    toast.error("Block deleted");
  }
};

const openRelatedDocument = (doc) => {
  const doctype = doc.doctype.toLowerCase().replace(/ /g, "-");
  const url = `/app/${doctype}/${doc.name}`;
  window.open(url, "_blank");
};

const handleMoreAction = (action) => {
  if (action.handler) {
    action.handler();
  }
};
</script>

<style scoped>
.dynamic-block-details {
  @apply max-w-full;
}

.detail-card {
  @apply transition-all duration-200 hover:shadow-md;
}

.detail-label {
  @apply text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide;
}

.detail-value {
  @apply text-sm font-medium text-gray-900 dark:text-white;
}

.detail-item {
  @apply space-y-1;
}

/* Smooth transitions */
* {
  transition: all 0.15s ease;
}

/* Progress bar animation */
.detail-item .h-full {
  transition: width 0.5s ease-in-out;
}

/* Hover effects */
.detail-card:hover {
  transform: translateY(-1px);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .block-header {
    @apply flex-col items-start gap-4;
  }

  .block-header .flex-1 {
    @apply w-full;
  }
}

/* Dark mode enhancements */
@media (prefers-color-scheme: dark) {
  .detail-card {
    @apply bg-gray-800/50 backdrop-blur-sm;
  }
}

/* Print styles */
@media print {
  .footer-actions {
    @apply hidden;
  }

  .detail-card {
    @apply shadow-none border-gray-300;
  }
}
</style>
