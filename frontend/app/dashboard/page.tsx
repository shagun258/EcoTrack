"use client";

import Link from "next/link";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/auth-context";
import { useApi } from "@/lib/use-api";
import { StatCard, LoadingState, ErrorState, EmptyState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import type { WasteReport, PickupRequest, RecyclingCenter } from "@/types";
import { Recycle, Truck, Award, FileText, Camera, ArrowRight } from "lucide-react";

function DashboardContent() {
  const { user } = useAuth();
  const { data: reports, loading: reportsLoading, error: reportsError, refetch: refetchReports } = useApi<WasteReport[]>("/api/waste/reports");
  const { data: pickups, loading: pickupsLoading } = useApi<PickupRequest[]>("/api/pickups/my");
  const { data: centers } = useApi<RecyclingCenter[]>("/api/recycling-centers");

  const completedPickups = pickups?.filter((p) => p.status === "COMPLETED").length ?? 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Welcome back, {user?.full_name.split(" ")[0]} 👋</h1>
          <p className="mt-1 text-sm text-slate-500">Here&apos;s your environmental impact so far.</p>
        </div>
        <Link href="/report-waste" className="btn-primary">
          <Camera className="h-4 w-4" /> Report Waste
        </Link>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Waste Reports" value={reports?.length ?? "—"} icon={FileText} accent="eco" />
        <StatCard label="Pickups Completed" value={completedPickups} icon={Truck} accent="blue" />
        <StatCard label="Reward Points" value={user?.points ?? 0} icon={Award} accent="amber" />
        <StatCard label="Nearby Centers" value={centers?.length ?? "—"} icon={Recycle} accent="violet" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card p-6 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-semibold text-slate-900">Recent Waste Reports</h2>
            <Link href="/waste-reports" className="flex items-center gap-1 text-sm font-medium text-eco-700 hover:underline">
              View all <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          {reportsLoading ? (
            <LoadingState />
          ) : reportsError ? (
            <ErrorState message={reportsError} onRetry={refetchReports} />
          ) : !reports?.length ? (
            <EmptyState title="No reports yet" description="Report your first piece of waste to start earning points." />
          ) : (
            <div className="divide-y divide-slate-100">
              {reports.slice(0, 5).map((r) => (
                <div key={r.id} className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{r.category}</p>
                    <p className="text-xs text-slate-500">{r.description || "No description"}</p>
                  </div>
                  <StatusBadge status={r.status} />
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card p-6">
          <h2 className="mb-4 font-semibold text-slate-900">Upcoming Pickups</h2>
          {pickupsLoading ? (
            <LoadingState />
          ) : !pickups?.length ? (
            <EmptyState title="No pickups scheduled" />
          ) : (
            <div className="space-y-3">
              {pickups.slice(0, 4).map((p) => (
                <div key={p.id} className="rounded-xl border border-slate-100 p-3">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-800">{p.waste_type}</span>
                    <StatusBadge status={p.status} />
                  </div>
                  <p className="text-xs text-slate-500">{p.preferred_date} at {p.preferred_time}</p>
                </div>
              ))}
            </div>
          )}
          <Link href="/pickups" className="btn-secondary mt-4 w-full">
            Schedule a Pickup
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute allowedRoles={["USER"]}>
      <DashboardContent />
    </ProtectedRoute>
  );
}
