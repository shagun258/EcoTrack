export type UserRole = "USER" | "COLLECTOR" | "ADMIN";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  phone: string | null;
  points: number;
  is_active: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export type WasteCategory =
  | "Plastic" | "Paper" | "Glass" | "Metal" | "Organic" | "E-Waste" | "Textile" | "Other";

export type ReportStatus = "PENDING" | "VERIFIED" | "REJECTED" | "RESOLVED";

export interface MLPrediction {
  category: string;
  confidence: number;
  recyclable: boolean;
  recommended_disposal: string;
  mode: "demo" | "production";
}

export interface WasteReport {
  id: number;
  reporter_id: number;
  image_url: string;
  description: string | null;
  category: WasteCategory;
  status: ReportStatus;
  latitude: number;
  longitude: number;
  address: string | null;
  possible_duplicate_of: number | null;
  created_at: string;
  ml_prediction: MLPrediction | null;
}

export type PickupStatus = "PENDING" | "ASSIGNED" | "ACCEPTED" | "PICKED_UP" | "COMPLETED" | "CANCELLED";

export interface PickupRequest {
  id: number;
  requester_id: number;
  collector_id: number | null;
  waste_type: string;
  quantity_kg: number;
  address: string;
  latitude: number;
  longitude: number;
  preferred_date: string;
  preferred_time: string;
  notes: string | null;
  proof_image_url: string | null;
  status: PickupStatus;
  created_at: string;
  updated_at: string;
}

export interface RecyclingCenter {
  id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  phone: string | null;
  opening_hours: string | null;
  is_active: boolean;
  accepted_waste_types: string[];
  distance_km?: number;
}

export interface RewardTransaction {
  id: number;
  points: number;
  reason: string;
  created_at: string;
}

export interface Badge {
  id: number;
  name: string;
  description: string;
  points_required: number;
  icon: string;
}

export interface LeaderboardEntry {
  rank: number;
  user_id: number;
  full_name: string;
  points: number;
  reports_count: number;
}

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface AnalyticsOverview {
  total_users: number;
  total_waste_reports: number;
  total_pickups: number;
  pickup_completion_rate: number;
  waste_by_category: Record<string, number>;
  reports_last_30_days: Record<string, number>;
}
