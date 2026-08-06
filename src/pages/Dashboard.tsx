import { Users, UserMinus, Activity, Clock, Target, TrendingUp, AlertCircle, Database } from "lucide-react"
import { MetricCard } from "@/src/components/ui/MetricCard"
import { Card, CardHeader, CardTitle, CardContent } from "@/src/components/ui/Card"
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, LineChart, Line, Legend
} from "recharts"

const metrics = [
  { title: "Total Predictions", value: "12,450", change: 12.5, trend: "up" as const, icon: Activity },
  { title: "Today's Predictions", value: "342", change: 5.2, trend: "up" as const, icon: Clock },
  { title: "Churn Customers", value: "2,105", change: -2.4, trend: "down" as const, icon: UserMinus },
  { title: "Non-Churn Customers", value: "10,345", change: 4.1, trend: "up" as const, icon: Users },
  { title: "Prediction Accuracy", value: "94.2%", change: 1.2, trend: "up" as const, icon: Target },
  { title: "Average Confidence", value: "88.5%", change: -0.5, trend: "down" as const, icon: TrendingUp },
  { title: "Avg Response Time", value: "145ms", change: 0, trend: "neutral" as const, icon: AlertCircle },
  { title: "Active Model", value: "v2.4.1", change: 0, trend: "neutral" as const, icon: Database },
]

const areaData = [
  { name: 'Mon', churn: 400, nonChurn: 2400 },
  { name: 'Tue', churn: 300, nonChurn: 1398 },
  { name: 'Wed', churn: 200, nonChurn: 9800 },
  { name: 'Thu', churn: 278, nonChurn: 3908 },
  { name: 'Fri', churn: 189, nonChurn: 4800 },
  { name: 'Sat', churn: 239, nonChurn: 3800 },
  { name: 'Sun', churn: 349, nonChurn: 4300 },
];

const confidenceData = [
  { name: 'Week 1', confidence: 85 },
  { name: 'Week 2', confidence: 86 },
  { name: 'Week 3', confidence: 88 },
  { name: 'Week 4', confidence: 87.5 },
  { name: 'Week 5', confidence: 89 },
];

export default function Dashboard() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Executive Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Overview of model predictions and customer churn metrics.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} data={metric} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 bg-slate-50 border border-slate-200 relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle>Prediction Trend (Weekly)</CardTitle>
            <div className="flex gap-2">
              <span className="px-2 py-1 bg-white border border-slate-200 rounded text-[10px] font-bold">Daily</span>
              <span className="px-2 py-1 bg-blue-600 text-white rounded text-[10px] font-bold shadow-sm">Weekly</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={areaData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorChurn" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorNonChurn" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Legend iconType="circle" />
                  <Area type="monotone" dataKey="nonChurn" name="Non-Churn" stroke="#2563eb" fillOpacity={1} fill="url(#colorNonChurn)" />
                  <Area type="monotone" dataKey="churn" name="Churn" stroke="#ef4444" fillOpacity={1} fill="url(#colorChurn)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Model Confidence Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={confidenceData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis domain={['auto', 'auto']} stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}%`} />
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Line type="monotone" dataKey="confidence" name="Avg Confidence %" stroke="#10b981" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
