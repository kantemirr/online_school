import { Link } from 'react-router-dom'

import { Button, EmptyState } from '../components/ui'

export function NotFoundPage() {
  return (
    <div className="mx-auto max-w-lg pt-6">
      <EmptyState
        title="Страница не найдена"
        description="Похоже, такой страницы нет или она переехала. Вернёмся на главную?"
        mood="sad"
        action={
          <Link to="/">
            <Button>На главную</Button>
          </Link>
        }
      />
    </div>
  )
}
