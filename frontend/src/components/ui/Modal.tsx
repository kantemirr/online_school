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
            <Dialog.Content asChild forceMount>
              <div className="pointer-events-none fixed inset-0 z-50 flex items-center justify-center p-4">
                <motion.div
                  className={cn(
                    'pointer-events-auto w-full max-w-md rounded-2xl bg-surface p-6 shadow-pop',
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
              </div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  )
}
