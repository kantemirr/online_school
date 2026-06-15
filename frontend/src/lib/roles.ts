import type { UserRole } from './types'

/** Домашний маршрут кабинета по роли (куда вести после входа). */
export const ROLE_HOME: Record<UserRole, string> = {
  student: '/',
  parent: '/parent',
  teacher: '/teacher',
  admin: '/admin',
}

export const ROLE_LABEL: Record<UserRole, string> = {
  student: 'Ученик',
  parent: 'Родитель',
  teacher: 'Преподаватель',
  admin: 'Администратор',
}
