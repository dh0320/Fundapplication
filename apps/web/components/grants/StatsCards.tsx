"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GrantListResponse } from "@/lib/types";
import { FileText, AlertTriangle, Globe, BookOpen } from "lucide-react";

interface StatsCardsProps {
  data: GrantListResponse | null;
  statusCounts: Record<string, number>;
}

export function StatsCards({ data, statusCounts }: StatsCardsProps) {
  const sources = data?.meta?.sources || {};

  const cards = [
    {
      title: "募集中",
      value: statusCounts.open || 0,
      icon: FileText,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "締切間近",
      value: statusCounts.closing_soon || 0,
      icon: AlertTriangle,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
    {
      title: "JGrants",
      value: sources.jgrants || 0,
      icon: Globe,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "e-Rad",
      value: sources.erad || 0,
      icon: BookOpen,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              {card.title}
            </CardTitle>
            <div className={`p-2 rounded-lg ${card.bgColor}`}>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${card.color}`}>
              {card.value.toLocaleString()}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
