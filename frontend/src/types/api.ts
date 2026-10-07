/**
 * API types for ClaimLens.
 * Synced with backend Pydantic schemas.
 */

export type ClaimOutcome =
  | 'supported'
  | 'contradicted'
  | 'conflicting'
  | 'insufficient'
  | 'not_checkable';

export type AnalysisStatus =
  | 'queued'
  | 'running'
  | 'completed'
  | 'partial'
  | 'failed'
  | 'cancelled';

export type EvidenceMode = 'local' | 'live' | 'auto';

export type EvidenceStance = 'supports' | 'contradicts' | 'neutral';

export type ProvenanceCategory = 'documented' | 'partially_documented' | 'unknown';

export interface CredibilitySignal {
  name: string;
  value: string | number;
  status: 'observed' | 'unknown' | 'not_applicable';
  supporting_url?: string;
  reason?: string;
  last_reviewed?: string;
}

export interface SourceCredibility {
  provenance_category: ProvenanceCategory;
  signals: CredibilitySignal[];
}

export interface LinguisticFeatures {
  entities?: Array<{ text: string; label: string }> | string[];
  dates?: string[];
  numbers?: string[];
  noun_phrases?: string[];
  has_negation?: boolean;
  has_qualifier?: boolean;
  has_attribution?: boolean;
}

export interface EvidenceItem {
  id: string;
  doc_id?: string;
  title?: string;
  publisher?: string;
  url?: string;
  publication_date?: string;
  excerpt: string;
  full_context?: string;
  stance: EvidenceStance;
  stance_scores?: {
    entailment?: number;
    contradiction?: number;
    neutral?: number;
  };
  relevance_score?: number;
  source_credibility?: SourceCredibility;
}

export interface ClaimResult {
  id: string;
  claim_text: string;
  original_sentence?: string;
  char_start?: number;
  char_end?: number;
  outcome: ClaimOutcome;
  reason?: string;
  evidence: EvidenceItem[];
  linguistic_features?: LinguisticFeatures;
}

export interface AnalysisReport {
  input_summary?: string;
  analysis_date: string;
  evidence_mode: EvidenceMode;
  corpus_version?: string;
  model_versions?: Record<string, string>;
  claims: ClaimResult[];
  coverage_warnings: string[];
}

export interface AnalysisRequest {
  input_text?: string;
  input_url?: string;
  evidence_mode?: EvidenceMode;
}

export interface AnalysisResponse {
  id: string;
  status: AnalysisStatus;
  stage?: string;
  created_at: string;
  completed_at?: string;
  report?: AnalysisReport;
  access_token?: string;
}

export interface HealthResponse {
  status: string;
}

export interface ReadinessResponse {
  ready: boolean;
  models: Record<string, string>;
  corpus: {
    loaded: boolean;
    version: string;
    passages: number;
  };
  providers: {
    brave_configured: boolean;
    google_factcheck_configured: boolean;
  };
}
