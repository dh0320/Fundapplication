"use client";

import { SyncButton } from "@/components/grants/SyncButton";
import { formatDate } from "@/lib/utils";
import { FileSearch } from "lucide-react";

interface HeaderProps {
  lastSynced: string | null;
  onSyncComplete?: () => void;
}

export function Header({ lastSynced, onSyncComplete }: HeaderProps) {
  return (
    <header className="border-b bg-white">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <FileSearch className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">GrantDraft</h1>
            <p className="text-xs text-gray-500">補助金情報ダッシュボード</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {lastSynced && (
            <span className="text-xs text-gray-400 hidden sm:block">
              最終更新: {new Date(lastSynced).toLocaleString("ja-JP")}
            </span>
          )}
          <SyncButton onSyncComplete={onSyncComplete} />
        </div>
      </div>
    </header>
  );
}
