"use client";
// Thin client for the BrokerAssist backend. Creates a session, then sends chat messages.
const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8200";
const WIDGET_KEY = process.env.NEXT_PUBLIC_WIDGET_KEY || "demo-public-key";

let _token = null;

export async function ensureSession() {
  if (_token) return _token;
  const r = await fetch(`${BASE}/api/v1/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ widget_key: WIDGET_KEY }),
  });
  if (!r.ok) throw new Error(`session failed: ${r.status}`);
  _token = (await r.json()).session_token;
  return _token;
}

export async function sendChat(message, language) {
  const token = await ensureSession();
  const r = await fetch(`${BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ message, language }),
  });
  if (!r.ok) throw new Error(`chat failed: ${r.status}`);
  return r.json();
}
