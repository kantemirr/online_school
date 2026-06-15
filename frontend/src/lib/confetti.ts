import confetti from 'canvas-confetti'

const BRAND_COLORS = ['#6C5CE7', '#13C0BC', '#FDB833', '#FF6B9D']

/** Праздничное конфетти бренд-цветами (достижение, верный ответ, завершение курса). */
export function celebrate(): void {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  confetti({
    particleCount: 90,
    spread: 70,
    startVelocity: 38,
    origin: { y: 0.7 },
    colors: BRAND_COLORS,
  })
}
