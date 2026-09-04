export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Source = {
  episode: string;
  guest: string;
  timestamp?: string | null;
  score: number;
  text: string;
};

export type Artifact = {
  artifact_type: "markdown" | "html";
  title: string;
  content: string;
};

export async function createSession(title = "Growth session") {
  const r = await fetch(`${API_URL}/api/sessions`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!r.ok) throw new Error("Could not create session");
  return r.json();
}
