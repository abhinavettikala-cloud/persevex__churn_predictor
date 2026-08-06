import * as React from "react"
import { Card, CardContent } from "@/src/components/ui/Card"
import { cn } from "@/src/lib/utils"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import type { MetricData } from "@/src/types"

interface MetricCardProps {
  data: MetricData
  className?: string
  key?: string
}

export function MetricCard({ data, className }: MetricCardProps) {
  const Icon = data.icon

  return (
    <Card className={cn("bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow", className)}>
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-2">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-tighter">{data.title}</span>
          <div className={cn("p-2 rounded-lg", 
            data.title.includes("Churn") && !data.title.includes("Non") ? "bg-rose-50 text-rose-600" :
            data.title.includes("Accuracy") ? "bg-emerald-50 text-emerald-600" :
            data.title.includes("Time") ? "bg-amber-50 text-amber-600" :
            "bg-blue-50 text-blue-600"
          )}>
            <Icon className="w-4 h-4" />
          </div>
        </div>
        <h3 className="text-2xl font-bold text-slate-900">{data.value}</h3>
        <div className="flex items-center mt-1">
          <span
            className={cn(
              "text-xs font-semibold",
              data.trend === "up" && (data.title.includes("Churn") && !data.title.includes("Non") ? "text-rose-600" : "text-emerald-600"),
              data.trend === "down" && (data.title.includes("Churn") && !data.title.includes("Non") ? "text-emerald-600" : "text-rose-600"),
              data.trend === "neutral" && "text-slate-400"
            )}
          >
            {data.change > 0 ? "+" : ""}{data.change}%
          </span>
          <span className="text-[10px] text-slate-400 ml-1">since last month</span>
        </div>
      </CardContent>
    </Card>
  )
}
