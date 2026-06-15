import { Provider } from 'react-redux'
import { RouterProvider } from 'react-router-dom'
import { Toaster } from 'sonner'

import { KodikProvider } from './components/mascot/KodikProvider'
import { router } from './router'
import { store } from './store'

export default function App() {
  return (
    <Provider store={store}>
      <KodikProvider>
        <RouterProvider router={router} />
        <Toaster richColors position="top-center" />
      </KodikProvider>
    </Provider>
  )
}
