import { PredictionResult, RiskLevel, Severity } from "../types.ts";

const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";

interface ModelPrediction {
  interaction: string;
  confidence: number;
  risk_level: string;
  severity?: string | null;
  structured_features: {
    analyzed_drugs?: string[];
    interaction?: string;
    risk_level?: string;
    severity?: string | null;
    confidence?: number;
  };
  base_explanation: string;
  base_precautions: string;
  base_recommendations: any[];
  side_effect_overlap?: string[];
}

interface GeminiRefinement {
  refined_explanation?: string;
  precautions?: string;
  recommendations?: any[];
  interactionMechanism?: string;
  sideEffectOverlap?: string[];
  monitoringGuideline?: string;
}

const normalizeRiskLevel = (risk: string | undefined | null): RiskLevel => {
  const value = (risk || "").toLowerCase();
  if (value === "high") return RiskLevel.HIGH;
  if (value === "moderate") return RiskLevel.MODERATE;
  if (value === "low") return RiskLevel.LOW;
  if (value === "contraindicated") return RiskLevel.CONTRAINDICATED;
  return RiskLevel.LOW;
};

const normalizeSeverity = (severity: string | undefined | null): Severity => {
  const value = (severity || "").toLowerCase();
  if (value === "severe") return Severity.SEVERE;
  if (value === "moderate") return Severity.MODERATE;
  if (value === "mild") return Severity.MILD;
  if (value === "toxic") return Severity.TOXIC;
  return Severity.MILD;
};

const safeString = (value: string | undefined | null, fallback: string): string =>
  value && value.trim().length > 0 ? value : fallback;

const safeArray = <T>(value: T[] | undefined | null, fallback: T[]): T[] =>
  Array.isArray(value) && value.length > 0 ? value : fallback;

export const runHybridPrediction = async (
  drugs: string[],
  userQuestion?: string
): Promise<PredictionResult> => {
  if (!drugs || drugs.length < 2) {
    throw new Error("At least two drugs are required for analysis.");
  }

  const payload: any = {
    drug1: drugs[0],
    drug2: drugs[1],
  };

  if (drugs[2]) payload.drug3 = drugs[2];
  if (drugs[3]) payload.drug4 = drugs[3];
  if (drugs[4]) payload.drug5 = drugs[4];

  const token = typeof window !== "undefined"
    ? window.localStorage.getItem("ddips_auth_token")
    : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const resp = await fetch(`${API_BASE_URL}/model/predict`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    throw new Error("Backend model prediction failed.");
  }

  const modelData: ModelPrediction = await resp.json();

  const classificationRisk = normalizeRiskLevel(modelData.risk_level);
  const classificationSeverity = normalizeSeverity(modelData.severity || null);

  const question =
    userQuestion ||
    `What are the clinical interaction risks, mechanisms, and management recommendations for the combination of: ${drugs.join(
      " + "
    )}?`;

  const { refineWithGemini } = await import("./geminiService.ts");

  const refinement: GeminiRefinement = await refineWithGemini(question, modelData);

  const explanation = safeString(
    refinement.refined_explanation,
    modelData.base_explanation
  );

  const monitoringGuideline = safeString(
    refinement.monitoringGuideline || refinement.precautions,
    modelData.base_precautions
  );

  const recommendations = safeArray(
    refinement.recommendations as any[],
    modelData.base_recommendations
  );

  const interactionMechanism = safeString(
    refinement.interactionMechanism,
    explanation
  );

  let sideEffectOverlap = safeArray(
    refinement.sideEffectOverlap || modelData.side_effect_overlap || [],
    []
  );

  if (sideEffectOverlap.length <= 1) {
    const sideEffectQuestion = [
      "List the primary overlapping side effects between the following drugs.",
      "Return them strictly as concise clinical labels in the sideEffectOverlap array.",
      "Do not change the interaction, confidence, risk_level, or severity.",
      "",
      `Drugs: ${drugs.join(" + ")}`
    ].join("\n");

    const secondaryRefinement: GeminiRefinement = await refineWithGemini(
      sideEffectQuestion,
      modelData
    );

    sideEffectOverlap = safeArray(
      secondaryRefinement.sideEffectOverlap || sideEffectOverlap,
      sideEffectOverlap
    );
  }

  const confidenceScore =
    typeof modelData.confidence === "number" && modelData.confidence >= 0
      ? modelData.confidence
      : 0.9;

  const finalDrugs =
    modelData.structured_features.analyzed_drugs && modelData.structured_features.analyzed_drugs.length > 0
      ? modelData.structured_features.analyzed_drugs
      : drugs;

  const result: PredictionResult = {
    id: Math.random().toString(36).substr(2, 9),
    drugs: finalDrugs,
    riskLevel: classificationRisk,
    severity: classificationSeverity,
    explanation,
    clinicalNotes: explanation,
    recommendation: monitoringGuideline,
    recommendations: recommendations as any[],
    confidenceScore,
    interactionMechanism,
    sideEffectOverlap,
    monitoringGuideline,
    timestamp: Date.now(),
  };

  return result;
};
