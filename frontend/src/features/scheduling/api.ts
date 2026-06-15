import { baseApi } from '../../api/baseApi'

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

export const schedulingApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    myGroups: b.query<StudentGroup[], void>({ query: () => '/scheduling/my/groups', providesTags: ['Groups'] }),
    mySchedule: b.query<StudentScheduleItem[], void>({
      query: () => '/scheduling/my/schedule',
      providesTags: ['Schedule'],
    }),
    myAttendance: b.query<StudentAttendanceItem[], void>({
      query: () => '/scheduling/my/attendance',
      providesTags: ['Schedule'],
    }),
  }),
})

export const { useMyGroupsQuery, useMyScheduleQuery, useMyAttendanceQuery } = schedulingApi
