export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  auth_provider?: string;
  avatar_url?: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ScanStage {
  name: string;
  label: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'skipped';
  detail?: string;
}

export interface DetectedEntity {
  id: string;
  entity_type: string;
  confidence: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  masked_preview: string;
  page_number: number;
  sheet_name?: string;
  location_data?: any;
  detection_source?: string[];
  action: string;
}

export interface Scan {
  id: string;
  document_id?: string;
  original_filename?: string;
  file_type?: string;
  status: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_explanation?: string;
  stages: ScanStage[];
  entity_count: number;
  ocr_status: string;
  started_at: string;
  completed_at?: string;
  entities: DetectedEntity[];
  has_protected_file: boolean;
  protected_action_id?: string;
  sharing_purpose?: string;
  purpose_recommendations?: PurposeRecommendation[];
}

export interface ProtectionAction {
  id: string;
  scan_id: string;
  document_id: string;
  mode: 'MASK' | 'REDACT';
  output_filename: string;
  entities_protected: number;
  verification_passed: boolean;
  download_url: string;
  created_at: string;
}

export interface RecentScanItem {
  id: string;
  document_id?: string;
  filename: string;
  file_type: string;
  scan_date: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  entity_count: number;
  status: string;
  has_protected_file: boolean;
}

export interface DashboardStats {
  total_scans: number;
  protected_documents: number;
  high_risk_documents: number;
  total_entities_detected: number;
  pii_distribution: Record<string, number>;
  risk_distribution: Record<string, number>;
  recent_scans: RecentScanItem[];
}

export interface AuditLogItem {
  id: string;
  action: string;
  status: string;
  details?: string;
  created_at: string;
  document_id?: string;
  filename?: string;
}

export interface ModelMetrics {
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  true_negatives: number;
  precision: number;
  recall: number;
  f1: number;
  false_positive_rate: number;
  false_negative_rate: number;
  avg_latency_ms: number;
  total_samples: number;
}

export interface EvaluationReport {
  timestamp: string;
  dataset_name: string;
  total_samples: number;
  total_ground_truth_entities: number;
  models: {
    hybrid_context_aware: ModelMetrics;
    pattern_only_baseline: ModelMetrics;
  };
}

export interface PurposeRecommendation {
  entity_type: string;
  count: number;
  what: string;
  why: string;
  evidence: string;
  risk: string;
  recommended_action: 'KEEP' | 'PROTECT';
  reason: string;
}

export interface GatewayProvider {
  id: string;
  name: string;
  display_name: string;
  is_demo: boolean;
  is_available: boolean;
}

export interface GatewayAnalyzeRequest {
  prompt: string;
  provider?: string;
  session_id?: string;
}

export interface GatewayAnalyzeResponse {
  session_id: string;
  policy_decision: 'ALLOW' | 'WARN' | 'PROTECT' | 'BLOCK';
  policy_reasons: string[];
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  entities_detected: Array<{
    entity_type: string;
    masked_preview: string;
    confidence: number;
    risk_level: string;
    context_signals: string[];
  }>;
  original_prompt_preview: string;
  protected_prompt: string | null;
  provider_received_prompt: string | null;
  provider_name: string;
  provider_display_name: string;
  provider_is_demo: boolean;
  provider_raw_response: string | null;
  rehydrated_response: string | null;
  latencies_ms: {
    detection_ms: number;
    policy_ms: number;
    tokenization_ms: number;
    provider_ms: number;
    total_ms: number;
  };
  exposure_summary: {
    sensitive_values_detected: number;
    sensitive_values_transmitted_externally: number;
    protection_applied: boolean;
    tokens_mapped_count: number;
  };
}

export interface GatewayStats {
  total_requests: number;
  protected_requests: number;
  blocked_requests: number;
  total_entities_shielded: number;
  zero_cloud_exposure_guarantee: boolean;
}
