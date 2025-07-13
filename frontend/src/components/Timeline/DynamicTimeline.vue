<template>
	<div class="dynamic-timeline min-h-screen bg-gray-50">
		<!-- Header -->
		<div class="timeline-header mb-6 p-6 bg-white rounded-lg shadow border mx-6 mt-6">
			<div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
				<!-- Left Section -->
				<div class="flex items-center gap-4">
					<Button
						variant="ghost"
						@click="$emit('backToSelector')"
						class="flex items-center gap-2"
					>
						<FeatherIcon name="arrow-left" class="w-4 h-4" />
						Back to Configurations
					</Button>

					<div class="border-l pl-4">
						<div class="flex items-center gap-3 mb-1">
							<h1 class="text-xl font-semibold text-gray-900">
								{{ config?.configuration_name || "Dynamic Timeline" }}
							</h1>
						</div>
						<div class="flex items-center gap-2 text-sm text-gray-600">
							<span class="px-2 py-1 bg-gray-100 rounded font-medium">
								{{ config?.row_doctype }}
							</span>
							<FeatherIcon name="arrow-right" class="w-3 h-3" />
							<span class="px-2 py-1 bg-gray-100 rounded font-medium">
								{{ config?.block_doctype }}
							</span>
						</div>
					</div>
				</div>

				<!-- Right Section -->
				<div class="flex items-center gap-4">
					<!-- Date Navigation -->
					<div class="flex items-center gap-2 bg-white rounded-lg p-2 border">
						<Button variant="ghost" size="sm" @click="navigateDate(-1)">
							<FeatherIcon name="chevron-left" class="w-4 h-4" />
						</Button>

						<div class="px-4 py-2 text-center font-medium min-w-[200px]">
							{{ formatDateRange() }}
						</div>

						<Button variant="ghost" size="sm" @click="navigateDate(1)">
							<FeatherIcon name="chevron-right" class="w-4 h-4" />
						</Button>

						<div class="h-6 w-px bg-gray-300 mx-2"></div>

						<Button variant="ghost" size="sm" @click="goToToday">
							<FeatherIcon name="calendar" class="w-4 h-4 mr-2" />
							Today
						</Button>
					</div>

					<!-- View Mode Toggle -->
					<div class="flex bg-gray-100 rounded-lg p-1">
						<button
							v-for="mode in viewModes"
							:key="mode.value"
							@click="currentViewMode = mode.value"
							:class="[
								'px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2',
								currentViewMode === mode.value
									? 'bg-white text-gray-900 shadow-sm'
									: 'text-gray-600 hover:text-gray-900',
							]"
						>
							<FeatherIcon :name="mode.icon" class="w-4 h-4" />
							{{ mode.label }}
						</button>
					</div>

					<!-- Unassigned Panel Toggle -->
					<Button
						variant="ghost"
						size="sm"
						@click="toggleUnassignedPanel"
						:class="showUnassignedPanel ? 'bg-amber-50' : ''"
					>
						<FeatherIcon
							name="inbox"
							:class="['w-4 h-4', showUnassignedPanel ? 'text-amber-600' : '']"
						/>
					</Button>

					<!-- Refresh Button -->
					<Button
						variant="ghost"
						size="sm"
						@click="refreshData"
						:loading="loading"
					>
						<FeatherIcon
							name="refresh-cw"
							:class="['w-4 h-4', loading ? 'animate-spin' : '']"
						/>
					</Button>
				</div>
			</div>

			<!-- Stats Bar -->
			<div class="mt-4 p-4 bg-gray-50 rounded-lg border">
				<div class="flex items-center justify-between text-sm">
					<div class="flex items-center gap-6">
						<div class="flex items-center gap-2">
							<div class="w-3 h-3 bg-blue-500 rounded-full"></div>
							<div>
								<div class="font-semibold text-lg text-gray-800">
									{{ rows.length }}
								</div>
								<div class="text-xs text-gray-600">
									{{ config?.row_doctype || "Rows" }}
								</div>
							</div>
						</div>

						<div class="flex items-center gap-2">
							<div class="w-3 h-3 bg-green-500 rounded-full"></div>
							<div>
								<div class="font-semibold text-lg text-gray-800">
									{{ blocks.length }}
								</div>
								<div class="text-xs text-gray-600">
									{{ config?.block_doctype || "Blocks" }}
								</div>
							</div>
						</div>

						<div class="flex items-center gap-2">
							<div class="w-3 h-3 bg-amber-500 rounded-full"></div>
							<div>
								<div class="font-semibold text-lg text-gray-800">
									{{ unassignedBlocks.length }}
								</div>
								<div class="text-xs text-gray-600">Unassigned</div>
							</div>
						</div>
					</div>

					<div class="flex items-center gap-2 text-gray-600">
						<FeatherIcon name="clock" class="w-4 h-4" />
						<span>{{ formatDateRange() }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Loading State -->
		<div v-if="loading" class="flex items-center justify-center py-16">
			<div class="bg-white rounded-lg p-6 shadow border">
				<div class="flex items-center gap-4">
					<div
						class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"
					></div>
					<div>
						<div class="font-medium text-gray-900 mb-1">
							Loading Timeline Data
						</div>
						<div class="text-sm text-gray-600">
							Please wait while we fetch your data...
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Error State -->
		<div v-else-if="error" class="mx-6">
			<div class="bg-red-50 border border-red-200 rounded-lg p-6">
				<div class="flex items-start gap-4">
					<div class="flex-shrink-0">
						<div
							class="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center"
						>
							<FeatherIcon name="alert-triangle" class="w-5 h-5 text-white" />
						</div>
					</div>
					<div class="flex-1">
						<h3 class="text-lg font-semibold text-red-900 mb-2">
							Unable to Load Timeline Data
						</h3>
						<p class="text-red-700 mb-4">{{ error }}</p>
						<Button variant="outline" size="sm" @click="refreshData">
							<FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
							Try Again
						</Button>
					</div>
				</div>
			</div>
		</div>

		<!-- Timeline Views -->
		<div v-else class="timeline-view mx-6 mb-6">
			<div class="bg-white rounded-lg border overflow-hidden shadow">
				<!-- Day View -->
				<DynamicTimelineDayView
					v-if="currentViewMode === 'day'"
					:config="config"
					:rows="rows"
					:blocks="blocks"
					:currentDate="currentDate"
					:loading="loading"
					@blockMove="handleBlockMove"
					@blockClick="handleBlockClick"
					@addBlock="handleAddBlock"
					@blockResize="handleBlockResize"
					@goToToday="goToToday"
					class="enhanced-day-view"
				/>
				
				<!-- Standard Grid View (Week/Month/etc.) -->
				<DynamicTimelineGrid
					v-else
					:config="config"
					:rows="rows"
					:blocks="blocks"
					:dateColumns="dateColumns"
					:loading="loading"
					:showUnassignedPanel="showUnassignedPanel"
					@blockMove="handleBlockMove"
					@blockClick="handleBlockClick"
					@addBlock="handleAddBlock"
					@blockResize="handleBlockResize"
					@assignTask="handleAssignTask"
					@toggleUnassignedPanel="toggleUnassignedPanel"
					class="enhanced-grid"
				/>
			</div>
		</div>

		<!-- Block Details Dialog -->
		<Dialog
			v-model="showBlockDetails"
			:options="{
				title: config?.block_doctype + ' Details',
				size: 'large',
			}"
		>
			<template #body-content>
				<DynamicBlockDetails
					v-if="selectedBlock"
					:block="selectedBlock"
					:config="config"
					@close="closeBlockDetails"
					@update="handleBlockUpdate"
				/>
			</template>
		</Dialog>

		<!-- Add Block Button -->
		<div class="fixed bottom-6 right-6 z-40">
			<Button
				variant="solid"
				size="lg"
				@click="showAddBlockDialog = true"
				class="rounded-full shadow-lg"
			>
				<FeatherIcon name="plus" class="w-5 h-5" />
			</Button>
		</div>

		<!-- Add Block Dialog -->
		<Dialog
			v-model="showAddBlockDialog"
			:options="{
				title: 'Add New Block',
				size: 'large',
			}"
		>
			<template #body-content>
				<div class="space-y-4">
					<div class="grid grid-cols-2 gap-4">
						<FormControl
							label="Title"
							v-model="newBlockForm.title"
							placeholder="Enter block title"
						/>
						<FormControl
							type="select"
							label="Priority"
							v-model="newBlockForm.priority"
							:options="['Low', 'Medium', 'High']"
						/>
					</div>
					<FormControl
						type="textarea"
						label="Description"
						v-model="newBlockForm.description"
						placeholder="Enter block description"
					/>
					<div class="grid grid-cols-2 gap-4">
						<FormControl
							type="date"
							label="Start Date"
							v-model="newBlockForm.start_date"
						/>
						<FormControl
							type="date"
							label="End Date"
							v-model="newBlockForm.end_date"
						/>
					</div>
					<FormControl
						type="number"
						label="Duration (hours)"
						v-model="newBlockForm.duration"
						placeholder="Enter duration in hours"
					/>
				</div>
			</template>
			<template #actions>
				<Button variant="outline" @click="showAddBlockDialog = false">
					Cancel
				</Button>
				<Button variant="solid" @click="handleCreateBlock">
					Create Block
				</Button>
			</template>
		</Dialog>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { Button, FeatherIcon, Dialog, FormControl } from "frappe-ui";
import { call } from "frappe-ui";
import DynamicTimelineGrid from "./DynamicTimelineGrid.vue";
import DynamicTimelineDayView from "./DynamicTimelineDayView.vue";
import DynamicBlockDetails from "./DynamicBlockDetails.vue";
import { toast } from "../../composables/useToast";

const props = defineProps({
	configuration: {
		type: Object,
		required: true,
	},
});

const emit = defineEmits(["backToSelector"]);

// Reactive state
const config = ref(null);
const rows = ref([]);
const blocks = ref([]);
const loading = ref(false);
const error = ref(null);
const selectedBlock = ref(null);
const showAddBlockDialog = ref(false);
const addBlockData = ref(null);
const showUnassignedPanel = ref(true);

// View state
const currentViewMode = ref("week");
const currentDate = ref(new Date());
const newBlockForm = ref({
	title: "",
	description: "",
	priority: "Medium",
	start_date: "",
	end_date: "",
	duration: 1,
});

// Constants
const viewModes = [
	{ label: "Day", value: "day", icon: "clock" },
	{ label: "Week", value: "week", icon: "calendar" },
	{ label: "Month", value: "month", icon: "calendar" },
	{ label: "2 Weeks", value: "biweek", icon: "calendar" },
];

// Computed properties
const showBlockDetails = computed({
	get: () => !!selectedBlock.value,
	set: (value) => {
		if (!value) selectedBlock.value = null;
	},
});

const dateColumns = computed(() => {
	const columns = [];
	const today = new Date();
	let startDate, daysToShow;

	switch (currentViewMode.value) {
		case "week":
			startDate = getWeekStart(currentDate.value);
			daysToShow = 7;
			break;
		case "biweek":
			startDate = getWeekStart(currentDate.value);
			daysToShow = 14;
			break;
		case "month":
			startDate = new Date(
				currentDate.value.getFullYear(),
				currentDate.value.getMonth(),
				1,
			);
			daysToShow = getDaysInMonth(currentDate.value);
			break;
		default:
			startDate = getWeekStart(currentDate.value);
			daysToShow = 7;
	}

	for (let i = 0; i < daysToShow; i++) {
		const date = new Date(startDate);
		date.setDate(startDate.getDate() + i);

		const isToday = date.toDateString() === today.toDateString();
		const isWeekend = date.getDay() === 0 || date.getDay() === 6;

		columns.push({
			key: date.toISOString().split("T")[0],
			date: date,
			label: date.getDate().toString(),
			sublabel: date.toLocaleDateString("en-US", { weekday: "short" }),
			isToday,
			isWeekend,
		});
	}

	return columns;
});

const unassignedBlocks = computed(() => {
	return blocks.value.filter((block) => !block.row_id);
});

// Methods
const loadTimelineData = async () => {
	if (!props.configuration) return;

	loading.value = true;
	error.value = null;

	try {
		const startDate = dateColumns.value[0]?.date.toISOString().split("T")[0];
		const endDate = dateColumns.value[dateColumns.value.length - 1]?.date
			.toISOString()
			.split("T")[0];

		const response = await call("planner.api.get_timeline_data", {
			configuration_name: props.configuration.name,
			start_date: startDate,
			end_date: endDate,
			filters: {},
		});

		if (response.success) {
			config.value = response.config;
			rows.value = response.rows || [];
			blocks.value = response.blocks || [];
		} else {
			error.value = response.error || "Failed to load timeline data";
		}
	} catch (err) {
		error.value = err.message || "Failed to load timeline data";
		config.value = null;
		rows.value = [];
		blocks.value = [];
	} finally {
		loading.value = false;
	}
};

const refreshData = () => {
	loadTimelineData();
};

const navigateDate = (direction) => {
	const newDate = new Date(currentDate.value);
	let daysToMove;

	switch (currentViewMode.value) {
		case "week":
			daysToMove = 7;
			break;
		case "biweek":
			daysToMove = 14;
			break;
		case "month":
			newDate.setMonth(newDate.getMonth() + direction);
			currentDate.value = newDate;
			return;
		default:
			daysToMove = 7;
	}

	newDate.setDate(newDate.getDate() + direction * daysToMove);
	currentDate.value = newDate;
};

const goToToday = () => {
	currentDate.value = new Date();
};

const formatDateRange = () => {
	if (!dateColumns.value.length) return "";

	switch (currentViewMode.value) {
		case "week":
		case "biweek":
			const start = dateColumns.value[0].date;
			const end = dateColumns.value[dateColumns.value.length - 1].date;
			return `${start.toLocaleDateString("en-US", { month: "short", day: "numeric" })} - ${end.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`;
		case "month":
			return currentDate.value.toLocaleDateString("en-US", {
				year: "numeric",
				month: "long",
			});
		default:
			return "";
	}
};

const getWeekStart = (date) => {
	const d = new Date(date);
	const day = d.getDay();
	const diff = d.getDate() - day + (day === 0 ? -6 : 1);
	return new Date(d.setDate(diff));
};

const getDaysInMonth = (date) => {
	return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
};

const handleBlockMove = async (data) => {
	try {
		let moveDate = data.newDate;
		if (data.newDateTime) {
			moveDate = new Date(data.newDateTime).toISOString().split('T')[0];
		}
		
		const response = await call("planner.api.update_block_assignment", {
			block_doctype: config.value.block_doctype,
			block_name: data.blockId,
			new_row_assignment: data.newRowId,
			new_date: moveDate,
			new_datetime: data.newDateTime,
			config_name: config.value.name,
		});

		if (response.success) {
			await loadTimelineData();
			toast.success("Block moved successfully");
		} else {
			throw new Error(response.error || "Failed to move block");
		}
	} catch (err) {
		toast.error("Failed to move block: " + err.message);
	}
};

const handleBlockClick = (blockId) => {
	const block = blocks.value.find((b) => b.id === blockId);
	selectedBlock.value = block;
};

const handleAddBlock = (data) => {
	showAddBlockDialog.value = true;
	addBlockData.value = data;
};

const handleBlockUpdate = async (data) => {
	try {
		closeBlockDetails();
		await loadTimelineData();
	} catch (err) {
		// Handle error
	}
};

const handleBlockResize = async (data) => {
	try {
		const response = await call("planner.api.update_block_date_range", {
			block_doctype: config.value.block_doctype,
			block_name: data.blockId,
			new_duration: data.newDuration,
			new_start_date: data.newStartDate,
			new_end_date: data.newEndDate,
			config_name: config.value.name,
			direction: data.direction
		});

		if (response.success) {
			await loadTimelineData();
			toast.success("Block duration updated successfully");
		} else {
			throw new Error(response.error || "Failed to update block duration");
		}
	} catch (err) {
		toast.error("Failed to update block duration: " + err.message);
	}
};

const closeBlockDetails = () => {
	selectedBlock.value = null;
};

const handleCreateBlock = async () => {
	try {
		if (!newBlockForm.value.title.trim()) {
			toast.error("Please enter a block title");
			return;
		}

		const blockData = {
			...newBlockForm.value,
			row_id: addBlockData.value?.rowId,
			date: addBlockData.value?.date,
			doctype: config.value.block_doctype,
		};

		await call("planner.api.create_block", blockData);

		// Reset form
		newBlockForm.value = {
			title: "",
			description: "",
			priority: "Medium",
			start_date: "",
			end_date: "",
			duration: 1,
		};

		showAddBlockDialog.value = false;
		addBlockData.value = null;

		// Refresh data
		await refreshData();

		toast.success("Block created successfully");
	} catch (error) {
		toast.error("Failed to create block");
	}
};

const handleAssignTask = async (data) => {
	try {
		const { taskId, rowId, date, taskData } = data;

		await call("planner.api.assign_task", {
			task_id: taskId,
			row_id: rowId,
			date: date,
			task_data: taskData,
		});

		await refreshData();
		toast.success("Task assigned successfully");
	} catch (error) {
		toast.error("Failed to assign task");
	}
};

const toggleUnassignedPanel = () => {
	showUnassignedPanel.value = !showUnassignedPanel.value;
};

// Watch for configuration changes
watch(
	() => props.configuration,
	() => {
		if (props.configuration) {
			loadTimelineData();
		}
	},
	{ immediate: true },
);

// Watch for date/view changes
watch([currentDate, currentViewMode], () => {
	loadTimelineData();
});

// Initialize
onMounted(() => {
	if (props.configuration) {
		loadTimelineData();
	}
});
</script>

<style scoped>
.dynamic-timeline {
	width: 100%;
	min-height: 100vh;
}

.timeline-grid {
	min-height: 600px;
}

.enhanced-grid {
	animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
	from {
		opacity: 0;
	}
	to {
		opacity: 1;
	}
}
</style>