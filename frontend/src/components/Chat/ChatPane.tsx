"use client";

import { FormEvent, useEffect, useState } from "react";
import MessageItem from "./MessageItem";
import ModelSelector, { Provider } from "./ModelSelector";
import { useChatStream } from "../../hooks/useChatStream";

export default function ChatPane({ sessionId, onArtifact }: { sessionId: string; onArtifact: (artifact: any) => void }) {
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState<Provider>("ollama");
  const [mode, setMode] = useState<"default" | "ship30">("default");
  const [history, setHistory] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const { state, send } = useChatStream();

  useEffect(() => { if (state.artifact) onArtifact(state.artifact); }, [state.artifact, onArtifact]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const value = input.trim();
    if (!value || state.loading) return;
    setInput("");
    setHistory(h => [...h, { role: "user", content: value }]);
    await send(sessionId, value, mode, provider);
  }

  const visible = [...history];
  if (state.text || state.loading || state.error) {
    visible.push({ role: "assistant", content: state.error ? `Error: ${state.error}` : state.text || "…" });
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 p-4">
        <div>
          <div className="font-semibold">Lenny Growth Assistant</div>
          <div className="text-xs text-zinc-500">Grounded in indexed podcast transcripts</div>
        </div>
        <ModelSelector value={provider} onChange={setProvider} />
      </header>

      <div className="flex items-center gap-2 border-b border-zinc-900 px-4 py-2">
        <button
          onClick={() => setMode("default")}
          className={`rounded-full px-3 py-1 text-xs ${mode === "default" ? "bg-zinc-200 text-black" : "bg-zinc-900 text-zinc-400"}`}
        >Grounded QA</button>
        <button
          onClick={() => setMode("ship30")}
          className={`rounded-full px-3 py-1 text-xs ${mode === "ship30" ? "bg-zinc-200 text-black" : "bg-zinc-900 text-zinc-400"}`}
        >Ship 30 for 30</button>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {visible.length === 0 && (
          <div className="mx-auto mt-16 max-w-lg text-center">
            <h1 className="text-2xl font-semibold">Ask a product or growth question.</h1>
            <p className="mt-3 text-sm text-zinc-500">
              The assistant retrieves transcript evidence first and refuses unsupported questions.
            </p>
          </div>
        )}
        {visible.map((m, i) => (
          <MessageItem key={i} role={m.role} content={m.content} sources={i === visible.length - 1 && m.role === "assistant" ? state.sources : []} />
        ))}
        {state.status && state.loading && <div className="text-xs text-zinc-600">{state.status}</div>}
      </div>

      <form onSubmit={submit} className="border-t border-zinc-800 p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={mode === "ship30" ? "Turn a grounded insight into a ~1,250-word essay…" : "Ask a grounded product/growth question…"}
            rows={3}
            className="min-w-0 flex-1 resize-none rounded-xl border border-zinc-700 bg-zinc-900 p-3 text-sm outline-none focus:border-zinc-400"
          />
          <button
            disabled={state.loading}
            className="self-end rounded-xl bg-white px-4 py-2 text-sm font-semibold text-black disabled:opacity-40"
          >{state.loading ? "…" : "Send"}</button>
        </div>
      </form>
    </section>
  );
}
