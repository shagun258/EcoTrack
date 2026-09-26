"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import type { RecyclingCenter } from "@/types";
import { MapPin, Phone, Clock, Filter } from "lucide-react";

const RecyclingCentersMap = dynamic(() => import("@/components/RecyclingCentersMap").then((m) => m.RecyclingCentersMap), {
  ssr: false,
  loading: () => <div className="flex h-full items-center justify-center text-sm text-slate-400">Loading map…</div>,
});

const WASTE_TYPES = ["Plastic", "Paper", "Glass", "Metal", "Organic", "E-Waste", "Textile", "Other"];
const DEFAULT_CENTER: [number, number] = [31.1048, 77.1734]; // Shimla, HP - used as a sensible default

function CentersContent() {
  const [wasteType, setWasteType] = useState("");
  const url = wasteType ? `/api/recycling-centers?waste_type=${encodeURIComponent(wasteType)}` : "/api/recycling-centers";
  const { data: centers, loading, error, refetch } = useApi<RecyclingCenter[]>(url, [wasteType]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <h1 className="text-2xl font-bold text-slate-900">Recycling Centers</h1>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400" />
          <select className="input w-48" value={wasteType} onChange={(e) => setWasteType(e.target.value)}>
            <option value="">All waste types</option>
            {WASTE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !centers?.length ? (
        <EmptyState title="No recycling centers found" description="Try a different waste type filter." />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="h-[500px] overflow-hidden rounded-2xl border border-slate-200">
            <RecyclingCentersMap centers={centers} center={centers[0] ? [centers[0].latitude, centers[0].longitude] : DEFAULT_CENTER} />
          </div>
          <div className="max-h-[500px] space-y-3 overflow-y-auto pr-1">
            {centers.map((c) => (
              <div key={c.id} className="card p-4">
                <h3 className="font-semibold text-slate-900">{c.name}</h3>
                <p className="mt-1 flex items-start gap-1.5 text-sm text-slate-600">
                  <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {c.address}
                </p>
                {c.phone && (
                  <p className="mt-1 flex items-center gap-1.5 text-sm text-slate-600">
                    <Phone className="h-3.5 w-3.5 shrink-0" /> {c.phone}
                  </p>
                )}
                {c.opening_hours && (
                  <p className="mt-1 flex items-center gap-1.5 text-sm text-slate-600">
                    <Clock className="h-3.5 w-3.5 shrink-0" /> {c.opening_hours}
                  </p>
                )}
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {c.accepted_waste_types.map((t) => (
                    <span key={t} className="badge bg-eco-50 text-eco-700">{t}</span>
                  ))}
                </div>
                <a
                  href={`https://www.openstreetmap.org/directions?to=${c.latitude},${c.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 inline-block text-sm font-medium text-eco-700 hover:underline"
                >
                  Get directions →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function RecyclingCentersPage() {
  return (
    <ProtectedRoute>
      <CentersContent />
    </ProtectedRoute>
  );
}
