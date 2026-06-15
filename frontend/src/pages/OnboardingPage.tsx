import { useState } from 'react'

import { AnimatePresence, motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

import { Kodik, type KodikMood } from '../components/mascot/Kodik'
import { Button } from '../components/ui'
import { cn } from '../lib/cn'

const STEPS: { mood: KodikMood; title: string; text: string }[] = [
  { mood: 'wave', title: 'Привет! Я Кодик', text: 'Я твой помощник в мире программирования. Будем учиться вместе — это весело!' },
  { mood: 'happy', title: 'Уроки и задания', text: 'Читай теорию, проходи квизы и пиши настоящий код прямо в браузере.' },
  { mood: 'celebrate', title: 'Награды и рейтинг', text: 'За успехи получай очки опыта, награды и поднимайся в рейтинге школы!' },
]

export function OnboardingPage() {
  const [step, setStep] = useState(0)
  const nav = useNavigate()
  const last = step === STEPS.length - 1

  function finish() {
    localStorage.setItem('codekids_onboarded', '1')
    nav('/home', { replace: true })
  }

  const s = STEPS[step]

  return (
    <div className="flex min-h-screen items-center justify-center bg-cloud p-4">
      <div className="w-full max-w-md text-center">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -14 }}
            transition={{ duration: 0.25 }}
          >
            <div className="flex justify-center">
              <Kodik mood={s.mood} size={140} aria-hidden />
            </div>
            <h1 className="mt-3 text-2xl font-extrabold text-ink">{s.title}</h1>
            <p className="mt-2 text-muted">{s.text}</p>
          </motion.div>
        </AnimatePresence>

        <div className="mt-5 flex justify-center gap-2">
          {STEPS.map((_, i) => (
            <span
              key={i}
              className={cn('h-2 rounded-full transition-all', i === step ? 'w-6 bg-brand' : 'w-2 bg-brand-100')}
            />
          ))}
        </div>

        <div className="mt-6 flex items-center justify-center gap-3">
          {last ? (
            <Button variant="reward" size="lg" onClick={finish}>
              Поехали!
            </Button>
          ) : (
            <Button size="lg" onClick={() => setStep((p) => p + 1)}>
              Дальше
            </Button>
          )}
        </div>
        {!last && (
          <button onClick={finish} className="mt-3 text-sm font-bold text-hint hover:text-muted">
            Пропустить
          </button>
        )}
      </div>
    </div>
  )
}
