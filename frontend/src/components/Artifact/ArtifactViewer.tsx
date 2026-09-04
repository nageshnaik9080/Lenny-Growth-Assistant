"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SandboxedIframe from "./SandboxedIframe";
import { Artifact } from "../../lib/api";

export default function ArtifactViewer({ artifact }: { artifact?: Artifact }) {
  if (!artifact) {
    return (
      <aside className="flex min-h-0 flex-1 items-center justify-center border-l border-zinc-800 bg-zinc-950 p-8 text-center">
        <div>
          <div className="text-sm font-medium text-zinc-400">No artifact yet</div>
          <div className="mt-2 text-xs text-zinc-600">Use Ship 30 for 30 mode to generate a preview.</div>
        </div>
      </aside>
    );
  }

  return (
    <aside className="flex min-h-0 flex-1 flex-col border-l border-zinc-800 bg-zinc-950 p-3">
      {artifact.artifact_type === "html" ? (
        <SandboxedIframe content={artifact.content} title={artifact.title} />
      ) : (
        <div className="min-h-0 flex-1 overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900 p-6">
          <div className="mb-5 text-xs font-semibold uppercase tracking-wider text-zinc-500">{artifact.title}</div>
          <div className="prose-like text-zinc-200">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.content}</ReactMarkdown>
          </div>
        </div>
      )}
    </aside>
  );
}
