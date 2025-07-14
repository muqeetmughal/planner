<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">
        Choose Timeline View
      </h2>
      <p class="text-gray-600">
        Select a timeline configuration to visualize your data in different ways
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="flex items-center gap-3">
        <div
          class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
        ></div>
        <span class="text-gray-600">Loading configurations...</span>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6"
    >
      <div class="flex items-center gap-2">
        <FeatherIcon name="alert-circle" class="w-5 h-5 text-red-500" />
        <span class="text-red-700 font-medium">Error loading configurations</span>
      </div>
      <p class="text-red-600 text-sm mt-1">{{ error }}</p>
      <Button
        variant="outline"
        theme="red"
        size="sm"
        class="mt-3"
        @click="loadConfigurations"
      >
        <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
        Retry
      </Button>
    </div>

    <!-- Empty State -->
    <div v-else-if="configurations.length === 0" class="text-center py-12">
      <div
        class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4"
      >
        <FeatherIcon name="calendar" class="w-8 h-8 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        No Timeline Configurations
      </h3>
      <p class="text-gray-600 mb-4">
        Create a timeline configuration to get started
      </p>
      <Button
        variant="solid"
        theme="blue"
        @click="createSampleConfiguration"
        :loading="creatingSample"
      >
        <FeatherIcon name="plus" class="w-4 h-4 mr-2" />
        Create Sample Configuration
      </Button>
    </div>

    <!-- Configuration List -->
    <div v-else class="space-y-4">
      <ListItem
        v-for="config in configurations"
        :key="config.name"
        :title="config.configuration_name"
        :description="config.description || `Timeline view showing ${config.block_doctype} blocks organized by ${config.row_doctype}`"
        @click="selectConfiguration(config)"
        clickable
      >
        <template #prefix>
          <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <FeatherIcon name="grid" class="w-4 h-4 text-blue-600" />
          </div>
        </template>
        
        <template #subtitle>
          <div class="flex items-center gap-2 mt-1">
            <Badge variant="subtle" theme="blue" size="sm">
              {{ config.row_doctype }}
            </Badge>
            <FeatherIcon name="arrow-right" class="w-3 h-3 text-gray-400" />
            <Badge variant="subtle" theme="green" size="sm">
              {{ config.block_doctype }}
            </Badge>
          </div>
        </template>

        <template #suffix>
          <FeatherIcon name="chevron-right" class="w-4 h-4 text-gray-400" />
        </template>
      </ListItem>
    </div>

    <!-- Action Buttons -->
    <div
      class="flex items-center justify-between mt-8 pt-6 border-t border-gray-200"
    >
      <div class="flex items-center gap-3">
        <Button
          variant="outline"
          theme="gray"
          @click="loadConfigurations"
          :loading="loading"
        >
          <FeatherIcon name="refresh-cw" class="w-4 h-4 mr-2" />
          Refresh
        </Button>

        <Button
          variant="outline"
          theme="blue"
          @click="createSampleConfiguration"
          :loading="creatingSample"
        >
          <FeatherIcon name="plus" class="w-4 h-4 mr-2" />
          Create Sample
        </Button>
      </div>

      <div class="text-sm text-gray-500">
        {{ configurations.length }} configuration{{
          configurations.length !== 1 ? "s" : ""
        }}
        available
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Button, FeatherIcon, ListItem, Badge } from "frappe-ui";
import { call } from "frappe-ui";
import { toast } from "../../composables/useToast";

const emit = defineEmits(["configurationSelected"]);

// Reactive state
const configurations = ref([]);
const loading = ref(false);
const error = ref(null);
const creatingSample = ref(false);

// Methods
const loadConfigurations = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await call("planner.api.timeline_data.get_timeline_configurations");
    configurations.value = response || [];
  } catch (err) {
    error.value = err.message || "Failed to load configurations";
    console.error("Error loading configurations:", err);
  } finally {
    loading.value = false;
  }
};

const selectConfiguration = (config) => {
  emit("configurationSelected", config);
};

const createSampleConfiguration = async () => {
  creatingSample.value = true;

  try {
    const response = await call(
      "planner.api.timeline_data.create_sample_workstation_configuration",
    );

    if (response.success) {
      // Reload configurations to show the new one
      await loadConfigurations();

      // Show success message
      toast.success("Sample configuration created successfully!");
    } else {
      throw new Error(
        response.error || "Failed to create sample configuration",
      );
    }
  } catch (err) {
    error.value = err.message || "Failed to create sample configuration";
    console.error("Error creating sample configuration:", err);

    toast.error("Failed to create sample configuration: " + err.message);
  } finally {
    creatingSample.value = false;
  }
};

// Initialize
onMounted(() => {
  loadConfigurations();
});
</script>

<style scoped>
/* Minimal custom styling - let Frappe UI handle the rest */
</style>
