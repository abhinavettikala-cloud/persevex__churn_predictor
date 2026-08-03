"""
Export Service for Telecom Churn Prediction System.
Generates downloadable report files in CSV, Excel, and PDF formats.
"""

import io
import json
import logging
import pandas as pd
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ExportService:
    """Provides methods for exporting prediction history to CSV, Excel, and PDF."""

    @staticmethod
    def export_csv(records: List[Dict[str, Any]]) -> bytes:
        """Generates a CSV byte buffer from prediction history records."""
        if not records:
            df = pd.DataFrame(columns=["ID", "Timestamp", "Prediction", "Probability", "Risk Level", "Contract"])
        else:
            flat_records = []
            for r in records:
                flat = {
                    "ID": r.get("id"),
                    "Timestamp": r.get("timestamp"),
                    "Prediction": r.get("prediction"),
                    "Probability": r.get("probability"),
                    "Confidence": r.get("confidence_score"),
                    "Risk Level": r.get("risk_level"),
                    "Tenure (Months)": r.get("tenure"),
                    "Contract": r.get("Contract"),
                    "Internet Service": r.get("InternetService"),
                    "Payment Method": r.get("PaymentMethod"),
                    "Monthly Charges ($)": r.get("MonthlyCharges"),
                    "Total Charges ($)": r.get("TotalCharges"),
                    "Execution Time (ms)": r.get("execution_time_ms")
                }
                flat_records.append(flat)
            df = pd.DataFrame(flat_records)

        output = io.BytesIO()
        df.to_csv(output, index=False, encoding="utf-8")
        return output.getvalue()

    @staticmethod
    def export_excel(records: List[Dict[str, Any]]) -> bytes:
        """Generates an Excel workbook byte buffer from prediction history records."""
        if not records:
            df = pd.DataFrame(columns=["ID", "Timestamp", "Prediction", "Probability", "Risk Level"])
        else:
            flat_records = []
            for r in records:
                flat = {
                    "ID": r.get("id"),
                    "Timestamp": r.get("timestamp"),
                    "Prediction": r.get("prediction"),
                    "Probability": r.get("probability"),
                    "Confidence": r.get("confidence_score"),
                    "Risk Level": r.get("risk_level"),
                    "Tenure": r.get("tenure"),
                    "Contract": r.get("Contract"),
                    "Internet Service": r.get("InternetService"),
                    "Payment Method": r.get("PaymentMethod"),
                    "Monthly Charges": r.get("MonthlyCharges"),
                    "Total Charges": r.get("TotalCharges"),
                    "Execution Time (ms)": r.get("execution_time_ms")
                }
                flat_records.append(flat)
            df = pd.DataFrame(flat_records)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Prediction History")
        return output.getvalue()

    @staticmethod
    def export_pdf_report(records: List[Dict[str, Any]]) -> bytes:
        """Generates a styled PDF/HTML formatted report byte buffer."""
        total = len(records)
        churn_count = sum(1 for r in records if r.get("prediction") == "Churn")
        non_churn_count = total - churn_count
        churn_pct = (churn_count / total * 100) if total > 0 else 0.0

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; color: #1E293B; background: #FFFFFF; }}
                h1 {{ color: #2563EB; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }}
                .summary-box {{ background: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #CBD5E1; padding: 8px 12px; text-align: left; font-size: 13px; }}
                th {{ background-color: #2563EB; color: white; }}
                tr:nth-child(even) {{ background-color: #F8FAFC; }}
                .churn {{ color: #DC2626; font-weight: bold; }}
                .no-churn {{ color: #16A34A; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Telecom Customer Churn Analytics Report</h1>
            <div class="summary-box">
                <p><strong>Generated Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                <p><strong>Total Sampled Predictions:</strong> {total}</p>
                <p><strong>Predicted Churn Rate:</strong> {churn_pct:.1f}% ({churn_count} Churn / {non_churn_count} Non-Churn)</p>
                <p><strong>Model Version:</strong> v1.0.0 (Logistic Regression)</p>
            </div>
            
            <h2>Recent Prediction Log</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp</th>
                        <th>Prediction</th>
                        <th>Probability</th>
                        <th>Risk Level</th>
                        <th>Contract</th>
                        <th>Monthly ($)</th>
                    </tr>
                </thead>
                <tbody>
        """

        for r in records[:25]:
            pred = r.get("prediction", "")
            css_cls = "churn" if pred == "Churn" else "no-churn"
            html_content += f"""
                    <tr>
                        <td>{r.get('id', '')}</td>
                        <td>{str(r.get('timestamp', ''))[:19]}</td>
                        <td class="{css_cls}">{pred}</td>
                        <td>{float(r.get('probability', 0))*100:.1f}%</td>
                        <td>{r.get('risk_level', '')}</td>
                        <td>{r.get('Contract', '')}</td>
                        <td>${float(r.get('MonthlyCharges', 0)):.2f}</td>
                    </tr>
            """

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        return html_content.encode("utf-8")
