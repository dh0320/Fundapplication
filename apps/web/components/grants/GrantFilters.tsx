"use client";

import { useCallback, useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import { GrantFilters as FilterType } from "@/lib/types";
import { Search } from "lucide-react";

interface GrantFiltersProps {
  filters: FilterType;
  onFilterChange: (filters: FilterType) => void;
}

export function GrantFilters({ filters, onFilterChange }: GrantFiltersProps) {
  const [keyword, setKeyword] = useState(filters.keyword || "");

  // Debounced keyword search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (keyword !== (filters.keyword || "")) {
        onFilterChange({ ...filters, keyword: keyword || undefined, page: 1 });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [keyword]);

  const handleSelectChange = useCallback(
    (key: string, value: string) => {
      onFilterChange({
        ...filters,
        [key]: value || undefined,
        page: 1,
      });
    },
    [filters, onFilterChange]
  );

  return (
    <div className="flex flex-col sm:flex-row gap-3">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          placeholder="キーワードで検索..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="pl-10"
        />
      </div>
      <select
        className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-950"
        value={filters.status || ""}
        onChange={(e) => handleSelectChange("status", e.target.value)}
      >
        <option value="">全てのステータス</option>
        <option value="open">募集中</option>
        <option value="closing_soon">締切間近</option>
        <option value="closed">募集終了</option>
        <option value="upcoming">公募予定</option>
      </select>
      <select
        className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-950"
        value={filters.source || ""}
        onChange={(e) => handleSelectChange("source", e.target.value)}
      >
        <option value="">全てのソース</option>
        <option value="jgrants">JGrants</option>
        <option value="erad">e-Rad</option>
      </select>
      <select
        className="h-10 rounded-md border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-950"
        value={`${filters.sort || "deadline"}_${filters.order || "asc"}`}
        onChange={(e) => {
          const [sort, order] = e.target.value.split("_");
          onFilterChange({ ...filters, sort, order, page: 1 });
        }}
      >
        <option value="deadline_asc">締切日順（昇順）</option>
        <option value="deadline_desc">締切日順（降順）</option>
        <option value="created_desc">登録日順（新しい順）</option>
        <option value="created_asc">登録日順（古い順）</option>
        <option value="amount_desc">金額順（高い順）</option>
        <option value="amount_asc">金額順（低い順）</option>
      </select>
    </div>
  );
}
