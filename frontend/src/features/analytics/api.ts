import { baseApi } from '../../api/baseApi'

export interface CourseProgressItem {
  course_id: number
  title: string
  progress_pct: number
  status: string
  completed_lessons: number
  avg_score: number
}

export interface StudentDashboard {
  xp: number
  streak: number
  rank_global: number | null
  achievements_earned: number
  achievements_total: number
  submissions_total: number
  code_passed: number
  courses: CourseProgressItem[]
}

export interface ChildBrief {
  child_id: number
  nickname: string
  xp: number
  streak: number
  courses_enrolled: number
  courses_completed: number
  avg_progress: number
}

export interface FamilyExpenses {
  total_spent: string | number
  payments_count: number
  active_subscriptions: number
}

export interface ParentOverview {
  children: ChildBrief[]
  expenses: FamilyExpenses
}

export interface AttendanceSummary {
  present: number
  absent: number
  excused: number
  rate: number
}

export interface AchievementBrief {
  code: string
  title: string
  earned_at: string | null
}

export interface ChildReport {
  child_id: number
  nickname: string
  xp: number
  streak: number
  courses: CourseProgressItem[]
  attendance: AttendanceSummary
  achievements: AchievementBrief[]
}

export interface GroupStudentRow {
  student_id: number
  nickname: string
  progress_pct: number
  attendance_rate: number
  last_active: string | null
}

export interface GroupAnalytics {
  group_id: number
  name: string
  course_id: number
  students: GroupStudentRow[]
  avg_progress: number
  avg_attendance: number
  active_count: number
}

export const analyticsApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    studentDashboard: b.query<StudentDashboard, void>({
      query: () => '/analytics/me',
      providesTags: ['Enrollment'],
    }),
    parentOverview: b.query<ParentOverview, void>({
      query: () => '/analytics/children',
      providesTags: ['Payments', 'Children'],
    }),
    childReport: b.query<ChildReport, number>({
      query: (childId) => `/analytics/children/${childId}`,
      providesTags: ['Enrollment'],
    }),
    groupAnalytics: b.query<GroupAnalytics, number>({
      query: (groupId) => `/analytics/groups/${groupId}`,
      providesTags: ['Groups'],
    }),
  }),
})

export const {
  useStudentDashboardQuery,
  useParentOverviewQuery,
  useChildReportQuery,
  useGroupAnalyticsQuery,
} = analyticsApi
