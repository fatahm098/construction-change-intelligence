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
