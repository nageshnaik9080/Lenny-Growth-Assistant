"use client";

export type Provider = "ollama" | "anthropic" | "openai";

export default function ModelSelector({
  value,
  onChange,
}: {
  value: Provider;
  onChange: (v: Provider) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-xs">
      <span className="text-zinc-500">Provider</span>
      <select
        aria-label="LLM provider"
        value={value}
        onChange={e => onChange(e.target.value as Provider)}
        className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-zinc-100"
      >
        <option value="ollama">Ollama · Local</option>
        <option value="anthropic">Anthropic · Cloud</option>
        <option value="openai">OpenAI · Cloud</option>
      </select>
    </label>
  );
}
