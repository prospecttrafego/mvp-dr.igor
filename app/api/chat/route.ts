import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const apiBase = process.env.API_BASE_URL;
    
    // Debug logs
    console.log('API_BASE_URL:', apiBase);
    console.log('Request body:', JSON.stringify(body));
    
    if (!apiBase) {
      console.error('API_BASE_URL não configurada');
      return NextResponse.json({ error: 'API_BASE_URL não configurada' }, { status: 500 });
    }

    const url = `${apiBase}/webhook/dr-igor`;
    console.log('Calling URL:', url);

    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    console.log('Response status:', resp.status);
    console.log('Response headers:', Object.fromEntries(resp.headers.entries()));

    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('Response error:', errorText);
      return NextResponse.json({ error: `Backend error: ${errorText}` }, { status: resp.status });
    }

    const data = await resp.json();
    console.log('Response data:', JSON.stringify(data));
    
    return NextResponse.json(data, { status: resp.status });
  } catch (err: any) {
    console.error('Proxy error:', err);
    return NextResponse.json({ 
      error: err?.message || 'Erro interno do servidor',
      details: err?.stack || 'Sem detalhes'
    }, { status: 500 });
  }
}

