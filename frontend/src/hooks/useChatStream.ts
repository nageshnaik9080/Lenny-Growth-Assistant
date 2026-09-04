"use client";

import { useCallback, useState } from "react";
import { API_URL, Artifact, Source } from "../lib/api";

type StreamState = {
  text: string;
  sources: Source[];
  artifact?: Artifact;
  status?: string;
  error?: string;
  loading: boolean;
};

export function useChatStream() {
  const [state, setState] = useState<StreamState>({
    text: "",
    sources: [],
    loading: false,
  });

  const send = useCallback(async (
    sessionId: string,
    message: string,
    mode: "default" | "ship30",
    provider: "ollama" | "anthropic" | "openai",
  ) => {
    setState({ text: "", sources: [], loading: true });
    const response = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message, mode, provider }),
    });

    if (!response.ok || !response.body) {
      setState(s => ({ ...s, loading: false, error: "Chat request failed" }));
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";

      for (const event of events) {
        const line = event.split("\n").find(x => x.startsWith("data: "));
        if (!line) continue;
        const raw = line.slice(6);
        try {
          const data = JSON.parse(raw);
          if (data.type === "status") setState(s => ({ ...s, status: data.content }));
          if (data.type === "sources") setState(s => ({ ...s, sources: data.sources }));
          if (data.type === "token") setState(s => ({ ...s, text: s.text + data.content }));
          if (data.type === "artifact") setState(s => ({ ...s, artifact: data.artifact }));
          if (data.type === "error") setState(s => ({ ...s, error: data.content }));
        } catch {
          // Ignore malformed/incomplete SSE frames.
        }
      }
    }
    setState(s => ({ ...s, loading: false }));
  }, []);

  return { state, send };
}
