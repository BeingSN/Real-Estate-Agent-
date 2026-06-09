import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import { API_BASE_URL } from './config'

export default function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = async (text) => {
    if (!text.trim() || isLoading) return

    setMessages((prev) => [...prev, { role: 'user', content: text.trim() }])
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text.trim() }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from server')
      }

      const data = await response.json()

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.assistant_message,
          recommendations: data.recommendations || [],
          extractedCriteria: data.extracted_criteria,
        },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'Sorry, something went wrong connecting to the server. Please make sure the backend is running on port 8000.',
          recommendations: [],
          extractedCriteria: null,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ChatWindow
      messages={messages}
      isLoading={isLoading}
      onSendMessage={sendMessage}
    />
  )
}
