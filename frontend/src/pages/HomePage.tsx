import { motion } from 'framer-motion'
import { Flame, Star, Trophy } from 'lucide-react'
import { Link } from 'react-router-dom'

import { useHealthQuery } from '../api/baseApi'
import { Kodik } from '../components/mascot/Kodik'
import { Badge, Button, Card, ProgressBar } from '../components/ui'
import { listItem, listStagger } from '../lib/motion'

const DEMO_COURSES = [
  { id: 1, title: 'Python с нуля', track: 'Python', tone: 'teal' as const, pct: 62, lessons: 8 },
  { id: 2, title: 'Scratch: первые игры', track: 'Scratch', tone: 'sun' as const, pct: 30, lessons: 6 },
  { id: 3, title: 'Веб: HTML и CSS', track: 'Веб', tone: 'coral' as const, pct: 0, lessons: 10 },
]

const STATS = [
  { label: 'Очки опыта', value: '1 240', icon: Star, tone: 'text-sun-700 bg-sun-50' },
  { label: 'Серия дней', value: '5', icon: Flame, tone: 'text-coral-700 bg-coral-50' },
  { label: 'Награды', value: '7', icon: Trophy, tone: 'text-teal-700 bg-teal-50' },
]

export function HomePage() {
  const { data: health } = useHealthQuery()

  return (
    <div className="space-y-6">
      <Card className="flex flex-col items-center gap-5 border-0 bg-brand text-white sm:flex-row">
        <Kodik mood="wave" size={96} aria-hidden />
        <div className="text-center sm:text-left">
          <h1 className="text-2xl font-extrabold">Привет, Аня!</h1>
          <p className="mt-1 text-white/85">Продолжим учиться? Ты на 5-дневной серии — так держать.</p>
          <div className="mt-4 flex flex-wrap justify-center gap-3 sm:justify-start">
            <Link to="/catalog">
              <Button variant="reward">Продолжить обучение</Button>
            </Link>
            {health?.status === 'ok' && (
              <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1.5 text-sm font-bold">
                <span className="h-2 w-2 rounded-full bg-success" /> Сервер на связи
              </span>
            )}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {STATS.map(({ label, value, icon: Icon, tone }) => (
          <Card key={label} className="flex items-center gap-3">
            <span className={`flex h-11 w-11 items-center justify-center rounded-md ${tone}`}>
              <Icon className="h-6 w-6" aria-hidden />
            </span>
            <div>
              <div className="text-sm text-muted">{label}</div>
              <div className="text-xl font-extrabold text-ink">{value}</div>
            </div>
          </Card>
        ))}
      </div>

      <section>
        <h2 className="mb-3 text-lg font-extrabold text-ink">Мои курсы</h2>
        <motion.div
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
          variants={listStagger}
          initial="initial"
          animate="animate"
        >
          {DEMO_COURSES.map((c) => (
            <motion.div key={c.id} variants={listItem}>
              <Card className="h-full">
                <Badge tone={c.tone}>{c.track}</Badge>
                <h3 className="mt-3 text-lg font-extrabold text-ink">{c.title}</h3>
                <p className="mb-3 text-sm text-muted">{c.lessons} уроков</p>
                <ProgressBar value={c.pct} />
                <p className="mt-2 text-xs text-hint">Пройдено {c.pct}%</p>
                <Button className="mt-4 w-full" variant={c.pct > 0 ? 'primary' : 'secondary'}>
                  {c.pct > 0 ? 'Продолжить' : 'Начать'}
                </Button>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </section>
    </div>
  )
}
