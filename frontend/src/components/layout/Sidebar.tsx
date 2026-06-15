import { Bell, LogOut } from 'lucide-react'
import { Link, NavLink, useNavigate } from 'react-router-dom'

import { useLogoutMutation } from '../../features/auth/api'
import { logout } from '../../features/auth/authSlice'
import { useUnreadCountQuery } from '../../features/notifications/api'
import { cn } from '../../lib/cn'
import { ROLE_LABEL } from '../../lib/roles'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { Kodik } from '../mascot/Kodik'
import { Avatar } from '../ui/Avatar'
import { navItemsFor } from './navConfig'

const linkCls = ({ isActive }: { isActive: boolean }) =>
  cn(
    'flex items-center gap-3 rounded-md px-3 py-2.5 font-bold transition',
    isActive ? 'bg-brand-50 text-brand-700' : 'text-muted hover:bg-cloud',
  )

export function Sidebar() {
  const user = useAppSelector((s) => s.auth.user)
  const role = user?.role ?? 'student'
  const refreshToken = useAppSelector((s) => s.auth.refreshToken)
  const dispatch = useAppDispatch()
  const nav = useNavigate()
  const [doLogout] = useLogoutMutation()
  const items = navItemsFor(role)
  const { data: unread } = useUnreadCountQuery(undefined, { skip: !user, pollingInterval: 30000 })

  async function handleLogout() {
    if (refreshToken) {
      await doLogout({ refresh_token: refreshToken }).unwrap().catch(() => undefined)
    }
    dispatch(logout())
    nav('/login', { replace: true })
  }

  return (
    <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-line bg-surface p-4 lg:flex">
      <div className="mb-4 flex items-center gap-2 px-2">
        <Kodik mood="wave" size={40} aria-hidden />
        <span className="text-xl font-extrabold text-brand">CodeKids</span>
      </div>

      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto">
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/home' || to === '/parent' || to === '/teacher' || to === '/admin'}
            className={linkCls}
          >
            <Icon className="h-5 w-5" aria-hidden />
            {label}
          </NavLink>
        ))}
        <NavLink to="/notifications" className={linkCls}>
          <span className="relative">
            <Bell className="h-5 w-5" aria-hidden />
            {!!unread?.count && (
              <span className="absolute -right-1.5 -top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-coral px-1 text-[10px] font-extrabold text-white">
                {unread.count > 9 ? '9+' : unread.count}
              </span>
            )}
          </span>
          Уведомления
        </NavLink>
      </nav>

      <div className="mt-2 flex items-center gap-1 border-t border-line pt-3">
        <Link
          to="/profile"
          className="flex min-w-0 flex-1 items-center gap-3 rounded-md p-2 transition hover:bg-cloud"
        >
          <Avatar name={user?.display_name ?? user?.email ?? 'CodeKids'} size={36} />
          <span className="min-w-0">
            <span className="block truncate text-sm font-bold text-ink">
              {user?.display_name ?? user?.email ?? 'Профиль'}
            </span>
            <span className="block truncate text-xs text-muted">{ROLE_LABEL[role]}</span>
          </span>
        </Link>
        <button
          onClick={handleLogout}
          className="shrink-0 rounded-md p-2 text-muted transition hover:bg-cloud"
          aria-label="Выйти"
          title="Выйти"
        >
          <LogOut className="h-5 w-5" aria-hidden />
        </button>
      </div>
    </aside>
  )
}
