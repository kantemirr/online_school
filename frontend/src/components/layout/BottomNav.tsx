import { NavLink } from 'react-router-dom'

import { cn } from '../../lib/cn'
import { useAppSelector } from '../../store/hooks'
import { navItemsFor } from './navConfig'

/** Нижняя таб-навигация для телефона (крупные тач-зоны ≥44px). */
export function BottomNav() {
  const role = useAppSelector((s) => s.auth.user?.role) ?? 'student'
  const items = navItemsFor(role)
  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-surface lg:hidden">
      {items.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/home' || to === '/parent' || to === '/teacher' || to === '/admin'}
          className={({ isActive }) =>
            cn(
              'flex flex-1 flex-col items-center gap-0.5 py-2 text-xs font-bold transition',
              isActive ? 'text-brand' : 'text-hint',
            )
          }
        >
          <Icon className="h-6 w-6" aria-hidden />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
