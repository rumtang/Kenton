import { NextRequest } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, model = 'o3' } = body;

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

    // Create SSE response
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        // Send initial status messages
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({
          type: 'status',
          message: `Initializing Deep Research Agent with ${model}...`
        })}\n\n`));

        await new Promise(resolve => setTimeout(resolve, 500));

        controller.enqueue(encoder.encode(`data: ${JSON.stringify({
          type: 'status',
          message: `🔬 Starting research on: ${query}`
        })}\n\n`));

        // Get root directory for the project
        const projectRoot = path.resolve(process.cwd(), '..');
        
        // Spawn Python process running the main CLI script with poetry
        const pythonProcess = spawn('poetry', [
          'run',
          'python',
          'main.py',
          '--model', model,
          '--query', query
        ], {
          cwd: projectRoot, // Run from the project root directory
          env: {
            ...process.env,
            PYTHONUNBUFFERED: '1' // Ensure Python output is unbuffered
          }
        });

        let isCapturingOutput = false;
        let outputBuffer = '';
        let errorBuffer = '';

        // Process stdout
        pythonProcess.stdout.on('data', (data) => {
          const text = data.toString();
          
          // Look for markers in the output
          if (text.includes('📊 Final Research Report:')) {
            isCapturingOutput = true;
            // Send a status message
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'status',
              message: 'Generating report...'
            })}\n\n`));
            return;
          }
          
          if (isCapturingOutput) {
            // Check if we've reached the end marker
            if (text.includes('='.repeat(20))) {
              // If we have content in the buffer and this is an end marker
              if (outputBuffer && text.trim() === '='.repeat(50)) {
                // Send the content
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                  type: 'content',
                  data: outputBuffer
                })}\n\n`));
                
                // Clear the buffer
                outputBuffer = '';
                
                // Assume we're now at the end
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                  type: 'complete'
                })}\n\n`));
                
                isCapturingOutput = false;
              } else {
                // This might be the start marker or another separator
                // Just add it to the buffer
                outputBuffer += text;
              }
            } else {
              // This is regular content
              outputBuffer += text;
              
              // If we have a substantial amount of content, send it in chunks
              if (outputBuffer.length > 300) {
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                  type: 'content',
                  data: outputBuffer
                })}\n\n`));
                outputBuffer = '';
              }
            }
          } else {
            // Send other output as debug info
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'debug',
              message: text
            })}\n\n`));
          }
        });

        // Process stderr
        pythonProcess.stderr.on('data', (data) => {
          errorBuffer += data.toString();
        });

        // Process exit
        pythonProcess.on('close', (code) => {
          if (code !== 0) {
            // Send any error
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'error',
              message: errorBuffer || `Process exited with code ${code}`
            })}\n\n`));
          }
          
          // Ensure any remaining content is sent
          if (outputBuffer.trim()) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'content',
              data: outputBuffer
            })}\n\n`));
          }
          
          // Always send a complete signal
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({
            type: 'complete'
          })}\n\n`));
          
          controller.close();
        });
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('CLI proxy error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}