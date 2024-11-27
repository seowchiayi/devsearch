'use client'

import { useState } from 'react'
import { Sidebar } from '@/app/ui/sidebar'
import { ChatArea } from '@/app/ui/chat-area'
import { Header } from '@/app/ui/header'

export default function Home() {
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [selectedLLM, setSelectedLLM] = useState('openai')

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header 
        toggleSidebar={toggleSidebar}
        selectedLLM={selectedLLM}
        setSelectedLLM={setSelectedLLM}
      />
      <div className="flex flex-1 overflow-hidden">
        {isSidebarOpen && (
          <Sidebar 
            selectedConversation={selectedConversation}
            onSelectConversation={setSelectedConversation}
          />
        )}
        <ChatArea 
          selectedConversation={selectedConversation}
          selectedLLM={selectedLLM}
        />
      </div>
    </div>
  )
}
