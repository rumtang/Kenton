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
        
        // Spawn Python process running the test script directly
        const pythonProcess = spawn('python3', [
          'test_dummy.py',
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
            
            // We're starting to see the report output
            console.log("Found report marker, starting content capture");
            
            // Start capturing with this text
            outputBuffer = text;
            return;
          }
          
          // Special case for the successful completion message
          if (text.includes('✅ Research complete!') && !isCapturingOutput) {
            // Add this to the output buffer if we're not already capturing
            outputBuffer += text;
            
            // Send the completion message
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'content',
              data: outputBuffer
            })}\n\n`));
            
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'complete'
            })}\n\n`));
            
            outputBuffer = '';
            return;
          }
          
          if (isCapturingOutput) {
            // Check if we've reached the end marker (==== separator)
            if (text.includes('='.repeat(20))) {
              // Include the separator line in the content
              outputBuffer += text;
              console.log("Found end marker, sending content");
              
              // Send the accumulated content
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                type: 'content',
                data: outputBuffer
              })}\n\n`));
              
              // Reset the buffer
              outputBuffer = '';
              
              // If this is the final end marker, we're done
              if (text.trim() === '==================================================') {
                console.log("Found final end marker, sending completion");
                controller.enqueue(encoder.encode(`data: ${JSON.stringify({
                  type: 'complete'
                })}\n\n`));
                isCapturingOutput = false;
              }
            } else {
              // This is regular content
              outputBuffer += text;
              
              // Send content in smaller chunks but not too small
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
          console.log(`Python process exited with code ${code}`);
          console.log(`Final output buffer (${outputBuffer.length} chars):`, outputBuffer.substring(0, 100) + '...');
          
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
          
          // Always send a complete signal if we haven't already
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