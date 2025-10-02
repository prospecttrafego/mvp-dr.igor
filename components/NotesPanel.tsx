"use client";
import React, { useState } from 'react';

export default function NotesPanel() {
  const [text, setText] = useState("");
  const [author, setAuthor] = useState("");
  const [info, setInfo] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!text.trim()) return;
    setSaving(true);
    setInfo(null);
    try {
      const resp = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: text, autor: author || undefined })
      });
      const data = await resp.json();
      if (resp.ok) {
        setInfo(`Observação salva. ${data?.saved_to ? 'Arquivo: ' + data.saved_to : ''}`);
        setText("");
      } else {
        setInfo(`Erro ao salvar: ${data?.error || data?.detail || 'desconhecido'}`);
      }
    } catch (e: any) {
      setInfo(`Erro: ${e?.message || 'falha na requisição'}`);
    } finally {
      setSaving(false);
    }
  };

  const clear = () => { setText(""); setAuthor(""); setInfo(null); };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 space-y-2">
        <div className="text-sm text-gray-700">Use este espaço para registrar observações e ajustes a realizar. As notas serão salvas em um documento interno.</div>
        <div className="flex gap-2 items-center">
          <input value={author} onChange={(e)=>setAuthor(e.target.value)} placeholder="Seu nome (opcional)" className="border rounded px-3 py-2 text-sm w-64" />
        </div>
        <textarea
          className="w-full h-64 border rounded p-3 text-sm resize-none"
          placeholder="Descreva aqui o que o agente precisa melhorar ou ajustar."
          value={text}
          onChange={(e)=>setText(e.target.value)}
        />
        <div className="flex gap-2">
          <button onClick={save} disabled={saving} className="bg-blue-600 hover:bg-blue-700 text-white text-sm rounded px-4 py-2 disabled:opacity-60">Salvar</button>
          <button onClick={clear} className="bg-gray-200 hover:bg-gray-300 text-sm rounded px-4 py-2">Limpar</button>
        </div>
        {info && <div className="text-xs text-gray-600">{info}</div>}
      </div>
    </div>
  );
}
