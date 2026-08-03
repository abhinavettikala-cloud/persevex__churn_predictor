export interface CustomerData {
  gender: string;
  seniorCitizen: string;
  partner: string;
  dependents: string;
  tenure: number;
  phoneService: string;
  internetService: string;
  contract: string;
  monthlyCharges: number;
  totalCharges: number;
  paymentMethod: string;
}

export interface PredictionResult {
  prediction: "Churn" | "No Churn";
  probability: number;
  confidence_score: number;
  timestamp: string;
}

export interface HistoryRecord {
  id: string;
  data: CustomerData;
  result: PredictionResult;
}
