import { useEffect, useState } from 'react'
import type { SenderCast } from './sender-capture'
import { SenderChrome } from './sender-capture'

export type Sender = {
	cast: SenderCast
	chrome: SenderChrome
}

const load = (() => {
	let promise: Promise<Sender> | null = null

	return () => {
		if (promise === null) {
			promise = new Promise((resolve) => {
				const script = document.createElement('script')
				script.src =
					'https://www.gstatic.com/cv/js/sender/v1/cast_sender.js?loadCastFramework=1'
				window.__onGCastApiAvailable = (isAvailable) => {
					if (isAvailable) {
						resolve({
							cast,
							chrome,
						})
					}
				}
				document.body.appendChild(script)
			})
		}
		return promise
	}
})()

export const useChromecastCafSender = () => {
	const [sender, setSender] = useState<
		| Sender
		| {
				cast: null
				chrome: null
		  }
	>({
		cast: null,
		chrome: null,
	})

	useEffect(() => {
		load().then((sender) => {
			setSender(sender)
		})
	}, [])

	return sender
}
