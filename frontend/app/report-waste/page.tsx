"use client";

import { useState, useRef } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useToast } from "@/lib/toast-context";
import { api } from "@/lib/api";
import { Camera, MapPin, Loader2, CheckCircle2, Upload } from "lucide-react";
import { useRouter } from "next/navigation";

const CATEGORIES = ["Plastic", "Paper", "Glass", "Metal", "Organic", "E-Waste", "Textile", "Other"];

function ReportWasteContent() {
  const { show } = useToast();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [description, setDescription] = useState("");
  const [manualCategory, setManualCategory] = useState("");
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);
  const [address, setAddress] = useState("");
  const [locating, setLocating] = useState(false);
  const [classifying, setClassifying] = useState(false);
  const [prediction, setPrediction] = useState<{ category: string; confidence: number; recyclable: boolean; recommended_disposal: string; mode: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setPrediction(null);

    setClassifying(true);
    try {
      const formData = new FormData();
      formData.append("image", file);
      const res = await api.post("/api/ml/classify", formData);
      setPrediction(res.data);
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not classify image");
    } finally {
      setClassifying(false);
    }
  }

  function useMyLocation() {
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLocating(false);
      },
      () => {
        show("error", "Could not access your location. Enter an address manually instead.");
        setLocating(false);
      }
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!imageFile) return show("error", "Please upload an image first");
    if (!coords) return show("error", "Please share your location");

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append("image", imageFile);
      formData.append("latitude", String(coords.lat));
      formData.append("longitude", String(coords.lng));
      if (description) formData.append("description", description);
      if (address) formData.append("address", address);
      if (manualCategory) formData.append("manual_category", manualCategory);

      await api.post("/api/waste/report", formData);
      show("success", "Waste report submitted! You earned 10 points.");
      router.push("/waste-reports");
    } catch (err: any) {
      show("error", err?.response?.data?.detail || "Could not submit report");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <h1 className="mb-1 text-2xl font-bold text-slate-900">Report Waste</h1>
      <p className="mb-6 text-sm text-slate-500">Upload a photo and we&apos;ll classify it automatically.</p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="card p-6">
          <label className="label">Photo</label>
          <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" onChange={handleFileChange} className="hidden" />
          {imagePreview ? (
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={imagePreview} alt="Waste preview" className="h-64 w-full rounded-xl object-cover" />
              <button type="button" onClick={() => fileInputRef.current?.click()} className="btn-secondary absolute bottom-3 right-3">
                <Upload className="h-4 w-4" /> Change
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex h-64 w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 text-slate-500 hover:border-eco-400 hover:text-eco-600"
            >
              <Camera className="h-8 w-8" />
              <span className="text-sm font-medium">Click to upload a photo</span>
              <span className="text-xs">JPEG, PNG or WEBP, up to 8MB</span>
            </button>
          )}

          {classifying && (
            <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" /> Classifying image…
            </div>
          )}

          {prediction && (
            <div className="mt-4 rounded-xl border border-eco-100 bg-eco-50 p-4">
              <div className="mb-1 flex items-center gap-2 text-eco-800">
                <CheckCircle2 className="h-4 w-4" />
                <span className="font-semibold">{prediction.category}</span>
                <span className="text-xs text-eco-600">({Math.round(prediction.confidence * 100)}% confidence)</span>
                {prediction.mode === "demo" && <span className="badge bg-amber-100 text-amber-700">Demo prediction</span>}
              </div>
              <p className="text-sm text-eco-700">
                {prediction.recyclable ? "Recyclable" : "Not typically recyclable"} — recommended disposal: {prediction.recommended_disposal}
              </p>
            </div>
          )}
        </div>

        <div className="card space-y-4 p-6">
          <div>
            <label className="label">Description (optional)</label>
            <textarea className="input" rows={3} placeholder="Describe what you found..." value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>

          <div>
            <label className="label">Override category (optional)</label>
            <select className="input" value={manualCategory} onChange={(e) => setManualCategory(e.target.value)}>
              <option value="">Use AI prediction</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Location</label>
            {coords ? (
              <div className="flex items-center gap-2 text-sm text-eco-700">
                <MapPin className="h-4 w-4" /> Location captured ({coords.lat.toFixed(4)}, {coords.lng.toFixed(4)})
              </div>
            ) : (
              <button type="button" onClick={useMyLocation} disabled={locating} className="btn-secondary">
                {locating ? <Loader2 className="h-4 w-4 animate-spin" /> : <MapPin className="h-4 w-4" />}
                Use My Current Location
              </button>
            )}
            <input className="input mt-3" placeholder="Address (optional)" value={address} onChange={(e) => setAddress(e.target.value)} />
          </div>
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full py-3">
          {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
          Submit Report
        </button>
      </form>
    </div>
  );
}

export default function ReportWastePage() {
  return (
    <ProtectedRoute allowedRoles={["USER"]}>
      <ReportWasteContent />
    </ProtectedRoute>
  );
}
