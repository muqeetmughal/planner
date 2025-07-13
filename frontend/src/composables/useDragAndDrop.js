import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useErrorHandler } from '@/services/errorHandler'

export function useDragAndDrop() {
  const { handleApiError } = useErrorHandler()
  const isDragging = ref(false)
  const draggedTask = ref(null)
  const dropTarget = ref(null)

  // Resource for updating task position
  const moveTaskResource = createResource({
    url: 'planner.api.move_task',
    onError: (error) => {
      handleApiError(error)
    }
  })

  // Start dragging
  const onDragStart = (task, event) => {
    isDragging.value = true
    draggedTask.value = task
    
    // Add dragging class for visual feedback
    if (event.item) {
      event.item.classList.add('dragging')
    }
  }

  // End dragging
  const onDragEnd = (event) => {
    isDragging.value = false
    draggedTask.value = null
    dropTarget.value = null

    // Remove dragging class
    if (event.item) {
      event.item.classList.remove('dragging')
    }
  }

  // Handle dropping task with enhanced date/datetime support
  const onDrop = async (target) => {
    if (!draggedTask.value || !target) return

    try {
      const updates = {
        task_id: draggedTask.value.id,
        assignee_id: target.assigneeId,
        start_date: target.date,
        end_date: target.date // Will be adjusted based on task duration
      }

      // Enhanced date handling for both date and datetime fields
      if (target.date) {
        let targetDate = target.date
        
        // Normalize date format - handle both date and datetime strings
        if (typeof targetDate === 'string') {
          if (targetDate.includes(' ')) {
            targetDate = targetDate.split(' ')[0] // Extract date part from datetime
          } else if (targetDate.includes('T')) {
            targetDate = targetDate.split('T')[0] // Extract date part from ISO datetime
          }
        } else if (targetDate instanceof Date) {
          targetDate = targetDate.toISOString().split('T')[0]
        }
        
        updates.start_date = targetDate
        
        // Calculate end date based on task duration
        if (draggedTask.value.duration) {
          const startDate = new Date(targetDate)
          const endDate = new Date(startDate)
          
          // Handle different duration types
          if (typeof draggedTask.value.duration === 'number') {
            if (draggedTask.value.duration >= 1) {
              // Duration in days
              endDate.setDate(startDate.getDate() + Math.floor(draggedTask.value.duration))
            } else {
              // Duration in hours
              endDate.setHours(endDate.getHours() + (draggedTask.value.duration * 24))
            }
          }
          
          updates.end_date = endDate.toISOString().split('T')[0]
        } else {
          updates.end_date = targetDate // Single day task
        }
      }

      await moveTaskResource.submit(updates)

    } catch (error) {
      console.error('Error moving task:', error)
      handleApiError(error)
    }
  }

  // Handle dragging over a drop zone
  const onDragOver = (target, event) => {
    event.preventDefault()
    dropTarget.value = target

    // Add visual feedback for valid drop targets
    const dropZone = event.currentTarget
    if (dropZone) {
      dropZone.classList.add('drop-target')
    }
  }

  // Handle dragging out of a drop zone
  const onDragLeave = (event) => {
    const dropZone = event.currentTarget
    if (dropZone) {
      dropZone.classList.remove('drop-target')
    }
  }

  // Computed properties for drag state
  const isDraggingTask = computed(() => isDragging.value && draggedTask.value !== null)
  const currentDropTarget = computed(() => dropTarget.value)

  // Drag options for Vue.Draggable
  const dragOptions = {
    animation: 150,
    ghostClass: 'ghost',
    dragClass: 'dragging',
    group: 'tasks',
    handle: '.draggable-handle'
  }

  return {
    // State
    isDragging,
    draggedTask,
    dropTarget,
    isDraggingTask,
    currentDropTarget,

    // Methods
    onDragStart,
    onDragEnd,
    onDrop,
    onDragOver,
    onDragLeave,

    // Configuration
    dragOptions,

    // Resources
    moveTaskResource
  }
}
