"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

export function ArticleActions({ articleLink }: { articleLink: string }) {
  const [state, setState] = useState<"idle" | "loading" | "queued" | "error">("idle");

  const queueDigest = async () => {
    setState("loading");
    try {
      const response = await fetch("/api/digest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ article_link: articleLink }),
      });
      if (!response.ok) throw new Error("Request failed");
      setState("queued");
    } catch {
      setState("error");
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button onClick={queueDigest} size="sm" variant="outline" disabled={state === "loading"}>
        {state === "loading" ? "Queueing..." : "Digest now"}
      </Button>
      {state === "queued" && <span className="text-xs text-emerald-700">Queued</span>}
      {state === "error" && <span className="text-xs text-red-700">Failed</span>}
    </div>
  );
}
