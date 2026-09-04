"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Source } from "../../lib/api";

export default function MessageItem({
  role,
  content,
  sources = [],
}: {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}) {
  return (
    <div className={`rounded-2xl border p-4 ${role === "user" ? "ml-8 border-zinc-700 bg-zinc-900" : "mr-8 border-zinc-800 bg-zinc-950"}`}>
      <div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-zinc-500">
        {role === "user" ? "You" : "Lenny Assistant"}
      </div>
      <div className="prose-like text-sm text-zinc-200">
        {role === "assistant" ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        ) : <p>{content}</p>}
      </div>
      {sources.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">Sources</div>
          {sources.map((s, i) => (
            <div key={i} className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-2 text-xs">
              <div className="font-medium text-zinc-300">
                {s.episode} · {s.guest}
                {s.timestamp ? ` · ${s.timestamp}` : ""}
              </div>
              <div className="mt-1 text-zinc-500">Similarity {s.score.toFixed(2)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
