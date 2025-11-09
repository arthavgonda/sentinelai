import { useEffect, useRef, useState } from 'react'

export function useWebSocket(url, onMessage) {
  const [connected, setConnected] = useState(false)
  const ws = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttempts = useRef(0)

  useEffect(() => {
    const connect = () => {
      try {
        const wsUrl = url.startsWith('ws://') || url.startsWith('wss://') 
          ? url 
          : `ws://localhost:8000${url}`
        
        ws.current = new WebSocket(wsUrl)

        ws.current.onopen = () => {
          setConnected(true)
          reconnectAttempts.current = 0
        }

        ws.current.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            onMessage(data)
          } catch (err) {
            console.error('WebSocket message parse error:', err)
          }
        }

        ws.current.onclose = () => {
          setConnected(false)
          if (reconnectAttempts.current < 5) {
            reconnectAttempts.current += 1
            reconnectTimeoutRef.current = setTimeout(() => {
              connect()
            }, 1000 * reconnectAttempts.current)
          }
        }

        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error)
        }
      } catch (err) {
        console.error('WebSocket connection error:', err)
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [url, onMessage])

  return { connected }
}

