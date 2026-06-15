import { useEffect, useState } from 'react'

type Health = { status: string; db: boolean; redis: boolean }

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/v1/health')
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(String(e)))
  }, [])

  return (
    <div className="app-shell">
      <span className="badge">Этап 0 — фундамент</span>
      <h1>CodeKids</h1>
      <p>Онлайн-школа программирования для детей 8–14 лет</p>
      <div className="status">
        {error && <span>Бэкенд недоступен: {error}</span>}
        {!error && !health && <span>Проверка связи с бэкендом…</span>}
        {health && (
          <span>
            Статус API: <b>{health.status}</b> · БД: {health.db ? '✅' : '❌'} · Redis:{' '}
            {health.redis ? '✅' : '❌'}
          </span>
        )}
      </div>
    </div>
  )
}
