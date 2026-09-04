"use client";

import { useEffect, useState } from "react";
import { createSession } from "../lib/api";
import ChatPane from "../components/Chat/ChatPane";
import ArtifactViewer from "../components/Artifact/ArtifactViewer";

export default function Home() {
  const [sessionId, setSessionId] = useState<string>("");
  const [artifact, setArtifact] = useState<any>(undefined);

  useEffect(() => {
    createSession().then(data => setSessionId(data.id)).catch(console.error);
  }, []);

  if (!sessionId) {
    return <main className="flex min-h-screen items-center justify-center text-sm text-zinc-500">Starting session…</main>;
  }

  return (
    <main className="min-h-screen bg-[#0b0d10]">
      <div className="mx-auto flex min-h-screen max-w-[1800px] flex-col">
        <div className="flex min-h-0 flex-1 flex-col md:flex-row">
          <ChatPane sessionId={sessionId} onArtifact={setArtifact} />
          <ArtifactViewer artifact={artifact} />
        </div>
      </div>
    </main>
  );
}
