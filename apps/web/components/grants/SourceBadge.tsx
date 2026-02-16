"use client";

import { Badge } from "@/components/ui/badge";

const SOURCE_CONFIG: Record<string, { label: string; className: string }> = {
  jgrants: {
    label: "JGrants",
    className: "bg-blue-100 text-blue-700 border-blue-200",
  },
  erad: {
    label: "e-Rad",
    className: "bg-purple-100 text-purple-700 border-purple-200",
  },
};

export function SourceBadge({ source }: { source: string }) {
  const config = SOURCE_CONFIG[source] || SOURCE_CONFIG.jgrants;
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
