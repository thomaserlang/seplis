import { CastReceiver } from '@/features/cast/components/cast-receiver'
import ReactDOM from 'react-dom/client'

// Minimal entry — no Mantine, no React Query needed.
// CastReceiver uses only plain async functions (ky), no hooks that need providers.
ReactDOM.createRoot(
    document.getElementById('cast-receiver-root') as HTMLElement,
).render(<CastReceiver />)
