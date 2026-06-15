import { useState } from 'react'

import { Receipt as ReceiptIcon } from 'lucide-react'

import { Badge, Button, Card, EmptyState, Modal, Skeleton } from '../../components/ui'
import { CheckoutFlow } from '../../features/payments/CheckoutFlow'
import { ReceiptModal } from '../../features/payments/ReceiptModal'
import {
  useCancelSubscriptionMutation,
  usePaymentsQuery,
  useSubscriptionsQuery,
  type Subscription,
} from '../../features/payments/api'
import { formatDate, formatMoney } from '../../lib/format'
import { PAY_STATUS_LABEL, PLAN_LABEL, SUB_STATUS_LABEL } from '../../lib/labels'
import { notify } from '../../lib/toast'

const SUB_TONE: Record<string, 'success' | 'muted' | 'danger' | 'sun'> = {
  active: 'success',
  pending: 'sun',
  expired: 'muted',
  cancelled: 'danger',
}
const PAY_TONE: Record<string, 'success' | 'muted' | 'danger' | 'sun'> = {
  paid: 'success',
  pending: 'sun',
  failed: 'danger',
  refunded: 'muted',
}

export function PaymentsPage() {
  const { data: subs, isLoading: subsLoading } = useSubscriptionsQuery()
  const { data: payments, isLoading: payLoading } = usePaymentsQuery()
  const [cancel, { isLoading: cancelling }] = useCancelSubscriptionMutation()
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const [receiptId, setReceiptId] = useState<number | null>(null)
  const [toCancel, setToCancel] = useState<Subscription | null>(null)

  async function confirmCancel() {
    if (!toCancel) return
    try {
      await cancel(toCancel.id).unwrap()
      notify.success('Абонемент отменён')
    } catch {
      notify.error('Не удалось отменить')
    }
    setToCancel(null)
  }

  if (subsLoading || payLoading) return <Skeleton className="h-72 w-full rounded-xl" />

  const activeSubs = subs?.filter((s) => s.status === 'active' || s.status === 'pending') ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Оплата</h1>
        <Button onClick={() => setCheckoutOpen(true)}>Оформить абонемент</Button>
      </div>

      <section>
        <h2 className="mb-3 text-lg font-extrabold text-ink">Абонементы</h2>
        {activeSubs.length === 0 ? (
          <EmptyState
            title="Нет активных абонементов"
            description="Оформите абонемент, чтобы открыть платные курсы."
            mood="thinking"
            action={<Button onClick={() => setCheckoutOpen(true)}>Оформить</Button>}
          />
        ) : (
          <div className="space-y-3">
            {activeSubs.map((s) => (
              <Card key={s.id} className="flex flex-wrap items-center gap-3">
                <div className="flex-1">
                  <div className="font-bold text-ink">{PLAN_LABEL[s.plan] ?? s.plan}</div>
                  <div className="text-xs text-hint">
                    {formatDate(s.period_start)} — {formatDate(s.period_end)}
                  </div>
                </div>
                <Badge tone={SUB_TONE[s.status]}>{SUB_STATUS_LABEL[s.status]}</Badge>
                {s.status === 'active' && (
                  <Button variant="ghost" size="sm" className="text-danger-700" onClick={() => setToCancel(s)}>
                    Отменить
                  </Button>
                )}
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-extrabold text-ink">История платежей</h2>
        {!payments || payments.length === 0 ? (
          <Card className="text-muted">Платежей пока нет.</Card>
        ) : (
          <div className="space-y-2">
            {payments.map((p) => (
              <Card key={p.id} className="flex flex-wrap items-center gap-3">
                <div className="flex-1">
                  <div className="font-bold text-ink">{formatMoney(p.amount)}</div>
                  {p.paid_at && <div className="text-xs text-hint">{formatDate(p.paid_at)}</div>}
                </div>
                <Badge tone={PAY_TONE[p.status]}>{PAY_STATUS_LABEL[p.status]}</Badge>
                {p.status === 'paid' && (
                  <Button variant="ghost" size="sm" onClick={() => setReceiptId(p.id)}>
                    <ReceiptIcon className="h-4 w-4" aria-hidden /> Квитанция
                  </Button>
                )}
              </Card>
            ))}
          </div>
        )}
      </section>

      <CheckoutFlow open={checkoutOpen} onOpenChange={setCheckoutOpen} onPaid={(id) => setReceiptId(id)} />
      <ReceiptModal paymentId={receiptId} onClose={() => setReceiptId(null)} />

      <Modal open={!!toCancel} onOpenChange={(o) => !o && setToCancel(null)} title="Отменить абонемент?">
        <div className="space-y-3 text-center">
          <p className="text-muted">Доступ к платным курсам закроется. Продолжить?</p>
          <div className="flex justify-center gap-2">
            <Button variant="secondary" onClick={() => setToCancel(null)}>
              Нет
            </Button>
            <Button variant="danger" loading={cancelling} onClick={confirmCancel}>
              Отменить абонемент
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
