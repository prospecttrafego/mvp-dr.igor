"use client";
import React from 'react';

type ModalProps = {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  wide?: boolean;
};

export default function Modal({ open, onClose, title, children, wide }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-0 sm:p-4">
      <div
        className={
          `bg-white ${wide ? 'sm:max-w-5xl' : 'sm:max-w-2xl'} w-full sm:rounded-xl shadow-xl ` +
          `h-[100dvh] sm:h-[90vh] flex flex-col`
        }
      >
        <div className="flex items-center justify-between border-b px-4 py-3">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
