import { Card, CardHeader, CardTitle, CardContent } from "@/src/components/ui/Card"
import { Badge } from "@/src/components/ui/Badge"
import { Activity, Database, Server, Cpu, Clock, CheckCircle2 } from "lucide-react"

export default function SystemStatus() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">System Status</h1>
        <p className="mt-1 text-sm text-slate-500">Real-time monitoring of application infrastructure and APIs.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-50 rounded-lg text-green-600">
                  <Activity className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">API Status</h3>
                  <p className="text-sm text-gray-500">Prediction Engine</p>
                </div>
              </div>
              <Badge variant="success">Operational</Badge>
            </div>
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Uptime</span>
                <span className="font-medium text-gray-900">99.99%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Response Time</span>
                <span className="font-medium text-gray-900">~120ms</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-50 rounded-lg text-green-600">
                  <Database className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Database</h3>
                  <p className="text-sm text-gray-500">PostgreSQL Primary</p>
                </div>
              </div>
              <Badge variant="success">Operational</Badge>
            </div>
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Load</span>
                <span className="font-medium text-gray-900">14%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Connections</span>
                <span className="font-medium text-gray-900">142 / 500</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-50 rounded-lg text-green-600">
                  <Server className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Model Server</h3>
                  <p className="text-sm text-gray-500">XGBoost Inference Worker</p>
                </div>
              </div>
              <Badge variant="success">Operational</Badge>
            </div>
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Memory Usage</span>
                <span className="font-medium text-gray-900">2.1 GB</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Worker Nodes</span>
                <span className="font-medium text-gray-900">4 Active</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent System Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { time: '14:22:05', msg: 'Prediction model inference completed successfully (142ms)' },
              { time: '13:15:12', msg: 'Database backup completed' },
              { time: '11:00:00', msg: 'System health check passed' },
              { time: '09:45:22', msg: 'New user batch uploaded for batch prediction' }
            ].map((log, i) => (
              <div key={i} className="flex items-start gap-3 text-sm">
                <span className="text-gray-400 font-mono w-20">{log.time}</span>
                <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                <span className="text-gray-700">{log.msg}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
