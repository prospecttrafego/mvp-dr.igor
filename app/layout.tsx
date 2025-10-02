import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'MVP Instituto Aguiar Neri',
  description: 'Teste do Agente Conversacional',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-white text-slate-900">{children}</body>
    </html>
  );
}
