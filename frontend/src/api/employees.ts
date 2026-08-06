import http from './http'
import type { Employee, EmployeeListResponse, EmployeeSelfUpdate } from '@/types/employee'

export interface EmployeeListParams {
  search?: string
  position?: string
  is_active?: boolean
  offset?: number
  limit?: number
}

export function fetchEmployees(params: EmployeeListParams) {
  return http.get<EmployeeListResponse>('/employees', { params }).then((res) => res.data)
}

export function fetchPositions() {
  return http.get<string[]>('/employees/positions').then((res) => res.data)
}

export function fetchEmployee(id: number) {
  return http.get<Employee>(`/employees/${id}`).then((res) => res.data)
}

export function fetchMyEmployee() {
  return http.get<Employee>('/employees/me').then((res) => res.data)
}

export function updateMyEmployee(data: EmployeeSelfUpdate) {
  return http.patch<Employee>('/employees/me', data).then((res) => res.data)
}
