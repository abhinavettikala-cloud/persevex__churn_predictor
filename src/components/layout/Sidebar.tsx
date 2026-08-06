import { NavLink } from "react-router-dom"
import { 
  LayoutDashboard, 
  Wand2, 
  History, 
  BarChart3, 
  BrainCircuit, 
  FileText, 
  Settings, 
  Info,
  Activity
} from "lucide-react"
import { cn } from "@/src/lib/utils"

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Make Prediction", href: "/predict", icon: Wand2 },
  { name: "Prediction History", href: "/history", icon: History },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Model Performance", href: "/performance", icon: BrainCircuit },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "System Status", href: "/status", icon: Activity },
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "About", href: "/about", icon: Info },
]

export function Sidebar() {
  return (
    <div className="hidden border-r border-slate-200 bg-slate-50 md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 h-full">
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
            <BrainCircuit className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-slate-800">ChurnAI</span>
        </div>
        <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Enterprise Edition</p>
      </div>
      <div className="flex flex-1 flex-col overflow-y-auto px-4 py-4 space-y-1">
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "group flex items-center rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer gap-3",
                  isActive
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-500 hover:bg-slate-100"
                )
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon
                    className={cn(
                      "h-5 w-5 flex-shrink-0 transition-colors",
                      isActive ? "text-blue-700" : "text-slate-500 group-hover:text-slate-600"
                    )}
                    aria-hidden="true"
                  />
                  {item.name}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 mt-auto border-t border-slate-200 bg-slate-100/50 rounded-xl mb-4">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-[11px] text-slate-500 uppercase font-bold tracking-widest">System Health</span>
              <span className="flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">API Gateway</span>
              <span className="font-mono text-emerald-600">Online</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-500">Model v2.4.1</span>
              <span className="font-mono text-emerald-600">Stable</span>
            </div>
            <div className="flex items-center gap-3 pt-4 border-t border-slate-200">
              <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center">
                <span className="text-xs font-bold text-slate-600">AC</span>
              </div>
              <div>
                <p className="text-xs font-bold text-slate-800">Alex Chen</p>
                <p className="text-[10px] text-slate-500">Lead Analyst</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
