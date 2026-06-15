import { Link } from 'react-router-dom'

import { Button, EmptyState } from '../components/ui'
import type { KodikMood } from '../components/mascot/Kodik'

export function ComingSoonPage({ title, mood = 'thinking' }: { title: string; mood?: KodikMood }) {
  return (
    <div className="mx-auto max-w-lg pt-6">
      <EmptyState
        title={title}
        description="Этот раздел появится на следующих под-этапах. Пока загляни в дизайн-систему — там живут все компоненты."
        mood={mood}
        action={
          <Link to="/styleguide">
            <Button variant="secondary">Открыть UI-кит</Button>
          </Link>
        }
      />
    </div>
  )
}
