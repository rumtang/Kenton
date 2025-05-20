// Direct API mode implementation - using the backend API server
// This ensures reliable and fast response streaming
import { NextRequest } from 'next/server';
import { POST as directApiHandler } from './direct-route';

export async function POST(request: NextRequest) {
  // Use the API proxy implementation for consistency and reliability
  return directApiHandler(request);
}