import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const API_BASE = import.meta.env.VITE_SKILLS_RUNNER_API || 'http://localhost:8003'

// --- Icons ---

const BotIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-emerald-600" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
  </svg>
)

const UserIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6 text-slate-500" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
    <circle cx="8.5" cy="7" r="4" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M20 8v6M23 11h-6" />
  </svg>
)

const SendIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
  </svg>
)

const StopIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2">
    <rect x="6" y="6" width="12" height="12" rx="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const PlusIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
)

const TrashIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
)

const ChatIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
  </svg>
)

const ToolIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" />
  </svg>
)

// --- Constants & Logic ---

const starterMessages = [
  {
    role: 'assistant',
    content: 'Hi! I’m your Skills Runner assistant. How can I help you today?',
  },
]

const storageKey = 'skillsRunnerChatRooms'

const createRoom = (title = 'New Chat') => ({
  id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
  title,
  messages: starterMessages,
  createdAt: Date.now(),
})

function App() {
  const [rooms, setRooms] = useState(() => {
    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed
        }
      }
    } catch {
      // Ignore
    }
    return [createRoom()]
  })
  
  const [activeRoomId, setActiveRoomId] = useState(() => {
    const firstRoom = rooms[0]
    return firstRoom ? firstRoom.id : null
  })
  
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [error, setError] = useState('')
  
  const streamIndexRef = useRef(null)
  const abortRef = useRef(null)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  const activeRoom = rooms.find((room) => room.id === activeRoomId) || rooms[0]
  const messages = activeRoom?.messages || []

  // Auto-scroll logic
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Persistence logic
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(rooms))
    } catch (e) {
      console.error('Failed to save rooms', e)
    }
  }, [rooms])

  // Select fallback room logic
  useEffect(() => {
    if (!activeRoom && rooms.length > 0) {
      setActiveRoomId(rooms[0].id)
    }
  }, [activeRoom, rooms])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 192) + 'px'
    }
  }, [input])

  const updateActiveMessages = (updater) => {
    setRooms((prev) =>
      prev.map((room) => {
        if (room.id !== activeRoomId) return room
        const nextMessages = typeof updater === 'function' ? updater(room.messages) : updater
        
        // Update title based on first user message if it's "New Chat" and we have a user msg
        let nextTitle = room.title
        if (room.title === 'New Chat' || room.title.startsWith('New chat')) {
           const firstUserMsg = nextMessages.find(m => m.role === 'user')
           if (firstUserMsg) {
             const cleanContent = firstUserMsg.content.slice(0, 30).replace(/\n/g, ' ')
             nextTitle = cleanContent + (firstUserMsg.content.length > 30 ? '...' : '')
           }
        }
        
        return { ...room, title: nextTitle, messages: nextMessages }
      })
    )
  }

  const updateLastAssistant = (delta) => {
    updateActiveMessages((prev) => {
      const next = [...prev]
      if (streamIndexRef.current === null || !next[streamIndexRef.current]) {
        // Look for the last assistant message after any trailing tool messages
        // so we continue appending instead of creating a split bubble
        let lastAssistantIdx = null
        for (let i = next.length - 1; i >= 0; i--) {
          if (next[i].role === 'assistant') { lastAssistantIdx = i; break }
          if (next[i].role === 'user') break
        }
        if (lastAssistantIdx !== null) {
          streamIndexRef.current = lastAssistantIdx
          next[lastAssistantIdx] = { ...next[lastAssistantIdx], content: `${next[lastAssistantIdx].content}${delta}` }
          return next
        }
        next.push({ role: 'assistant', content: delta })
        streamIndexRef.current = next.length - 1
        return next
      }
      const idx = streamIndexRef.current
      next[idx] = { ...next[idx], content: `${next[idx].content}${delta}` }
      return next
    })
  }

  const pushToolEvent = (phase, toolCall, result) => {
    const name = toolCall?.function?.name || 'tool'
    const args = toolCall?.function?.arguments || '{}'
    updateActiveMessages((prev) => [
      ...prev,
      {
        role: 'tool',
        phase,
        toolName: name,
        args,
        result,
      },
    ])
    streamIndexRef.current = null
  }

  const handleSubmit = async () => {
    const trimmed = input.trim()
    if (!trimmed || isStreaming) {
      return
    }

    setError('')
    setIsStreaming(true)
    abortRef.current = new AbortController()

    const nextMessages = [...messages, { role: 'user', content: trimmed }]
    streamIndexRef.current = null
    updateActiveMessages(nextMessages)
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    const payloadMessages = nextMessages.filter((message) => message.role !== 'tool')

    try {
      const response = await fetch(`${API_BASE}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'qwen/qwen3-next-80b',
          stream: true,
          messages: payloadMessages,
        }),
        signal: abortRef.current.signal,
      })

      if (!response.ok || !response.body) {
        throw new Error('Chat API request failed')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const normalized = buffer.replace(/\r\n/g, '\n')
        const parts = normalized.split('\n\n')
        buffer = parts.pop() || ''

        for (const part of parts) {
          const line = part.split('\n').find((item) => item.startsWith('data: '))
          if (!line) {
            continue
          }

          const data = line.replace('data: ', '').trim()
          if (data === '[DONE]') {
            break
          }

          try {
            const payload = JSON.parse(data)

            if (payload?.type === 'tool') {
              pushToolEvent(payload.phase || 'end', payload.tool_call, payload.result)
              continue
            }

            if (payload?.type === 'error') {
              setError(payload.message || 'Chat stream error')
              continue
            }

            const delta = payload?.choices?.[0]?.delta?.content
            if (delta) {
              updateLastAssistant(delta)
            }
          } catch (e) {
            console.warn('Failed to parse SSE data', data)
          }
        }
      }
    } catch (err) {
      if (err?.name !== 'AbortError') {
        setError('Unable to reach the Skills Runner API. Check that the server is running.')
      }
    } finally {
      setIsStreaming(false)
      abortRef.current = null
      streamIndexRef.current = null
    }
  }

  const handleStop = () => {
    abortRef.current?.abort()
  }

  const handleNewRoom = () => {
    const room = createRoom()
    setRooms((prev) => [room, ...prev])
    setActiveRoomId(room.id)
  }

  const handleDeleteRoom = (e, id) => {
    e.stopPropagation()
    const remaining = rooms.filter((room) => room.id !== id)
    if (remaining.length === 0) {
      const room = createRoom()
      setRooms([room])
      setActiveRoomId(room.id)
      return
    }
    setRooms(remaining)
    if (activeRoomId === id) {
      setActiveRoomId(remaining[0].id)
    }
  }

  const onKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-white text-slate-900" data-theme="light">
      {/* Sidebar - Desktop */}
      <div className="hidden w-[280px] flex-col border-r border-slate-200 bg-slate-50/50 md:flex">
        <div className="p-3">
          <button
            onClick={handleNewRoom}
            className="flex w-full items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 hover:text-slate-900"
          >
            <PlusIcon />
            <span>New Chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-2 py-2">
          {rooms.length > 0 && (
            <div className="flex flex-col gap-1">
              <span className="px-2 pb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">History</span>
              {rooms.map((room) => (
                <div
                  key={room.id}
                  onClick={() => setActiveRoomId(room.id)}
                  className={`group relative flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all ${
                    activeRoomId === room.id
                      ? 'bg-slate-200/60 font-medium text-slate-900'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <ChatIcon />
                  <span className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap">{room.title}</span>
                  {/* Delete button (only visible on hover or active) */}
                  <button
                    onClick={(e) => handleDeleteRoom(e, room.id)}
                    className={`absolute right-2 rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-500 hover:opacity-100 ${
                      activeRoomId === room.id ? 'opacity-0 group-hover:opacity-100' : 'opacity-0 group-hover:opacity-100'
                    }`}
                    title="Delete chat"
                  >
                    <TrashIcon />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="border-t border-slate-200 p-4">
          <div className="flex items-center gap-3">
             <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
               <span className="text-xs font-bold">U</span>
             </div>
             <div className="flex flex-col">
               <span className="text-sm font-medium text-slate-700">Guest User</span>
               <span className="text-[10px] text-slate-400">Local Session</span>
             </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col relative bg-white">
        {/* Mobile Header (only visible on small screens) */}
        <header className="flex h-14 items-center justify-between border-b border-slate-100 px-4 md:hidden">
            <span className="font-bold text-slate-800">Skills Runner</span>
            <div className="text-[10px] uppercase tracking-wider text-slate-400">
              Qwen3-Next
            </div>
        </header>

        {/* Desktop Header */}
        <header className="hidden h-14 items-center justify-between border-b border-transparent bg-white/80 px-6 backdrop-blur md:flex z-10 absolute top-0 w-full">
           <div className="flex items-center gap-2">
             <span className="text-sm font-semibold text-slate-500">{activeRoom?.title}</span>
           </div>
           <div className="flex items-center gap-1.5 rounded-full border border-slate-100 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-500">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Qwen 80B
           </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto chat-scroll md:pt-14 pb-32">
          <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-6 md:py-10">
            {messages.map((message, index) => {
              // Tool Message
              if (message.role === 'tool') {
                return (
                  <div key={index} className="flex gap-4 pl-0 md:pl-12">
                     <div className="w-full overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-100/50 px-4 py-2">
                           <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                              <ToolIcon />
                              <span>{message.phase === 'start' ? 'Running Tool...' : 'Tool Output'}</span>
                           </div>
                           <span className="font-mono text-[10px] text-slate-500">{message.toolName}</span>
                        </div>
                        <div className="p-3 text-xs font-mono text-slate-600 overflow-x-auto">
                           {message.phase === 'start' ? (
                              <div className="opacity-80">Input: {message.args}</div>
                           ) : (
                              <pre className="whitespace-pre-wrap">{JSON.stringify(message.result, null, 2)}</pre>
                           )}
                        </div>
                     </div>
                  </div>
                )
              }
              
              const isUser = message.role === 'user'
              return (
                <div key={index} className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* Avatar */}
                  <div className={`mt-1 flex h-8 w-8 flex-none items-center justify-center rounded-full border shadow-sm ${
                    isUser 
                      ? 'bg-white border-slate-100' 
                      : 'bg-emerald-50 border-emerald-100 text-emerald-600'
                  }`}>
                    {isUser ? <UserIcon /> : <BotIcon />}
                  </div>
                  
                  {/* Bubble */}
                  <div className={`relative max-w-[85%] rounded-2xl px-5 py-3.5 shadow-sm text-[15px] leading-relaxed ${
                    isUser 
                      ? 'bg-slate-900 text-slate-50' 
                      : 'bg-white border border-slate-100 text-slate-700'
                  }`}>
                    <div className="markdown" style={{ color: isUser ? '#f8fafc' : undefined }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              )
            })}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Input Dock */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white to-transparent pt-12 pb-6 px-4">
          <div className="mx-auto w-full max-w-3xl">
            {error && (
              <div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-2 text-center text-xs text-red-600">
                {error}
              </div>
            )}
            
            <div className="group relative flex items-end gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-xl shadow-slate-200/40 ring-1 ring-slate-200/50 focus-within:ring-emerald-500/20 focus-within:border-emerald-500/50 transition-all">
              <textarea
                ref={textareaRef}
                className="max-h-[200px] flex-1 resize-none bg-transparent px-3 py-3 text-slate-700 placeholder:text-slate-400 focus:outline-none"
                placeholder="Send a message..."
                rows={1}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKeyDown}
                disabled={isStreaming}
              />
              <button 
                onClick={isStreaming ? handleStop : handleSubmit}
                className={`flex h-10 w-10 flex-none items-center justify-center rounded-xl transition-all ${
                   input.trim() || isStreaming
                    ? 'bg-slate-900 text-white hover:bg-slate-800 hover:scale-105 active:scale-95'
                    : 'bg-slate-100 text-slate-300 cursor-not-allowed'
                }`}
                disabled={!input.trim() && !isStreaming}
              >
                {isStreaming ? <StopIcon /> : <SendIcon />}
              </button>
            </div>
            <div className="mt-2 text-center text-[11px] text-slate-400">
              AI-generated content may be incorrect.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
