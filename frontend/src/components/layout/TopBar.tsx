import { Bell } from 'lucide-react'

import { Avatar } from '../ui/Avatar'

export function TopBar() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-line bg-surface px-4 lg:px-6">
      <span className="text-lg font-extrabold text-brand lg:hidden">CodeKids</span>
      <div className="ml-auto flex items-center gap-3">
        <button
          className="relative rounded-full p-2 text-muted transition hover:bg-cloud"
          aria-label="Уведомления"
        >
          <Bell className="h-5 w-5" aria-hidden />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-coral" />
        </button>
        <Avatar name="Аня Кодова" size={36} />
      </div>
    </header>
  )
}
