export interface UserResponse {
  id: string;
  email: string;
  is_active: boolean;
  subscription_tier: "free" | "basic" | "pro";
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface MajorPeriod {
  index: number;
  start_age: number;
  end_age: number;
  palace_branch: number;
  palace_name: string;
}

export interface ChartResponse {
  id: string;
  gregorian_date: string;
  birth_time: string;
  is_male: boolean;
  lunar_year: number;
  lunar_month: number;
  lunar_day: number;
  is_leap_month: boolean;
  year_stem: number;
  year_branch: number;
  ming_branch: number;
  wu_xing_ju: number;
  star_placements: Record<string, number>; // star name → branch index
  major_periods: MajorPeriod[];
  created_at: string;
}

export interface ChartRequest {
  gregorian_date: string;
  birth_time: string;
  is_male: boolean;
  timezone_offset: number;
}

export type ReadingType = "core" | "relationship" | "career" | "annual";
export type ReadingStatus = "pending" | "generating" | "complete" | "failed";

export interface ReadingResponse {
  id: string;
  chart_id: string;
  reading_type: ReadingType;
  status: ReadingStatus;
  content: string | null;
  created_at: string;
  completed_at: string | null;
}
