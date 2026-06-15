import { baseApi } from '../../api/baseApi'

// ── Представления ученика ────────────────────────────────────────────────────
export interface StudentGroup {
  group_id: number
  name: string
  course_id: number
}

export interface StudentScheduleItem {
  session_id: number
  group_id: number
  group_name: string
  starts_at: string
  ends_at: string
  meeting_url: string | null
}

export interface StudentAttendanceItem {
  session_id: number
  starts_at: string
  status: 'present' | 'absent' | 'excused'
}

// ── Преподаватель ────────────────────────────────────────────────────────────
export interface GroupOut {
  id: number
  course_id: number
  name: string
  member_count: number
  session_count: number
}

export interface Member {
  student_id: number
  nickname: string | null
}

export interface SessionItem {
  id: number
  group_id: number
  starts_at: string
  ends_at: string
  meeting_url: string | null
}

export interface GroupDetail {
  id: number
  course_id: number
  name: string
  members: Member[]
  sessions: SessionItem[]
}

export interface AttendanceRecord {
  student_id: number
  nickname: string | null
  status: 'present' | 'absent' | 'excused'
}

export interface StudentSearch {
  student_id: number
  nickname: string
  login_username: string | null
}

export const schedulingApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    // ученик
    myGroups: b.query<StudentGroup[], void>({ query: () => '/scheduling/my/groups', providesTags: ['Groups'] }),
    mySchedule: b.query<StudentScheduleItem[], void>({ query: () => '/scheduling/my/schedule', providesTags: ['Schedule'] }),
    myAttendance: b.query<StudentAttendanceItem[], void>({ query: () => '/scheduling/my/attendance', providesTags: ['Schedule'] }),
    // преподаватель
    teacherGroups: b.query<GroupOut[], void>({ query: () => '/scheduling/groups', providesTags: ['Groups'] }),
    group: b.query<GroupDetail, number>({ query: (id) => `/scheduling/groups/${id}`, providesTags: ['Groups'] }),
    createGroup: b.mutation<GroupOut, { course_id: number; name: string }>({
      query: (body) => ({ url: '/scheduling/groups', method: 'POST', body }),
      invalidatesTags: ['Groups'],
    }),
    deleteGroup: b.mutation<void, number>({
      query: (id) => ({ url: `/scheduling/groups/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Groups'],
    }),
    addMember: b.mutation<void, { group_id: number; student_id: number }>({
      query: ({ group_id, student_id }) => ({ url: `/scheduling/groups/${group_id}/members`, method: 'POST', body: { student_id } }),
      invalidatesTags: ['Groups'],
    }),
    removeMember: b.mutation<void, { group_id: number; student_id: number }>({
      query: ({ group_id, student_id }) => ({ url: `/scheduling/groups/${group_id}/members/${student_id}`, method: 'DELETE' }),
      invalidatesTags: ['Groups'],
    }),
    createSession: b.mutation<SessionItem, { group_id: number; starts_at: string; ends_at: string; meeting_url?: string }>({
      query: ({ group_id, ...body }) => ({ url: `/scheduling/groups/${group_id}/sessions`, method: 'POST', body }),
      invalidatesTags: ['Groups'],
    }),
    deleteSession: b.mutation<void, { session_id: number }>({
      query: ({ session_id }) => ({ url: `/scheduling/sessions/${session_id}`, method: 'DELETE' }),
      invalidatesTags: ['Groups'],
    }),
    sessionAttendance: b.query<AttendanceRecord[], number>({
      query: (sessionId) => `/scheduling/sessions/${sessionId}/attendance`,
    }),
    markAttendance: b.mutation<void, { session_id: number; records: { student_id: number; status: string }[] }>({
      query: ({ session_id, records }) => ({ url: `/scheduling/sessions/${session_id}/attendance`, method: 'POST', body: { records } }),
    }),
    searchStudents: b.query<StudentSearch[], string>({
      query: (q) => ({ url: '/scheduling/students', params: q ? { q } : {} }),
    }),
  }),
})

export const {
  useMyGroupsQuery,
  useMyScheduleQuery,
  useMyAttendanceQuery,
  useTeacherGroupsQuery,
  useGroupQuery,
  useCreateGroupMutation,
  useDeleteGroupMutation,
  useAddMemberMutation,
  useRemoveMemberMutation,
  useCreateSessionMutation,
  useDeleteSessionMutation,
  useSessionAttendanceQuery,
  useMarkAttendanceMutation,
  useLazySearchStudentsQuery,
} = schedulingApi
