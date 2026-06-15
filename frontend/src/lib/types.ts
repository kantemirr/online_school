export type UserRole = 'student' | 'parent' | 'teacher' | 'admin'

export interface MeOut {
  id: number
  email: string | null
  role: UserRole
  is_active: boolean
  display_name: string | null
}

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  size: number
}
