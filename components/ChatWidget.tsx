"use client";
import React, { useEffect, useMemo, useRef, useState } from 'react';

type Msg = { role: 'user' | 'assistant'; content: string; meta?: any };

function uuid() { return (globalThis.crypto?.randomUUID?.() || Math.random().toString(36).slice(2)); }

export default function ChatWidget() {
  const [sessionId, setSessionId] = useState<string>(uuid());
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollerRef = useRef<HTMLDivElement>(null);
  const bufferRef = useRef<string[]>([]);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const flushingRef = useRef(false);
  const HOLD_MS = 1800;

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight });
  }, [messages]);

  const header = useMemo(() => ({ name: 'Alice', subtitle: 'Instituto Aguiar Neri' }), []);

  const reset = () => {
    setSessionId(uuid());
    setMessages([]);
    bufferRef.current = [];
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  };

  const scheduleFlush = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    timerRef.current = setTimeout(() => {
      timerRef.current = null;
      void flushBuffer();
    }, HOLD_MS);
  };

  const flushBuffer = async () => {
    if (flushingRef.current || bufferRef.current.length === 0) return;
    const payload = bufferRef.current.join('\n');
    bufferRef.current = [];
    flushingRef.current = true;
    setSending(true);
    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          mensagem: payload
        })
      });
      const data = await resp.json();
      const parts: string[] | undefined = Array.isArray(data?.parts) ? data.parts : undefined;
      if (parts && parts.length > 0) {
        setMessages((m) => [
          ...m,
          ...parts.map((p) => ({ role: 'assistant', content: p, meta: { score: data?.score, decisao: data?.decisao } } as Msg)),
        ]);
      } else {
        const assistantText = data?.text || data?.resposta || 'Sem resposta.';
        setMessages((m) => [...m, { role: 'assistant', content: assistantText, meta: { score: data?.score, decisao: data?.decisao } }]);
      }
    } catch (e: any) {
      setMessages((m) => [...m, { role: 'assistant', content: `Erro: ${e?.message || 'falha ao enviar'}` }]);
      bufferRef.current.unshift(payload);
      if (!timerRef.current) {
        scheduleFlush();
      }
    } finally {
      setSending(false);
      flushingRef.current = false;
      if (bufferRef.current.length > 0 && !timerRef.current) {
        scheduleFlush();
      }
    }
  };

  const send = () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: 'user', content: userMsg }]);
    bufferRef.current.push(userMsg);
    scheduleFlush();
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header estilo WhatsApp */}
      <div className="bg-emerald-600 text-white px-4 py-3 flex items-center justify-between">
        <div>
          <div className="font-semibold">{header.name}</div>
          <div className="text-xs opacity-90">{header.subtitle}</div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={reset} className="text-xs bg-white/20 hover:bg-white/30 rounded px-2 py-1">Reset</button>
          <span className="text-xs opacity-90">Sessão: {sessionId.slice(0,6)}</span>
        </div>
      </div>

      {/* Mensagens */}
      <div ref={scrollerRef} className="flex-1 overflow-auto bg-[#e5ddd5] p-3 space-y-2">
        {messages.length === 0 && (
          <div className="space-y-4">
            <div className="text-center text-sm text-gray-600 mt-6">Envie uma mensagem para iniciar o teste ou use um dos atalhos:</div>
            <div className="flex flex-col sm:flex-row gap-2 sm:justify-center">
              <button
                onClick={() => setInput('Olá! Tenho interesse e queria mais informações, por favor.')}
                className="bg-white hover:bg-gray-50 text-gray-800 border rounded-full px-4 py-2 text-xs shadow"
              >Olá! Tenho interesse e queria mais informações, por favor.</button>
              <button
                onClick={() => setInput('Olá! Vim pelo anúncio e queria marcar uma consulta.')}
                className="bg-white hover:bg-gray-50 text-gray-800 border rounded-full px-4 py-2 text-xs shadow"
              >Olá! Vim pelo anúncio e queria marcar uma consulta.</button>
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`${msg.role === 'user' ? 'bg-[#dcf8c6]' : 'bg-white'} max-w-[80%] rounded-lg px-3 py-2 shadow text-sm`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.meta?.decisao && (
                <div className="mt-2 flex items-center gap-2 text-[10px] text-gray-500">
                  <span className="bg-gray-100 rounded px-1 py-0.5">
                    Score: {msg.meta.score}/10
                  </span>
                  <span className={`rounded px-1 py-0.5 font-medium ${
                    msg.meta.decisao?.acao === 'transferir_humano' ? 'bg-green-100 text-green-700' :
                    msg.meta.decisao?.acao === 'agendar_preliminar' ? 'bg-blue-100 text-blue-700' :
                    msg.meta.decisao?.acao === 'continuar_conversa' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {msg.meta.decisao?.acao === 'transferir_humano' ? '→ Transferir' :
                     msg.meta.decisao?.acao === 'agendar_preliminar' ? '📅 Agendar' :
                     msg.meta.decisao?.acao === 'continuar_conversa' ? '💬 Conversar' :
                     msg.meta.decisao?.acao}
                  </span>
                  {msg.meta.decisao?.prioridade && (
                    <span className={`rounded px-1 py-0.5 text-[9px] ${
                      msg.meta.decisao.prioridade === 'alta' ? 'bg-red-100 text-red-600' :
                      msg.meta.decisao.prioridade === 'media' ? 'bg-orange-100 text-orange-600' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {msg.meta.decisao.prioridade}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Indicador de typing quando enviando */}
        {sending && (
          <div className="flex justify-start mb-2">
            <div className="bg-white max-w-[80%] rounded-lg px-3 py-2 shadow text-sm">
              <div className="flex items-center gap-1">
                <span className="text-gray-500">Alice está digitando</span>
                <div className="flex gap-1">
                  <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t p-2 bg-[#f0f0f0]">
        <div className="flex items-center gap-2">
          <input
            className={`flex-1 rounded-full border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 ${
              sending ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
            }`}
            placeholder={sending ? "Aguarde a resposta..." : "Digite sua mensagem..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !sending) send(); }}
            disabled={sending}
          />
          <button
            onClick={send}
            disabled={sending || !input.trim()}
            className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              sending || !input.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-emerald-600 hover:bg-emerald-700 text-white'
            }`}
          >
            {sending ? '...' : 'Enviar'}
          </button>
        </div>
      </div>
    </div>
  );
}
