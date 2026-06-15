import { NavLink } from 'react-router-dom'

import { cn } from '../../lib/cn'
import { useAppSelector } from '../../store/hooks'
import { Kodik } from '../mascot/Kodik'
import { navItemsFor } from './navConfig'

export function Sidebar() {
  const role = useAppSelector((s) => s.auth.user?.role) ?? 'student'
  const items = navItemsFor(role)
  return (
    <aside className="hidden w-60 shrink-0 flex-col gap-1 border-r border-line bg-surface p-4 lg:flex">
      <div className="mb-4 flex items-center gap-2 px-2">
        <Kodik mood="wave" size={40} aria-hidden />
        <span className="text-xl font-extrabold text-brand">CodeKids</span>
      </div>
      <nav className="flex flex-col gap-1">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/home' || to === '/parent' || to === '/teacher' || to === '/admin'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2.5 font-bold transition',
                isActive ? 'bg-brand-50 text-brand-700' : 'text-muted hover:bg-cloud',
              )
            }
          >
            <Icon className="h-5 w-5" aria-hidden />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
