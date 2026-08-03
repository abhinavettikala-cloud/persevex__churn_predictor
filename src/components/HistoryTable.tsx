import React from 'react';
import { HistoryRecord } from '../types';
import { format } from 'date-fns';
import { Download } from 'lucide-react';

interface HistoryTableProps {
  history: HistoryRecord[];
}

export default function HistoryTable({ history }: HistoryTableProps) {
  const handleDownload = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(history, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href",     dataStr);
    downloadAnchorNode.setAttribute("download", "prediction_history.json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <>
      <div className="px-6 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <h2 className="text-sm font-bold text-slate-800 uppercase tracking-tight">Recent Prediction Logs</h2>
        <div className="flex items-center gap-3">
          <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-bold uppercase">Session Active</span>
          <button 
            onClick={handleDownload}
            className="text-[10px] text-slate-500 hover:text-slate-800 font-bold uppercase flex items-center gap-1 transition-colors"
          >
            <Download className="w-3 h-3" /> Export
          </button>
        </div>
      </div>
      
      {history.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-slate-400 text-sm py-8">
          No prediction history yet.
        </div>
      ) : (
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse">
            <thead className="text-[11px] text-slate-400 font-bold uppercase border-b border-slate-100 bg-white sticky top-0">
              <tr>
                <th className="px-6 py-3">Timestamp</th>
                <th className="px-6 py-3">Tenure</th>
                <th className="px-6 py-3">Contract</th>
                <th className="px-6 py-3">Charges</th>
                <th className="px-6 py-3">Risk Score</th>
                <th className="px-6 py-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="text-sm text-slate-600 divide-y divide-slate-50 bg-white">
              {history.map((record) => (
                <tr key={record.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-2.5 font-mono text-xs">
                    {format(new Date(record.result.timestamp), 'HH:mm:ss')}
                  </td>
                  <td className="px-6 py-2.5 font-medium">{record.data.tenure} mos</td>
                  <td className="px-6 py-2.5 text-xs">{record.data.contract}</td>
                  <td className="px-6 py-2.5">${record.data.monthlyCharges}</td>
                  <td className="px-6 py-2.5">
                    <div className="w-24 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${record.result.probability > 0.7 ? 'bg-rose-500' : record.result.probability > 0.4 ? 'bg-amber-500' : 'bg-emerald-500'}`} 
                        style={{ width: `${record.result.probability * 100}%` }}
                      ></div>
                    </div>
                  </td>
                  <td className="px-6 py-2.5 text-right">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      record.result.prediction === 'Churn' 
                        ? 'bg-rose-50 text-rose-600' 
                        : 'bg-emerald-50 text-emerald-600'
                    }`}>
                      {record.result.prediction === 'Churn' ? 'High Churn' : 'Retain'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
