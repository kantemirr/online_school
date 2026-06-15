import { CheckCircle2, XCircle } from 'lucide-react'

import { Kodik } from '../../components/mascot/Kodik'
import { Badge, Button, Card } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useLazyHintQuery, type Submission, type SubmissionTest } from './api'

const VERDICT: Record<string, { tone: 'success' | 'sun' | 'danger'; label: string }> = {
  passed: { tone: 'success', label: 'Все тесты пройдены' },
  partial: { tone: 'sun', label: 'Часть тестов пройдена' },
  failed: { tone: 'danger', label: 'Есть ошибки' },
}

function TestList({ tests }: { tests: SubmissionTest[] }) {
  return (
    <ul className="space-y-2">
      {tests.map((t) => (
        <li key={t.test_no} className="rounded-md border border-line p-2 text-sm">
          <div className="flex items-center gap-2">
            {t.passed ? (
              <CheckCircle2 className="h-4 w-4 text-success" aria-hidden />
            ) : (
              <XCircle className="h-4 w-4 text-danger" aria-hidden />
            )}
            <span className="font-bold text-ink">Тест {t.test_no}</span>
            {t.hidden && <Badge tone="muted">скрытый</Badge>}
          </div>
          {!t.hidden && !t.passed && (
            <div className="mt-1 space-y-0.5 font-mono text-xs text-muted">
              <div>ввод: {t.stdin?.trim() || '—'}</div>
              <div>ожидалось: {t.expected}</div>
              <div>получено: {t.got || '—'}</div>
            </div>
          )}
        </li>
      ))}
    </ul>
  )
}

export function SubmissionResult({ submission }: { submission: Submission }) {
  const rj = submission.result_json

  // Деградация песочницы: автопроверка недоступна — дружелюбная плашка, не «ошибка».
  if (rj?.unavailable) {
    return (
      <Card className="flex items-center gap-3 border-sun-200 bg-sun-50">
        <Kodik mood="thinking" size={48} aria-hidden />
        <p className="text-sm font-bold text-sun-ink">
          {submission.feedback ?? 'Автопроверка кода временно недоступна, попробуйте позже.'}
        </p>
      </Card>
    )
  }

  const verdict = submission.verdict ?? 'failed'
  const meta = VERDICT[verdict] ?? VERDICT.failed
  const [getHint, { data: hint, isFetching }] = useLazyHintQuery()

  async function askHint() {
    try {
      await getHint(submission.id).unwrap()
    } catch (e) {
      const status = (e as { status?: number }).status
      notify.error(status === 429 ? 'Подсказки на сегодня закончились' : 'Подсказка сейчас недоступна')
    }
  }

  return (
    <Card className="space-y-4">
      <div className="flex items-center gap-2">
        <Badge tone={meta.tone}>{meta.label}</Badge>
        {submission.score != null && <span className="text-sm text-muted">{submission.score} баллов</span>}
      </div>

      {rj?.tests && rj.tests.length > 0 && <TestList tests={rj.tests} />}

      {rj?.stderr && (
        <pre className="overflow-x-auto rounded-md bg-ink p-3 font-mono text-xs text-coral">{rj.stderr}</pre>
      )}

      {verdict !== 'passed' && (
        <div>
          <Button variant="secondary" onClick={askHint} loading={isFetching}>
            Подсказка от Кодика
          </Button>
          {hint && (
            <div className="mt-3 rounded-md bg-brand-50 p-3 text-sm text-ink">
              <Badge tone="brand">{hint.source === 'ai' ? 'ИИ-подсказка' : 'Подсказка'}</Badge>
              <p className="mt-2">{hint.hint}</p>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
