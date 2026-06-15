import { AnimatePresence, motion } from 'framer-motion'
import { Outlet, useLocation } from 'react-router-dom'

import { pageTransition } from '../../lib/motion'
import { BottomNav } from './BottomNav'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

/** Адаптивная оболочка: боковая навигация на десктопе ↔ нижняя на телефоне. */
export function AppShell() {
  const location = useLocation()
  return (
    <div className="flex min-h-screen bg-cloud">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main className="flex-1 px-4 pb-24 pt-5 lg:px-8 lg:pb-8">
          <div className="mx-auto w-full max-w-6xl">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                variants={pageTransition}
                initial="initial"
                animate="animate"
                exit="exit"
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
        <BottomNav />
      </div>
    </div>
  )
}
