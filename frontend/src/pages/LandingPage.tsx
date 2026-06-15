import { Code2, Shield, Trophy, Users, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Kodik } from '../components/mascot/Kodik'
import { Badge, Button, Card } from '../components/ui'
import { useTracksQuery } from '../features/catalog/api'
import { TRACK_LABEL } from '../lib/labels'

const FEATURES: { icon: LucideIcon; title: string; text: string }[] = [
  { icon: Code2, title: 'Код в браузере', text: 'Дети пишут и запускают программы прямо на сайте — в безопасной песочнице.' },
  { icon: Shield, title: 'Безопасно', text: 'Изолированное выполнение кода, минимум данных ребёнка, контроль родителя.' },
  { icon: Trophy, title: 'Геймификация', text: 'Очки, награды, серии и рейтинг — учиться интересно и хочется возвращаться.' },
  { icon: Users, title: 'Живые занятия', text: 'Группы с преподавателем, расписание онлайн-уроков и проверка проектов.' },
]

export function LandingPage() {
  const { data: tracks } = useTracksQuery()

  return (
    <div className="min-h-screen bg-cloud">
      <header className="flex items-center justify-between px-4 py-4 sm:px-8">
        <div className="flex items-center gap-2">
          <Kodik mood="idle" size={36} aria-hidden />
          <span className="text-xl font-extrabold text-brand">CodeKids</span>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/login">
            <Button variant="ghost" size="sm">Войти</Button>
          </Link>
          <Link to="/register">
            <Button size="sm">Регистрация</Button>
          </Link>
        </div>
      </header>

      <section className="mx-auto grid max-w-5xl items-center gap-6 px-4 py-10 sm:px-8 md:grid-cols-2">
        <div>
          <Badge tone="sun">Программирование для детей 8–14 лет</Badge>
          <h1 className="mt-3 text-3xl font-extrabold leading-tight text-ink sm:text-4xl">
            Научим ребёнка программировать — с удовольствием
          </h1>
          <p className="mt-3 text-lg text-muted">
            Интерактивные уроки, код в браузере, награды и живые занятия с преподавателем. Первые шаги — бесплатно.
          </p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link to="/register">
              <Button variant="reward" size="lg">Начать бесплатно</Button>
            </Link>
            <Link to="/login/child">
              <Button variant="secondary" size="lg">Вход для ребёнка</Button>
            </Link>
          </div>
        </div>
        <div className="flex justify-center">
          <div className="rounded-2xl bg-brand p-8">
            <Kodik mood="wave" size={200} aria-hidden />
          </div>
        </div>
      </section>

      {tracks && tracks.length > 0 && (
        <section className="mx-auto max-w-5xl px-4 py-6 sm:px-8">
          <h2 className="mb-3 text-lg font-extrabold text-ink">Направления обучения</h2>
          <div className="flex flex-wrap gap-2">
            {tracks.map((t) => (
              <Badge key={t.code} tone="brand">
                {TRACK_LABEL[t.code] ?? t.label} · {t.course_count}
              </Badge>
            ))}
          </div>
        </section>
      )}

      <section className="mx-auto max-w-5xl px-4 py-8 sm:px-8">
        <h2 className="mb-4 text-2xl font-extrabold text-ink">Почему CodeKids</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <Card key={f.title}>
              <span className="flex h-11 w-11 items-center justify-center rounded-md bg-brand-50 text-brand">
                <f.icon className="h-6 w-6" aria-hidden />
              </span>
              <h3 className="mt-3 font-extrabold text-ink">{f.title}</h3>
              <p className="mt-1 text-sm text-muted">{f.text}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 pb-12 sm:px-8">
        <Card className="flex flex-col items-center gap-4 border-0 bg-brand py-10 text-center text-white">
          <Kodik mood="celebrate" size={96} aria-hidden />
          <h2 className="text-2xl font-extrabold">Готовы начать приключение?</h2>
          <Link to="/register">
            <Button variant="reward" size="lg">Создать аккаунт родителя</Button>
          </Link>
        </Card>
      </section>

      <footer className="border-t border-line px-4 py-6 text-center text-sm text-hint sm:px-8">
        CodeKids — онлайн-школа программирования для детей · демонстрационный проект ВКР
      </footer>
    </div>
  )
}
