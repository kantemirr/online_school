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

export const analyticsApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    studentDashboard: b.query<StudentDashboard, void>({
      query: () => '/analytics/me',
      providesTags: ['Enrollment'],
    }),
  }),
})

export const { useStudentDashboardQuery } = analyticsApi
