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
          console.log(`CLI Output: "${text}"`); // Debug log
          
          // Look for markers in the output
          if (text.includes('📊 Final Research Report:')) {
            isCapturingOutput = true;
            // Send a status message
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'status',
              message: 'Generating report...'
            })}\n\n`));
            
            // Create a mock report for testing
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'content',
              data: "Sample report content to test if display works correctly."
            })}\n\n`));
            
            return;
          }
          
          // Special case for the successful completion message
          if (text.includes('✅ Research complete!')) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'complete'
            })}\n\n`));
            return;
          }
          
          if (isCapturingOutput) {
            // Check if we've reached the end marker
            if (text.includes('='.repeat(20))) {
              // This is likely the separator line
              // Don't add this to the content, but send what we have
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                type: 'content',
                data: outputBuffer
              })}\n\n`));
              outputBuffer = '';
              
              // If this is the end marker, we're done
              if (text.includes('='.repeat(50))) {
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                  type: 'complete'
                })}\n\n`));
                isCapturingOutput = false;
              }
            } else {
              // This is regular content
              outputBuffer += text;
              
              // Send content more frequently in smaller chunks
              if (outputBuffer.length > 100) {
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