export interface Employee {
  id: number
  user_id: number | null
  full_name: string
  email: string
  phone: string | null
  telegram: string | null
  department: string | null
  position: string | null
  hire_date: string | null
  is_active: boolean
  created_at: string
}

export interface EmployeeListResponse {
  items: Employee[]
  total: number
}

export interface EmployeeSelfUpdate {
  phone?: string
  telegram?: string
}
