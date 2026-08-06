import * as React from "react"
import { useState } from "react"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/src/components/ui/Card"
import { Button } from "@/src/components/ui/Button"
import { Badge } from "@/src/components/ui/Badge"
import { ShieldAlert, CheckCircle2, RotateCcw, Play, AlertCircle, RefreshCw } from "lucide-react"

interface PredictionResponse {
  prediction: 'Churn' | 'No Churn'
  churn_label: number
  probability: number
  confidence_score: number
  risk_level: 'High' | 'Medium' | 'Low'
  timestamp: string
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export default function MakePrediction() {
  const [formData, setFormData] = useState({
    gender: 'Female',
    SeniorCitizen: 0,
    Partner: 'Yes',
    Dependents: 'No',
    tenure: 12,
    PhoneService: 'Yes',
    MultipleLines: 'No',
    InternetService: 'Fiber optic',
    OnlineSecurity: 'No',
    OnlineBackup: 'Yes',
    DeviceProtection: 'No',
    TechSupport: 'No',
    StreamingTV: 'Yes',
    StreamingMovies: 'No',
    Contract: 'Month-to-month',
    PaperlessBilling: 'Yes',
    PaymentMethod: 'Electronic check',
    MonthlyCharges: 70.35,
    TotalCharges: 844.20
  })

  const [isPredicting, setIsPredicting] = useState(false)
  const [result, setResult] = useState<PredictionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : name === 'SeniorCitizen' ? parseInt(value, 10) : value
    }))
  }

  const executePredictionFetch = async (retryCount = 2, delayMs = 1000): Promise<PredictionResponse> => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 10000) // 10s timeout

    try {
      const response = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formData),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        let errorDetail = `HTTP ${response.status} ${response.statusText}`
        try {
          const errData = await response.json()
          errorDetail = errData.detail || errData.message || errorDetail
        } catch {
          // Fallback to HTTP status
        }
        throw new Error(errorDetail)
      }

      return await response.json()
    } catch (err: any) {
      clearTimeout(timeoutId)
      if (retryCount > 0 && err.name !== 'AbortError') {
        await new Promise(res => setTimeout(res, delayMs))
        return executePredictionFetch(retryCount - 1, delayMs * 1.5)
      }
      throw err
    }
  }

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsPredicting(true)
    setError(null)
    setResult(null)

    try {
      const data = await executePredictionFetch()
      setResult(data)
    } catch (err: any) {
      console.error('Prediction API call failed:', err)
      setError(
        err.name === 'AbortError'
          ? 'Request timed out. Backend server took too long to respond.'
          : err.message || 'Unable to connect to prediction API service.'
      )
    } finally {
      setIsPredicting(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setFormData({
      gender: 'Female',
      SeniorCitizen: 0,
      Partner: 'Yes',
      Dependents: 'No',
      tenure: 12,
      PhoneService: 'Yes',
      MultipleLines: 'No',
      InternetService: 'Fiber optic',
      OnlineSecurity: 'No',
      OnlineBackup: 'Yes',
      DeviceProtection: 'No',
      TechSupport: 'No',
      StreamingTV: 'Yes',
      StreamingMovies: 'No',
      Contract: 'Month-to-month',
      PaperlessBilling: 'Yes',
      PaymentMethod: 'Electronic check',
      MonthlyCharges: 70.35,
      TotalCharges: 844.20
    })
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Make Customer Churn Prediction</h1>
        <p className="mt-1 text-sm text-slate-500">
          Enter customer subscription details across all 19 attributes to run the real FastAPI ML pipeline model.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start space-x-3" role="alert">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-red-800">API Connection Failed</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <p className="text-xs text-red-600 mt-2">
              Ensure FastAPI backend is running at <code className="bg-red-100 px-1 py-0.5 rounded">{API_BASE_URL}</code>.
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={handlePredict} className="border-red-300 text-red-700 hover:bg-red-100">
            <RefreshCw className="h-4 w-4 mr-1" /> Retry
          </Button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Customer Information (19 Required Features)</CardTitle>
            </CardHeader>
            <CardContent>
              <form id="prediction-form" onSubmit={handlePredict} className="space-y-6">
                
                {/* 1. Demographics */}
                <div className="space-y-4">
                  <h4 className="text-sm font-semibold text-slate-900 border-b pb-2">1. Demographics</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="gender" className="block text-sm font-medium text-slate-700">Gender</label>
                      <select
                        id="gender"
                        name="gender"
                        value={formData.gender}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Female">Female</option>
                        <option value="Male">Male</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="SeniorCitizen" className="block text-sm font-medium text-slate-700">Senior Citizen</label>
                      <select
                        id="SeniorCitizen"
                        name="SeniorCitizen"
                        value={formData.SeniorCitizen}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value={0}>No (0)</option>
                        <option value={1}>Yes (1)</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="Partner" className="block text-sm font-medium text-slate-700">Partner</label>
                      <select
                        id="Partner"
                        name="Partner"
                        value={formData.Partner}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="Dependents" className="block text-sm font-medium text-slate-700">Dependents</label>
                      <select
                        id="Dependents"
                        name="Dependents"
                        value={formData.Dependents}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* 2. Subscription & Phone / Internet Services */}
                <div className="space-y-4">
                  <h4 className="text-sm font-semibold text-slate-900 border-b pb-2">2. Telecommunications & Add-On Services</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label htmlFor="PhoneService" className="block text-sm font-medium text-slate-700">Phone Service</label>
                      <select
                        id="PhoneService"
                        name="PhoneService"
                        value={formData.PhoneService}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="MultipleLines" className="block text-sm font-medium text-slate-700">Multiple Lines</label>
                      <select
                        id="MultipleLines"
                        name="MultipleLines"
                        value={formData.MultipleLines}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No phone service">No phone service</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="InternetService" className="block text-sm font-medium text-slate-700">Internet Service</label>
                      <select
                        id="InternetService"
                        name="InternetService"
                        value={formData.InternetService}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Fiber optic">Fiber optic</option>
                        <option value="DSL">DSL</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="OnlineSecurity" className="block text-sm font-medium text-slate-700">Online Security</label>
                      <select
                        id="OnlineSecurity"
                        name="OnlineSecurity"
                        value={formData.OnlineSecurity}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="OnlineBackup" className="block text-sm font-medium text-slate-700">Online Backup</label>
                      <select
                        id="OnlineBackup"
                        name="OnlineBackup"
                        value={formData.OnlineBackup}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="DeviceProtection" className="block text-sm font-medium text-slate-700">Device Protection</label>
                      <select
                        id="DeviceProtection"
                        name="DeviceProtection"
                        value={formData.DeviceProtection}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="TechSupport" className="block text-sm font-medium text-slate-700">Tech Support</label>
                      <select
                        id="TechSupport"
                        name="TechSupport"
                        value={formData.TechSupport}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="StreamingTV" className="block text-sm font-medium text-slate-700">Streaming TV</label>
                      <select
                        id="StreamingTV"
                        name="StreamingTV"
                        value={formData.StreamingTV}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="StreamingMovies" className="block text-sm font-medium text-slate-700">Streaming Movies</label>
                      <select
                        id="StreamingMovies"
                        name="StreamingMovies"
                        value={formData.StreamingMovies}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                        <option value="No internet service">No internet service</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* 3. Account Billing & Contract Terms */}
                <div className="space-y-4">
                  <h4 className="text-sm font-semibold text-slate-900 border-b pb-2">3. Billing & Contract Terms</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label htmlFor="tenure" className="block text-sm font-medium text-slate-700">Tenure (Months)</label>
                      <input
                        type="number"
                        id="tenure"
                        name="tenure"
                        min="0"
                        max="120"
                        value={formData.tenure}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label htmlFor="Contract" className="block text-sm font-medium text-slate-700">Contract Type</label>
                      <select
                        id="Contract"
                        name="Contract"
                        value={formData.Contract}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Month-to-month">Month-to-month</option>
                        <option value="One year">One year</option>
                        <option value="Two year">Two year</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="PaperlessBilling" className="block text-sm font-medium text-slate-700">Paperless Billing</label>
                      <select
                        id="PaperlessBilling"
                        name="PaperlessBilling"
                        value={formData.PaperlessBilling}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Yes">Yes</option>
                        <option value="No">No</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="PaymentMethod" className="block text-sm font-medium text-slate-700">Payment Method</label>
                      <select
                        id="PaymentMethod"
                        name="PaymentMethod"
                        value={formData.PaymentMethod}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      >
                        <option value="Electronic check">Electronic check</option>
                        <option value="Mailed check">Mailed check</option>
                        <option value="Bank transfer (automatic)">Bank transfer (automatic)</option>
                        <option value="Credit card (automatic)">Credit card (automatic)</option>
                      </select>
                    </div>

                    <div>
                      <label htmlFor="MonthlyCharges" className="block text-sm font-medium text-slate-700">Monthly Charges ($)</label>
                      <input
                        type="number"
                        id="MonthlyCharges"
                        name="MonthlyCharges"
                        step="0.01"
                        min="0"
                        value={formData.MonthlyCharges}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        required
                      />
                    </div>

                    <div>
                      <label htmlFor="TotalCharges" className="block text-sm font-medium text-slate-700">Total Charges ($)</label>
                      <input
                        type="number"
                        id="TotalCharges"
                        name="TotalCharges"
                        step="0.01"
                        min="0"
                        value={formData.TotalCharges}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-lg border-gray-300 border p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        required
                      />
                    </div>
                  </div>
                </div>
              </form>
            </CardContent>
            <CardFooter className="border-t border-gray-100 bg-gray-50/50 py-4 px-6 flex justify-between">
              <Button variant="outline" onClick={handleReset} type="button">
                <RotateCcw className="mr-2 h-4 w-4" />
                Reset Form
              </Button>
              <Button form="prediction-form" type="submit" disabled={isPredicting}>
                {isPredicting ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Running ML Pipeline...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Play className="mr-2 h-4 w-4" />
                    Predict Churn Risk
                  </span>
                )}
              </Button>
            </CardFooter>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card className="h-full bg-slate-900 text-white border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Real-Time Model Inference</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center h-[calc(100%-80px)]">
              {!result && !isPredicting && !error && (
                <div className="text-slate-400 space-y-4">
                  <ShieldAlert className="h-16 w-16 mx-auto opacity-50" />
                  <p>Submit customer feature details to view the real FastAPI model prediction.</p>
                </div>
              )}

              {isPredicting && (
                <div className="text-blue-400 space-y-4">
                  <div className="relative w-16 h-16 mx-auto">
                    <div className="absolute inset-0 border-4 border-slate-700 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
                  </div>
                  <p className="animate-pulse">Evaluating 55 feature matrix in FastAPI backend...</p>
                </div>
              )}

              {result && !isPredicting && (
                <div className="space-y-6 w-full animate-in fade-in zoom-in duration-300">
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-400 uppercase tracking-wider">Churn Risk Verdict</p>
                    <div className="text-5xl font-bold flex items-center justify-center gap-3">
                      {result.prediction === 'Churn' ? (
                        <span className="text-red-400">Churn</span>
                      ) : (
                        <span className="text-green-400">No Churn</span>
                      )}
                    </div>
                  </div>

                  <div className="bg-slate-800/50 rounded-xl p-6 space-y-4 border border-slate-700/50">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400 text-sm">Churn Probability</span>
                      <span className="font-bold text-lg">{(result.probability * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-1000 ${
                          result.risk_level === 'High'
                            ? 'bg-red-500'
                            : result.risk_level === 'Medium'
                            ? 'bg-amber-500'
                            : 'bg-emerald-500'
                        }`}
                        style={{ width: `${(result.probability * 100).toFixed(1)}%` }}
                      ></div>
                    </div>

                    <div className="pt-2 flex justify-between items-center">
                      <span className="text-slate-400 text-sm">Model Confidence</span>
                      <span className="font-semibold text-slate-200">{(result.confidence_score * 100).toFixed(1)}%</span>
                    </div>

                    <div className="pt-4 border-t border-slate-700/50 flex justify-between items-center">
                      <span className="text-slate-400 text-sm">Risk Classification</span>
                      <Badge variant={result.risk_level === 'High' ? 'destructive' : result.risk_level === 'Medium' ? 'warning' : 'success'}>
                        {result.risk_level} Risk
                      </Badge>
                    </div>
                  </div>

                  <div className="pt-4 space-y-2 text-left">
                    <p className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-blue-400" />
                      Prescriptive Action
                    </p>
                    <p className="text-sm text-slate-400 leading-relaxed">
                      {result.prediction === 'Churn'
                        ? 'High churn probability detected. Offer a 1-year contract discount and assign dedicated customer retention agent.'
                        : 'Low churn risk. Retain current subscription tier and engagement schedule.'}
                    </p>
                  </div>

                  <div className="text-xs text-slate-500 pt-2 text-right">
                    Processed at: {new Date(result.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
