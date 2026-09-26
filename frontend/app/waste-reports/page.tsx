"use client";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import type { WasteReport } from "@/types";
import { API_URL } from "@/lib/api";

function ReportsContent() {
  const { data: reports, loading, error, refetch } = useApi<WasteReport[]>("/api/waste/reports");

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">My Waste Reports</h1>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !reports?.length ? (
        <EmptyState title="No reports yet" description="Reports you submit will show up here." />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {reports.map((r) => (
            <div key={r.id} className="card overflow-hidden">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`${API_URL}${r.image_url}`} alt={r.category} className="h-40 w-full object-cover" />
              <div className="p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-semibold text-slate-800">{r.category}</span>
                  <StatusBadge status={r.status} />
                </div>
                {r.description && <p className="mb-2 text-sm text-slate-600">{r.description}</p>}
                {r.ml_prediction && (
                  <p className="text-xs text-slate-400">
                    AI confidence: {Math.round(r.ml_prediction.confidence * 100)}%
                    {r.ml_prediction.mode === "demo" && " (demo mode)"}
                  </p>
                )}
                {r.possible_duplicate_of && (
                  <p className="mt-2 text-xs font-medium text-amber-600">⚠ Possible duplicate of report #{r.possible_duplicate_of}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function WasteReportsPage() {
  return (
    <ProtectedRoute allowedRoles={["USER"]}>
      <ReportsContent />
    </ProtectedRoute>
  );
}
