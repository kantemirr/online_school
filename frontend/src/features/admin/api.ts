import { baseApi } from '../../api/baseApi'
import type { CourseDetail } from '../catalog/api'
import type { Paginated, UserRole } from '../../lib/types'

// ── Пользователи ─────────────────────────────────────────────────────────────
export interface AdminUser {
  id: number
  email: string | null
  role: UserRole
  is_active: boolean
  is_email_verified: boolean
  display_name: string | null
  created_at: string
}

// ── Реестры ──────────────────────────────────────────────────────────────────
export interface AdminPayment {
  id: number
  payer_email: string | null
  plan: string
  amount: string | number
  status: string
  receipt_no: string | null
  paid_at: string | null
}

export interface AdminGroup {
  id: number
  name: string
  teacher_name: string | null
  course_title: string | null
  members: number
  sessions: number
}

export interface AuditEntry {
  id: number
  actor_email: string | null
  action: string
  target: string | null
  created_at: string
}

export interface ReferenceItem {
  value: string
  label: string
}
export interface ReferenceOut {
  sections: Record<string, ReferenceItem[]>
}

export interface PopularCourse {
  course_id: number
  title: string
  enrollments: number
}
export interface AdminOverview {
  users: Record<string, number>
  enrollments: number
  submissions: number
  active_students_7d: number
  popular_courses: PopularCourse[]
  revenue_total: string | number
  payments_count: number
}

// ── Контент ──────────────────────────────────────────────────────────────────
export interface CourseAdmin {
  id: number
  title: string
  description: string | null
  track: string
  age_min: number
  age_max: number
  level: string
  cover_url: string | null
  price: string | number
  is_published: boolean
}

export interface LessonAdmin {
  id: number
  title: string
  order_index: number
  theory_md: string | null
  video_url: string | null
  assignments: { id: number; type: 'quiz' | 'code' | 'project'; title: string; max_score: number }[]
}

export interface QuestionCreate {
  text: string
  kind: 'single' | 'multiple'
  options_json: string[]
  correct_json: number[]
}
export interface CodeTestCreate {
  stdin: string | null
  expected_stdout: string
  is_hidden: boolean
  weight: number
}

export const adminApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    adminOverview: b.query<AdminOverview, void>({ query: () => '/analytics/admin/overview' }),

    // пользователи
    adminUsers: b.query<Paginated<AdminUser>, { role?: string; is_active?: boolean; q?: string; page?: number; size?: number }>({
      query: (params) => ({ url: '/admin/users', params }),
      providesTags: ['AdminUsers'],
    }),
    updateUser: b.mutation<AdminUser, { id: number; is_active?: boolean; role?: string }>({
      query: ({ id, ...body }) => ({ url: `/admin/users/${id}`, method: 'PATCH', body }),
      invalidatesTags: ['AdminUsers'],
    }),
    resetPassword: b.mutation<void, { id: number; new_password: string }>({
      query: ({ id, new_password }) => ({ url: `/admin/users/${id}/reset-password`, method: 'POST', body: { new_password } }),
    }),
    createStaff: b.mutation<AdminUser, { email: string; password: string; role: string; full_name: string; specialization?: string }>({
      query: (body) => ({ url: '/admin/users', method: 'POST', body }),
      invalidatesTags: ['AdminUsers'],
    }),

    // реестры
    adminPayments: b.query<Paginated<AdminPayment>, { status?: string; page?: number; size?: number }>({
      query: (params) => ({ url: '/admin/payments', params }),
      providesTags: ['AdminPayments'],
    }),
    refundPayment: b.mutation<void, number>({
      query: (id) => ({ url: `/admin/payments/${id}/refund`, method: 'POST' }),
      invalidatesTags: ['AdminPayments'],
    }),
    adminGroups: b.query<Paginated<AdminGroup>, { page?: number; size?: number }>({
      query: (params) => ({ url: '/admin/groups', params }),
    }),
    audit: b.query<Paginated<AuditEntry>, { page?: number; size?: number }>({
      query: (params) => ({ url: '/admin/audit', params }),
    }),
    reference: b.query<ReferenceOut, void>({ query: () => '/admin/reference' }),

    // контент: чтение
    adminCourses: b.query<CourseAdmin[], void>({
      query: () => '/admin/catalog/courses',
      providesTags: ['AdminContent'],
    }),
    adminCourse: b.query<CourseDetail, number>({
      query: (id) => `/admin/catalog/courses/${id}`,
      providesTags: ['AdminContent'],
    }),
    adminLesson: b.query<LessonAdmin, number>({
      query: (id) => `/admin/catalog/lessons/${id}`,
      providesTags: ['AdminContent'],
    }),

    // контент: курсы
    createCourse: b.mutation<CourseAdmin, Partial<CourseAdmin>>({
      query: (body) => ({ url: '/admin/catalog/courses', method: 'POST', body }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    updateCourse: b.mutation<CourseAdmin, { id: number } & Partial<CourseAdmin>>({
      query: ({ id, ...body }) => ({ url: `/admin/catalog/courses/${id}`, method: 'PATCH', body }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    deleteCourse: b.mutation<void, number>({
      query: (id) => ({ url: `/admin/catalog/courses/${id}`, method: 'DELETE' }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    setPublished: b.mutation<CourseAdmin, { id: number; publish: boolean }>({
      query: ({ id, publish }) => ({ url: `/admin/catalog/courses/${id}/${publish ? 'publish' : 'unpublish'}`, method: 'POST' }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),

    // контент: модули / уроки / задания
    createModule: b.mutation<{ id: number }, { course_id: number; title: string; order_index?: number }>({
      query: ({ course_id, ...body }) => ({ url: `/admin/catalog/courses/${course_id}/modules`, method: 'POST', body }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    deleteModule: b.mutation<void, number>({
      query: (id) => ({ url: `/admin/catalog/modules/${id}`, method: 'DELETE' }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    createLesson: b.mutation<{ id: number }, { module_id: number; title: string; theory_md?: string; video_url?: string }>({
      query: ({ module_id, ...body }) => ({ url: `/admin/catalog/modules/${module_id}/lessons`, method: 'POST', body }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    updateLesson: b.mutation<{ id: number }, { id: number; title?: string; theory_md?: string; video_url?: string }>({
      query: ({ id, ...body }) => ({ url: `/admin/catalog/lessons/${id}`, method: 'PATCH', body }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    deleteLesson: b.mutation<void, number>({
      query: (id) => ({ url: `/admin/catalog/lessons/${id}`, method: 'DELETE' }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    createAssignment: b.mutation<
      { id: number },
      { lesson_id: number; type: string; title: string; max_score: number; due_at?: string | null; questions: QuestionCreate[]; code_tests: CodeTestCreate[] }
    >({
      query: ({ lesson_id, ...body }) => ({ url: `/admin/catalog/lessons/${lesson_id}/assignments`, method: 'POST', body }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
    deleteAssignment: b.mutation<void, number>({
      query: (id) => ({ url: `/admin/catalog/assignments/${id}`, method: 'DELETE' }),
      invalidatesTags: ['AdminContent', 'Catalog'],
    }),
  }),
})

export const {
  useAdminOverviewQuery,
  useAdminUsersQuery,
  useUpdateUserMutation,
  useResetPasswordMutation,
  useCreateStaffMutation,
  useAdminPaymentsQuery,
  useRefundPaymentMutation,
  useAdminGroupsQuery,
  useAuditQuery,
  useReferenceQuery,
  useAdminCoursesQuery,
  useAdminCourseQuery,
  useAdminLessonQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  useSetPublishedMutation,
  useCreateModuleMutation,
  useDeleteModuleMutation,
  useCreateLessonMutation,
  useUpdateLessonMutation,
  useDeleteLessonMutation,
  useCreateAssignmentMutation,
  useDeleteAssignmentMutation,
} = adminApi
