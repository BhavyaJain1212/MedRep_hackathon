const API_BASE = "/api";

/** POST /api/query — main RAG chat endpoint */
export async function sendQuery(message, mode = "doctor") {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: message, mode }),
  });
  if (!res.ok) throw new Error(`Query failed: ${res.status}`);
  return res.json();
}

/** GET /api/drug/:name — single drug lookup */
export async function getDrug(name) {
  const res = await fetch(`${API_BASE}/drug/${encodeURIComponent(name)}`);
  if (!res.ok) throw new Error(`Drug lookup failed: ${res.status}`);
  return res.json();
}

/** POST /api/interact — interaction check */
export async function checkInteraction(drugA, drugB) {
  const res = await fetch(`${API_BASE}/interact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ drug_a: drugA, drug_b: drugB }),
  });
  if (!res.ok) throw new Error(`Interaction check failed: ${res.status}`);
  return res.json();
}

/** GET /api/health — backend health check */
export async function healthCheck() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

/** POST /api/transcribe — voice-to-text via Whisper */
export async function transcribeAudio(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");

  const res = await fetch(`${API_BASE}/transcribe`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`Transcription failed: ${res.status}`);
  return res.json();
}
