import { useState } from 'react'

import { useNavigate } from 'react-router-dom'

import { Kodik } from '../../components/mascot/Kodik'
import { useKodik } from '../../components/mascot/KodikProvider'
import { Button, Card } from '../../components/ui'
import { celebrate } from '../../lib/confetti'
import { cn } from '../../lib/cn'
import { notify } from '../../lib/toast'
import { useSubmitQuizMutation, type AssignmentForSolve, type Submission } from './api'

interface MatchOptions {
  left: string[]
  right: string[]
}

export function QuizPlayer({ assignment }: { assignment: AssignmentForSolve }) {
  const [answers, setAnswers] = useState<Record<string, unknown>>({})
  const [result, setResult] = useState<Submission | null>(null)
  const [submit, { isLoading }] = useSubmitQuizMutation()
  const { react } = useKodik()
  const nav = useNavigate()

  const setSingle = (qid: string, idx: number) => setAnswers((a) => ({ ...a, [qid]: [idx] }))
  const toggleMultiple = (qid: string, idx: number) =>
    setAnswers((a) => {
      const cur = (a[qid] as number[] | undefined) ?? []
      return { ...a, [qid]: cur.includes(idx) ? cur.filter((x) => x !== idx) : [...cur, idx] }
    })
  const setMatch = (qid: string, leftIdx: number, rightIdx: number) =>
    setAnswers((a) => {
      const cur = (a[qid] as number[][] | undefined) ?? []
      return { ...a, [qid]: [...cur.filter((p) => p[0] !== leftIdx), [leftIdx, rightIdx]] }
    })

  async function onSubmit() {
    try {
      const r = await submit({ id: assignment.id, answers }).unwrap()
      setResult(r)
      if (r.result_json?.passed) {
        celebrate()
        react('celebrate')
      } else {
        react('thinking')
      }
    } catch {
      notify.error('Не удалось отправить ответы')
    }
  }

  function retry() {
    setResult(null)
    setAnswers({})
  }

  const wrong = new Set(result?.result_json?.wrong_question_ids ?? [])
  const answeredAll = assignment.questions.every((q) => answers[String(q.id)] !== undefined)

  return (
    <Card className="space-y-6">
      {assignment.questions.map((q, qi) => {
        const qid = String(q.id)
        const state = result ? (wrong.has(q.id) ? 'wrong' : 'right') : 'idle'
        return (
          <div
            key={q.id}
            className={cn(
              'rounded-lg border p-4',
              state === 'wrong'
                ? 'border-danger bg-danger-50'
                : state === 'right'
                  ? 'border-success bg-success-50'
                  : 'border-line',
            )}
          >
            <p className="mb-3 font-bold text-ink">
              {qi + 1}. {q.text}
            </p>

            {(q.kind === 'single' || q.kind === 'multiple') && (
              <div className="space-y-2">
                {(q.options as string[]).map((opt, idx) => (
                  <label key={idx} className="flex cursor-pointer items-center gap-2">
                    <input
                      type={q.kind === 'single' ? 'radio' : 'checkbox'}
                      name={`q${q.id}`}
                      className="h-4 w-4 accent-brand"
                      disabled={!!result}
                      checked={((answers[qid] as number[] | undefined) ?? []).includes(idx)}
                      onChange={() => (q.kind === 'single' ? setSingle(qid, idx) : toggleMultiple(qid, idx))}
                    />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>
            )}

            {q.kind === 'matching' && (
              <div className="space-y-2">
                {(q.options as MatchOptions).left.map((leftLabel, li) => (
                  <div key={li} className="flex items-center gap-2">
                    <span className="flex-1">{leftLabel}</span>
                    <select
                      className="rounded-md border-2 border-line px-2 py-1.5"
                      disabled={!!result}
                      defaultValue=""
                      onChange={(e) => setMatch(qid, li, Number(e.target.value))}
                    >
                      <option value="" disabled>
                        — выбери —
                      </option>
                      {(q.options as MatchOptions).right.map((r, ri) => (
                        <option key={ri} value={ri}>
                          {r}
                        </option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            )}
          </div>
        )
      })}

      {!result ? (
        <Button onClick={onSubmit} loading={isLoading} disabled={!answeredAll}>
          Проверить
        </Button>
      ) : (
        <div className={cn('rounded-lg p-4 text-center', result.result_json?.passed ? 'bg-success-50' : 'bg-sun-50')}>
          <div className="flex justify-center">
            <Kodik mood={result.result_json?.passed ? 'celebrate' : 'thinking'} size={72} aria-hidden />
          </div>
          <p className="mt-2 font-extrabold text-ink">
            {result.result_json?.passed ? 'Отлично! Задание зачтено' : 'Почти получилось!'}
          </p>
          <p className="text-sm text-muted">
            Верно {result.result_json?.correct} из {result.result_json?.total} · {result.score} баллов
          </p>
          <div className="mt-3 flex justify-center gap-2">
            {!result.result_json?.passed && (
              <Button variant="secondary" onClick={retry}>
                Попробовать снова
              </Button>
            )}
            <Button onClick={() => nav(-1)}>{result.result_json?.passed ? 'Продолжить' : 'К уроку'}</Button>
          </div>
        </div>
      )}
    </Card>
  )
}
