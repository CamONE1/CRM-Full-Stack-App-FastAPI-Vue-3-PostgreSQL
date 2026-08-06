import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as employeesApi from '@/api/employees'
import type { EmployeeListParams } from '@/api/employees'
import type { Employee, EmployeeSelfUpdate } from '@/types/employee'

export const useEmployeesStore = defineStore('employees', () => {
  const items = ref<Employee[]>([])
  const total = ref(0)
  const positions = ref<string[]>([])
  const current = ref<Employee | null>(null)
  const myProfile = ref<Employee | null>(null)
  const isLoading = ref(false)

  async function fetchList(params: EmployeeListParams): Promise<void> {
    isLoading.value = true
    try {
      const data = await employeesApi.fetchEmployees(params)
      items.value = data.items
      total.value = data.total
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPositions(): Promise<void> {
    positions.value = await employeesApi.fetchPositions()
  }

  async function fetchById(id: number): Promise<void> {
    current.value = await employeesApi.fetchEmployee(id)
  }

  async function fetchMyProfile(): Promise<void> {
    myProfile.value = await employeesApi.fetchMyEmployee()
  }

  async function updateMyProfile(data: EmployeeSelfUpdate): Promise<void> {
    myProfile.value = await employeesApi.updateMyEmployee(data)
  }

  return {
    items,
    total,
    positions,
    current,
    myProfile,
    isLoading,
    fetchList,
    fetchPositions,
    fetchById,
    fetchMyProfile,
    updateMyProfile,
  }
})
