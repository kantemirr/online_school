import { useEffect } from 'react'

import { Modal } from '../../components/ui'
import { formatDate, formatDateTime, formatMoney } from '../../lib/format'
import { PLAN_LABEL } from '../../lib/labels'
import { useLazyReceiptQuery } from './api'

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-line py-2 text-sm last:border-0">
      <span className="text-muted">{label}</span>
      <span className="font-bold text-ink">{value}</span>
    </div>
  )
}

export function ReceiptModal({ paymentId, onClose }: { paymentId: number | null; onClose: () => void }) {
  const [fetchReceipt, { data, isFetching }] = useLazyReceiptQuery()

  useEffect(() => {
    if (paymentId != null) fetchReceipt(paymentId)
  }, [paymentId, fetchReceipt])

  return (
    <Modal open={paymentId != null} onOpenChange={(o) => !o && onClose()} title="Квитанция об оплате">
      {isFetching || !data ? (
        <p className="text-muted">Загрузка…</p>
      ) : (
        <div>
          <Row label="Номер квитанции" value={data.receipt_no} />
          <Row label="Сумма" value={formatMoney(data.amount)} />
          <Row label="Оплачено" value={formatDateTime(data.paid_at)} />
          <Row label="Тариф" value={PLAN_LABEL[data.plan] ?? data.plan} />
          <Row label="Период" value={`${formatDate(data.period_start)} — ${formatDate(data.period_end)}`} />
          {data.payer && <Row label="Плательщик" value={data.payer} />}
        </div>
      )}
    </Modal>
  )
}
