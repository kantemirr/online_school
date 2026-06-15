import { type ReactNode } from 'react'

import { createBrowserRouter } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { RequireAuth } from './features/auth/RequireAuth'
import type { UserRole } from './lib/types'
import { ComingSoonPage } from './pages/ComingSoonPage'
import { StyleguidePage } from './pages/StyleguidePage'
import { ChildLoginPage } from './pages/auth/ChildLoginPage'
import { LoginPage } from './pages/auth/LoginPage'
import { RegisterPage } from './pages/auth/RegisterPage'
import { ResetConfirmPage } from './pages/auth/ResetConfirmPage'
import { ResetRequestPage } from './pages/auth/ResetRequestPage'
import { VerifyEmailPage } from './pages/auth/VerifyEmailPage'
import { AchievementsPage } from './pages/student/AchievementsPage'
import { AssignmentPage } from './pages/student/AssignmentPage'
import { CatalogPage } from './pages/student/CatalogPage'
import { CoursePage } from './pages/student/CoursePage'
import { DashboardPage } from './pages/student/DashboardPage'
import { LearnCoursePage } from './pages/student/LearnCoursePage'
import { LeaderboardPage } from './pages/student/LeaderboardPage'
import { LessonPage } from './pages/student/LessonPage'
import { NotificationsPage } from './pages/student/NotificationsPage'
import { SchedulePage } from './pages/student/SchedulePage'
import { ChildReportPage } from './pages/parent/ChildReportPage'
import { ChildrenPage } from './pages/parent/ChildrenPage'
import { ParentDashboardPage } from './pages/parent/ParentDashboardPage'
import { PaymentsPage } from './pages/parent/PaymentsPage'

const guard = (roles: UserRole[], el: ReactNode) => <RequireAuth roles={roles}>{el}</RequireAuth>
const student = (el: ReactNode) => guard(['student'], el)

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
      { path: '/', element: student(<DashboardPage />) },
      { path: '/catalog', element: student(<CatalogPage />) },
      { path: '/courses/:id', element: student(<CoursePage />) },
      { path: '/learn/:courseId', element: student(<LearnCoursePage />) },
      { path: '/learn/lessons/:lessonId', element: student(<LessonPage />) },
      { path: '/assignments/:assignmentId', element: student(<AssignmentPage />) },
      { path: '/achievements', element: student(<AchievementsPage />) },
      { path: '/leaderboard', element: student(<LeaderboardPage />) },
      { path: '/schedule', element: student(<SchedulePage />) },
      { path: '/notifications', element: <NotificationsPage /> },
      { path: '/parent', element: guard(['parent'], <ParentDashboardPage />) },
      { path: '/parent/children', element: guard(['parent'], <ChildrenPage />) },
      { path: '/parent/children/:id', element: guard(['parent'], <ChildReportPage />) },
      { path: '/parent/payments', element: guard(['parent'], <PaymentsPage />) },
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
