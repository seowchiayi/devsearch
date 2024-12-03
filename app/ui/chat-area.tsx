'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/app/ui/button"
import { Input } from "@/app/ui/input"
import { ScrollArea } from "@/app/ui/scroll-area"
import { Send, Upload, Link } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/app/ui/dropdown-menu"

interface Message {
  id: number
  content: string
  sender: 'user' | 'bot'
}

interface ChatAreaProps {
  selectedConversation: string | null
  selectedLLM: string
}

const backend = process.env.NEXT_PUBLIC_VERCEL_URL
  ? `https://${process.env.NEXT_PUBLIC_VERCEL_URL}`
  : "http://localhost:8000";

export function ChatArea({ selectedConversation, selectedLLM }: ChatAreaProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

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
        const response = await fetch(`${backend}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: userMessage.content, llm: selectedLLM }),
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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // TODO: Implement file upload logic
      console.log('File uploaded:', file.name)
    }
  }

  const handleUrlUpload = async () => {
    const url = prompt('Enter the URL:', 'https://github.com/seowchiayi/devsearch/blob/b8fe1e0378a19976fc941d4eb08167e23143afcd/README.md')
    if (url) {
      const userMessage: Message = {
        id: Date.now(),
        content: `${url}`,
        sender: 'user'
      }
      setMessages(prevMessages => [...prevMessages, userMessage])
      setInputValue('')
      setIsLoading(true)

      try {
        const response = await fetch(`${backend}/url`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: userMessage.content, llm: selectedLLM }),
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
    <div className="flex-1 flex flex-col">
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`p-2 rounded-lg max-w-[80%] ${
                  message.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="p-2 rounded-lg bg-secondary">
                Thinking...
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="p-4 border-t">
        <div className="flex space-x-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon">
                <Upload className="h-4 w-4" />
                <span className="sr-only">Upload options</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onSelect={() => fileInputRef.current?.click()}>
                <Upload className="mr-2 h-4 w-4" />
                <span>Upload File</span>
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={handleUrlUpload}>
                <Link className="mr-2 h-4 w-4" />
                <span>Upload URL</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={`Ask about internal documentation (using ${selectedLLM})...`}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isLoading}
            className="flex-grow"
          />
          <Button onClick={handleSendMessage} disabled={isLoading}>
            <Send className="h-4 w-4" />
            <span className="sr-only">Send</span>
          </Button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            aria-label="Upload file"
          />
        </div>
      </div>
    </div>
  )
}
