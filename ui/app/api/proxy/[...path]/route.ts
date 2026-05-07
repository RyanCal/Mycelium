import { NextRequest, NextResponse } from 'next/server';

const apiBaseUrl = process.env.MYCELIUM_API_BASE_URL ?? 'http://localhost:8000';
const adminToken = process.env.MYCELIUM_ADMIN_TOKEN ?? 'change-me';

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const target = new URL(path.join('/'), apiBaseUrl);
  target.search = request.nextUrl.search;

  const response = await fetch(target, {
    method: request.method,
    headers: {
      Authorization: `Bearer ${adminToken}`,
      'Content-Type': request.headers.get('content-type') ?? 'application/json',
    },
    body: request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.text(),
    cache: 'no-store',
  });

  return new NextResponse(response.body, {
    status: response.status,
    headers: response.headers,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
