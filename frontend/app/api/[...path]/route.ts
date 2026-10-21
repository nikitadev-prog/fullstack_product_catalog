import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function backendBase() {
  return (process.env.API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
}

async function proxy(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const url = `${backendBase()}/${path.join("/")}${req.nextUrl.search}`;
  const headers = new Headers();
  const cookie = req.headers.get("cookie");
  if (cookie) headers.set("cookie", cookie);
  const sessionId = req.headers.get("x-session-id");
  if (sessionId) headers.set("x-session-id", sessionId);
  const contentType = req.headers.get("content-type");
  const hasBody = req.method !== "GET" && req.method !== "HEAD";
  if (contentType && hasBody) headers.set("content-type", contentType);

  const res = await fetch(url, {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
    cache: "no-store",
  });

  const body = await res.arrayBuffer();
  const out = new NextResponse(body.byteLength ? body : null, { status: res.status });
  const type = res.headers.get("content-type");
  if (type) out.headers.set("content-type", type);
  for (const raw of res.headers.getSetCookie()) {
    out.headers.append("set-cookie", raw);
  }
  const responseSession = res.headers.get("x-session-id");
  if (responseSession) out.headers.set("x-session-id", responseSession);
  return out;
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
