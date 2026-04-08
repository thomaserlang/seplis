import { CastReceiver } from './components/cast-receiver'

// This page is loaded by the Chromecast device as the custom receiver app.
// The Cast Receiver SDK is pre-loaded via a blocking <script> in index.html.
// Must NOT include the main shell navigation.
export function Component() {
    return <CastReceiver />
}
