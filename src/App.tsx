import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { AlertCircle, RefreshCcw, CheckCircle2, Loader2, Play, Server } from 'lucide-react';
import Sidebar from './components/Sidebar';
import HistoryTable from './components/HistoryTable';
import GaugeChart from './components/GaugeChart';
import { CustomerData, PredictionResult, HistoryRecord } from './types';

const INITIAL_DATA: CustomerData = {
  gender: 'Female',
  seniorCitizen: 'No',
  partner: 'Yes',
  dependents: 'No',
  tenure: 12,
  phoneService: 'Yes',
  internetService: 'Fiber optic',
  contract: 'Month-to-month',
  monthlyCharges: 85.5,
  totalCharges: 1025.0,
  paymentMethod: 'Electronic check'
};

export default function App() {
  const [formData, setFormData] = useState<CustomerData>(INITIAL_DATA);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentResult, setCurrentResult] = useState<PredictionResult | null>(null);
  const [history, setHistory] = useState<HistoryRecord[]>([]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const parsedValue = type === 'number' || type === 'range' ? Number(value) : value;
    setFormData(prev => ({ ...prev, [name]: parsedValue }));
  };

  const clearForm = () => {
    setFormData(INITIAL_DATA);
    setCurrentResult(null);
    setError(null);
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setCurrentResult(null);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const result: PredictionResult = await response.json();
      setCurrentResult(result);
      
      const newRecord: HistoryRecord = {
        id: Math.random().toString(36).substr(2, 9),
        data: { ...formData },
        result
      };
      
      setHistory(prev => [newRecord, ...prev].slice(0, 10)); // Keep last 10

    } catch (err: any) {
      setError(err.message || "Failed to connect to prediction service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans flex text-slate-900 overflow-hidden">
      <Sidebar />
      
      <main className="ml-64 flex-1 flex flex-col h-screen overflow-hidden">
        {/* HEADER */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 flex-shrink-0">
          <div>
            <h1 className="text-xl font-bold text-slate-800">Customer Churn Prediction</h1>
            <p className="text-xs text-slate-500">Model: XGBoost-v4.2.1 • Last Trained: 2 days ago</p>
          </div>
          <div className="flex items-center space-x-4">
            <button type="button" className="px-4 py-2 border border-slate-200 rounded-md text-sm font-medium text-slate-600 hover:bg-slate-50">Export Data</button>
            <button type="button" className="px-4 py-2 bg-blue-600 rounded-md text-sm font-medium text-white hover:bg-blue-700 shadow-sm flex items-center gap-2">
              <Play className="w-4 h-4 fill-current" /> New Batch Prediction
            </button>
          </div>
        </header>

        {/* CONTENT AREA */}
        <div className="flex-1 p-6 space-y-6 overflow-auto flex flex-col">
          <div className="grid grid-cols-12 gap-6 min-h-[420px]">
            
            {/* INPUT FORM */}
            <div className="col-span-12 xl:col-span-8 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white">
                <h2 className="font-semibold text-slate-800">Customer Profiling</h2>
                <button type="button" onClick={clearForm} className="text-blue-600 text-xs font-semibold hover:underline">Reset Form</button>
              </div>
              
              <form onSubmit={handlePredict} className="flex-1 p-6 grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-4">
                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Gender</label>
                  <select name="gender" value={formData.gender} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Senior Citizen</label>
                  <select name="seniorCitizen" value={formData.seniorCitizen} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Partner</label>
                  <select name="partner" value={formData.partner} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                  </select>
                </div>
                
                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Dependents</label>
                  <select name="dependents" value={formData.dependents} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase flex justify-between">
                    <span>Tenure (Months)</span>
                    <span className="text-blue-600 font-semibold">{formData.tenure}</span>
                  </label>
                  <input type="range" name="tenure" min="0" max="72" value={formData.tenure} onChange={handleInputChange} className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600 mt-1" />
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono mt-0.5"><span>0m</span><span>36m</span><span>72m</span></div>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Phone Service</label>
                  <select name="phoneService" value={formData.phoneService} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Internet Service</label>
                  <select name="internetService" value={formData.internetService} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="Fiber optic">Fiber optic</option>
                    <option value="DSL">DSL</option>
                    <option value="No">No</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Contract</label>
                  <select name="contract" value={formData.contract} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="Month-to-month">Month-to-month</option>
                    <option value="One year">One year</option>
                    <option value="Two year">Two year</option>
                  </select>
                </div>
                
                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Payment Method</label>
                  <select name="paymentMethod" value={formData.paymentMethod} onChange={handleInputChange} className="w-full border border-slate-200 rounded px-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500">
                    <option value="Electronic check">Electronic check</option>
                    <option value="Mailed check">Mailed check</option>
                    <option value="Bank transfer (automatic)">Bank transfer (auto)</option>
                    <option value="Credit card (automatic)">Credit card (auto)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Monthly Charges</label>
                  <div className="relative">
                    <span className="absolute left-2 top-1.5 text-slate-400 text-sm">$</span>
                    <input type="number" step="0.01" name="monthlyCharges" value={formData.monthlyCharges} onChange={handleInputChange} className="w-full border border-slate-200 rounded pl-6 pr-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500" />
                  </div>
                </div>
                
                <div className="space-y-1">
                  <label className="text-[11px] font-bold text-slate-500 uppercase">Total Charges</label>
                  <div className="relative">
                    <span className="absolute left-2 top-1.5 text-slate-400 text-sm">$</span>
                    <input type="number" step="0.01" name="totalCharges" value={formData.totalCharges} onChange={handleInputChange} className="w-full border border-slate-200 rounded pl-6 pr-2 py-1.5 text-sm bg-slate-50 outline-none focus:border-blue-500" />
                  </div>
                </div>

                <div className="space-y-1 md:col-span-3 pt-4 border-t border-slate-50">
                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-slate-900 text-white font-bold py-3 rounded-lg hover:bg-slate-800 transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <><Loader2 className="w-5 h-5 animate-spin" /> PROCESSING...</>
                    ) : (
                      'GENERATE PREDICTION'
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* PREDICTION GAUGE */}
            <div className="col-span-12 xl:col-span-4 bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col items-center justify-center text-center">
              <AnimatePresence mode="wait">
                {error ? (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-rose-50 border border-rose-100 rounded-2xl p-5 flex flex-col items-center gap-3 w-full"
                  >
                    <AlertCircle className="w-8 h-8 text-rose-500" />
                    <div>
                      <h4 className="text-rose-800 font-semibold text-sm uppercase">Prediction Error</h4>
                      <p className="text-rose-600 text-xs mt-1">{error}</p>
                    </div>
                  </motion.div>
                ) : currentResult && !loading ? (
                  <motion.div 
                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    className="w-full flex flex-col items-center"
                  >
                    <h2 className="text-sm font-bold text-slate-500 uppercase mb-6">Churn Probability</h2>
                    
                    <GaugeChart score={currentResult.probability} label="Risk Score" />
                    
                    <div className="mt-6 w-full">
                      <div className={`border rounded-lg p-3 text-left ${currentResult.prediction === 'Churn' ? 'bg-rose-50 border-rose-100 text-rose-800' : 'bg-emerald-50 border-emerald-100 text-emerald-800'}`}>
                        <p className="text-xs font-semibold mb-1 uppercase tracking-wide">
                          Classification: {currentResult.prediction}
                        </p>
                        <p className="text-[11px] leading-tight">
                          {currentResult.prediction === 'Churn' 
                            ? 'High churn risk detected. Recommend immediate retention offer and service follow-up.' 
                            : 'High loyalty potential. Suggest cross-selling additional services to lock in retention.'}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center text-slate-400 w-full h-full min-h-[200px]"
                  >
                    <Server className="w-10 h-10 mb-4 text-slate-300" />
                    <p className="font-bold text-slate-500 uppercase text-xs mb-1">Awaiting Data</p>
                    <p className="text-[11px]">Submit the form to generate a risk score.</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <div className="flex-1 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden min-h-[300px]">
             <HistoryTable history={history} />
          </div>

        </div>

        {/* FOOTER */}
        <footer className="h-8 bg-slate-100 border-t border-slate-200 px-6 flex items-center justify-between text-[10px] text-slate-500 flex-shrink-0">
          <div>System Instance: <span className="font-mono">node-771-aws-east</span></div>
          <div className="flex space-x-4">
            <span>Documentation v2.0</span>
            <span>Terms of Service</span>
            <span className="font-bold">v4.2.1-stable</span>
          </div>
        </footer>
      </main>
    </div>
  );
}
