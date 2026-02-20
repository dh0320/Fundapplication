import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatAmount(amount: number | null): string {
  if (amount === null || amount === undefined) return "-";
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(1)}億円`;
  }
  if (amount >= 10000) {
    return `${Math.floor(amount / 10000)}万円`;
  }
  return `${amount.toLocaleString()}円`;
}

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}`;
}

export function isDeadlineSoon(dateStr: string | null): boolean {
  if (!dateStr) return false;
  const deadline = new Date(dateStr);
  const today = new Date();
  const diff = (deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24);
  return diff >= 0 && diff <= 14;
}
