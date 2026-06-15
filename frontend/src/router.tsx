import { type ReactNode } from 'react'

import { createBrowserRouter } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { RequireAuth } from './features/auth/RequireAuth'
import type { UserRole } from './lib/types'
import { ComingSoonPage } from './pages/ComingSoonPage'
import { HomePage } from './pages/HomePage'
import { StyleguidePage } from './pages/StyleguidePage'
import { ChildLoginPage } from './pages/auth/ChildLoginPage'
import { LoginPage } from './pages/auth/LoginPage'
import { RegisterPage } from './pages/auth/RegisterPage'
import { ResetConfirmPage } from './pages/auth/ResetConfirmPage'
import { ResetRequestPage } from './pages/auth/ResetRequestPage'
import { VerifyEmailPage } from './pages/auth/VerifyEmailPage'

const guard = (roles: UserRole[], el: ReactNode) => <RequireAuth roles={roles}>{el}</RequireAuth>

export const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { path: '/login/child', element: <ChildLoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/verify-email', element: <VerifyEmailPage /> },
  { path: '/reset-password', element: <ResetRequestPage /> },
  { path: '/reset-password/confirm', element: <ResetConfirmPage /> },
  { path: '/styleguide', element: <StyleguidePage /> },
  {
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { path: '/', element: guard(['student'], <HomePage />) },
      { path: '/catalog', element: guard(['student'], <ComingSoonPage title="Каталог курсов" />) },
      { path: '/achievements', element: guard(['student'], <ComingSoonPage title="Награды" />) },
      { path: '/schedule', element: guard(['student'], <ComingSoonPage title="Расписание" />) },
      { path: '/parent', element: guard(['parent'], <ComingSoonPage title="Кабинет родителя" />) },
      { path: '/parent/children', element: guard(['parent'], <ComingSoonPage title="Мои дети" />) },
      { path: '/parent/payments', element: guard(['parent'], <ComingSoonPage title="Оплата" />) },
      { path: '/teacher', element: guard(['teacher'], <ComingSoonPage title="Мои группы" />) },
      { path: '/teacher/queue', element: guard(['teacher'], <ComingSoonPage title="Очередь проверки" />) },
      { path: '/admin', element: guard(['admin'], <ComingSoonPage title="Админ-панель" />) },
      { path: '/admin/users', element: guard(['admin'], <ComingSoonPage title="Пользователи" />) },
      { path: '/admin/content', element: guard(['admin'], <ComingSoonPage title="Контент" />) },
      { path: '/admin/payments', element: guard(['admin'], <ComingSoonPage title="Платежи" />) },
      { path: '*', element: <ComingSoonPage title="Страница не найдена" mood="sad" /> },
    ],
  },
])
