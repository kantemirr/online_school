import { baseApi } from '../../api/baseApi'

export interface QuestionForSolve {
  id: number
  text: string
  kind: 'single' | 'multiple' | 'matching'
  options: unknown
}

export interface CodeExample {
  stdin: string | null
  expected_stdout: string
}

export interface AssignmentForSolve {
  id: number
  type: 'quiz' | 'code' | 'project'
  title: string
  max_score: number
  questions: QuestionForSolve[]
  examples: CodeExample[]
}

export interface SubmissionTest {
  test_no: number
  passed: boolean
  hidden: boolean
  stdin?: string | null
  expected?: string
  got?: string
}

export interface SubmissionResultJson {
  summary?: { passed: number; total: number; verdict?: string }
  tests?: SubmissionTest[]
  stderr?: string
  correct?: number
  total?: number
  wrong_question_ids?: number[]
  passed?: boolean
}

export interface Submission {
  id: number
  assignment_id: number
  status: 'queued' | 'running' | 'checked' | 'pending_review' | 'reviewed' | 'needs_revision'
  verdict: 'passed' | 'failed' | 'partial' | null
  score: number | null
  feedback: string | null
  result_json: SubmissionResultJson | null
  created_at: string
  checked_at: string | null
}

export interface Hint {
  hint: string
  source: 'ai' | 'heuristic'
}

export interface QueueItem {
  submission_id: number
  assignment_id: number
  student_id: number
  nickname: string | null
  assignment_title: string
  file_url: string | null
  created_at: string
}

export const gradingApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    assignment: b.query<AssignmentForSolve, number>({
      query: (id) => `/assignments/${id}`,
    }),
    submitQuiz: b.mutation<Submission, { id: number; answers: Record<string, unknown> }>({
      query: ({ id, answers }) => ({
        url: `/assignments/${id}/submit/quiz`,
        method: 'POST',
        body: { answers },
      }),
      invalidatesTags: ['Lesson', 'Enrollment'],
    }),
    submitCode: b.mutation<Submission, { id: number; code: string }>({
      query: ({ id, code }) => ({
        url: `/assignments/${id}/submit/code`,
        method: 'POST',
        body: { code },
      }),
    }),
    submitProject: b.mutation<Submission, { id: number; form: FormData }>({
      query: ({ id, form }) => ({
        url: `/assignments/${id}/submit/project`,
        method: 'POST',
        body: form,
      }),
    }),
    submission: b.query<Submission, number>({
      query: (id) => `/submissions/${id}`,
    }),
    hint: b.query<Hint, number>({
      query: (id) => `/submissions/${id}/hint`,
    }),
    gradingQueue: b.query<QueueItem[], void>({
      query: () => '/grading/queue',
      providesTags: ['GradingQueue'],
    }),
    reviewSubmission: b.mutation<
      Submission,
      { id: number; score: number; feedback?: string; status: 'reviewed' | 'needs_revision' }
    >({
      query: ({ id, ...body }) => ({ url: `/grading/submissions/${id}/review`, method: 'POST', body }),
      invalidatesTags: ['GradingQueue'],
    }),
  }),
})

export const {
  useAssignmentQuery,
  useSubmitQuizMutation,
  useSubmitCodeMutation,
  useSubmitProjectMutation,
  useSubmissionQuery,
  useLazyHintQuery,
  useGradingQueueQuery,
  useReviewSubmissionMutation,
} = gradingApi
