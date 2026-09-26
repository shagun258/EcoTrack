import clsx from "clsx";

const COLORS: Record<string, string> = {
  PENDING: "bg-amber-50 text-amber-700",
  ASSIGNED: "bg-blue-50 text-blue-700",
  ACCEPTED: "bg-indigo-50 text-indigo-700",
  PICKED_UP: "bg-violet-50 text-violet-700",
  COMPLETED: "bg-eco-50 text-eco-700",
  CANCELLED: "bg-slate-100 text-slate-500",
  VERIFIED: "bg-eco-50 text-eco-700",
  REJECTED: "bg-red-50 text-red-700",
  RESOLVED: "bg-eco-50 text-eco-700",
};

export function StatusBadge({ status }: { status: string }) {
  return <span className={clsx("badge", COLORS[status] || "bg-slate-100 text-slate-600")}>{status.replace("_", " ")}</span>;
}
