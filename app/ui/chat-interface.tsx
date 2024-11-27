'use client'

import { useState } from 'react'
import { Button } from "@/app/ui/button"
import { Input } from "@/app/ui/input"
import { ScrollArea } from "@/app/ui/scroll-area"
import { Send } from 'lucide-react'

interface Message {
  id: number
  content: string
  sender: 'user' | 'bot'
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async () => {
    if (inputValue.trim()) {
      const userMessage: Message = {
        id: Date.now(),
        content: inputValue,
        sender: 'user'
      }
      setMessages(prevMessages => [...prevMessages, userMessage])
      setInputValue('')
      setIsLoading(true)

      try {
        const response = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: userMessage.content }),
        })

        if (!response.ok) {
          throw new Error('Failed to get response from server')
        }

        const data = await response.json()
        const botMessage: Message = {
          id: Date.now(),
          content: data.response,
          sender: 'bot'
        }
        setMessages(prevMessages => [...prevMessages, botMessage])
      } catch (error) {
        console.error('Error:', error)
        const errorMessage: Message = {
          id: Date.now(),
          content: 'Sorry, there was an error processing your request.',
          sender: 'bot'
        }
        setMessages(prevMessages => [...prevMessages, errorMessage])
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="flex flex-col h-full">
      <ScrollArea className="flex-grow p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`p-4 rounded-lg ${
              message.sender === 'user' ? 'bg-primary text-primary-foreground ml-auto' : 'bg-muted'
            } max-w-[80%]`}
          >
            {message.content}
          </div>
        ))}
        {isLoading && (
          <div className="p-4 rounded-lg bg-muted max-w-[80%]">
            Thinking...
          </div>
        )}
      </ScrollArea>
      <div className="p-4 border-t">
        <div className="flex space-x-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about internal documentation..."
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isLoading}
            className="flex-grow"
          />
          <Button onClick={handleSendMessage} disabled={isLoading}>
            <Send className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
        </div>
      </div>
    </div>
  )
}
