import { useEffect, useState } from 'react'

import { Plus, Trash2 } from 'lucide-react'

import { Button, Field, Input, Modal } from '../../../components/ui'
import { notify } from '../../../lib/toast'
import {
  useAdminLessonQuery,
  useCreateLessonMutation,
  useDeleteAssignmentMutation,
  useUpdateLessonMutation,
} from '../api'
import { AssignmentForm } from './AssignmentForm'

interface Props {
  open: boolean
  onOpenChange: (o: boolean) => void
  moduleId?: number
  lessonId?: number
}

export function LessonEditorModal({ open, onOpenChange, moduleId, lessonId }: Props) {
  const editing = lessonId != null
  const { data: lesson } = useAdminLessonQuery(lessonId as number, { skip: !editing || !open })
  const [createLesson, { isLoading: creating }] = useCreateLessonMutation()
  const [updateLesson, { isLoading: updating }] = useUpdateLessonMutation()
  const [deleteAssignment] = useDeleteAssignmentMutation()

  const [title, setTitle] = useState('')
  const [theory, setTheory] = useState('')
  const [video, setVideo] = useState('')
  const [assignOpen, setAssignOpen] = useState(false)

  useEffect(() => {
    if (!open) return
    if (editing && lesson) {
      setTitle(lesson.title)
      setTheory(lesson.theory_md ?? '')
      setVideo(lesson.video_url ?? '')
    } else if (!editing) {
      setTitle('')
      setTheory('')
      setVideo('')
    }
  }, [open, editing, lesson])

  async function save() {
    if (!title.trim()) {
      notify.error('Укажите название урока')
      return
    }
    try {
      if (editing) {
        await updateLesson({ id: lessonId!, title, theory_md: theory || undefined, video_url: video || undefined }).unwrap()
        notify.success('Урок сохранён')
      } else {
        await createLesson({ module_id: moduleId!, title, theory_md: theory || undefined, video_url: video || undefined }).unwrap()
        notify.success('Урок создан')
        onOpenChange(false)
      }
    } catch {
      notify.error('Не удалось сохранить урок')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title={editing ? 'Урок' : 'Новый урок'}>
      <div className="space-y-4">
        <Field label="Название">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
        <Field label="Теория (Markdown)">
          <textarea className="w-full rounded-md border-2 border-line p-2 font-mono text-sm" rows={5} value={theory} onChange={(e) => setTheory(e.target.value)} />
        </Field>
        <Field label="Ссылка на видео (необязательно)">
          <Input value={video} onChange={(e) => setVideo(e.target.value)} placeholder="https://…" />
        </Field>
        <Button fullWidth loading={creating || updating} onClick={save}>
          {editing ? 'Сохранить урок' : 'Создать урок'}
        </Button>

        {editing && lesson && (
          <div className="border-t border-line pt-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="font-bold text-ink">Задания</span>
              <Button size="sm" onClick={() => setAssignOpen(true)}>
                <Plus className="h-4 w-4" aria-hidden /> Добавить
              </Button>
            </div>
            {lesson.assignments.length === 0 ? (
              <p className="text-sm text-hint">Заданий пока нет.</p>
            ) : (
              <ul className="space-y-1">
                {lesson.assignments.map((a) => (
                  <li key={a.id} className="flex items-center gap-2 rounded-md border border-line p-2 text-sm">
                    <span className="flex-1">
                      {a.title} <span className="text-xs text-hint">({a.type})</span>
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-danger-700"
                      aria-label="Удалить задание"
                      onClick={async () => {
                        try {
                          await deleteAssignment(a.id).unwrap()
                        } catch {
                          notify.error('Не удалось удалить задание')
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4" aria-hidden />
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {editing && <AssignmentForm open={assignOpen} onOpenChange={setAssignOpen} lessonId={lessonId!} />}
    </Modal>
  )
}
