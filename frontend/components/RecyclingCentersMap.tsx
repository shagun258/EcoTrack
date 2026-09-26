"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import type { RecyclingCenter } from "@/types";

// Leaflet's default marker icons reference image files that don't resolve
// correctly under Next.js's bundler - point them at the CDN explicitly.
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export function RecyclingCentersMap({ centers, center }: { centers: RecyclingCenter[]; center: [number, number] }) {
  return (
    <MapContainer center={center} zoom={12} scrollWheelZoom style={{ height: "100%", width: "100%", borderRadius: "1rem" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {centers.map((c) => (
        <Marker key={c.id} position={[c.latitude, c.longitude]} icon={icon}>
          <Popup>
            <strong>{c.name}</strong>
            <br />
            {c.address}
            <br />
            {c.accepted_waste_types.join(", ")}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
