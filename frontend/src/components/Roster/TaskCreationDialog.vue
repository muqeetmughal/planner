<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Create New Task',
      size: 'xl',
      actions: [
        {
          label: 'Cancel',
          theme: 'gray',
          variant: 'ghost',
          onClick: handleCancel
        },
        {
          label: 'Create Task',
          theme: 'blue',
          variant: 'solid',
          loading: loading,
          onClick: handleSubmit
        }
      ]
    }"
  >
    <div class="space-y-6">
      <!-- Task Templates -->
      <div v-if="templates.length > 0" class="space-y-3">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Quick Templates
        </label>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
          <button
            v-for="template in templates"
            :key="template.name"
            @click="applyTemplate(template)"
            class="p-3 text-left border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div class="font-medium text-sm text-gray-900 dark:text-white">
              {{ template.subject }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ template.expected_time }}h • {{ template.priority }}
            </div>
          </button>
        </div>
      </div>

      <!-- Task Subject -->
      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Task Subject <span class="text-red-500">*</span>
        </label>
        <FormControl
          v-model="formData.subject"
          placeholder="Enter task subject..."
          :error="errors.subject"
        />
      </div>

      <!-- Task Description -->
      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Description
        </label>
        <FormControl
          type="textarea"
          v-model="formData.description"
          placeholder="Describe the task in detail..."
          :rows="4"
        />
      </div>

      <!-- Task Details Row -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Priority -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Priority
          </label>
          <FormControl
            type="select"
            v-model="formData.priority"
            :options="priorityOptions"
          />
        </div>

        <!-- Expected Time -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Expected Time (hours)
          </label>
          <FormControl
            type="number"
            v-model="formData.expected_time"
            placeholder="0"
            :min="0"
            :step="0.5"
          />
        </div>

        <!-- Department -->
        <div class="space-y-3">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Department
          </label>
          <FormControl
            type="select"
            v-model="formData.department"
            :options="departmentOptions"
            placeholder="Select department..."
          />
        </div>
      </div>

      <!-- Project Selection -->
      <div class="space-y-3">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Project
        </label>
        <Autocomplete
          v-model="formData.project"
          :options="projectOptions"
          placeholder="Search and select a project..."
          :loading="loadingProjects"
          @input-change="searchProjects"
        >
          <template #item-label="{ option }">
            <div class="flex items-center gap-3">
              <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
              <div>
                <div class="font-medium text-gray-900 dark:text-white">{{ option.project_name }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ option.name }}</div>
              </div>
            </div>
          </template>
        </Autocomplete>
      </div>

      <!-- Assignment Option -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <div class="flex items-center justify-between">
          <div>
            <h4 class="font-medium text-gray-900 dark:text-white">Assign Immediately</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              Create task and assign to someone right away
            </p>
          </div>
          <FormControl
            type="checkbox"
            v-model="assignImmediately"
          />
        </div>

        <!-- Assignment Details -->
        <div v-if="assignImmediately" class="mt-4 space-y-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Assignee -->
            <div class="space-y-3">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Assignee <span class="text-red-500">*</span>
              </label>
              <Autocomplete
                v-model="assignmentData.assignee"
                :options="assigneeOptions"
                placeholder="Search team member..."
                :loading="loadingAssignees"
                @input-change="searchAssignees"
                :error="errors.assignee"
              >
                <template #item-label="{ option }">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                      <FeatherIcon name="user" class="w-4 h-4 text-gray-600" />
                    </div>
                    <div>
                      <div class="font-medium text-gray-900 dark:text-white">{{ option.full_name }}</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">{{ option.department }}</div>
                    </div>
                  </div>
                </template>
              </Autocomplete>
            </div>

            <!-- Date -->
            <div class="space-y-3">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Date <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="date"
                v-model="assignmentData.date"
                :error="errors.date"
              />
            </div>
          </div>

          <!-- Time Range -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-3">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Start Time <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="time"
                v-model="assignmentData.start_time"
                :error="errors.start_time"
              />
            </div>
            <div class="space-y-3">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                End Time <span class="text-red-500">*</span>
              </label>
              <FormControl
                type="time"
                v-model="assignmentData.end_time"
                :error="errors.end_time"
              />
            </div>
          </div>

          <!-- Assignment Duration -->
          <div v-if="assignmentDuration" class="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Duration:</span>
              <span class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ assignmentDuration }} hours
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Task Summary -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <h4 class="font-medium text-gray-900 dark:text-white mb-3">Task Summary</h4>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-500 dark:text-gray-400">Priority:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ formData.priority }}</span>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400">Expected Time:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ formData.expected_time || 0 }}h</span>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400">Department:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ formData.department || 'Not specified' }}</span>
          </div>
          <div>
            <span class="text-gray-500 dark:text-gray-400">Project:</span>
            <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ formData.project?.project_name || 'Not specified' }}</span>
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Dialog, Autocomplete, FormControl, FeatherIcon } from 'frappe-ui'
import { dayjs } from '@/utils/dateUtils'
import { call } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  departments: {
    type: Array,
    default: () => []
  },
  selectedDepartment: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'task-created', 'cancel'])

// Reactive state
const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const loadingProjects = ref(false)
const loadingAssignees = ref(false)
const templates = ref([])
const projectOptions = ref([])
const assigneeOptions = ref([])
const assignImmediately = ref(false)

const formData = ref({
  subject: '',
  description: '',
  priority: 'Medium',
  expected_time: 0,
  department: '',
  project: null
})

const assignmentData = ref({
  assignee: null,
  date: dayjs().format('YYYY-MM-DD'),
  start_time: '09:00',
  end_time: '17:00'
})

const errors = ref({})

// Computed properties
const priorityOptions = computed(() => [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Urgent', value: 'Urgent' }
])

const departmentOptions = computed(() => [
  { label: 'Select Department', value: '' },
  ...props.departments.map(dept => ({ label: dept, value: dept }))
])

const assignmentDuration = computed(() => {
  if (!assignmentData.value.start_time || !assignmentData.value.end_time) return null

  const start = dayjs(`2023-01-01 ${assignmentData.value.start_time}`)
  const end = dayjs(`2023-01-01 ${assignmentData.value.end_time}`)

  if (end.isBefore(start)) return null

  return end.diff(start, 'hour', true).toFixed(1)
})

// Methods
const loadTemplates = async () => {
  try {
    const response = await call('planner.api.roster.get_task_templates')
    templates.value = response || []
  } catch (error) {
    console.error('Error loading templates:', error)
  }
}

const searchProjects = async (query) => {
  if (!query || query.length < 2) {
    projectOptions.value = []
    return
  }

  loadingProjects.value = true
  try {
    const response = await call('planner.api.roster.get_projects')
    projectOptions.value = (response || []).filter(project =>
      project.project_name.toLowerCase().includes(query.toLowerCase()) ||
      project.name.toLowerCase().includes(query.toLowerCase())
    )
  } catch (error) {
    console.error('Error searching projects:', error)
    projectOptions.value = []
  } finally {
    loadingProjects.value = false
  }
}

const searchAssignees = async (query) => {
  if (!query || query.length < 2) {
    assigneeOptions.value = []
    return
  }

  loadingAssignees.value = true
  try {
    const response = await call('planner.api.roster.get_assignees', {
      department: props.selectedDepartment
    })
    assigneeOptions.value = (response || []).filter(assignee =>
      assignee.full_name.toLowerCase().includes(query.toLowerCase()) ||
      assignee.department.toLowerCase().includes(query.toLowerCase())
    )
  } catch (error) {
    console.error('Error searching assignees:', error)
    assigneeOptions.value = []
  } finally {
    loadingAssignees.value = false
  }
}

const applyTemplate = (template) => {
  formData.value = {
    ...formData.value,
    subject: template.subject,
    description: template.description,
    priority: template.priority,
    expected_time: template.expected_time
  }
}

const validateForm = () => {
  errors.value = {}

  if (!formData.value.subject.trim()) {
    errors.value.subject = 'Task subject is required'
  }

  if (assignImmediately.value) {
    if (!assignmentData.value.assignee) {
      errors.value.assignee = 'Please select an assignee'
    }
    if (!assignmentData.value.date) {
      errors.value.date = 'Please select a date'
    }
    if (!assignmentData.value.start_time) {
      errors.value.start_time = 'Please select start time'
    }
    if (!assignmentData.value.end_time) {
      errors.value.end_time = 'Please select end time'
    }

    // Check if end time is after start time
    if (assignmentData.value.start_time && assignmentData.value.end_time) {
      const start = dayjs(`2023-01-01 ${assignmentData.value.start_time}`)
      const end = dayjs(`2023-01-01 ${assignmentData.value.end_time}`)
      if (end.isBefore(start) || end.isSame(start)) {
        errors.value.end_time = 'End time must be after start time'
      }
    }
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true
  try {
    // Create the task
    const taskData = {
      subject: formData.value.subject,
      description: formData.value.description,
      priority: formData.value.priority,
      expected_time: formData.value.expected_time,
      project: formData.value.project?.name || null,
      department: formData.value.department || props.selectedDepartment
    }

    const taskResponse = await call('planner.api.roster.create_task', taskData)

    if (taskResponse.success) {
      // If immediate assignment is requested, create assignment
      if (assignImmediately.value) {
        await call('planner.api.roster.quick_assign_task', {
          task_name: taskResponse.task.name,
          assignee: assignmentData.value.assignee.name,
          date: assignmentData.value.date,
          start_time: assignmentData.value.start_time,
          end_time: assignmentData.value.end_time
        })
      }

      emit('task-created', {
        task: taskResponse.task,
        assigned: assignImmediately.value,
        assignment: assignImmediately.value ? assignmentData.value : null
      })

      resetForm()
      show.value = false
    }
  } catch (error) {
    console.error('Error creating task:', error)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  resetForm()
  emit('cancel')
  show.value = false
}

const resetForm = () => {
  formData.value = {
    subject: '',
    description: '',
    priority: 'Medium',
    expected_time: 0,
    department: props.selectedDepartment || '',
    project: null
  }

  assignmentData.value = {
    assignee: null,
    date: dayjs().format('YYYY-MM-DD'),
    start_time: '09:00',
    end_time: '17:00'
  }

  assignImmediately.value = false
  errors.value = {}
  projectOptions.value = []
  assigneeOptions.value = []
}

// Lifecycle
onMounted(() => {
  loadTemplates()
})

// Watchers
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    formData.value.department = props.selectedDepartment || ''
  }
})

watch(() => props.selectedDepartment, (newVal) => {
  if (newVal) {
    formData.value.department = newVal
  }
})
</script>

<style scoped>
/* Custom form styling */
:deep(.form-control) {
  transition: all 0.2s ease;
}

:deep(.form-control:focus) {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Template button hover effects */
.template-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Enhanced checkbox styling */
:deep(.checkbox) {
  transition: all 0.2s ease;
}

/* Grid responsiveness */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }

  .grid-cols-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
