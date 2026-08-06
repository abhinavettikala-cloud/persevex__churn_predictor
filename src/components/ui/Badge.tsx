import * as React from "react"
import { cn } from "@/src/lib/utils"

export interface BadgeProps {
  variant?: "default" | "secondary" | "destructive" | "outline" | "success" | "warning"
  className?: string
  children?: React.ReactNode
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] uppercase font-bold tracking-wider",
        {
          "bg-blue-600 text-white shadow-sm": variant === "default",
          "bg-slate-100 text-slate-800": variant === "secondary",
          "bg-rose-50 text-rose-600 border border-rose-100": variant === "destructive",
          "bg-emerald-50 text-emerald-600 border border-emerald-100": variant === "success",
          "bg-amber-50 text-amber-600 border border-amber-100": variant === "warning",
          "border border-slate-200 text-slate-800": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
