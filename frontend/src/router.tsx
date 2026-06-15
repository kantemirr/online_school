import { type ReactNode } from 'react'

import { Navigate, createBrowserRouter } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { RequireAuth } from './features/auth/RequireAuth'
import { ROLE_HOME } from './lib/roles'
import type { UserRole } from './lib/types'
import { useAppSelector } from './store/hooks'
import { ComingSoonPage } from './pages/ComingSoonPage'
import { LandingPage } from './pages/LandingPage'
import { OnboardingPage } from './pages/OnboardingPage'
import { ProfilePage } from './pages/ProfilePage'
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
import { GradingQueuePage } from './pages/teacher/GradingQueuePage'
import { GroupAnalyticsPage } from './pages/teacher/GroupAnalyticsPage'
import { GroupDetailPage } from './pages/teacher/GroupDetailPage'
import { TeacherGroupsPage } from './pages/teacher/TeacherGroupsPage'
import { AdminAuditPage } from './pages/admin/AdminAuditPage'
import { AdminContentPage } from './pages/admin/AdminContentPage'
import { AdminGroupsPage } from './pages/admin/AdminGroupsPage'
import { AdminOverviewPage } from './pages/admin/AdminOverviewPage'
import { AdminPaymentsPage } from './pages/admin/AdminPaymentsPage'
import { AdminUsersPage } from './pages/admin/AdminUsersPage'
import { CourseEditorPage } from './pages/admin/CourseEditorPage'

const guard = (roles: UserRole[], el: ReactNode) => <RequireAuth roles={roles}>{el}</RequireAuth>
const student = (el: ReactNode) => guard(['student'], el)

// Публичный корень: гость видит лендинг, авторизованный — уходит в свой кабинет.
function RootGate() {
  const { accessToken, user } = useAppSelector((s) => s.auth)
  if (accessToken && user) return <Navigate to={ROLE_HOME[user.role]} replace />
  return <LandingPage />
}

export const router = createBrowserRouter([
  { path: '/', element: <RootGate /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/login/child', element: <ChildLoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/verify-email', element: <VerifyEmailPage /> },
  { path: '/reset-password', element: <ResetRequestPage /> },
  { path: '/reset-password/confirm', element: <ResetConfirmPage /> },
  { path: '/onboarding', element: student(<OnboardingPage />) },
  { path: '/styleguide', element: <StyleguidePage /> },
  {
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { path: '/home', element: student(<DashboardPage />) },
      { path: '/catalog', element: student(<CatalogPage />) },
      { path: '/courses/:id', element: student(<CoursePage />) },
      { path: '/learn/:courseId', element: student(<LearnCoursePage />) },
      { path: '/learn/lessons/:lessonId', element: student(<LessonPage />) },
      { path: '/assignments/:assignmentId', element: student(<AssignmentPage />) },
      { path: '/achievements', element: student(<AchievementsPage />) },
      { path: '/leaderboard', element: student(<LeaderboardPage />) },
      { path: '/schedule', element: student(<SchedulePage />) },
      { path: '/notifications', element: <NotificationsPage /> },
      { path: '/profile', element: <ProfilePage /> },
      { path: '/parent', element: guard(['parent'], <ParentDashboardPage />) },
      { path: '/parent/children', element: guard(['parent'], <ChildrenPage />) },
      { path: '/parent/children/:id', element: guard(['parent'], <ChildReportPage />) },
      { path: '/parent/payments', element: guard(['parent'], <PaymentsPage />) },
      { path: '/teacher', element: guard(['teacher'], <TeacherGroupsPage />) },
      { path: '/teacher/groups/:id', element: guard(['teacher'], <GroupDetailPage />) },
      { path: '/teacher/groups/:id/analytics', element: guard(['teacher'], <GroupAnalyticsPage />) },
      { path: '/teacher/queue', element: guard(['teacher'], <GradingQueuePage />) },
      { path: '/admin', element: guard(['admin'], <AdminOverviewPage />) },
      { path: '/admin/users', element: guard(['admin'], <AdminUsersPage />) },
      { path: '/admin/content', element: guard(['admin'], <AdminContentPage />) },
      { path: '/admin/content/:courseId', element: guard(['admin'], <CourseEditorPage />) },
      { path: '/admin/payments', element: guard(['admin'], <AdminPaymentsPage />) },
      { path: '/admin/groups', element: guard(['admin'], <AdminGroupsPage />) },
      { path: '/admin/audit', element: guard(['admin'], <AdminAuditPage />) },
      { path: '*', element: <ComingSoonPage title="Страница не найдена" mood="sad" /> },
    ],
  },
])
