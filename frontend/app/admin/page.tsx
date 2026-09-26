"use client";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { LoadingState, ErrorState } from "@/components/States";
import { StatCard } from "@/components/States";
import type { AnalyticsOverview, User } from "@/types";
import { Users, FileText, Truck, CheckCircle2 } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from "recharts";
import Link from "next/link";

function AdminContent() {
  const { data: overview, loading, error, refetch } = useApi<AnalyticsOverview>("/api/analytics/overview");
  const { data: users } = useApi<User[]>("/api/admin/users");

  if (loading) return <div className="mx-auto max-w-7xl px-4 py-8"><LoadingState /></div>;
  if (error || !overview) return <div className="mx-auto max-w-7xl px-4 py-8"><ErrorState message={error || "Could not load analytics"} onRetry={refetch} /></div>;

  const categoryData = Object.entries(overview.waste_by_category).map(([category, count]) => ({ category, count }));
  const trendData = Object.entries(overview.reports_last_30_days)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({ date: date.slice(5), count }));

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Admin Overview</h1>
        <div className="flex gap-2">
          <Link href="/admin/users" className="btn-secondary">Manage Users</Link>
          <Link href="/admin/centers" className="btn-secondary">Recycling Centers</Link>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Users" value={overview.total_users} icon={Users} accent="eco" />
        <StatCard label="Waste Reports" value={overview.total_waste_reports} icon={FileText} accent="blue" />
        <StatCard label="Pickup Requests" value={overview.total_pickups} icon={Truck} accent="amber" />
        <StatCard label="Completion Rate" value={`${overview.pickup_completion_rate}%`} icon={CheckCircle2} accent="violet" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h2 className="mb-4 font-semibold text-slate-900">Waste by Category</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categoryData}>
              <XAxis dataKey="category" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#16a34a" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-6">
          <h2 className="mb-4 font-semibold text-slate-900">Reports — Last 30 Days</h2>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#16a34a" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {users && (
        <div className="mt-8 card p-6">
          <h2 className="mb-4 font-semibold text-slate-900">Most Recent Users</h2>
          <div className="divide-y divide-slate-100">
            {users.slice(0, 6).map((u) => (
              <div key={u.id} className="flex items-center justify-between py-2.5 text-sm">
                <span className="font-medium text-slate-800">{u.full_name}</span>
                <span className="text-slate-500">{u.email}</span>
                <span className="badge bg-slate-100 text-slate-600">{u.role}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function AdminPage() {
  return (
    <ProtectedRoute allowedRoles={["ADMIN"]}>
      <AdminContent />
    </ProtectedRoute>
  );
}
