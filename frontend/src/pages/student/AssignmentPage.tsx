import { useParams } from 'react-router-dom'

import { Badge, EmptyState, Skeleton } from '../../components/ui'
import { useAssignmentQuery } from '../../features/grading/api'
import { CodeSandbox } from '../../features/grading/CodeSandbox'
import { ProjectUpload } from '../../features/grading/ProjectUpload'
import { QuizPlayer } from '../../features/grading/QuizPlayer'
import { formatDateTime } from '../../lib/format'

export function AssignmentPage() {
  const { assignmentId } = useParams()
  const aid = Number(assignmentId)
  const { data, isLoading, isError } = useAssignmentQuery(aid)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return <EmptyState title="Задание недоступно" description="Сначала открой урок с этим заданием." mood="thinking" />
  }

  const overdue = !!data.due_at && new Date(data.due_at).getTime() < Date.now()

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-extrabold text-ink">{data.title}</h1>
        {data.due_at && (
          <Badge tone={overdue ? 'danger' : 'sun'}>
            {overdue ? 'Просрочено' : `Срок до ${formatDateTime(data.due_at)}`}
          </Badge>
        )}
      </div>
      {data.type === 'quiz' && <QuizPlayer assignment={data} />}
      {data.type === 'code' && <CodeSandbox assignment={data} />}
      {data.type === 'project' && <ProjectUpload assignment={data} />}
    </div>
  )
}
