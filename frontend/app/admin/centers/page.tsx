"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { useToast } from "@/lib/toast-context";
import { api } from "@/lib/api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import type { RecyclingCenter } from "@/types";
import { Plus, Trash2, Loader2 } from "lucide-react";

const WASTE_TYPES = ["Plastic", "Paper", "Glass", "Metal", "Organic", "E-Waste", "Textile", "Other"];

function AddCenterForm({ onCreated }: { onCreated: () => void }) {
  const { show } = useToast();
  const [open, setOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: "", address: "", latitude: "", longitude: "", phone: "", opening_hours: "" });
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);

  function toggleType(t: string) {
    setSelectedTypes((cur) => (cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/api/recycling-centers", {
        name: form.name,
        address: form.address,
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        phone: form.phone || undefined,
        opening_hours: form.opening_hours || undefined,
        accepted_waste_types: selectedTypes,
      });
      show("success", "Recycling center added");
      setOpen(false);
      onCreated();
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not add center");
    } finally {
      setSubmitting(false);
    }
  }

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="btn-primary">
        <Plus className="h-4 w-4" /> Add Recycling Center
      </button>
    );
  }

  return (
    <form onSubmit={submit} className="card space-y-4 p-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <input className="input" placeholder="Name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input className="input" placeholder="Phone (optional)" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <input className="input sm:col-span-2" placeholder="Address" required value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        <input className="input" placeholder="Latitude" type="number" step="any" required value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} />
        <input className="input" placeholder="Longitude" type="number" step="any" required value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} />
        <input className="input sm:col-span-2" placeholder="Opening hours (e.g. Mon-Sat 9:00-18:00)" value={form.opening_hours} onChange={(e) => setForm({ ...form, opening_hours: e.target.value })} />
      </div>
      <div>
        <label className="label">Accepted waste types</label>
        <div className="flex flex-wrap gap-2">
          {WASTE_TYPES.map((t) => (
            <button type="button" key={t} onClick={() => toggleType(t)} className={`badge ${selectedTypes.includes(t) ? "bg-eco-600 text-white" : "bg-slate-100 text-slate-600"}`}>
              {t}
            </button>
          ))}
        </div>
      </div>
      <button type="submit" disabled={submitting} className="btn-primary">
        {submitting && <Loader2 className="h-4 w-4 animate-spin" />} Save Center
      </button>
    </form>
  );
}

function AdminCentersContent() {
  const { data: centers, loading, error, refetch } = useApi<RecyclingCenter[]>("/api/recycling-centers");
  const { show } = useToast();

  async function remove(id: number) {
    try {
      await api.delete(`/api/recycling-centers/${id}`);
      show("success", "Center deactivated");
      refetch();
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not deactivate center");
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Recycling Centers</h1>
      <div className="mb-6"><AddCenterForm onCreated={refetch} /></div>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !centers?.length ? (
        <EmptyState title="No recycling centers yet" />
      ) : (
        <div className="space-y-3">
          {centers.map((c) => (
            <div key={c.id} className="card flex items-center justify-between p-4">
              <div>
                <p className="font-medium text-slate-800">{c.name}</p>
                <p className="text-sm text-slate-500">{c.address}</p>
              </div>
              <button onClick={() => remove(c.id)} className="rounded-lg p-2 text-red-500 hover:bg-red-50">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function AdminCentersPage() {
  return (
    <ProtectedRoute allowedRoles={["ADMIN"]}>
      <AdminCentersContent />
    </ProtectedRoute>
  );
}
