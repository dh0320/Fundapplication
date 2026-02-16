import { GrantFilters, GrantListResponse, GrantDetail } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchGrants(
  filters: GrantFilters
): Promise<GrantListResponse> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== "") {
      params.set(key, String(val));
    }
  });
  const res = await fetch(`${API_BASE}/api/v1/grants?${params.toString()}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function fetchGrantDetail(id: string): Promise<GrantDetail> {
  const res = await fetch(`${API_BASE}/api/v1/grants/${id}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function triggerSync(
  source: string
): Promise<{ scrape_log_id: string; message: string }> {
  const res = await fetch(`${API_BASE}/api/v1/grants/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
