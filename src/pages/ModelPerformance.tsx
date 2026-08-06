import { Card, CardHeader, CardTitle, CardContent } from "@/src/components/ui/Card"
import { Badge } from "@/src/components/ui/Badge"
import { CheckCircle2, Cpu, Database, Zap } from "lucide-react"

export default function ModelPerformance() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Model Performance</h1>
        <p className="mt-1 text-sm text-slate-500">Evaluate model metrics, ROC curves, and cross-validation scores.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1 bg-gradient-to-br from-blue-900 to-slate-900 text-white border-none">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              Active Model
              <Badge variant="success" className="bg-green-500/20 text-green-300 border-none">Deployed</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="text-3xl font-bold">XGBoost Classifier</div>
              <div className="text-blue-300 mt-1">Version 2.4.1</div>
            </div>
            
            <div className="space-y-3 pt-4 border-t border-slate-700/50">
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Training Samples</span>
                <span className="font-medium">5,634</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Testing Samples</span>
                <span className="font-medium">1,409</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Features Used</span>
                <span className="font-medium">24</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400 text-sm">Inference Time</span>
                <span className="font-medium">~120ms</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Accuracy', value: '82.4%', icon: CheckCircle2 },
            { label: 'Precision', value: '78.1%', icon: Zap },
            { label: 'Recall', value: '85.2%', icon: Database },
            { label: 'F1 Score', value: '81.5%', icon: Cpu },
            { label: 'ROC-AUC', value: '0.892', icon: Zap },
            { label: 'Log Loss', value: '0.341', icon: Cpu },
          ].map(metric => (
            <Card key={metric.label}>
              <CardContent className="p-4 sm:p-6 flex flex-col justify-center items-center text-center h-full space-y-2">
                <metric.icon className="h-6 w-6 text-blue-500 mb-2" />
                <div className="text-2xl font-bold text-slate-900">{metric.value}</div>
                <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">{metric.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Why this Model?</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-600 leading-relaxed max-w-4xl">
            The <strong>XGBoost</strong> model outperformed standard Logistic Regression and Random Forest in cross-validation tests by maintaining a high Recall rate (85.2%) without sacrificing overall Precision. In telecom churn prediction, identifying at-risk customers early (Recall) is typically more valuable than avoiding false positives. Furthermore, XGBoost handles non-linear relationships in customer tenure and monthly charges natively, leading to a superior ROC-AUC score of 0.892.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
