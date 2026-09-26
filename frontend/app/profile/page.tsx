"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/auth-context";
import { useToast } from "@/lib/toast-context";
import { api } from "@/lib/api";
import { Loader2, User as UserIcon } from "lucide-react";

function ProfileContent() {
  const { user, refreshUser } = useAuth();
  const { show } = useToast();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [saving, setSaving] = useState(false);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.patch("/api/users/me", { full_name: fullName, phone: phone || null });
      await refreshUser();
      show("success", "Profile updated");
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not update profile");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-8 sm:px-6">
      <div className="mb-6 flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-eco-100 text-eco-700">
          <UserIcon className="h-8 w-8" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900">{user?.full_name}</h1>
          <p className="text-sm text-slate-500">{user?.email} · {user?.role}</p>
        </div>
      </div>

      <form onSubmit={save} className="card space-y-4 p-6">
        <div>
          <label className="label">Full name</label>
          <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div>
          <label className="label">Phone</label>
          <input className="input" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Optional" />
        </div>
        <div>
          <label className="label">Email</label>
          <input className="input" value={user?.email} disabled />
          <p className="mt-1 text-xs text-slate-400">Email cannot be changed</p>
        </div>
        <button type="submit" disabled={saving} className="btn-primary w-full">
          {saving && <Loader2 className="h-4 w-4 animate-spin" />}
          Save Changes
        </button>
      </form>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}
