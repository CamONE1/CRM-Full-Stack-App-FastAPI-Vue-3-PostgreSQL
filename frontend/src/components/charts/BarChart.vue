<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

// Simple single-series bar chart. Colors are nominal (one flat accent hue,
// same for every bar) unless `colors` is passed — one hex per category, used
// for ordered categories (e.g. a funnel) where a light->dark ramp reinforces
// the sequence. Per dataviz-skill guidance: a value-ramp must never encode
// magnitude on unordered categories, only position in a real ordering.
const props = withDefaults(
  defineProps<{
    categories: string[]
    values: number[]
    colors?: string[]
    height?: number
  }>(),
  { height: 260 },
)

const ACCENT = '#4f46e5' // indigo-600, matches BaseButton's primary accent

const options = computed(() => ({
  chart: {
    type: 'bar' as const,
    toolbar: { show: false },
    fontFamily: 'inherit',
  },
  plotOptions: {
    bar: {
      columnWidth: '45%',
      borderRadius: 4,
      borderRadiusApplication: 'end' as const,
      distributed: !!props.colors,
    },
  },
  colors: props.colors ?? [ACCENT],
  dataLabels: {
    enabled: true,
    offsetY: -20,
    style: { colors: ['#374151'], fontSize: '12px' },
    formatter: (val: number) => String(Math.round(val)),
  },
  grid: {
    borderColor: '#e5e7eb',
    strokeDashArray: 0,
  },
  xaxis: {
    categories: props.categories,
    axisBorder: { color: '#d1d5db' },
    axisTicks: { color: '#d1d5db' },
    labels: { style: { colors: '#6b7280' } },
  },
  yaxis: {
    labels: {
      style: { colors: '#6b7280' },
      formatter: (val: number) => String(Math.round(val)),
    },
  },
  legend: { show: false },
  tooltip: { y: { formatter: (val: number) => String(Math.round(val)) } },
}))

const series = computed(() => [{ name: 'Значение', data: props.values }])
</script>

<template>
  <VueApexCharts type="bar" :height="height" :options="options" :series="series" />
</template>
