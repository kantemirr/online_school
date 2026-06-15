import { createBrowserRouter } from 'react-router-dom'

import { AppShell } from './components/layout/AppShell'
import { ComingSoonPage } from './pages/ComingSoonPage'
import { HomePage } from './pages/HomePage'
import { StyleguidePage } from './pages/StyleguidePage'

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/catalog', element: <ComingSoonPage title="Каталог курсов" /> },
      { path: '/achievements', element: <ComingSoonPage title="Награды" /> },
      { path: '/styleguide', element: <StyleguidePage /> },
      { path: '*', element: <ComingSoonPage title="Страница не найдена" mood="sad" /> },
    ],
  },
])
