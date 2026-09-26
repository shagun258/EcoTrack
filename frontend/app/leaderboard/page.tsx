"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { useAuth } from "@/lib/auth-context";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import type { LeaderboardEntry } from "@/types";
import { Trophy } from "lucide-react";
import clsx from "clsx";

const PERIODS = [
  { key: "weekly", label: "This Week" },
  { key: "monthly", label: "This Month" },
  { key: "all_time", label: "All Time" },
] as const;

const MEDAL_COLORS = ["text-amber-500", "text-slate-400", "text-amber-700"];

function LeaderboardContent() {
  const { user } = useAuth();
  const [period, setPeriod] = useState<(typeof PERIODS)[number]["key"]>("all_time");
  const { data, loading, error, refetch } = useApi<LeaderboardEntry[]>(`/api/leaderboard?period=${period}`, [period]);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Leaderboard</h1>

      <div className="mb-6 flex gap-2">
        {PERIODS.map((p) => (
          <button
            key={p.key}
            onClick={() => setPeriod(p.key)}
            className={clsx("rounded-lg px-3 py-1.5 text-sm font-medium", period === p.key ? "bg-eco-600 text-white" : "bg-white text-slate-600 hover:bg-slate-100")}
          >
            {p.label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !data?.length ? (
        <EmptyState title="No leaderboard data yet" />
      ) : (
        <div className="card divide-y divide-slate-100">
          {data.map((entry) => (
            <div key={entry.user_id} className={clsx("flex items-center justify-between px-4 py-3", entry.user_id === user?.id && "bg-eco-50/50")}>
              <div className="flex items-center gap-3">
                <span className={clsx("w-6 text-center font-bold", entry.rank <= 3 ? MEDAL_COLORS[entry.rank - 1] : "text-slate-400")}>
                  {entry.rank <= 3 ? <Trophy className="h-4 w-4" /> : entry.rank}
                </span>
                <div>
                  <p className="text-sm font-medium text-slate-800">{entry.full_name}{entry.user_id === user?.id && " (You)"}</p>
                  <p className="text-xs text-slate-500">{entry.reports_count} reports</p>
                </div>
              </div>
              <span className="font-semibold text-eco-600">{entry.points} pts</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function LeaderboardPage() {
  return (
    <ProtectedRoute>
      <LeaderboardContent />
    </ProtectedRoute>
  );
}
