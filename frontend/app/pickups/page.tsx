"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { useToast } from "@/lib/toast-context";
import { api } from "@/lib/api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import type { PickupRequest } from "@/types";
import { Loader2, Plus, X } from "lucide-react";

const WASTE_TYPES = ["Plastic", "Paper", "Glass", "Metal", "Organic", "E-Waste", "Textile", "Other"];

function ScheduleForm({ onCreated }: { onCreated: () => void }) {
  const { show } = useToast();
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    waste_type: "Plastic", quantity_kg: "", address: "", preferred_date: "", preferred_time: "", notes: "",
  });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!navigator.geolocation) return show("error", "Geolocation is not supported in this browser");

    setSubmitting(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          await api.post("/api/pickups", {
            waste_type: form.waste_type,
            quantity_kg: parseFloat(form.quantity_kg),
            address: form.address,
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            preferred_date: form.preferred_date,
            preferred_time: form.preferred_time,
            notes: form.notes || undefined,
          });
          show("success", "Pickup scheduled!");
          setOpen(false);
          onCreated();
        } catch (err: any) {
          show("error", err?.response?.data?.detail || "Could not schedule pickup");
        } finally {
          setSubmitting(false);
        }
      },
      () => {
        show("error", "Location access is required to schedule a pickup");
        setSubmitting(false);
      }
    );
  }

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="btn-primary">
        <Plus className="h-4 w-4" /> Schedule Pickup
      </button>
    );
  }

  return (
    <form onSubmit={submit} className="card space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold text-slate-900">Schedule a Pickup</h2>
        <button type="button" onClick={() => setOpen(false)}><X className="h-4 w-4 text-slate-400" /></button>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="label">Waste Type</label>
          <select className="input" value={form.waste_type} onChange={(e) => setForm({ ...form, waste_type: e.target.value })}>
            {WASTE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Quantity (kg)</label>
          <input className="input" type="number" step="0.1" min="0.1" required value={form.quantity_kg} onChange={(e) => setForm({ ...form, quantity_kg: e.target.value })} />
        </div>
        <div className="sm:col-span-2">
          <label className="label">Address</label>
          <input className="input" required value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        </div>
        <div>
          <label className="label">Preferred Date</label>
          <input className="input" type="date" required value={form.preferred_date} onChange={(e) => setForm({ ...form, preferred_date: e.target.value })} />
        </div>
        <div>
          <label className="label">Preferred Time</label>
          <input className="input" type="time" required value={form.preferred_time} onChange={(e) => setForm({ ...form, preferred_time: e.target.value })} />
        </div>
        <div className="sm:col-span-2">
          <label className="label">Notes (optional)</label>
          <textarea className="input" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
      </div>
      <button type="submit" disabled={submitting} className="btn-primary w-full">
        {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
        Confirm Pickup (uses your current location)
      </button>
    </form>
  );
}

function PickupsContent() {
  const { data: pickups, loading, error, refetch } = useApi<PickupRequest[]>("/api/pickups/my");

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Pickups</h1>
      </div>

      <div className="mb-6">
        <ScheduleForm onCreated={refetch} />
      </div>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !pickups?.length ? (
        <EmptyState title="No pickups scheduled" description="Schedule your first pickup above." />
      ) : (
        <div className="space-y-3">
          {pickups.map((p) => (
            <div key={p.id} className="card flex items-center justify-between p-4">
              <div>
                <p className="font-medium text-slate-800">{p.waste_type} — {p.quantity_kg} kg</p>
                <p className="text-sm text-slate-500">{p.address}</p>
                <p className="text-xs text-slate-400">{p.preferred_date} at {p.preferred_time}</p>
              </div>
              <StatusBadge status={p.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PickupsPage() {
  return (
    <ProtectedRoute allowedRoles={["USER"]}>
      <PickupsContent />
    </ProtectedRoute>
  );
}
