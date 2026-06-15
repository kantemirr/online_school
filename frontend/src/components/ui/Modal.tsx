import { type ReactNode } from 'react'

import * as Dialog from '@radix-ui/react-dialog'
import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'

import { cn } from '../../lib/cn'
import { modalPop } from '../../lib/motion'

interface ModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  children: ReactNode
  className?: string
}

export function Modal({ open, onOpenChange, title, children, className }: ModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild forceMount>
              <motion.div
                className="fixed inset-0 z-40 bg-ink/40"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              />
            </Dialog.Overlay>
            {/* Обычная центрирующая обёртка: клик по ней — снаружи Content → Radix закрывает. */}
            <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto p-4">
              <Dialog.Content asChild forceMount>
                <motion.div
                  className={cn(
                    'w-full max-w-md rounded-2xl bg-surface p-6 shadow-pop',
                    className,
                  )}
                  variants={modalPop}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                >
                  <div className="mb-3 flex items-center justify-between gap-4">
                    {title ? (
                      <Dialog.Title className="text-xl font-extrabold text-ink">{title}</Dialog.Title>
                    ) : (
                      <span />
                    )}
                    <Dialog.Close
                      className="rounded-md p-1 text-hint transition hover:bg-cloud"
                      aria-label="Закрыть"
                    >
                      <X className="h-5 w-5" />
                    </Dialog.Close>
                  </div>
                  {children}
                </motion.div>
              </Dialog.Content>
            </div>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  )
}
