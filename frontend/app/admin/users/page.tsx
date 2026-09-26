"use client";

import { useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { useToast } from "@/lib/toast-context";
import { api } from "@/lib/api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import type { User, UserRole } from "@/types";
import { Search } from "lucide-react";

const ROLES: UserRole[] = ["USER", "COLLECTOR", "ADMIN"];

function AdminUsersContent() {
  const [search, setSearch] = useState("");
  const url = search ? `/api/admin/users?search=${encodeURIComponent(search)}` : "/api/admin/users";
  const { data: users, loading, error, refetch } = useApi<User[]>(url, [search]);
  const { show } = useToast();

  async function changeRole(userId: number, role: UserRole) {
    try {
      await api.patch(`/api/admin/users/${userId}/role`, { role });
      show("success", "Role updated");
      refetch();
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not update role");
    }
  }

  async function toggleActive(user: User) {
    try {
      await api.patch(`/api/admin/users/${user.id}/${user.is_active ? "deactivate" : "activate"}`);
      show("success", user.is_active ? "User deactivated" : "User activated");
      refetch();
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not update user");
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Manage Users</h1>

      <div className="mb-4 flex items-center gap-2">
        <Search className="h-4 w-4 text-slate-400" />
        <input className="input" placeholder="Search by name or email..." value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !users?.length ? (
        <EmptyState title="No users found" />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-100 text-left text-slate-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Points</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((u) => (
                <tr key={u.id}>
                  <td className="px-4 py-3 font-medium text-slate-800">{u.full_name}</td>
                  <td className="px-4 py-3 text-slate-500">{u.email}</td>
                  <td className="px-4 py-3">
                    <select className="input py-1.5 text-xs" value={u.role} onChange={(e) => changeRole(u.id, e.target.value as UserRole)}>
                      {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3">{u.points}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${u.is_active ? "bg-eco-50 text-eco-700" : "bg-red-50 text-red-700"}`}>
                      {u.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => toggleActive(u)} className="text-xs font-medium text-eco-700 hover:underline">
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function AdminUsersPage() {
  return (
    <ProtectedRoute allowedRoles={["ADMIN"]}>
      <AdminUsersContent />
    </ProtectedRoute>
  );
}
