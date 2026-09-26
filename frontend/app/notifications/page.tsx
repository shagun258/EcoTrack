"use client";

import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useApi } from "@/lib/use-api";
import { api } from "@/lib/api";
import { LoadingState, ErrorState, EmptyState } from "@/components/States";
import type { NotificationItem } from "@/types";
import { Bell } from "lucide-react";
import clsx from "clsx";
import { formatDistanceToNow } from "date-fns";

function NotificationsContent() {
  const { data: notifications, loading, error, refetch } = useApi<NotificationItem[]>("/api/notifications");

  async function markRead(id: number) {
    await api.patch(`/api/notifications/${id}/read`);
    refetch();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Notifications</h1>

      {loading ? (
        <LoadingState />
      ) : error ? (
        <ErrorState message={error} onRetry={refetch} />
      ) : !notifications?.length ? (
        <EmptyState title="You're all caught up" description="New notifications about your reports and pickups will show up here." />
      ) : (
        <div className="card divide-y divide-slate-100">
          {notifications.map((n) => (
            <button
              key={n.id}
              onClick={() => !n.is_read && markRead(n.id)}
              className={clsx("flex w-full items-start gap-3 px-4 py-3 text-left transition", !n.is_read && "bg-eco-50/50")}
            >
              <Bell className={clsx("mt-0.5 h-4 w-4 shrink-0", !n.is_read ? "text-eco-600" : "text-slate-300")} />
              <div>
                <p className="text-sm font-medium text-slate-800">{n.title}</p>
                <p className="text-sm text-slate-500">{n.message}</p>
                <p className="mt-0.5 text-xs text-slate-400">{formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsContent />
    </ProtectedRoute>
  );
}
