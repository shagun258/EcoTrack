"use client";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { useAuth } from "@/lib/auth-context";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import type { RewardTransaction, Badge } from "@/types";
import { Award, Trophy, Lock } from "lucide-react";
import clsx from "clsx";

function RewardsContent() {
  const { user } = useAuth();
  const { data: rewards, loading, error, refetch } = useApi<RewardTransaction[]>("/api/rewards/my");
  const { data: allBadges } = useApi<Badge[]>("/api/rewards/badges");
  const { data: myBadges } = useApi<Badge[]>("/api/rewards/my/badges");

  const earnedIds = new Set(myBadges?.map((b) => b.id));

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="card mb-6 flex items-center justify-between bg-gradient-to-r from-eco-600 to-eco-500 p-6 text-white">
        <div>
          <p className="text-sm text-eco-100">Total Reward Points</p>
          <p className="text-3xl font-bold">{user?.points ?? 0}</p>
        </div>
        <Award className="h-12 w-12 text-eco-200" />
      </div>

      <h2 className="mb-3 font-semibold text-slate-900">Badges</h2>
      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {allBadges?.map((b) => {
          const earned = earnedIds.has(b.id);
          return (
            <div key={b.id} className={clsx("card p-4 text-center", !earned && "opacity-50")}>
              <div className={clsx("mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full", earned ? "bg-eco-100 text-eco-600" : "bg-slate-100 text-slate-400")}>
                {earned ? <Trophy className="h-5 w-5" /> : <Lock className="h-4 w-4" />}
              </div>
              <p className="text-sm font-medium text-slate-800">{b.name}</p>
              <p className="text-xs text-slate-500">{b.points_required} pts</p>
            </div>
          );
        })}
      </div>

      <h2 className="mb-3 font-semibold text-slate-900">Points History</h2>
      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !rewards?.length ? (
        <EmptyState title="No points earned yet" />
      ) : (
        <div className="card divide-y divide-slate-100">
          {rewards.map((r) => (
            <div key={r.id} className="flex items-center justify-between px-4 py-3">
              <span className="text-sm text-slate-700">{r.reason}</span>
              <span className="font-semibold text-eco-600">+{r.points}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function RewardsPage() {
  return (
    <ProtectedRoute allowedRoles={["USER"]}>
      <RewardsContent />
    </ProtectedRoute>
  );
}
