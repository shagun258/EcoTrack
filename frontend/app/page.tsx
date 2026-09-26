import Link from "next/link";
import { Leaf, Camera, MapPin, Truck, Award, ArrowRight } from "lucide-react";

const FEATURES = [
  { icon: Camera, title: "AI Waste Classification", desc: "Snap a photo and our ML model identifies the waste category instantly." },
  { icon: MapPin, title: "Find Recycling Centers", desc: "Locate nearby centers, see accepted waste types, hours, and get directions." },
  { icon: Truck, title: "Schedule Pickups", desc: "Book a pickup and track its status in real time, from request to completion." },
  { icon: Award, title: "Earn Rewards", desc: "Get points and badges for reporting, recycling, and completing pickups." },
];

export default function LandingPage() {
  return (
    <div>
      <section className="mx-auto max-w-7xl px-4 pb-16 pt-20 text-center sm:px-6">
        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-eco-600 text-white shadow-lg shadow-eco-600/30">
          <Leaf className="h-7 w-7" />
        </div>
        <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Smarter waste management, powered by AI
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-600">
          EcoTrack connects citizens, collectors and recycling centers to make reporting, sorting,
          and recycling waste effortless — and rewarding.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link href="/register" className="btn-primary px-6 py-3 text-base">
            Get Started <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/login" className="btn-secondary px-6 py-3 text-base">
            Sign In
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-24 sm:px-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card p-6">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-eco-50 text-eco-600">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mb-1.5 font-semibold text-slate-900">{title}</h3>
              <p className="text-sm text-slate-600">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
