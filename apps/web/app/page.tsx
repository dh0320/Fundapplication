"use client";

import { useCallback, useEffect, useState } from "react";
import { Header } from "@/components/layout/Header";
import { StatsCards } from "@/components/grants/StatsCards";
import { GrantFilters } from "@/components/grants/GrantFilters";
import { GrantTable } from "@/components/grants/GrantTable";
import { Pagination } from "@/components/grants/Pagination";
import { fetchGrants } from "@/lib/api";
import { GrantFilters as FilterType, GrantListResponse } from "@/lib/types";

export default function DashboardPage() {
  const [data, setData] = useState<GrantListResponse | null>(null);
  const [statusCounts, setStatusCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<FilterType>({
    sort: "deadline",
    order: "asc",
    page: 1,
    limit: 20,
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchGrants(filters);
      setData(result);
    } catch (error) {
      console.error("Failed to fetch grants:", error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Load status counts for stats cards (unfiltered)
  const loadStatusCounts = useCallback(async () => {
    try {
      const openResult = await fetchGrants({ status: "open", limit: 1 });
      const closingSoonResult = await fetchGrants({
        status: "closing_soon",
        limit: 1,
      });
      setStatusCounts({
        open: openResult.pagination.total,
        closing_soon: closingSoonResult.pagination.total,
      });
    } catch (error) {
      console.error("Failed to fetch status counts:", error);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    loadStatusCounts();
  }, [loadStatusCounts]);

  const handleFilterChange = (newFilters: FilterType) => {
    setFilters(newFilters);
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  const handleSyncComplete = () => {
    loadData();
    loadStatusCounts();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        lastSynced={data?.meta?.last_synced || null}
        onSyncComplete={handleSyncComplete}
      />
      <main className="container mx-auto px-4 py-6 space-y-6">
        <StatsCards data={data} statusCounts={statusCounts} />
        <div className="bg-white rounded-lg border shadow-sm p-6 space-y-4">
          <GrantFilters filters={filters} onFilterChange={handleFilterChange} />
          <GrantTable grants={data?.data || []} loading={loading} />
          {data && (
            <Pagination
              page={data.pagination.page}
              totalPages={data.pagination.total_pages}
              total={data.pagination.total}
              limit={data.pagination.limit}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      </main>
    </div>
  );
}
