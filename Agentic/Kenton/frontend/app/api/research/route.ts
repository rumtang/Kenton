// Direct CLI mode implementation - using the same CLI agent
// This ensures identical behavior between CLI and web interface
import { NextRequest } from 'next/server';
import { POST as directCliHandler } from './cli-route';

export async function POST(request: NextRequest) {
  // Directly use the CLI implementation for consistency
  return directCliHandler(request);
}