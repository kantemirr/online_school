import type { Transition, Variants } from 'framer-motion'

// Общие пресеты анимаций (Framer Motion). Декоративные анимации глобально гасятся
// через @media (prefers-reduced-motion) в styles/index.css.

export const springSoft: Transition = { type: 'spring', stiffness: 300, damping: 24 }

/** Переход между страницами: мягкое появление снизу. */
export const pageTransition: Variants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: springSoft },
  exit: { opacity: 0, y: -8, transition: { duration: 0.15 } },
}

/** Контейнер со ступенчатым появлением детей (списки карточек). */
export const listStagger: Variants = {
  animate: { transition: { staggerChildren: 0.06 } },
}

export const listItem: Variants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: springSoft },
}

/** Всплывающая модалка/поповер. */
export const modalPop: Variants = {
  initial: { opacity: 0, scale: 0.92 },
  animate: { opacity: 1, scale: 1, transition: springSoft },
  exit: { opacity: 0, scale: 0.95, transition: { duration: 0.12 } },
}

export const cardHover = { scale: 1.02, transition: springSoft }
export const buttonTap = { scale: 0.96 }
