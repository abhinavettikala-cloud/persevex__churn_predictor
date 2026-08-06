import { useState } from "react"
import { Search, Filter, Download, MoreVertical, Trash2, Eye } from "lucide-react"
import { Card, CardContent } from "@/src/components/ui/Card"
import { Badge } from "@/src/components/ui/Badge"
import { Button } from "@/src/components/ui/Button"

// Mock Data
const historyData = [
  { id: 'PRD-7829', date: '2026-08-03', time: '14:22:05', name: 'Sarah Jenkins', prediction: 'Churn', confidence: 89, timeTaken: '142ms', version: 'v2.4.1' },
  { id: 'PRD-7828', date: '2026-08-03', time: '13:15:12', name: 'Michael Chen', prediction: 'Retain', confidence: 94, timeTaken: '128ms', version: 'v2.4.1' },
  { id: 'PRD-7827', date: '2026-08-03', time: '11:45:00', name: 'Emma Watson', prediction: 'Retain', confidence: 78, timeTaken: '156ms', version: 'v2.4.1' },
  { id: 'PRD-7826', date: '2026-08-02', time: '16:30:22', name: 'James Rodriguez', prediction: 'Churn', confidence: 92, timeTaken: '145ms', version: 'v2.4.1' },
  { id: 'PRD-7825', date: '2026-08-02', time: '09:12:45', name: 'David Smith', prediction: 'Retain', confidence: 88, timeTaken: '132ms', version: 'v2.4.1' },
  { id: 'PRD-7824', date: '2026-08-01', time: '15:20:10', name: 'Lisa Kudrow', prediction: 'Churn', confidence: 76, timeTaken: '160ms', version: 'v2.4.0' },
  { id: 'PRD-7823', date: '2026-08-01', time: '10:05:30', name: 'Tom Hardy', prediction: 'Retain', confidence: 95, timeTaken: '120ms', version: 'v2.4.0' },
]

export default function PredictionHistory() {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredData = historyData.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    item.id.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Prediction History</h1>
          <p className="mt-1 text-sm text-slate-500">View and manage past customer churn predictions.</p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <div className="p-4 border-b border-slate-200 flex flex-col sm:flex-row gap-4 items-center justify-between bg-slate-50/50 rounded-t-2xl">
            <div className="relative w-full sm:max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search by ID or Name..." 
                className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-slate-800 placeholder:text-slate-400"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline" size="sm" className="w-full sm:w-auto">
              <Filter className="mr-2 h-4 w-4" />
              Advanced Filters
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="text-[11px] font-bold text-slate-500 uppercase tracking-wider bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 font-medium">Prediction ID</th>
                  <th className="px-6 py-4 font-medium">Timestamp</th>
                  <th className="px-6 py-4 font-medium">Customer Name</th>
                  <th className="px-6 py-4 font-medium">Prediction</th>
                  <th className="px-6 py-4 font-medium">Confidence</th>
                  <th className="px-6 py-4 font-medium">Version</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredData.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-blue-600">{row.id}</td>
                    <td className="px-6 py-4">
                      <div className="text-slate-900">{row.date}</div>
                      <div className="text-slate-400 text-xs">{row.time}</div>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-900">{row.name}</td>
                    <td className="px-6 py-4">
                      <Badge variant={row.prediction === 'Churn' ? 'destructive' : 'success'}>
                        {row.prediction}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-2 rounded-full bg-slate-100 overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${row.confidence >= 90 ? 'bg-emerald-500' : row.confidence >= 80 ? 'bg-blue-500' : 'bg-amber-500'}`} 
                            style={{ width: `${row.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-slate-600">{row.confidence}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-500">{row.version}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-blue-600 hover:bg-blue-50">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-rose-600 hover:bg-rose-50">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredData.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                      No predictions found matching your search.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-4 border-t border-slate-200 flex items-center justify-between bg-slate-50/50 rounded-b-2xl">
            <span className="text-xs font-medium text-slate-500">Showing {filteredData.length} results</span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>Previous</Button>
              <Button variant="outline" size="sm">Next</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
