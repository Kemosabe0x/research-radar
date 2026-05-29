import { NextResponse } from "next/server";

const API_BASE =
  process.env.NEXT_PUBLIC_RSSAGENT_API_BASE_URL ?? "http://127.0.0.1:8787";

export async function POST(request: Request) {
  const body = await request.json();
  const response = await fetch(`${API_BASE}/api/articles/digest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const payload = await response.json().catch(() => ({ ok: false }));
  return NextResponse.json(payload, { status: response.status });
}
