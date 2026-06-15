/** Открывает печатный HTML-отчёт ребёнка в новой вкладке.
 *
 * Запрос идёт с Bearer-токеном (через `<a target=_blank>` заголовок не передать),
 * ответ кладём в Blob и открываем — родитель печатает отчёт в PDF из браузера.
 */
export async function openReport(childId: number, token: string | null): Promise<void> {
  const res = await fetch(`/api/v1/analytics/children/${childId}/report/download`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) throw new Error('report_failed')
  const html = await res.text()
  const url = URL.createObjectURL(new Blob([html], { type: 'text/html' }))
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 60000)
}
