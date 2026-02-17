
import { GoogleGenAI, Type } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const responseSchema = {
  type: Type.OBJECT,
  properties: {
    refined_explanation: { type: Type.STRING },
    precautions: { type: Type.STRING },
    monitoringGuideline: { type: Type.STRING },
    interactionMechanism: { type: Type.STRING },
    sideEffectOverlap: { type: Type.ARRAY, items: { type: Type.STRING } },
    recommendations: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          saferAlternative: { type: Type.STRING },
          comparisonReason: { type: Type.STRING },
          clinicalBenefit: { type: Type.STRING },
          efficacyComparison: { type: Type.STRING },
          sideEffectProfile: { type: Type.STRING },
          contraindicationSummary: { type: Type.STRING },
          benefitScore: { type: Type.NUMBER }
        }
      }
    }
  }
};

export const refineWithGemini = async (
  userQuestion: string,
  modelOutput: any
): Promise<any> => {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-pro-preview",
      contents: [
        {
          role: "user",
          parts: [
            {
              text: [
                "You are a clinical pharmacologist specializing in drug-drug interactions.",
                "",
                "You are given:",
                "- A user question or analysis request.",
                "- The JSON output of an authoritative Deep Learning DDI model.",
                "",
                "STRICT POLICY:",
                "- You MUST respect the model classification fields:",
                "  interaction, confidence, risk_level, severity.",
                "- You are NOT allowed to override or contradict these fields.",
                "- Do NOT change the interpretation of interaction presence or severity.",
                "",
                "ALLOWED ACTIONS:",
                "- Refine and clarify the natural language explanation.",
                "- Add clinically conservative safety insights and monitoring precautions.",
                "- Provide structured therapeutic recommendations and safer alternatives.",
                "- Improve formatting and structure for clinical readability.",
                "",
                "PROHIBITED ACTIONS:",
                "- Do NOT modify interaction, confidence, risk_level, or severity.",
                "- Do NOT downplay or upgrade the model's risk assessment.",
                "- Do NOT introduce new hard classifications.",
                "",
                "OUTPUT REQUIREMENTS:",
                "- Return only JSON following the provided response schema.",
                "- If you lack information for any field, leave it empty; the client will fall back to model-generated text.",
                "",
                "User Question:",
                userQuestion,
                "",
                "Authoritative Model Output JSON:",
                JSON.stringify(modelOutput, null, 2)
              ].join("\n"),
            },
          ],
        },
      ],
      config: {
        systemInstruction:
          "You are a refinement layer, not a decision engine. Never override model classification.",
        responseMimeType: "application/json",
        responseSchema,
      },
    });

    const text = (response as any).text || "{}";
    const data = JSON.parse(text);
    return data;
  } catch (error) {
    console.error("Gemini refinement failed:", error);
    return {};
  }
};
