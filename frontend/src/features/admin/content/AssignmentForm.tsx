import { useState } from 'react'

import { Plus, Trash2 } from 'lucide-react'

import { Button, Field, Input, Modal } from '../../../components/ui'
import { notify } from '../../../lib/toast'
import { useCreateAssignmentMutation } from '../api'

interface QState {
  text: string
  kind: 'single' | 'multiple'
  options: string
  correct: string
}
interface TState {
  stdin: string
  expected_stdout: string
  is_hidden: boolean
  weight: number
}

export function AssignmentForm({ open, onOpenChange, lessonId }: { open: boolean; onOpenChange: (o: boolean) => void; lessonId: number }) {
  const [type, setType] = useState<'quiz' | 'code' | 'project'>('quiz')
  const [title, setTitle] = useState('')
  const [maxScore, setMaxScore] = useState('100')
  const [dueAt, setDueAt] = useState('')
  const [questions, setQuestions] = useState<QState[]>([])
  const [tests, setTests] = useState<TState[]>([])
  const [create, { isLoading }] = useCreateAssignmentMutation()

  function reset() {
    setType('quiz'); setTitle(''); setMaxScore('100'); setDueAt(''); setQuestions([]); setTests([])
  }

  async function submit() {
    if (!title.trim()) {
      notify.error('Укажите название задания')
      return
    }
    const qpayload = questions.map((q) => ({
      text: q.text,
      kind: q.kind,
      options_json: q.options.split('\n').map((s) => s.trim()).filter(Boolean),
      correct_json: q.correct.split(',').map((n) => Number(n.trim()) - 1).filter((n) => n >= 0),
    }))
    const tpayload = tests.map((t) => ({
      stdin: t.stdin || null,
      expected_stdout: t.expected_stdout,
      is_hidden: t.is_hidden,
      weight: Number(t.weight) || 1,
    }))
    try {
      await create({
        lesson_id: lessonId,
        type,
        title,
        max_score: Number(maxScore) || 100,
        due_at: dueAt ? new Date(dueAt).toISOString() : null,
        questions: type === 'quiz' ? qpayload : [],
        code_tests: type === 'code' ? tpayload : [],
      }).unwrap()
      notify.success('Задание создано')
      reset()
      onOpenChange(false)
    } catch {
      notify.error('Не удалось создать задание')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Новое задание">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field label="Тип">
            <select className="w-full rounded-md border-2 border-line px-3 py-2" value={type} onChange={(e) => setType(e.target.value as typeof type)}>
              <option value="quiz">Квиз</option>
              <option value="code">Код</option>
              <option value="project">Проект</option>
            </select>
          </Field>
          <Field label="Макс. балл">
            <Input type="number" value={maxScore} onChange={(e) => setMaxScore(e.target.value)} />
          </Field>
        </div>
        <Field label="Название">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
        <Field label="Срок сдачи (необязательно)">
          <Input type="datetime-local" value={dueAt} onChange={(e) => setDueAt(e.target.value)} />
        </Field>

        {type === 'quiz' && (
          <div className="space-y-3">
            {questions.map((q, qi) => (
              <div key={qi} className="space-y-2 rounded-md border border-line p-3">
                <div className="flex items-center gap-2">
                  <Input placeholder="Текст вопроса" value={q.text} onChange={(e) => setQuestions((arr) => arr.map((x, i) => (i === qi ? { ...x, text: e.target.value } : x)))} />
                  <Button variant="ghost" size="sm" className="text-danger-700" onClick={() => setQuestions((arr) => arr.filter((_, i) => i !== qi))} aria-label="Удалить вопрос">
                    <Trash2 className="h-4 w-4" aria-hidden />
                  </Button>
                </div>
                <select className="w-full rounded-md border-2 border-line px-2 py-1.5 text-sm" value={q.kind} onChange={(e) => setQuestions((arr) => arr.map((x, i) => (i === qi ? { ...x, kind: e.target.value as 'single' | 'multiple' } : x)))}>
                  <option value="single">Один верный</option>
                  <option value="multiple">Несколько верных</option>
                </select>
                <textarea className="w-full rounded-md border-2 border-line p-2 text-sm" rows={3} placeholder="Варианты — по одному на строку" value={q.options} onChange={(e) => setQuestions((arr) => arr.map((x, i) => (i === qi ? { ...x, options: e.target.value } : x)))} />
                <Input placeholder="Номера верных через запятую (с 1)" value={q.correct} onChange={(e) => setQuestions((arr) => arr.map((x, i) => (i === qi ? { ...x, correct: e.target.value } : x)))} />
              </div>
            ))}
            <Button variant="secondary" size="sm" onClick={() => setQuestions((arr) => [...arr, { text: '', kind: 'single', options: '', correct: '' }])}>
              <Plus className="h-4 w-4" aria-hidden /> Вопрос
            </Button>
          </div>
        )}

        {type === 'code' && (
          <div className="space-y-3">
            {tests.map((t, ti) => (
              <div key={ti} className="space-y-2 rounded-md border border-line p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-ink">Тест {ti + 1}</span>
                  <Button variant="ghost" size="sm" className="text-danger-700" onClick={() => setTests((arr) => arr.filter((_, i) => i !== ti))} aria-label="Удалить тест">
                    <Trash2 className="h-4 w-4" aria-hidden />
                  </Button>
                </div>
                <Input placeholder="Ввод (stdin)" value={t.stdin} onChange={(e) => setTests((arr) => arr.map((x, i) => (i === ti ? { ...x, stdin: e.target.value } : x)))} />
                <Input placeholder="Ожидаемый вывод" value={t.expected_stdout} onChange={(e) => setTests((arr) => arr.map((x, i) => (i === ti ? { ...x, expected_stdout: e.target.value } : x)))} />
                <label className="flex items-center gap-2 text-sm text-muted">
                  <input type="checkbox" className="h-4 w-4 accent-brand" checked={t.is_hidden} onChange={(e) => setTests((arr) => arr.map((x, i) => (i === ti ? { ...x, is_hidden: e.target.checked } : x)))} />
                  Скрытый тест
                </label>
              </div>
            ))}
            <Button variant="secondary" size="sm" onClick={() => setTests((arr) => [...arr, { stdin: '', expected_stdout: '', is_hidden: false, weight: 1 }])}>
              <Plus className="h-4 w-4" aria-hidden /> Тест
            </Button>
          </div>
        )}

        <Button fullWidth loading={isLoading} onClick={submit}>
          Создать задание
        </Button>
      </div>
    </Modal>
  )
}
