<template>
  <div class="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
    <!-- Form Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
          <FeatherIcon name="plus-circle" class="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ isEditing ? 'Edit Task' : 'Create New Task' }}
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ isEditing ? 'Update task details' : 'Add a new task to the planner' }}
          </p>
        </div>
      </div>
      
      <Button
        v-if="!isEditing"
        variant="ghost"
        theme="gray"
        size="sm"
        @click="resetForm"
      >
        <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
        Reset
      </Button>
    </div>

    <!-- Form Content -->
    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Basic Information -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Task Subject -->
        <div class="lg:col-span-2 space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Task Subject <span class="text-red-500">*</span>
          </label>
          <FormControl
            v-model="formData.subject"
            type="text"
            placeholder="Enter task subject..."
            :error="errors.subject"
            required
          />
        </div>

        <!-- Project -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Project
          </label>
          <Autocomplete
            v-model="formData.project"
            :options="projectOptions"
            placeholder="Select or search project..."
            :loading="loadingProjects"
            @input-change="searchProjects"
          />
        </div>

        <!-- Priority -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Priority <span class="text-red-500">*</span>
          </label>
          <Select
            v-model="formData.priority"
            :options="priorityOptions"
            placeholder="Select priority"
            :error="errors.priority"
            required
          />
        </div>

        <!-- Status -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Status
          </label>
          <Select
            v-model="formData.status"
            :options="statusOptions"
            placeholder="Select status"
          />
        </div>

        <!-- Expected Time -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Expected Time (Hours)
          </label>
          <FormControl
            v-model="formData.expected_time"
            type="number"
            placeholder="0"
            :min="0"
            :step="0.5"
          />
        </div>
      </div>

      <!-- Description -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Description
        </label>
        <FormControl
          v-model="formData.description"
          type="textarea"
          placeholder="Enter task description..."
          :rows="4"
        />
      </div>

      <!-- Dates Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Expected Start Date -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Expected Start Date
          </label>
          <FormControl
            v-model="formData.exp_start_date"
            type="date"
          />
        </div>

        <!-- Expected End Date -->
        <div class="space-y-2">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Expected End Date
          </label>
          <FormControl
            v-model="formData.exp_end_date"
            type="date"
          />
        </div>
      </div>

      <!-- Assignment Section -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Assignment Details</h3>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Assigned To -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Assigned To
            </label>
            <Autocomplete
              v-model="formData.assigned_to"
              :options="userOptions"
              placeholder="Search and select user..."
              :loading="loadingUsers"
              @input-change="searchUsers"
            >
              <template #item-label="{ option }">
                <div class="flex items-center gap-3">
                  <Avatar
                    :image="option.user_image"
                    :label="option.full_name"
                    size="sm"
                  />
                  <div>
                    <div class="font-medium text-gray-900 dark:text-white">{{ option.full_name }}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">{{ option.email }}</div>
                  </div>
                </div>
              </template>
            </Autocomplete>
          </div>

          <!-- Department -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Department
            </label>
            <Select
              v-model="formData.department"
              :options="departmentOptions"
              placeholder="Select department"
            />
          </div>
        </div>
      </div>

      <!-- Custom Fields Section -->
      <div v-if="customFields.length" class="border-t border-gray-200 dark:border-gray-700 pt-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Additional Information</h3>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            v-for="field in customFields"
            :key="field.fieldname"
            class="space-y-2"
          >
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ field.label }}
              <span v-if="field.reqd" class="text-red-500">*</span>
            </label>
            
            <!-- Dynamic field rendering based on field type -->
            <FormControl
              v-if="['Data', 'Text', 'Small Text'].includes(field.fieldtype)"
              v-model="formData[field.fieldname]"
              :type="field.fieldtype === 'Text' ? 'textarea' : 'text'"
              :placeholder="field.placeholder || `Enter ${field.label.toLowerCase()}...`"
              :required="field.reqd"
            />
            
            <Select
              v-else-if="field.fieldtype === 'Select'"
              v-model="formData[field.fieldname]"
              :options="getSelectOptions(field.options)"
              :placeholder="`Select ${field.label.toLowerCase()}`"
              :required="field.reqd"
            />
            
            <FormControl
              v-else-if="field.fieldtype === 'Date'"
              v-model="formData[field.fieldname]"
              type="date"
              :required="field.reqd"
            />
            
            <FormControl
              v-else-if="['Int', 'Float', 'Currency'].includes(field.fieldtype)"
              v-model="formData[field.fieldname]"
              type="number"
              :step="field.fieldtype === 'Float' ? '0.01' : '1'"
              :required="field.reqd"
            />
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
        <div class="flex items-center gap-3">
          <Button
            v-if="isEditing"
            variant="ghost"
            theme="red"
            @click="handleDelete"
            :loading="deleting"
          >
            <FeatherIcon name="trash-2" class="w-4 h-4 mr-2" />
            Delete Task
          </Button>
        </div>
        
        <div class="flex items-center gap-3">
          <Button
            variant="ghost"
            theme="gray"
            @click="handleCancel"
          >
            Cancel
          </Button>
          
          <Button
            type="submit"
            variant="solid"
            theme="blue"
            :loading="loading"
          >
            <FeatherIcon name="save" class="w-4 h-4 mr-2" />
            {{ isEditing ? 'Update Task' : 'Create Task' }}
          </Button>
        </div>
      </div>
    </form>

    <!-- Success/Error Messages -->
    <div v-if="message" class="mt-4">
      <div
        :class="[
          'p-4 rounded-lg border',
          message.type === 'success' 
            ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-700 dark:text-green-200'
            : 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-700 dark:text-red-200'
        ]"
      >
        <div class="flex items-center gap-2">
          <FeatherIcon 
            :name="message.type === 'success' ? 'check-circle' : 'alert-circle'" 
            class="w-5 h-5" 
          />
          <span class="font-medium">{{ message.text }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Button, FormControl, Select, Autocomplete, Avatar, FeatherIcon } from 'frappe-ui'
import { call } from 'frappe-ui'

const props = defineProps({
  taskId: {
    type: String,
    default: null
  },
  initialData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['submit', 'cancel', 'delete'])

// Reactive state
const loading = ref(false)
const deleting = ref(false)
const loadingProjects = ref(false)
const loadingUsers = ref(false)
const message = ref(null)
const errors = ref({})

// Form data
const formData = ref({
  subject: '',
  description: '',
  project: null,
  priority: 'Medium',
  status: 'Open',
  expected_time: 0,
  exp_start_date: '',
  exp_end_date: '',
  assigned_to: null,
  department: ''
})

// Options
const projectOptions = ref([])
const userOptions = ref([])
const departmentOptions = ref([])
const customFields = ref([])

// Constants
const priorityOptions = [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' },
  { label: 'Urgent', value: 'Urgent' }
]

const statusOptions = [
  { label: 'Open', value: 'Open' },
  { label: 'Working', value: 'Working' },
  { label: 'Pending Review', value: 'Pending Review' },
  { label: 'Overdue', value: 'Overdue' },
  { label: 'Template', value: 'Template' },
  { label: 'Completed', value: 'Completed' },
  { label: 'Cancelled', value: 'Cancelled' }
]

// Computed
const isEditing = computed(() => !!props.taskId)

// Methods
const loadInitialData = async () => {
  try {
    // Load departments
    const departments = await call('frappe.desk.search.search_link', {
      doctype: 'Department',
      txt: ''
    })
    departmentOptions.value = departments.map(d => ({ label: d.value, value: d.value }))

    // Load custom fields
    const fields = await call('frappe.desk.form.load.get_meta', {
      doctype: 'Task'
    })
    customFields.value = fields.docs[0].fields.filter(f => 
      f.is_custom_field && !f.hidden && f.fieldtype !== 'Section Break'
    )

    // If editing, load task data
    if (props.taskId) {
      const taskDoc = await call('frappe.desk.form.load.getdoc', {
        doctype: 'Task',
        name: props.taskId
      })
      Object.assign(formData.value, taskDoc.docs[0])
    } else if (props.initialData) {
      Object.assign(formData.value, props.initialData)
    }
  } catch (error) {
    console.error('Error loading initial data:', error)
    showMessage('error', 'Failed to load form data')
  }
}

const searchProjects = async (query) => {
  if (!query || query.length < 2) {
    projectOptions.value = []
    return
  }
  
  loadingProjects.value = true
  try {
    const projects = await call('frappe.desk.search.search_link', {
      doctype: 'Project',
      txt: query
    })
    projectOptions.value = projects.map(p => ({ label: p.value, value: p.value }))
  } catch (error) {
    console.error('Error searching projects:', error)
  } finally {
    loadingProjects.value = false
  }
}

const searchUsers = async (query) => {
  if (!query || query.length < 2) {
    userOptions.value = []
    return
  }
  
  loadingUsers.value = true
  try {
    const users = await call('frappe.desk.search.search_link', {
      doctype: 'User',
      txt: query
    })
    
    // Enrich with user details
    const enrichedUsers = await Promise.all(
      users.map(async (user) => {
        try {
          const userDoc = await call('frappe.desk.form.load.getdoc', {
            doctype: 'User',
            name: user.value
          })
          return {
            label: userDoc.docs[0].full_name || user.value,
            value: user.value,
            full_name: userDoc.docs[0].full_name || user.value,
            email: user.value,
            user_image: userDoc.docs[0].user_image
          }
        } catch {
          return {
            label: user.value,
            value: user.value,
            full_name: user.value,
            email: user.value
          }
        }
      })
    )
    
    userOptions.value = enrichedUsers
  } catch (error) {
    console.error('Error searching users:', error)
  } finally {
    loadingUsers.value = false
  }
}

const getSelectOptions = (optionsString) => {
  if (!optionsString) return []
  return optionsString.split('\n').map(option => ({
    label: option.trim(),
    value: option.trim()
  }))
}

const validateForm = () => {
  errors.value = {}
  
  if (!formData.value.subject?.trim()) {
    errors.value.subject = 'Task subject is required'
  }
  
  if (!formData.value.priority) {
    errors.value.priority = 'Priority is required'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    showMessage('error', 'Please fix the errors and try again')
    return
  }
  
  loading.value = true
  try {
    const method = isEditing.value ? 'frappe.desk.form.save.savedocs' : 'frappe.desk.form.save.savedocs'
    const docData = {
      doctype: 'Task',
      ...formData.value
    }
    
    if (isEditing.value) {
      docData.name = props.taskId
    }
    
    const result = await call(method, {
      doc: JSON.stringify(docData),
      action: 'Save'
    })
    
    showMessage('success', isEditing.value ? 'Task updated successfully' : 'Task created successfully')
    emit('submit', result)
  } catch (error) {
    console.error('Error saving task:', error)
    showMessage('error', error.message || 'Failed to save task')
  } finally {
    loading.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Are you sure you want to delete this task?')) {
    return
  }
  
  deleting.value = true
  try {
    await call('frappe.client.delete', {
      doctype: 'Task',
      name: props.taskId
    })
    
    showMessage('success', 'Task deleted successfully')
    emit('delete')
  } catch (error) {
    console.error('Error deleting task:', error)
    showMessage('error', error.message || 'Failed to delete task')
  } finally {
    deleting.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

const resetForm = () => {
  formData.value = {
    subject: '',
    description: '',
    project: null,
    priority: 'Medium',
    status: 'Open',
    expected_time: 0,
    exp_start_date: '',
    exp_end_date: '',
    assigned_to: null,
    department: ''
  }
  errors.value = {}
  message.value = null
}

const showMessage = (type, text) => {
  message.value = { type, text }
  setTimeout(() => {
    message.value = null
  }, 5000)
}

// Lifecycle
onMounted(() => {
  loadInitialData()
})

// Watchers
watch(() => props.taskId, () => {
  if (props.taskId) {
    loadInitialData()
  }
})

watch(() => props.initialData, (newData) => {
  if (newData) {
    Object.assign(formData.value, newData)
  }
}, { deep: true })
</script>

<style scoped>
/* Form styling enhancements */
.form-control:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Smooth transitions */
* {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
