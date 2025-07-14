import { computed } from 'vue'

export function useDateCalculations() {
  const getWeekStart = (date) => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1)
    return new Date(d.setDate(diff))
  }

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
  }

  const formatDateRange = (currentDate, viewMode) => {
    switch (viewMode) {
      case 'week':
      case 'biweek':
        const start = getWeekStart(currentDate)
        const end = new Date(start)
        const days = viewMode === 'week' ? 6 : 13
        end.setDate(start.getDate() + days)
        return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
      case 'month':
        return currentDate.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
      default:
        return ''
    }
  }

  const calculateDateColumns = (currentDate, viewMode, holidays) => {
    const columns = []
    const today = new Date()
    let startDate, daysToShow
    
    switch (viewMode) {
      case 'week':
        startDate = getWeekStart(currentDate)
        daysToShow = 7
        break
      case 'biweek':
        startDate = getWeekStart(currentDate)
        daysToShow = 14
        break
      case 'month':
        startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
        daysToShow = getDaysInMonth(currentDate)
        break
      default:
        startDate = getWeekStart(currentDate)
        daysToShow = 7
    }
    
    for (let i = 0; i < daysToShow; i++) {
      const date = new Date(startDate)
      date.setDate(startDate.getDate() + i)
      
      const isToday = date.toDateString() === today.toDateString()
      const isWeekend = date.getDay() === 0 || date.getDay() === 6
      const isHoliday = holidays.some(holiday => 
        new Date(holiday.date).toDateString() === date.toDateString()
      )
      
      columns.push({
        key: date.toISOString().split('T')[0],
        date: date,
        label: date.getDate().toString(),
        sublabel: date.toLocaleDateString('en-US', { weekday: 'short' }),
        isToday,
        isWeekend,
        isHoliday
      })
    }
    
    return columns
  }

  return {
    getWeekStart,
    getDaysInMonth,
    formatDateRange,
    calculateDateColumns
  }
}
