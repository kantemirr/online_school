import { useParams } from 'react-router-dom'

import { EmptyState, Skeleton } from '../../components/ui'
import { useAssignmentQuery } from '../../features/grading/api'
import { CodeSandbox } from '../../features/grading/CodeSandbox'
import { ProjectUpload } from '../../features/grading/ProjectUpload'
import { QuizPlayer } from '../../features/grading/QuizPlayer'

export function AssignmentPage() {
  const { assignmentId } = useParams()
  const aid = Number(assignmentId)
  const { data, isLoading, isError } = useAssignmentQuery(aid)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return <EmptyState title="Задание недоступно" description="Сначала открой урок с этим заданием." mood="thinking" />
  }

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-extrabold text-ink">{data.title}</h1>
      {data.type === 'quiz' && <QuizPlayer assignment={data} />}
      {data.type === 'code' && <CodeSandbox assignment={data} />}
      {data.type === 'project' && <ProjectUpload assignment={data} />}
    </div>
  )
}
