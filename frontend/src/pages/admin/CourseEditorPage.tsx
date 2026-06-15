import { useState } from 'react'

import { ArrowLeft, Pencil, Plus, Trash2 } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { Button, Card, EmptyState, Input, Skeleton } from '../../components/ui'
import { LessonEditorModal } from '../../features/admin/content/LessonEditorModal'
import { useAdminCourseQuery, useCreateModuleMutation, useDeleteModuleMutation } from '../../features/admin/api'
import { notify } from '../../lib/toast'

export function CourseEditorPage() {
  const { courseId } = useParams()
  const cid = Number(courseId)
  const { data, isLoading, isError } = useAdminCourseQuery(cid)
  const [createModule] = useCreateModuleMutation()
  const [deleteModule] = useDeleteModuleMutation()
  const [moduleTitle, setModuleTitle] = useState('')
  const [lessonModal, setLessonModal] = useState<{ moduleId?: number; lessonId?: number } | null>(null)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return (
      <EmptyState
        title="Курс не найден"
        mood="sad"
        action={
          <Link to="/admin/content">
            <Button variant="secondary">К курсам</Button>
          </Link>
        }
      />
    )
  }

  async function addModule() {
    if (!moduleTitle.trim()) return
    try {
      await createModule({ course_id: cid, title: moduleTitle.trim() }).unwrap()
      setModuleTitle('')
    } catch {
      notify.error('Не удалось создать модуль')
    }
  }

  return (
    <div className="space-y-6">
      <Link to="/admin/content" className="inline-flex items-center gap-1 text-sm font-bold text-brand">
        <ArrowLeft className="h-4 w-4" aria-hidden /> К курсам
      </Link>
      <h1 className="text-2xl font-extrabold text-ink">{data.title}</h1>

      <Card className="flex gap-2">
        <Input
          value={moduleTitle}
          onChange={(e) => setModuleTitle(e.target.value)}
          placeholder="Название нового модуля"
          onKeyDown={(e) => e.key === 'Enter' && addModule()}
        />
        <Button onClick={addModule}>
          <Plus className="h-4 w-4" aria-hidden /> Модуль
        </Button>
      </Card>

      {data.modules.length === 0 ? (
        <Card className="text-muted">Модулей пока нет — добавьте первый.</Card>
      ) : (
        data.modules.map((m, mi) => (
          <Card key={m.id}>
            <div className="mb-2 flex items-center justify-between">
              <h3 className="font-extrabold text-ink">
                Модуль {mi + 1}. {m.title}
              </h3>
              <Button
                variant="ghost"
                size="sm"
                className="text-danger-700"
                aria-label="Удалить модуль"
                onClick={async () => {
                  try {
                    await deleteModule(m.id).unwrap()
                  } catch {
                    notify.error('Не удалось удалить модуль')
                  }
                }}
              >
                <Trash2 className="h-4 w-4" aria-hidden />
              </Button>
            </div>
            {m.lessons.length > 0 && (
              <ul className="divide-y divide-line">
                {m.lessons.map((l) => (
                  <li key={l.id} className="flex items-center gap-2 py-2">
                    <span className="flex-1 text-ink">
                      {l.title} <span className="text-xs text-hint">{l.assignment_count} зад.</span>
                    </span>
                    <Button variant="ghost" size="sm" aria-label="Редактировать урок" onClick={() => setLessonModal({ lessonId: l.id })}>
                      <Pencil className="h-4 w-4" aria-hidden />
                    </Button>
                  </li>
                ))}
              </ul>
            )}
            <Button variant="secondary" size="sm" className="mt-2" onClick={() => setLessonModal({ moduleId: m.id })}>
              <Plus className="h-4 w-4" aria-hidden /> Урок
            </Button>
          </Card>
        ))
      )}

      {lessonModal && (
        <LessonEditorModal
          open={!!lessonModal}
          onOpenChange={(o) => !o && setLessonModal(null)}
          moduleId={lessonModal.moduleId}
          lessonId={lessonModal.lessonId}
        />
      )}
    </div>
  )
}
