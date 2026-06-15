import { Bell, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { useLogoutMutation } from '../../features/auth/api'
import { logout } from '../../features/auth/authSlice'
import { useAppDispatch, useAppSelector } from '../../store/hooks'
import { Avatar } from '../ui/Avatar'
import { Tooltip } from '../ui/Tooltip'

export function TopBar() {
  const user = useAppSelector((s) => s.auth.user)
  const refreshToken = useAppSelector((s) => s.auth.refreshToken)
  const dispatch = useAppDispatch()
  const nav = useNavigate()
  const [doLogout] = useLogoutMutation()

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
    <header className="flex h-16 items-center justify-between border-b border-line bg-surface px-4 lg:px-6">
      <span className="text-lg font-extrabold text-brand lg:hidden">CodeKids</span>
      <div className="ml-auto flex items-center gap-3">
        <button
          className="relative rounded-full p-2 text-muted transition hover:bg-cloud"
          aria-label="Уведомления"
        >
          <Bell className="h-5 w-5" aria-hidden />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-coral" />
        </button>
        <Avatar name={user?.display_name ?? user?.email ?? 'CodeKids'} size={36} />
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
