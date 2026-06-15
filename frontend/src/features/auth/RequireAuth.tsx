import { type ReactNode } from 'react'

import { Navigate, useLocation } from 'react-router-dom'

import { ROLE_HOME } from '../../lib/roles'
import type { UserRole } from '../../lib/types'
import { useAppSelector } from '../../store/hooks'

interface RequireAuthProps {
  roles?: UserRole[]
  children: ReactNode
}

/** Гард маршрута: нет токена → /login; роль не подходит → домашняя роли. */
export function RequireAuth({ roles, children }: RequireAuthProps) {
  const { accessToken, user } = useAppSelector((s) => s.auth)
  const location = useLocation()

  if (!accessToken || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to={ROLE_HOME[user.role]} replace />
  }
  return <>{children}</>
}
