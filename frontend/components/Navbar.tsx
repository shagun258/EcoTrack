"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Leaf, LayoutDashboard, Camera, Truck, MapPin, Award, Trophy, Bell, User as UserIcon, LogOut, ShieldCheck } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import clsx from "clsx";

const USER_LINKS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/report-waste", label: "Report Waste", icon: Camera },
  { href: "/pickups", label: "Pickups", icon: Truck },
  { href: "/recycling-centers", label: "Centers", icon: MapPin },
  { href: "/rewards", label: "Rewards", icon: Award },
  { href: "/leaderboard", label: "Leaderboard", icon: Trophy },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  if (!user) return null;

  const links =
    user.role === "ADMIN"
      ? [{ href: "/admin", label: "Admin", icon: ShieldCheck }]
      : user.role === "COLLECTOR"
      ? [{ href: "/collector", label: "Collector", icon: Truck }]
      : USER_LINKS;

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-eco-700">
          <Leaf className="h-6 w-6" />
          <span>EcoTrack</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition",
                pathname === href ? "bg-eco-50 text-eco-700" : "text-slate-600 hover:bg-slate-100"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Link href="/notifications" className="rounded-lg p-2 text-slate-500 hover:bg-slate-100">
            <Bell className="h-5 w-5" />
          </Link>
          <Link href="/profile" className="rounded-lg p-2 text-slate-500 hover:bg-slate-100">
            <UserIcon className="h-5 w-5" />
          </Link>
          <button onClick={logout} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100" title="Log out">
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
