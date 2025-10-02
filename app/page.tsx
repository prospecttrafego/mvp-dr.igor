"use client";
import React, { useState } from 'react';
import Modal from '@/components/Modal';
import ChatWidget from '@/components/ChatWidget';
import NotesPanel from '@/components/NotesPanel';

export default function HomePage() {
  const [openChat, setOpenChat] = useState(false);
  const [openNotes, setOpenNotes] = useState(false);

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 to-slate-50">
      <div className="mx-auto max-w-5xl px-4 py-10">
        <div className="text-center">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-800">MVP Instituto Aguiar Neri - Teste do Agente Conversacional</h1>
          <p className="mt-2 text-slate-600">Abra o chat para testar o agente em tempo real ou anote observações de melhoria.</p>
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
            <button onClick={()=>setOpenChat(true)} className="w-full sm:w-auto rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 text-sm font-medium shadow">
              Abrir Chat (experiência WhatsApp)
            </button>
            <button onClick={()=>setOpenNotes(true)} className="w-full sm:w-auto rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 text-sm font-medium shadow">
              Abrir Observações/Ajustes
            </button>
          </div>
        </div>

        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 bg-white rounded-xl shadow border">
            <h2 className="font-semibold text-slate-800">Como usar</h2>
            <ul className="mt-2 text-sm text-slate-700 list-disc list-inside space-y-1">
              <li>Clique em "Abrir Chat" para conversar com a Agente SDR.</li>
              <li>Use o botão Reset no topo do chat para iniciar uma nova sessão sem memória.</li>
              <li>Teste diferentes objetivos, objeções e contextos.</li>
            </ul>
          </div>
          <div className="p-5 bg-white rounded-xl shadow border">
            <h2 className="font-semibold text-slate-800">Observação</h2>
            <ul className="mt-2 text-sm text-slate-700 list-disc list-inside space-y-1">
              <li>As notas serão salvas em um documento interno.</li>
              <li>Abra "Observações/Ajustes" para registrar melhorias a fazer.</li>
              <li>O desenvolvedor revisará e aplicará correções.</li>
            </ul>
          </div>
        </div>
      </div>

      <Modal open={openChat} onClose={()=>setOpenChat(false)} title="Chat - Alice (Instituto Aguiar Neri)" wide>
        <ChatWidget />
      </Modal>
      <Modal open={openNotes} onClose={()=>setOpenNotes(false)} title="Observações e ajustes">
        <NotesPanel />
      </Modal>
    </main>
  );
}
