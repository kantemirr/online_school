import { useState } from 'react'

import { Pencil, Plus, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Badge, Button, Card, EmptyState, Modal, Skeleton } from '../../components/ui'
import { CourseForm } from '../../features/admin/content/CourseForm'
import {
  useAdminCoursesQuery,
  useDeleteCourseMutation,
  useSetPublishedMutation,
  type CourseAdmin,
} from '../../features/admin/api'
import { formatMoney } from '../../lib/format'
import { TRACK_LABEL } from '../../lib/labels'
import { notify } from '../../lib/toast'

export function AdminContentPage() {
  const { data, isLoading } = useAdminCoursesQuery()
  const [setPublished] = useSetPublishedMutation()
  const [del, { isLoading: deleting }] = useDeleteCourseMutation()
  const [formOpen, setFormOpen] = useState(false)
  const [editCourse, setEditCourse] = useState<CourseAdmin | undefined>()
  const [toDelete, setToDelete] = useState<CourseAdmin | null>(null)

  async function confirmDelete() {
    if (!toDelete) return
    try {
      await del(toDelete.id).unwrap()
      notify.success('Курс удалён')
    } catch {
      notify.error('Не удалось удалить')
    }
    setToDelete(null)
  }

  if (isLoading) return <Skeleton className="h-60 w-full rounded-xl" />

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Управление контентом</h1>
        <Button onClick={() => { setEditCourse(undefined); setFormOpen(true) }}>
          <Plus className="h-4 w-4" aria-hidden /> Создать курс
        </Button>
      </div>

      {!data || data.length === 0 ? (
        <EmptyState title="Курсов нет" description="Создайте первый курс." mood="idle" action={<Button onClick={() => setFormOpen(true)}>Создать курс</Button>} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.map((c) => (
            <Card key={c.id} className="flex h-full flex-col">
              <div className="flex items-start justify-between gap-2">
                <Badge tone="brand">{TRACK_LABEL[c.track] ?? c.track}</Badge>
                <Badge tone={c.is_published ? 'success' : 'muted'}>{c.is_published ? 'Опубликован' : 'Черновик'}</Badge>
              </div>
              <h3 className="mt-2 text-lg font-extrabold text-ink">{c.title}</h3>
              <p className="text-sm text-muted">{Number(c.price) === 0 ? 'Бесплатно' : formatMoney(c.price)}</p>
              <div className="mt-auto pt-3">
                <Link to={`/admin/content/${c.id}`}>
                  <Button variant="secondary" className="w-full">Содержимое</Button>
                </Link>
                <div className="mt-2 flex flex-wrap gap-1">
                  <Button variant="ghost" size="sm" onClick={() => setPublished({ id: c.id, publish: !c.is_published })}>
                    {c.is_published ? 'Снять' : 'Опубликовать'}
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => { setEditCourse(c); setFormOpen(true) }} aria-label="Изменить">
                    <Pencil className="h-4 w-4" aria-hidden />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-danger-700" onClick={() => setToDelete(c)} aria-label="Удалить">
                    <Trash2 className="h-4 w-4" aria-hidden />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <CourseForm open={formOpen} onOpenChange={setFormOpen} course={editCourse} />
      <Modal open={!!toDelete} onOpenChange={(o) => !o && setToDelete(null)} title="Удалить курс?">
        <div className="space-y-3 text-center">
          <p className="text-muted">Курс «{toDelete?.title}» со всеми модулями и уроками будет удалён.</p>
          <div className="flex justify-center gap-2">
            <Button variant="secondary" onClick={() => setToDelete(null)}>Отмена</Button>
            <Button variant="danger" loading={deleting} onClick={confirmDelete}>Удалить</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
