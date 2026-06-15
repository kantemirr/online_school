import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const STYLES = [
  'space-y-3 text-ink leading-relaxed',
  '[&_h1]:text-xl [&_h1]:font-extrabold [&_h2]:text-lg [&_h2]:font-extrabold [&_h3]:font-extrabold',
  '[&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-1',
  '[&_a]:font-bold [&_a]:text-brand [&_a]:underline',
  '[&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:bg-ink [&_pre]:p-4 [&_pre]:text-white',
  '[&_code]:font-mono [&_code]:text-sm',
  '[&_:not(pre)>code]:rounded [&_:not(pre)>code]:bg-brand-50 [&_:not(pre)>code]:px-1.5 [&_:not(pre)>code]:py-0.5 [&_:not(pre)>code]:text-brand-700',
].join(' ')

/** Безопасный рендер markdown-теории урока (без сырого HTML). */
export function Markdown({ children }: { children: string }) {
  return (
    <div className={STYLES}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  )
}
