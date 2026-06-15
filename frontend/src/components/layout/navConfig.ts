import {
  BarChart3,
  BookOpen,
  Calendar,
  ClipboardList,
  CreditCard,
  Home,
  Trophy,
  Users,
  type LucideIcon,
} from 'lucide-react'

import type { UserRole } from '../../lib/types'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

const STUDENT: NavItem[] = [
  { to: '/', label: 'Главная', icon: Home },
  { to: '/catalog', label: 'Курсы', icon: BookOpen },
  { to: '/achievements', label: 'Награды', icon: Trophy },
  { to: '/schedule', label: 'Расписание', icon: Calendar },
]

const PARENT: NavItem[] = [
  { to: '/parent', label: 'Главная', icon: Home },
  { to: '/parent/children', label: 'Дети', icon: Users },
  { to: '/parent/payments', label: 'Оплата', icon: CreditCard },
]

const TEACHER: NavItem[] = [
  { to: '/teacher', label: 'Группы', icon: Users },
  { to: '/teacher/queue', label: 'Проверка', icon: ClipboardList },
]

const ADMIN: NavItem[] = [
  { to: '/admin', label: 'Сводка', icon: BarChart3 },
  { to: '/admin/users', label: 'Пользователи', icon: Users },
  { to: '/admin/content', label: 'Контент', icon: BookOpen },
  { to: '/admin/payments', label: 'Платежи', icon: CreditCard },
  { to: '/admin/groups', label: 'Группы', icon: Calendar },
]

export function navItemsFor(role: UserRole): NavItem[] {
  switch (role) {
    case 'student':
      return STUDENT
    case 'parent':
      return PARENT
    case 'teacher':
      return TEACHER
    case 'admin':
      return ADMIN
  }
}
