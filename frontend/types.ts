
export enum RiskLevel {
  LOW = 'LOW',
  MODERATE = 'MODERATE',
  HIGH = 'HIGH',
  CONTRAINDICATED = 'CONTRAINDICATED'
}

export enum Severity {
  MILD = 'MILD',
  MODERATE = 'MODERATE',
  SEVERE = 'SEVERE',
  TOXIC = 'TOXIC'
}

export interface Recommendation {
  saferAlternative: string;
  comparisonReason: string;
  clinicalBenefit: string;
  efficacyComparison: string;
  sideEffectProfile: string;
  contraindicationSummary: string;
  benefitScore: number; // 0-100 representing clinical advantage
}

export interface PredictionResult {
  id: string;
  drugs: string[];
  riskLevel: RiskLevel;
  severity: Severity;
  explanation: string;
  clinicalNotes: string;
  recommendation: string;
  recommendations?: Recommendation[];
  confidenceScore: number;
  interactionMechanism: string;
  sideEffectOverlap: string[];
  monitoringGuideline: string;
  timestamp: number;
}

export interface AppState {
  view: 'landing' | 'auth' | 'dashboard';
  currentDashboard: 'analysis' | 'explain' | 'safety' | 'recs' | 'history' | 'analytics' | 'settings';
  isAuthenticated: boolean;
  isLoading: boolean;
  currentPrediction: PredictionResult | null;
  history: PredictionResult[];
  error: string | null;
  userName: string | null;
}
