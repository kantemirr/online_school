import { BookOpen, Home, Palette, Trophy, type LucideIcon } from 'lucide-react'

export interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

// Базовая навигация. Ролевые наборы пунктов появятся на под-этапах кабинетов.
export const navItems: NavItem[] = [
  { to: '/', label: 'Главная', icon: Home },
  { to: '/catalog', label: 'Курсы', icon: BookOpen },
  { to: '/achievements', label: 'Награды', icon: Trophy },
  { to: '/styleguide', label: 'UI-кит', icon: Palette },
]
