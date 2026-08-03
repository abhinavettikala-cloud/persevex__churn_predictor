import React from 'react';

interface GaugeChartProps {
  score: number;
  label: string;
}

export default function GaugeChart({ score, label }: GaugeChartProps) {
  const radius = 80;
  const strokeWidth = 16;
  const circumference = 2 * Math.PI * radius;
  // For full circle, max dash array is circumference
  const strokeDashoffset = circumference - score * circumference;

  const color = score > 0.7 ? '#f43f5e' : score > 0.4 ? '#f59e0b' : '#10b981';
  const labelText = score > 0.7 ? 'High Risk' : score > 0.4 ? 'Medium Risk' : 'Low Risk';

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative w-48 h-48">
        <svg
          className="w-full h-full transform -rotate-90"
          viewBox="0 0 192 192"
        >
          {/* Background Circle */}
          <circle
            cx="96"
            cy="96"
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
          />
          {/* Foreground Circle */}
          <circle
            cx="96"
            cy="96"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-black text-slate-800">
            {Math.round(score * 100)}%
          </span>
          <span className="text-[10px] font-bold uppercase tracking-widest mt-1" style={{ color }}>
            {labelText}
          </span>
        </div>
      </div>
    </div>
  );
}
