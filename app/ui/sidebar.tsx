import { useState } from 'react'
import { Button } from "@/app/ui/button"
import { ScrollArea } from "@/app/ui/scroll-area"
import { PlusCircle } from 'lucide-react'

interface SidebarProps {
  selectedConversation: string | null
  onSelectConversation: (id: string) => void
}

export function Sidebar({ selectedConversation, onSelectConversation }: SidebarProps) {
  const [conversations, setConversations] = useState<string[]>(['New chat'])

  const addNewConversation = () => {
    const newConversation = `New chat ${conversations.length}`
    setConversations([...conversations, newConversation])
    onSelectConversation(newConversation)
  }

  return (
    <div className="w-64 bg-secondary h-full flex flex-col">
      <div className="p-4">
        <Button 
          variant="outline" 
          className="w-full justify-start"
          onClick={addNewConversation}
        >
          <PlusCircle className="mr-2 h-4 w-4" />
          New chat
        </Button>
      </div>
      <ScrollArea className="flex-grow">
        <div className="p-2 space-y-2">
          {conversations.map((conversation) => (
            <Button
              key={conversation}
              variant="ghost"
              className={`w-full justify-start ${selectedConversation === conversation ? 'bg-accent' : ''}`}
              onClick={() => onSelectConversation(conversation)}
            >
              {conversation}
            </Button>
          ))}
        </div>
      </ScrollArea>
    </div>
  )
}
