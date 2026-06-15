import { baseApi } from '../../api/baseApi'
import type { Paginated } from '../../lib/types'

export interface TrackOut {
  code: string
  label: string
  course_count: number
}

export interface CourseSummary {
  id: number
  title: string
  description: string | null
  track: string
  age_min: number
  age_max: number
  level: string
  cover_url: string | null
  price: string | number
}

export interface LessonNode {
  id: number
  title: string
  order_index: number
  assignment_count: number
}

export interface ModuleNode {
  id: number
  title: string
  order_index: number
  lessons: LessonNode[]
}

export interface CourseDetail extends CourseSummary {
  module_count: number
  lesson_count: number
  modules: ModuleNode[]
}

export interface CourseListParams {
  track?: string
  age?: number
  level?: string
  q?: string
  page?: number
  size?: number
}

export const catalogApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    tracks: b.query<TrackOut[], void>({
      query: () => '/catalog/tracks',
      providesTags: ['Catalog'],
    }),
    courses: b.query<Paginated<CourseSummary>, CourseListParams | void>({
      query: (params) => ({ url: '/catalog/courses', params: params ?? {} }),
      providesTags: ['Catalog'],
    }),
    course: b.query<CourseDetail, number>({
      query: (id) => `/catalog/courses/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'Course', id }],
    }),
  }),
})

export const { useTracksQuery, useCoursesQuery, useCourseQuery } = catalogApi
