import { baseApi } from '../../api/baseApi'

export interface Enrollment {
  id: number
  course_id: number
  status: string
  progress_pct: number
  enrolled_at: string
}

export interface LessonState {
  id: number
  title: string
  order_index: number
  status: 'not_started' | 'in_progress' | 'completed'
  locked: boolean
  assignment_count: number
}

export interface ModulePassage {
  id: number
  title: string
  order_index: number
  lessons: LessonState[]
}

export interface CoursePassage {
  course_id: number
  title: string
  status: string
  progress_pct: number
  resume_lesson_id: number | null
  modules: ModulePassage[]
}

export interface AssignmentSummary {
  id: number
  type: 'quiz' | 'code' | 'project'
  title: string
  max_score: number
}

export interface LessonContent {
  id: number
  title: string
  theory_md: string | null
  video_url: string | null
  status: 'not_started' | 'in_progress' | 'completed'
  assignments: AssignmentSummary[]
}

export const learningApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    enrollments: b.query<Enrollment[], void>({
      query: () => '/learning/enrollments',
      providesTags: ['Enrollment'],
    }),
    enroll: b.mutation<Enrollment, number>({
      query: (courseId) => ({ url: `/learning/courses/${courseId}/enroll`, method: 'POST' }),
      invalidatesTags: ['Enrollment'],
    }),
    passage: b.query<CoursePassage, number>({
      query: (courseId) => `/learning/courses/${courseId}`,
      providesTags: ['Lesson', 'Enrollment'],
    }),
    lesson: b.query<LessonContent, number>({
      query: (lessonId) => `/learning/lessons/${lessonId}`,
      providesTags: (_r, _e, id) => [{ type: 'Lesson', id }],
    }),
    completeLesson: b.mutation<CoursePassage, number>({
      query: (lessonId) => ({ url: `/learning/lessons/${lessonId}/complete`, method: 'POST' }),
      invalidatesTags: ['Lesson', 'Enrollment'],
    }),
  }),
})

export const {
  useEnrollmentsQuery,
  useEnrollMutation,
  usePassageQuery,
  useLessonQuery,
  useCompleteLessonMutation,
} = learningApi
