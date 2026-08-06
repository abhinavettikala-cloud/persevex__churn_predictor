import * as React from "react"

export type PredictionStatus = 'Completed' | 'Failed' | 'Processing';
export type RiskLevel = 'High' | 'Medium' | 'Low';

export interface PredictionRecord {
  id: string;
  date: string;
  time: string;
  customerName: string;
  prediction: string;
  confidence: number;
  probability: number;
  processingTime: string;
  modelVersion: string;
}

export interface MetricData {
  title: string;
  value: string | number;
  change: number;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ElementType;
}
