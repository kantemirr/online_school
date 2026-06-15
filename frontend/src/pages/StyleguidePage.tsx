import { useState, type ReactNode } from 'react'

import { PartyPopper } from 'lucide-react'

import { Kodik, type KodikMood } from '../components/mascot/Kodik'
import {
  Avatar,
  Badge,
  Button,
  Card,
  EmptyState,
  Field,
  Input,
  Modal,
  ProgressBar,
  Skeleton,
  Tooltip,
} from '../components/ui'
import { useKodik } from '../components/mascot/KodikProvider'
import { celebrate } from '../lib/confetti'
import { notify } from '../lib/toast'

const SWATCHES: { name: string; hex: string }[] = [
  { name: 'Индиго', hex: '#6C5CE7' },
  { name: 'Бирюза', hex: '#13C0BC' },
  { name: 'Солнце', hex: '#FDB833' },
  { name: 'Коралл', hex: '#FF6B9D' },
  { name: 'Успех', hex: '#34C77B' },
  { name: 'Ошибка', hex: '#F26D6D' },
  { name: 'Чернила', hex: '#20243A' },
  { name: 'Фон', hex: '#F6F7FB' },
]

const MOODS: KodikMood[] = ['idle', 'happy', 'thinking', 'celebrate', 'sad', 'wave']

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="text-lg font-extrabold text-ink">{title}</h2>
      {children}
    </section>
  )
}

export function StyleguidePage() {
  const [modal, setModal] = useState(false)
  const { react } = useKodik()

  return (
    <div className="space-y-8 pb-8">
      <header>
        <Badge tone="brand">Дизайн-система</Badge>
        <h1 className="mt-2 text-3xl font-extrabold text-ink">CodeKids UI-кит</h1>
        <p className="text-muted">Палитра, типографика, компоненты, маскот и анимации в одном месте.</p>
      </header>

      <Section title="Палитра">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {SWATCHES.map((s) => (
            <div key={s.hex}>
              <div className="h-16 rounded-lg" style={{ background: s.hex }} />
              <div className="mt-1.5 text-sm font-bold text-ink">{s.name}</div>
              <div className="text-xs text-hint">{s.hex}</div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Типографика">
        <Card className="space-y-2">
          <h1 className="text-4xl font-extrabold text-ink">Заголовок H1</h1>
          <h2 className="text-2xl font-extrabold text-ink">Заголовок H2</h2>
          <p className="text-base text-ink">Основной текст — крупный и читаемый для детей 8–14 лет.</p>
          <p className="text-sm text-muted">Вторичный текст и подписи.</p>
          <code className="font-mono text-sm text-brand-700">print("Привет, мир!")</code>
        </Card>
      </Section>

      <Section title="Кнопки">
        <Card className="flex flex-wrap items-center gap-3">
          <Button variant="primary">Основная</Button>
          <Button variant="reward">Награда</Button>
          <Button variant="secondary">Вторая</Button>
          <Button variant="ghost">Призрак</Button>
          <Button variant="danger">Удалить</Button>
          <Button loading>Загрузка</Button>
          <Button size="sm">Маленькая</Button>
          <Button size="lg">Большая</Button>
        </Card>
      </Section>

      <Section title="Бейджи и аватары">
        <Card className="flex flex-wrap items-center gap-3">
          <Badge tone="brand">Python</Badge>
          <Badge tone="teal">Scratch</Badge>
          <Badge tone="sun">Новичок</Badge>
          <Badge tone="coral">Достижение</Badge>
          <Badge tone="success">Сдано</Badge>
          <Badge tone="danger">Ошибка</Badge>
          <Avatar name="Аня Кодова" />
          <Avatar name="Иван Петров" size={56} />
        </Card>
      </Section>

      <Section title="Прогресс и загрузка">
        <Card className="space-y-4">
          <ProgressBar value={25} />
          <ProgressBar value={62} />
          <ProgressBar value={100} />
          <div className="flex gap-3">
            <Skeleton className="h-12 w-12 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-4 w-1/3" />
            </div>
          </div>
        </Card>
      </Section>

      <Section title="Поля ввода">
        <Card className="grid gap-4 sm:grid-cols-2">
          <Field label="Никнейм" hint="Так тебя увидят в рейтинге">
            <Input placeholder="Например, CodeStar" />
          </Field>
          <Field label="PIN-код" error="PIN должен состоять из 4 цифр">
            <Input placeholder="••••" />
          </Field>
        </Card>
      </Section>

      <Section title="Маскот «Кодик»">
        <Card>
          <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
            {MOODS.map((m) => (
              <div key={m} className="flex flex-col items-center gap-1">
                <Kodik mood={m} size={84} />
                <span className="text-xs font-bold text-muted">{m}</span>
              </div>
            ))}
          </div>
        </Card>
      </Section>

      <Section title="Обратная связь и анимации">
        <Card className="flex flex-wrap items-center gap-3">
          <Button
            variant="reward"
            onClick={() => {
              celebrate()
              react('celebrate')
            }}
          >
            <PartyPopper className="h-4 w-4" aria-hidden /> Конфетти
          </Button>
          <Button variant="primary" onClick={() => notify.success('Урок успешно пройден!')}>
            Тост успеха
          </Button>
          <Button variant="danger" onClick={() => notify.error('Тест не пройден, попробуй ещё')}>
            Тост ошибки
          </Button>
          <Button variant="secondary" onClick={() => setModal(true)}>
            Открыть модалку
          </Button>
          <Tooltip content="Привет, я подсказка!">
            <Button variant="ghost">Наведи на меня</Button>
          </Tooltip>
        </Card>
      </Section>

      <Section title="Пустое состояние">
        <EmptyState
          title="Здесь пока пусто"
          description="Запишись на первый курс — и Кодик будет рад тебе помочь!"
          mood="happy"
          action={<Button variant="primary">Выбрать курс</Button>}
        />
      </Section>

      <Modal open={modal} onOpenChange={setModal} title="Поздравляем!">
        <div className="flex flex-col items-center gap-3 text-center">
          <Kodik mood="celebrate" size={96} aria-hidden />
          <p className="text-muted">Ты открыл новое достижение «Первый код». Так держать!</p>
          <Button variant="reward" onClick={() => setModal(false)}>
            Ура!
          </Button>
        </div>
      </Modal>
    </div>
  )
}
