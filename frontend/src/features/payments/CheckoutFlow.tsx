import { useState } from 'react'

import { Kodik } from '../../components/mascot/Kodik'
import { Button, Modal } from '../../components/ui'
import { celebrate } from '../../lib/confetti'
import { cn } from '../../lib/cn'
import { formatMoney } from '../../lib/format'
import { notify } from '../../lib/toast'
import { useCoursesQuery } from '../catalog/api'
import { useCheckoutMutation, usePayMutation, type PlanCode } from './api'

const PLANS: { code: PlanCode; title: string; price: number | null; note: string }[] = [
  { code: 'monthly', title: 'Месяц', price: 990, note: 'Все курсы на 30 дней' },
  { code: 'annual', title: 'Год', price: 9900, note: 'Все курсы на год — выгодно' },
  { code: 'course', title: 'Один курс', price: null, note: 'Доступ к выбранному курсу' },
]

interface CheckoutFlowProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onPaid: (paymentId: number) => void
}

export function CheckoutFlow({ open, onOpenChange, onPaid }: CheckoutFlowProps) {
  const [step, setStep] = useState<'plan' | 'review' | 'done'>('plan')
  const [plan, setPlan] = useState<PlanCode>('monthly')
  const [courseId, setCourseId] = useState<number | undefined>()
  const [paidId, setPaidId] = useState<number | null>(null)

  const { data: courses } = useCoursesQuery({ size: 100 })
  const [checkout] = useCheckoutMutation()
  const [pay, { isLoading: paying }] = usePayMutation()

  function close() {
    onOpenChange(false)
    setTimeout(() => {
      setStep('plan')
      setPlan('monthly')
      setCourseId(undefined)
      setPaidId(null)
    }, 200)
  }

  const selectedCourse = courses?.items.find((c) => c.id === courseId)
  const amount =
    plan === 'course' ? (selectedCourse ? Number(selectedCourse.price) : null) : PLANS.find((p) => p.code === plan)!.price

  async function doPay() {
    try {
      const co = await checkout({ plan, course_id: plan === 'course' ? courseId : undefined }).unwrap()
      await pay({ payment_id: co.payment_id, outcome: 'paid' }).unwrap()
      celebrate()
      setPaidId(co.payment_id)
      setStep('done')
    } catch {
      notify.error('Платёж не прошёл, попробуйте снова')
    }
  }

  return (
    <Modal open={open} onOpenChange={(o) => !o && close()} title="Оформление абонемента">
      {step === 'plan' && (
        <div className="space-y-4">
          <div className="space-y-2">
            {PLANS.map((p) => (
              <button
                key={p.code}
                onClick={() => setPlan(p.code)}
                className={cn(
                  'flex w-full items-center justify-between rounded-lg border-2 p-3 text-left transition',
                  plan === p.code ? 'border-brand bg-brand-50' : 'border-line hover:border-brand-200',
                )}
              >
                <span>
                  <span className="block font-extrabold text-ink">{p.title}</span>
                  <span className="text-xs text-muted">{p.note}</span>
                </span>
                <span className="font-extrabold text-brand">{p.price ? formatMoney(p.price) : '—'}</span>
              </button>
            ))}
          </div>
          {plan === 'course' && (
            <select
              className="w-full rounded-md border-2 border-line px-3 py-2"
              value={courseId ?? ''}
              onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : undefined)}
            >
              <option value="">— выбери курс —</option>
              {courses?.items.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title} · {formatMoney(c.price)}
                </option>
              ))}
            </select>
          )}
          <Button fullWidth disabled={plan === 'course' && !courseId} onClick={() => setStep('review')}>
            Далее
          </Button>
        </div>
      )}

      {step === 'review' && (
        <div className="space-y-4 text-center">
          <p className="text-muted">К оплате</p>
          <p className="text-3xl font-extrabold text-ink">{amount != null ? formatMoney(amount) : '—'}</p>
          <Button fullWidth variant="reward" loading={paying} onClick={doPay}>
            Оплатить (демо)
          </Button>
        </div>
      )}

      {step === 'done' && (
        <div className="flex flex-col items-center gap-3 text-center">
          <Kodik mood="celebrate" size={96} aria-hidden />
          <h3 className="text-xl font-extrabold text-ink">Оплата прошла!</h3>
          <p className="text-muted">Абонемент активирован. Курсы открыты для ребёнка.</p>
          <div className="flex gap-2">
            {paidId && (
              <Button
                variant="secondary"
                onClick={() => {
                  const id = paidId
                  close()
                  onPaid(id)
                }}
              >
                Квитанция
              </Button>
            )}
            <Button onClick={close}>Готово</Button>
          </div>
        </div>
      )}
    </Modal>
  )
}
