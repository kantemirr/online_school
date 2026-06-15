import { NavLink } from 'react-router-dom'

import { cn } from '../../lib/cn'
import { navItems } from './navConfig'

/** Нижняя таб-навигация для телефона (крупные тач-зоны ≥44px). */
export function BottomNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-surface lg:hidden">
      {navItems.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
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
