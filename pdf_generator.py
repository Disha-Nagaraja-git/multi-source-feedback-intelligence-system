import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFReportTemplate(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Title
        self.cell(0, 10, 'Weekly Feedback Intelligence Report', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_trend_chart(df_trend: pd.DataFrame, save_path: str):
    """
    Generate a static matplotlib chart and save it to disk for the PDF.
    """
    if df_trend.empty:
        return False
        
    plt.figure(figsize=(8, 4))
    plt.plot(df_trend['date'], df_trend['avg_sentiment'], marker='o', linestyle='-', color='b')
    plt.title('Average Sentiment Trend')
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score (-1.0 to 1.0)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return True

def export_weekly_report(
    metrics: dict,
    df_trend: pd.DataFrame,
    df_issues: pd.DataFrame,
    output_path: str = "assets/weekly_report.pdf",
    charts_dir: str = "assets/charts"
) -> str:
    """
    Generates a PDF report containing summary stats, an embedded chart, and top issues.
    """
    try:
        os.makedirs(charts_dir, exist_ok=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        pdf = PDFReportTemplate()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # --- 1. Summary Statistics ---
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '1. Overview Statistics', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        pdf.cell(0, 8, f"Total Reviews Analyzed: {metrics.get('total_reviews', 0)}", 0, 1)
        pdf.cell(0, 8, f"Average Rating: {metrics.get('avg_rating', 0.0):.1f} / 5.0", 0, 1)
        pdf.cell(0, 8, f"Overall Sentiment Score: {metrics.get('avg_sentiment', 0.0):.2f}", 0, 1)
        pdf.cell(0, 8, f"Positive Feedback: {metrics.get('pct_positive', 0.0):.1f}%", 0, 1)
        pdf.cell(0, 8, f"Negative Feedback: {metrics.get('pct_negative', 0.0):.1f}%", 0, 1)
        pdf.ln(5)
        
        # --- 2. Trend Analysis Chart ---
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '2. Sentiment Trend', 0, 1)
        
        chart_path = os.path.join(charts_dir, 'trend_chart.png')
        chart_success = generate_trend_chart(df_trend, chart_path)
        
        if chart_success and os.path.exists(chart_path):
            pdf.image(chart_path, x=15, w=180)
            pdf.ln(5)
        else:
            pdf.set_font('Arial', 'I', 11)
            pdf.cell(0, 8, "Not enough data to display trend chart.", 0, 1)
            
        pdf.ln(5)
            
        # --- 3. Top Issues ---
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '3. Critical Issues & Top Complaints', 0, 1)
        
        if not df_issues.empty:
            pdf.set_font('Arial', 'B', 10)
            # Table Header
            pdf.cell(50, 8, 'Issue Keyword', 1)
            pdf.cell(40, 8, 'Mentions', 1)
            pdf.cell(40, 8, 'Avg Negativity', 1)
            pdf.cell(50, 8, 'Severity Score', 1)
            pdf.ln()
            
            pdf.set_font('Arial', '', 10)
            for _, row in df_issues.head(10).iterrows():
                pdf.cell(50, 8, str(row['issue_keyword'])[:20], 1)
                pdf.cell(40, 8, str(row['frequency']), 1)
                pdf.cell(40, 8, f"{row['avg_negative_sentiment']:.2f}", 1)
                pdf.cell(50, 8, f"{row['severity_score']:.2f}", 1)
                pdf.ln()
        else:
            pdf.set_font('Arial', 'I', 11)
            pdf.cell(0, 8, "No significant issues detected during this period.", 0, 1)

        pdf.ln(10)
        
        # --- 4. Recommendations ---
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '4. Product Improvement Suggestions', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        if not df_issues.empty:
            top_issue = str(df_issues.iloc[0]['issue_keyword'])
            pdf.multi_cell(0, 8, f"- Priority investigation required for instances relating to '{top_issue}' due to high negative sentiment impact and frequency.")
            if len(df_issues) > 1:
                second_issue = str(df_issues.iloc[1]['issue_keyword'])
                pdf.multi_cell(0, 8, f"- Address mentions of '{second_issue}' to improve overall customer satisfaction.")
        else:
            pdf.multi_cell(0, 8, "- Maintain current service quality. Continue monitoring feedback channels for emerging trends.")
        
        # Output
        pdf.output(output_path, 'F')
        logger.info(f"Report successfully generated at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {str(e)}")
        return ""

if __name__ == "__main__":
    pass
