"use client";

import Link from "next/link";
import { Grant } from "@/lib/types";
import { GrantStatusBadge } from "./GrantStatusBadge";
import { SourceBadge } from "./SourceBadge";
import { formatAmount, formatDate, isDeadlineSoon } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

interface GrantTableProps {
  grants: Grant[];
  loading: boolean;
}

export function GrantTable({ grants, loading }: GrantTableProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  if (grants.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">該当する補助金が見つかりません</p>
        <p className="text-sm mt-1">フィルタ条件を変更してお試しください</p>
      </div>
    );
  }

  return (
    <>
      {/* Desktop table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="text-left py-3 px-4 font-medium text-gray-500 w-[80px]">
                ソース
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-500">
                補助金名
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 w-[160px]">
                公募元
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 w-[140px] hidden lg:table-cell">
                金額
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 w-[120px]">
                締切日
              </th>
              <th className="text-left py-3 px-4 font-medium text-gray-500 w-[100px]">
                ステータス
              </th>
            </tr>
          </thead>
          <tbody>
            {grants.map((grant) => (
              <tr
                key={grant.id}
                className="border-b hover:bg-gray-50 transition-colors"
              >
                <td className="py-3 px-4">
                  <SourceBadge source={grant.source} />
                </td>
                <td className="py-3 px-4">
                  <Link
                    href={`/grants/${grant.id}`}
                    className="text-blue-600 hover:text-blue-800 hover:underline font-medium line-clamp-2"
                  >
                    {grant.title}
                  </Link>
                </td>
                <td className="py-3 px-4 text-gray-600 truncate max-w-[160px]">
                  {grant.organization}
                </td>
                <td className="py-3 px-4 text-gray-600 hidden lg:table-cell">
                  {grant.amount_max
                    ? `〜${formatAmount(grant.amount_max)}`
                    : "-"}
                </td>
                <td
                  className={`py-3 px-4 ${
                    isDeadlineSoon(grant.application_deadline)
                      ? "text-red-600 font-medium"
                      : "text-gray-600"
                  }`}
                >
                  {formatDate(grant.application_deadline)}
                </td>
                <td className="py-3 px-4">
                  <GrantStatusBadge status={grant.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="md:hidden space-y-3">
        {grants.map((grant) => (
          <div
            key={grant.id}
            className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2 mb-2">
              <SourceBadge source={grant.source} />
              <GrantStatusBadge status={grant.status} />
            </div>
            <Link
              href={`/grants/${grant.id}`}
              className="text-blue-600 hover:text-blue-800 hover:underline font-medium text-sm block mb-1"
            >
              {grant.title}
            </Link>
            <p className="text-xs text-gray-500 mb-1">{grant.organization}</p>
            <div className="flex justify-between text-xs text-gray-500">
              <span>
                {grant.amount_max
                  ? `〜${formatAmount(grant.amount_max)}`
                  : "-"}
              </span>
              <span
                className={
                  isDeadlineSoon(grant.application_deadline)
                    ? "text-red-600 font-medium"
                    : ""
                }
              >
                締切: {formatDate(grant.application_deadline)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
