"use client";

import { useMemo } from "react";
import DOMPurify from "dompurify";

export default function SandboxedIframe({ content, title }: { content: string; title: string }) {
  const cleanHtml = useMemo(() => DOMPurify.sanitize(content, {
    WHOLE_DOCUMENT: true,
    ADD_TAGS: ["style", "script"],
    FORBID_TAGS: ["iframe", "object", "embed", "form", "base", "meta"],
    FORBID_ATTR: ["srcdoc", "formaction"],
  }), [content]);

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-zinc-800 bg-white">
      <div className="flex items-center justify-between border-b border-zinc-200 bg-zinc-50 px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-zinc-700">Artifact: {title}</span>
        <span className="rounded border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-xs text-emerald-700">Sandboxed Preview</span>
      </div>
      <iframe
        title={title}
        srcDoc={cleanHtml}
        sandbox="allow-scripts"
        className="min-h-0 w-full flex-1 border-0"
      />
    </div>
  );
}
