export type RegionStatus = "pending" | "verified" | "rejected";
export type ElementType = "column" | "beam" | "slab" | "other";

export interface Project {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface Drawing {
  id: number;
  project_id: number;
  filename: string;
  revision: number;
  png_path?: string;
  width_px?: number;
  height_px?: number;
  created_at: string;
}

export interface DimensionVerification {
  id: number;
  change_region_id: number;
  element_type: ElementType;
  dim_before_w: number;
  dim_before_h: number;
  dim_after_w: number;
  dim_after_h: number;
  height_or_length_m: number;
  volume_before_m3: number;
  volume_after_m3: number;
  delta_volume_m3: number;
  verified_at: string;
}

export interface CostImpact {
  id: number;
  change_region_id: number;
  boq_item_id: number;
  delta_volume: number;
  unit_price: number;
  total_cost_delta: number;
  calculated_at: string;
  boq_item?: BOQItem;
}

export interface ChangeRegion {
  id: number;
  analysis_run_id: number;
  region_index: number;
  bbox_x: number;
  bbox_y: number;
  bbox_w: number;
  bbox_h: number;
  area: number;
  crop_v0_path?: string;
  crop_v1_path?: string;
  raw_text_v0?: string;
  raw_text_v1?: string;
  suggested_dim_v0?: string;
  suggested_dim_v1?: string;
  status: RegionStatus;
  verification?: DimensionVerification;
  cost_impact?: CostImpact;
}

export interface AnalysisRun {
  id: number;
  project_id: number;
  drawing_ref_id: number;
  drawing_rev_id: number;
  diff_image_path?: string;
  diff_image_url?: string | null;
  total_regions: number;
  created_at: string;
  regions: ChangeRegion[];
}

export interface BOQItem {
  id: number;
  project_id: number;
  code: string;
  description: string;
  unit: string;
  contract_volume: number;
  unit_price: number;
}

export interface ProjectSummary {
  project_id: number;
  project_name: string;
  total_drawings: number;
  total_analyses: number;
  total_changed_regions: number;
  verified_regions: number;
  total_cost_delta: number;
  boq_items_count: number;
}

export type DocumentType = "rks" | "kontrak" | "sni" | "ahsp" | "other";
export type DocumentStatus = "pending" | "indexed" | "failed";

export interface Document {
  id: number;
  project_id: number;
  filename: string;
  doc_type: DocumentType;
  status: DocumentStatus;
  num_chunks: number;
  error_message?: string | null;
  uploaded_at: string;
}

export interface ChatSource {
  filename: string;
  page?: number | null;
  snippet: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}

// --- BOQ & RAB (AHSP) ---

export type AHSPComponentType = "labor" | "material" | "equipment";

export interface AHSPComponent {
  id: number;
  component_type: AHSPComponentType;
  name: string;
  coefficient: number;
  unit: string;
  base_price: number;
  subtotal: number;
}

export interface AHSPItem {
  id: number;
  code: string;
  name: string;
  unit: string;
  category?: string | null;
  unit_price: number;
  components: AHSPComponent[];
}

export interface RABLine {
  boq_item_id: number;
  code: string;
  description: string;
  unit: string;
  contract_volume: number;
  delta_volume: number;
  adjusted_volume: number;
  unit_price: number;
  contract_amount: number;
  adjusted_amount: number;
  delta_amount: number;
  ahsp_item_id?: number | null;
  ahsp_code?: string | null;
}

export interface RABResponse {
  project_id: number;
  project_name: string;
  lines: RABLine[];
  total_contract: number;
  total_adjusted: number;
  total_delta: number;
  item_count: number;
  verified_region_count: number;
}

export interface BOQSuggestion {
  region_id: number;
  element_type: string;
  suggested_boq_item_id?: number | null;
  suggested_code?: string | null;
  suggested_description?: string | null;
  unit_price?: number | null;
  reason: string;
}

// --- Fase 4: Auth ---

export type UserRole = "admin" | "engineer" | "viewer";

export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string | null;
}

// --- Fase 4: Background jobs ---

export type JobStatus = "pending" | "running" | "success" | "failed";

export interface Job {
  id: number;
  project_id?: number | null;
  job_type: string;
  status: JobStatus;
  result?: unknown;
  error_message?: string | null;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
}

export interface JobEnqueueResponse {
  job_id: number;
  status: JobStatus;
  message: string;
}

// --- Progress & EVM ---

export interface ProgressPoint {
  period: string;
  planned_pct: number;
  actual_pct: number;
  planned_value: number;
  earned_value: number;
  actual_cost: number;
}

export interface ProgressSummary {
  project_id: number;
  project_name: string;
  bac: number;
  pv: number;
  ev: number;
  ac: number;
  sv: number;
  cv: number;
  spi: number;
  cpi: number;
  eac: number;
  etc: number;
  vac: number;
  progress_pct: number;
  periods: ProgressPoint[];
}

export interface ProgressEntry {
  id: number;
  project_id: number;
  period: string;
  planned_pct: number;
  actual_pct: number;
  actual_cost: number;
  note?: string | null;
  created_at: string;
}

// --- VO & RFI ---

export type VOStatus = "draft" | "submitted" | "approved" | "rejected";
export type RFIStatus = "open" | "answered" | "closed";

export interface VariationOrder {
  id: number;
  project_id: number;
  vo_number: string;
  title: string;
  description?: string | null;
  status: VOStatus;
  amount: number;
  change_region_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface RFI {
  id: number;
  project_id: number;
  rfi_number: string;
  subject: string;
  question: string;
  answer?: string | null;
  status: RFIStatus;
  variation_order_id?: number | null;
  created_at: string;
  answered_at?: string | null;
}

// --- QC / Mutu ---

export type InspectionCategory = "concrete" | "rebar" | "formwork" | "other";
export type InspectionStatus = "draft" | "passed" | "failed";
export type CheckResult = "ok" | "not_ok" | "na";

export interface InspectionItem {
  id: number;
  inspection_id: number;
  description: string;
  standard?: string | null;
  result: CheckResult;
  note?: string | null;
}

export interface Inspection {
  id: number;
  project_id: number;
  inspection_number: string;
  title: string;
  location?: string | null;
  category: InspectionCategory;
  status: InspectionStatus;
  inspector?: string | null;
  inspected_at?: string | null;
  note?: string | null;
  created_at: string;
  items: InspectionItem[];
}

export interface QCSummary {
  project_id: number;
  total: number;
  passed: number;
  failed: number;
  draft: number;
  pass_rate: number;
  total_items: number;
  not_ok_items: number;
}

// --- K3 / Safety ---

export type SafetyCategory = "incident" | "near_miss" | "unsafe_act" | "unsafe_condition";
export type Severity = "low" | "medium" | "high" | "critical";
export type SafetyStatus = "open" | "investigating" | "closed";

export interface SafetyReport {
  id: number;
  project_id: number;
  report_number: string;
  title: string;
  category: SafetyCategory;
  severity: Severity;
  description: string;
  action_taken?: string | null;
  status: SafetyStatus;
  reported_by?: string | null;
  occurred_at?: string | null;
  created_at: string;
}

export interface SafetySummary {
  project_id: number;
  total: number;
  open: number;
  investigating: number;
  closed: number;
  by_severity: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}
