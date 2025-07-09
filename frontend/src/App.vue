<template>
  <div
    class="min-h-screen bg-gray-50 dark:bg-dark-bg transition-colors duration-300"
  >
    <router-view />
    <Toast />
  </div>
</template>
<script setup>
import Toast from "./components/shared/Toast.vue";
</script>
