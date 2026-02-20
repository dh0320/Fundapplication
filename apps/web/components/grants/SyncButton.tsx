"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { triggerSync } from "@/lib/api";
import { RefreshCw } from "lucide-react";

interface SyncButtonProps {
  onSyncComplete?: () => void;
}

export function SyncButton({ onSyncComplete }: SyncButtonProps) {
  const [syncing, setSyncing] = useState(false);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await triggerSync("all");
      // Wait a bit for background sync to start processing
      setTimeout(() => {
        onSyncComplete?.();
        setSyncing(false);
      }, 3000);
    } catch (error) {
      console.error("Sync failed:", error);
      setSyncing(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleSync}
      disabled={syncing}
    >
      <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? "animate-spin" : ""}`} />
      {syncing ? "同期中..." : "データ同期"}
    </Button>
  );
}
