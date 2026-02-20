"use client";

import { Badge } from "@/components/ui/badge";

const STATUS_CONFIG: Record<
  string,
  { label: string; className: string }
> = {
  open: {
    label: "募集中",
    className: "bg-green-100 text-green-800 border-green-200",
  },
  closing_soon: {
    label: "締切間近",
    className: "bg-orange-100 text-orange-800 border-orange-200",
  },
  closed: {
    label: "募集終了",
    className: "bg-gray-100 text-gray-600 border-gray-200",
  },
  upcoming: {
    label: "公募予定",
    className: "bg-blue-100 text-blue-800 border-blue-200",
  },
};

export function GrantStatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.open;
  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
