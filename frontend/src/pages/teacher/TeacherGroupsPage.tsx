import { useState } from 'react'

import { Plus, Trash2, Users } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button, Card, EmptyState, Modal, Skeleton } from '../../components/ui'
import { useCoursesQuery } from '../../features/catalog/api'
import { GroupForm } from '../../features/scheduling/GroupForm'
import { useDeleteGroupMutation, useTeacherGroupsQuery } from '../../features/scheduling/api'
import { notify } from '../../lib/toast'

export function TeacherGroupsPage() {
  const { data, isLoading } = useTeacherGroupsQuery()
  const { data: courses } = useCoursesQuery({ size: 100 })
  const [del, { isLoading: deleting }] = useDeleteGroupMutation()
  const [formOpen, setFormOpen] = useState(false)
  const [toDelete, setToDelete] = useState<number | null>(null)
  const courseTitle = (cid: number) => courses?.items.find((c) => c.id === cid)?.title ?? '—'

  async function confirmDelete() {
    if (toDelete == null) return
    try {
      await del(toDelete).unwrap()
      notify.success('Группа удалена')
    } catch {
      notify.error('Не удалось удалить')
    }
    setToDelete(null)
  }

  if (isLoading) return <Skeleton className="h-60 w-full rounded-xl" />

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Мои группы</h1>
        <Button onClick={() => setFormOpen(true)}>
          <Plus className="h-4 w-4" aria-hidden /> Создать группу
        </Button>
      </div>

      {!data || data.length === 0 ? (
        <EmptyState
          title="Групп пока нет"
          description="Создайте первую группу и добавьте в неё учеников."
          mood="idle"
          action={<Button onClick={() => setFormOpen(true)}>Создать группу</Button>}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((g) => (
            <Card key={g.id}>
              <h3 className="text-lg font-extrabold text-ink">{g.name}</h3>
              <p className="text-sm text-muted">{courseTitle(g.course_id)}</p>
              <p className="mt-2 flex items-center gap-1 text-xs text-hint">
                <Users className="h-4 w-4" aria-hidden /> {g.member_count} учеников · {g.session_count} занятий
              </p>
              <div className="mt-3 flex gap-2">
                <Link to={`/teacher/groups/${g.id}`} className="flex-1">
                  <Button variant="secondary" className="w-full">
                    Открыть
                  </Button>
                </Link>
                <Button variant="ghost" className="text-danger-700" onClick={() => setToDelete(g.id)} aria-label="Удалить">
                  <Trash2 className="h-4 w-4" aria-hidden />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <GroupForm open={formOpen} onOpenChange={setFormOpen} />
      <Modal open={toDelete != null} onOpenChange={(o) => !o && setToDelete(null)} title="Удалить группу?">
        <div className="space-y-3 text-center">
          <p className="text-muted">Группа и все её занятия будут удалены.</p>
          <div className="flex justify-center gap-2">
            <Button variant="secondary" onClick={() => setToDelete(null)}>
              Отмена
            </Button>
            <Button variant="danger" loading={deleting} onClick={confirmDelete}>
              Удалить
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
