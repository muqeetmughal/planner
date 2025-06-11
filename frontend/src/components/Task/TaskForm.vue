<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Basic Information -->
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Subject</label>
        <input
          v-model="formData.subject"
          type="text"
          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          required
        >
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="formData.status"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          >
            <option value="Open">Open</option>
            <option value="Working">Working</option>
            <option value="Pending Review">Pending Review</option>
            <option value="Overdue">Overdue</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Priority</label>
          <select
            v-model="formData.priority"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          >
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Urgent">Urgent</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Department</label>
        <select
          v-model="formData.department"
          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          required
        >
          <option v-for="dept in availableDepartments" :key="dept" :value="dept">
            {{ dept }}
          </option>
        </select>
      </div>
    </div>

    <!-- Dates and Time -->
    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Start Date</label>
          <input
            v-model="formData.exp_start_date"
            type="date"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">End Date</label>
          <input
            v-model="formData.exp_end_date"
            type="date"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          >
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Expected Hours</label>
          <input
            v-model.number="formData.expected_time"
            type="number"
            min="0"
            step="0.5"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Progress (%)</label>
          <input
            v-model.number="formData.progress"
            type="number"
            min="0"
            max="100"
            class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
          >
        </div>
      </div>
    </div>

    <!-- Assignment -->
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Assign To</label>
      <select
        v-model="formData.assigned_to"
        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
      >
        <option value="">Unassigned</option>
        <option v-for="assignee in assignees" :key="assignee.id" :value="assignee.id">
          {{ assignee.name }}
        </option>
      </select>
    </div>

    <!-- Additional Fields -->
    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
        <textarea
          v-model="formData.description"
          rows="4"
          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
        ></textarea>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Color</label>
          <input
            v-model="formData.color"
            type="color"
            class="mt-1 block w-full h-10 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
        </div>

        <div class="flex items-center">
          <input
            v-model="formData.is_milestone"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          >
          <label class="ml-2 block text-sm text-gray-700 dark:text-gray-300">Is Milestone</label>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-end gap-3">
      <Button
        variant="ghost"
        theme="gray"
        @click="$emit('close')"
      >
        Cancel
      </Button>
      <Button
        variant="solid"
        theme="blue"
        type="submit"
        :loading="loading"
      >
        {{ task ? 'Update Task' : 'Create Task' }}
      </Button>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
  task: {
    type: Object,
    default: null
  },
  department: {
    type: String,
    default: ''
  },
  assignees: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'update', 'create'])

const loading = ref(false)
const formData = ref({
  subject: '',
  status: 'Open',
  priority: 'Medium',
  department: props.department,
  exp_start_date: '',
  exp_end_date: '',
  expected_time: 0,
  progress: 0,
  assigned_to: '',
  description: '',
  color: '#3B82F6',
  is_milestone: false
})

// Load task data if editing
watch(() => props.task, (newTask) => {
  if (newTask) {
    formData.value = {
      subject: newTask.subject,
      status: newTask.status,
      priority: newTask.priority,
      department: newTask.department,
      exp_start_date: newTask.exp_start_date,
      exp_end_date: newTask.exp_end_date,
      expected_time: newTask.expected_time,
      progress: newTask.progress || 0,
      assigned_to: newTask._assign ? JSON.parse(newTask._assign)[0] : '',
      description: newTask.description || '',
      color: newTask.color || '#3B82F6',
      is_milestone: newTask.is_milestone || false
    }
  }
}, { immediate: true })

// Available departments from assignees
const availableDepartments = computed(() => {
  const departments = new Set()
  props.assignees.forEach(assignee => {
    if (assignee.department) {
      departments.add(assignee.department)
    }
  })
  return Array.from(departments).sort()
})

const handleSubmit = async () => {
  loading.value = true
  try {
    const taskData = {
      ...formData.value,
      _assign: formData.value.assigned_to ? JSON.stringify([formData.value.assigned_to]) : null
    }
    
    if (props.task) {
      emit('update', { taskId: props.task.id, updates: taskData })
    } else {
      emit('create', taskData)
    }
  } catch (error) {
    console.error('Error submitting task:', error)
  } finally {
    loading.value = false
  }
}
</script>
