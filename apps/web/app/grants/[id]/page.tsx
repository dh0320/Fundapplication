"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchGrantDetail } from "@/lib/api";
import { GrantDetail } from "@/lib/types";
import { GrantStatusBadge } from "@/components/grants/GrantStatusBadge";
import { SourceBadge } from "@/components/grants/SourceBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatAmount, formatDate } from "@/lib/utils";
import {
  ArrowLeft,
  ExternalLink,
  Calendar,
  Building2,
  Banknote,
  Tag,
} from "lucide-react";

export default function GrantDetailPage() {
  const params = useParams();
  const [grant, setGrant] = useState<GrantDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadGrant = async () => {
      try {
        const data = await fetchGrantDetail(params.id as string);
        setGrant(data);
      } catch (err) {
        setError("補助金情報の取得に失敗しました");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    loadGrant();
  }, [params.id]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !grant) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-red-500">{error || "データが見つかりません"}</p>
        <Link href="/">
          <Button variant="outline" className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            一覧に戻る
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Link href="/">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            一覧に戻る
          </Button>
        </Link>

        <div className="space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <SourceBadge source={grant.source} />
              <GrantStatusBadge status={grant.status} />
              {grant.category && (
                <span className="inline-flex items-center gap-1 text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                  <Tag className="h-3 w-3" />
                  {grant.category}
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {grant.title}
            </h1>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Building2 className="h-4 w-4" />
              {grant.organization}
            </div>
          </div>

          {/* Key info cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  応募期間
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  {formatDate(grant.application_start)} 〜{" "}
                  {formatDate(grant.application_deadline)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500 flex items-center gap-2">
                  <Banknote className="h-4 w-4" />
                  助成金額
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm">
                  {grant.amount_min || grant.amount_max
                    ? `${formatAmount(grant.amount_min)} 〜 ${formatAmount(grant.amount_max)}`
                    : "記載なし"}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-500">
                  外部リンク
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {grant.detail_url && (
                  <a
                    href={grant.detail_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                  >
                    詳細ページ
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
                {grant.guideline_url && (
                  <a
                    href={grant.guideline_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                  >
                    公募要領
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Summary */}
          {grant.summary && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">概要</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {grant.summary}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Target audience */}
          {grant.target_audience && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">対象者</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {grant.target_audience}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Raw data */}
          {grant.raw_data && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">元データ（JSON）</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-gray-50 p-4 rounded-lg overflow-x-auto max-h-96">
                  {JSON.stringify(grant.raw_data, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}

          {/* Metadata */}
          <div className="text-xs text-gray-400 space-y-1">
            <p>
              最終同期:{" "}
              {new Date(grant.last_synced_at).toLocaleString("ja-JP")}
            </p>
            <p>
              作成日: {new Date(grant.created_at).toLocaleString("ja-JP")}
            </p>
            <p>
              更新日: {new Date(grant.updated_at).toLocaleString("ja-JP")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
