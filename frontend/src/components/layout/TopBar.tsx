import { Bell, LogOut } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

import { useLogoutMutation } from '../../features/auth/api'
import { logout } from '../../features/auth/authSlice'
import { useUnreadCountQuery } from '../../features/notifications/api'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { Avatar } from '../ui/Avatar'
import { Tooltip } from '../ui/Tooltip'

export function TopBar() {
  const user = useAppSelector((s) => s.auth.user)
  const refreshToken = useAppSelector((s) => s.auth.refreshToken)
  const dispatch = useAppDispatch()
  const nav = useNavigate()
  const [doLogout] = useLogoutMutation()
  // Колокольчик с непрочитанными — для любого авторизованного пользователя.
  const { data: unread } = useUnreadCountQuery(undefined, { skip: !user, pollingInterval: 30000 })

  async function handleLogout() {
    if (refreshToken) {
      await doLogout({ refresh_token: refreshToken })
        .unwrap()
        .catch(() => undefined)
    }
    dispatch(logout())
    nav('/login', { replace: true })
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-line bg-surface px-4 lg:hidden">
      <span className="text-lg font-extrabold text-brand">CodeKids</span>
      <div className="ml-auto flex items-center gap-3">
        <Link
          to="/notifications"
          className="relative rounded-full p-2 text-muted transition hover:bg-cloud"
          aria-label="Уведомления"
        >
          <Bell className="h-5 w-5" aria-hidden />
          {!!unread?.count && (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-coral px-1 text-[10px] font-extrabold text-white">
              {unread.count > 9 ? '9+' : unread.count}
            </span>
          )}
        </Link>
        <Link to="/profile" aria-label="Профиль">
          <Avatar name={user?.display_name ?? user?.email ?? 'CodeKids'} size={36} />
        </Link>
        <Tooltip content="Выйти">
          <button
            onClick={handleLogout}
            className="rounded-full p-2 text-muted transition hover:bg-cloud"
            aria-label="Выйти"
          >
            <LogOut className="h-5 w-5" aria-hidden />
          </button>
        </Tooltip>
      </div>
    </header>
  )
}
