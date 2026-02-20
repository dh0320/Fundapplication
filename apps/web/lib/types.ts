export interface Grant {
  id: string;
  source: "jgrants" | "erad";
  title: string;
  organization: string;
  category: string | null;
  summary: string | null;
  target_audience: string | null;
  amount_min: number | null;
  amount_max: number | null;
  application_start: string | null;
  application_deadline: string | null;
  detail_url: string | null;
  guideline_url: string | null;
  status: "open" | "closing_soon" | "closed" | "upcoming";
  last_synced_at: string;
}

export interface GrantDetail extends Grant {
  raw_data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface GrantListResponse {
  data: Grant[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    total_pages: number;
  };
  meta: {
    sources: Record<string, number>;
    last_synced: string | null;
  };
}

export interface GrantFilters {
  status?: string;
  source?: string;
  keyword?: string;
  sort?: string;
  order?: string;
  page?: number;
  limit?: number;
}
