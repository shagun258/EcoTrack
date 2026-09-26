"use client";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { useToast } from "@/lib/toast-context";
import { api } from "@/lib/api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import type { PickupRequest, PickupStatus } from "@/types";
import { Truck } from "lucide-react";

const NEXT_STATUS: Partial<Record<PickupStatus, PickupStatus>> = {
  ASSIGNED: "ACCEPTED",
  ACCEPTED: "PICKED_UP",
  PICKED_UP: "COMPLETED",
};

const ACTION_LABEL: Partial<Record<PickupStatus, string>> = {
  ASSIGNED: "Accept Pickup",
  ACCEPTED: "Mark Picked Up",
  PICKED_UP: "Mark Completed",
};

function CollectorContent() {
  const { data: pickups, loading, error, refetch } = useApi<PickupRequest[]>("/api/pickups/assigned");
  const { show } = useToast();

  async function advance(pickup: PickupRequest) {
    const next = NEXT_STATUS[pickup.status];
    if (!next) return;
    try {
      await api.patch(`/api/pickups/${pickup.id}/status`, { status: next });
      show("success", `Pickup #${pickup.id} updated to ${next}`);
      refetch();
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not update pickup");
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex items-center gap-2">
        <Truck className="h-6 w-6 text-eco-600" />
        <h1 className="text-2xl font-bold text-slate-900">Assigned Pickups</h1>
      </div>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !pickups?.length ? (
        <EmptyState title="No pickups assigned to you yet" />
      ) : (
        <div className="space-y-3">
          {pickups.map((p) => (
            <div key={p.id} className="card p-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="font-medium text-slate-800">{p.waste_type} — {p.quantity_kg} kg</p>
                <StatusBadge status={p.status} />
              </div>
              <p className="text-sm text-slate-600">{p.address}</p>
              <p className="mb-3 text-xs text-slate-400">Preferred: {p.preferred_date} at {p.preferred_time}</p>
              {NEXT_STATUS[p.status] && (
                <button onClick={() => advance(p)} className="btn-primary">
                  {ACTION_LABEL[p.status]}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CollectorPage() {
  return (
    <ProtectedRoute allowedRoles={["COLLECTOR", "ADMIN"]}>
      <CollectorContent />
    </ProtectedRoute>
  );
}
