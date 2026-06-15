import { useEffect, useRef, useState } from 'react'

import { python } from '@codemirror/lang-python'
import CodeMirror from '@uiw/react-codemirror'

import { baseApi } from '../../api/baseApi'
import { Kodik } from '../../components/mascot/Kodik'
import { useKodik } from '../../components/mascot/KodikProvider'
import { Button, Card } from '../../components/ui'
import { celebrate } from '../../lib/confetti'
import { notify } from '../../lib/toast'
import { useAppDispatch } from '../../store/hooks'
import { SubmissionResult } from './SubmissionResult'
import { useSubmissionQuery, useSubmitCodeMutation, type AssignmentForSolve } from './api'

const TEMPLATE = '# Напиши своё решение здесь\n'

export function CodeSandbox({ assignment }: { assignment: AssignmentForSolve }) {
  const [code, setCode] = useState(TEMPLATE)
  const [submissionId, setSubmissionId] = useState<number | null>(null)
  const [finished, setFinished] = useState(false)
  const [slow, setSlow] = useState(false)
  const celebrated = useRef(false)
  const slowTimer = useRef<ReturnType<typeof setTimeout>>()

  const [submit, { isLoading: submitting }] = useSubmitCodeMutation()
  const { react } = useKodik()
  const dispatch = useAppDispatch()

  const { data: sub } = useSubmissionQuery(submissionId ?? 0, {
    skip: submissionId === null,
    pollingInterval: submissionId !== null && !finished ? 1200 : 0,
  })

  useEffect(() => {
    if (!sub || sub.status !== 'checked') return
    setFinished(true)
    setSlow(false)
    if (slowTimer.current) clearTimeout(slowTimer.current)
    if (sub.verdict === 'passed' && !celebrated.current) {
      celebrated.current = true
      celebrate()
      react('celebrate')
      dispatch(baseApi.util.invalidateTags(['Lesson', 'Enrollment']))
    } else if (sub.verdict && sub.verdict !== 'passed') {
      react('thinking')
    }
  }, [sub, react, dispatch])

  async function run() {
    if (!code.trim()) return
    setFinished(false)
    setSlow(false)
    celebrated.current = false
    if (slowTimer.current) clearTimeout(slowTimer.current)
    slowTimer.current = setTimeout(() => setSlow(true), 40000)
    try {
      const s = await submit({ id: assignment.id, code }).unwrap()
      setSubmissionId(s.id)
    } catch {
      notify.error('Не удалось отправить код на проверку')
    }
  }

  const running = submissionId !== null && !finished && (!sub || sub.status === 'queued' || sub.status === 'running')

  return (
    <div className="space-y-5">
      {assignment.examples.length > 0 && (
        <Card>
          <h3 className="mb-2 font-bold text-ink">Примеры</h3>
          <div className="space-y-2">
            {assignment.examples.map((ex, i) => (
              <div key={i} className="rounded-md bg-cloud p-3 font-mono text-sm">
                <div>
                  <span className="text-hint">ввод:</span> {ex.stdin?.trim() || '—'}
                </div>
                <div>
                  <span className="text-hint">ожидание:</span> {ex.expected_stdout}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card className="overflow-hidden p-0">
        <CodeMirror
          value={code}
          height="280px"
          extensions={[python()]}
          editable={!running}
          onChange={(value) => setCode(value)}
        />
      </Card>

      <div className="flex flex-wrap items-center gap-3">
        <Button onClick={run} loading={submitting} disabled={!code.trim() || running}>
          Запустить проверку
        </Button>
        {running && (
          <span className="flex items-center gap-2 text-muted">
            <Kodik mood="thinking" size={36} aria-hidden />
            {sub?.status === 'running' ? 'Выполняется в песочнице…' : 'В очереди…'}
          </span>
        )}
        {slow && running && <span className="text-sm text-danger-700">Проверка затянулась — подожди ещё немного.</span>}
      </div>

      {sub?.status === 'checked' && <SubmissionResult submission={sub} />}
    </div>
  )
}
