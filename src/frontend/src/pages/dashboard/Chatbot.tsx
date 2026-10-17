/**
 * AI Chatbot page. Each question is sent on its own (stateless, D-033);
 * the server personalises answers from the stored user document.
 */
import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { queryChatbot } from '../../services/api';
import MarkdownMessage from '../../components/MarkdownMessage';

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
}

const MAX_QUESTION = 1000;

const bubbleClasses = {
  user: 'bg-accent text-white ml-auto',
  assistant: 'bg-secondary border border-gray-700 mr-auto',
};

export default function Chatbot() {
  const nextId = useRef(2);
  const listRef = useRef<HTMLDivElement | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: 'assistant',
      content:
        'Hi! I can explain your AI risk, suggest how to improve your career outlook, or answer questions about the jobs and courses data. English and Hindi both work.',
    },
  ]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState(false);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, pending]);

  const canSend = input.trim() !== '' && !pending;

  const send = async (e: FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (question === '' || pending) return;
    const userMsg: ChatMessage = { id: nextId.current++, role: 'user', content: question };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setPending(true);
    let reply: string;
    try {
      reply = await queryChatbot(question);
    } catch (err) {
      reply = `Error: ${err instanceof Error ? err.message : 'Unknown error'}`;
    }
    setMessages((m) => [...m, { id: nextId.current++, role: 'assistant', content: reply }]);
    setPending(false);
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">AI Chatbot</h1>
      <div className="card flex flex-col h-[70vh]">
        <div ref={listRef} className="flex-1 overflow-y-auto space-y-3 pr-2" aria-live="polite">
          {messages.map((m) => (
            <div key={m.id} className={`max-w-[85%] rounded-lg px-4 py-2 ${bubbleClasses[m.role]}`}>
              {m.role === 'assistant' ? <MarkdownMessage text={m.content} /> : <p className="whitespace-pre-wrap">{m.content}</p>}
            </div>
          ))}
          {pending && (
            <div className="max-w-[85%] rounded-lg px-4 py-2 bg-secondary border border-gray-700 text-textSecondary">
              Thinking...
            </div>
          )}
        </div>
        <form onSubmit={send} className="mt-4 flex gap-3">
          <input
            aria-label="Your question"
            className="input-field"
            value={input}
            maxLength={MAX_QUESTION}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your risk, learning paths, or the job data"
          />
          <button type="submit" className="btn-primary" disabled={!canSend}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
