import { useState } from 'react'

import { Pencil, Trash2, UserPlus } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Kodik } from '../../components/mascot/Kodik'
import { Avatar, Button, Card, EmptyState, Modal, Skeleton } from '../../components/ui'
import { ChildForm } from '../../features/parent/ChildForm'
import { useChildrenQuery, useDeleteChildMutation, type ChildOut } from '../../features/users/api'
import { AGE_GROUP_LABEL } from '../../lib/labels'
import { notify } from '../../lib/toast'

export function ChildrenPage() {
  const { data, isLoading } = useChildrenQuery()
  const [deleteChild, { isLoading: deleting }] = useDeleteChildMutation()
  const [formOpen, setFormOpen] = useState(false)
  const [editChild, setEditChild] = useState<ChildOut | undefined>()
  const [toDelete, setToDelete] = useState<ChildOut | null>(null)

  function openAdd() {
    setEditChild(undefined)
    setFormOpen(true)
  }
  function openEdit(child: ChildOut) {
    setEditChild(child)
    setFormOpen(true)
  }
  async function confirmDelete() {
    if (!toDelete) return
    try {
      await deleteChild(toDelete.user_id).unwrap()
      notify.success('Профиль удалён')
    } catch {
      notify.error('Не удалось удалить')
    }
    setToDelete(null)
  }

  if (isLoading) return <Skeleton className="h-60 w-full rounded-xl" />

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Мои дети</h1>
        <Button onClick={openAdd}>
          <UserPlus className="h-4 w-4" aria-hidden /> Добавить
        </Button>
      </div>

      <Card className="bg-brand-50 text-sm text-brand-700">
        Ребёнок входит на странице <b>«Вход для ребёнка»</b> по своему логину и PIN-коду.
      </Card>

      {!data || data.length === 0 ? (
        <EmptyState title="Профилей пока нет" description="Добавьте первого ребёнка." mood="happy" action={<Button onClick={openAdd}>Добавить ребёнка</Button>} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {data.map((c) => (
            <Card key={c.user_id}>
              <div className="flex items-center gap-3">
                <Avatar name={c.nickname} />
                <div className="flex-1">
                  <div className="font-extrabold text-ink">{c.nickname}</div>
                  <div className="text-xs text-hint">
                    Логин: <b>{c.login_username}</b> · {AGE_GROUP_LABEL[c.age_group] ?? c.age_group}
                  </div>
                </div>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <Link to={`/parent/children/${c.user_id}`}>
                  <Button variant="secondary" size="sm">
                    Отчёт
                  </Button>
                </Link>
                <Button variant="ghost" size="sm" onClick={() => openEdit(c)}>
                  <Pencil className="h-4 w-4" aria-hidden /> Изменить
                </Button>
                <Button variant="ghost" size="sm" className="text-danger-700" onClick={() => setToDelete(c)}>
                  <Trash2 className="h-4 w-4" aria-hidden /> Удалить
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ChildForm open={formOpen} onOpenChange={setFormOpen} child={editChild} />

      <Modal open={!!toDelete} onOpenChange={(o) => !o && setToDelete(null)} title="Удалить профиль?">
        <div className="flex flex-col items-center gap-3 text-center">
          <Kodik mood="sad" size={80} aria-hidden />
          <p className="text-muted">
            Профиль <b>{toDelete?.nickname}</b> и весь его прогресс будут удалены безвозвратно.
          </p>
          <div className="flex gap-2">
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
