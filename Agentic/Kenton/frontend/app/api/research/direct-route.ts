// Direct API proxy to the backend server
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, model = 'gpt-4.1', sessionId, includeIntelligence = true } = body;

    if (!query || typeof query !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Query is required' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }

    // Forward the request to the backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8001/api/research';
    console.log(`Sending request to backend: ${backendUrl}`);
    console.log(`Session ID: ${sessionId}, Model: ${model}`);
    
    // Add timeout to avoid hanging forever
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      // Create a streaming response that proxies the backend
      const backendResponse = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, model, sessionId, includeIntelligence }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!backendResponse.ok) {
        console.error(`Backend returned error: ${backendResponse.status} ${backendResponse.statusText}`);
        throw new Error(`Backend error: ${backendResponse.status}`);
      }
      
      // Return the streaming response directly from the backend
      return new Response(backendResponse.body, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    } catch (fetchError) {
      console.error('Backend fetch error:', fetchError);
      return new Response(
        JSON.stringify({ 
          error: 'Failed to connect to backend server', 
          details: fetchError instanceof Error ? fetchError.message : String(fetchError) 
        }),
        {
          status: 502,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }
  } catch (error) {
    console.error('API proxy error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : String(error)
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}