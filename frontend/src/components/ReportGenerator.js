import React, { useState, useRef } from 'react';
import api from '../services/api';
// Import for older jsPDF version
import * as jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const ReportGenerator = () => {
  const [dateRange, setDateRange] = useState({
    start_date: '',
    end_date: ''
  });
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pdfLoading, setPdfLoading] = useState(false);
  const reportRef = useRef();

  const handleDateChange = (e) => {
    setDateRange({
      ...dateRange,
      [e.target.name]: e.target.value
    });
  };

  const generateReport = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setReport(null);

    try {
      const response = await api.post('/reports/', dateRange);
      setReport(response.data);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const setQuickRange = (days) => {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - days);

    setDateRange({
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0]
    });
  };

  const downloadPDF = async () => {
    if (!report || !reportRef.current) {
      console.error('Report or reportRef not available');
      alert('Please generate a report first');
      return;
    }

    setPdfLoading(true);
    console.log('Starting PDF generation...');
    
    try {
      // Method 1: Try html2canvas approach
      console.log('Capturing canvas...');
      const canvas = await html2canvas(reportRef.current, {
        scale: 1.5,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        width: reportRef.current.scrollWidth,
        height: reportRef.current.scrollHeight
      });
      
      console.log('Canvas captured, creating PDF...');
      const imgData = canvas.getDataURL('image/png');
      const pdf = new jsPDF.jsPDF('p', 'mm', 'a4');
      
      const imgWidth = 210;
      const pageHeight = 295;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      
      let position = 0;
      
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
      
      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }
      
      console.log('Saving PDF...');
      pdf.save(`Financial_Report_${report.period.start_date}_to_${report.period.end_date}.pdf`);
      console.log('PDF saved successfully');
    } catch (error) {
      console.error('Error with html2canvas, trying text-based PDF:', error);
      
      // Method 2: Fallback to text-based PDF
      try {
        const pdf = new jsPDF.jsPDF('p', 'mm', 'a4');
        let yPosition = 20;
        
        // Title
        pdf.setFontSize(16);
        pdf.text('Financial Report', 20, yPosition);
        yPosition += 10;
        
        // Period
        pdf.setFontSize(12);
        pdf.text(`Period: ${report.period.start_date} to ${report.period.end_date}`, 20, yPosition);
        yPosition += 15;
        
        // Summary
        pdf.setFontSize(14);
        pdf.text('Summary', 20, yPosition);
        yPosition += 10;
        
        pdf.setFontSize(10);
        pdf.text(`Total Expenses: ₹${report.summary.total_expenses.toFixed(2)}`, 20, yPosition);
        yPosition += 7;
        pdf.text(`Transactions: ${report.summary.transaction_count}`, 20, yPosition);
        yPosition += 7;
        pdf.text(`Average Daily: ₹${report.summary.avg_daily_spending.toFixed(2)}`, 20, yPosition);
        yPosition += 15;
        
        // Categories
        pdf.setFontSize(14);
        pdf.text('Category Breakdown', 20, yPosition);
        yPosition += 10;
        
        pdf.setFontSize(10);
        Object.entries(report.category_breakdown).forEach(([category, data]) => {
          if (yPosition > 270) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(`${category}: ₹${data.amount.toFixed(2)} (${data.percentage.toFixed(1)}%)`, 20, yPosition);
          yPosition += 7;
        });
        
        // AI Summary
        if (report.ai_summary && yPosition < 250) {
          yPosition += 10;
          pdf.setFontSize(14);
          pdf.text('AI Analysis', 20, yPosition);
          yPosition += 10;
          
          pdf.setFontSize(10);
          const summaryLines = pdf.splitTextToSize(report.ai_summary, 170);
          summaryLines.forEach(line => {
            if (yPosition > 270) {
              pdf.addPage();
              yPosition = 20;
            }
            pdf.text(line, 20, yPosition);
            yPosition += 5;
          });
        }
        
        pdf.save(`Financial_Report_${report.period.start_date}_to_${report.period.end_date}.pdf`);
        console.log('Text-based PDF saved successfully');
      } catch (fallbackError) {
        console.error('Fallback PDF generation failed:', fallbackError);
        alert(`Error generating PDF: ${fallbackError.message}`);
      }
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Financial Reports</h3>
      
      <form onSubmit={generateReport}>
        <div className="grid grid-2">
          <div className="form-group">
            <label htmlFor="start_date">Start Date</label>
            <input
              type="date"
              id="start_date"
              name="start_date"
              className="form-control"
              value={dateRange.start_date}
              onChange={handleDateChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="end_date">End Date</label>
            <input
              type="date"
              id="end_date"
              name="end_date"
              className="form-control"
              value={dateRange.end_date}
              onChange={handleDateChange}
              required
            />
          </div>
        </div>

        {/* Quick Range Buttons */}
        <div style={{ marginBottom: '15px' }}>
          <span style={{ fontSize: '14px', color: '#666', marginRight: '10px' }}>
            Quick select:
          </span>
          <button
            type="button"
            onClick={() => setQuickRange(7)}
            className="btn btn-secondary"
            style={{ marginRight: '5px', padding: '5px 10px', fontSize: '12px' }}
          >
            Last 7 days
          </button>
          <button
            type="button"
            onClick={() => setQuickRange(30)}
            className="btn btn-secondary"
            style={{ marginRight: '5px', padding: '5px 10px', fontSize: '12px' }}
          >
            Last 30 days
          </button>
          <button
            type="button"
            onClick={() => setQuickRange(90)}
            className="btn btn-secondary"
            style={{ padding: '5px 10px', fontSize: '12px' }}
          >
            Last 90 days
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Generating Report...' : 'Generate Report'}
        </button>
      </form>

      {report && (
        <div style={{ marginTop: '30px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h4>Financial Report</h4>
            <button
              onClick={downloadPDF}
              className="btn btn-secondary"
              style={{ padding: '8px 16px', fontSize: '14px' }}
              disabled={pdfLoading}
            >
              {pdfLoading ? '⏳ Generating...' : '📄 Download PDF'}
            </button>
          </div>
          
          <div ref={reportRef} style={{ backgroundColor: 'white', padding: '20px' }}>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              {report.period.start_date} to {report.period.end_date} ({report.period.days} days)
            </p>

          {/* Summary Stats */}
          <div className="grid grid-3" style={{ marginBottom: '20px' }}>
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                ₹{report.summary.total_expenses.toFixed(2)}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Total Expenses</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
                {report.summary.transaction_count}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Transactions</div>
            </div>
            
            <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                ₹{report.summary.avg_daily_spending.toFixed(2)}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>Avg Daily</div>
            </div>
          </div>

          {/* Spending Change */}
          {report.summary.spending_change_percentage !== 0 && (
            <div style={{ 
              padding: '10px', 
              backgroundColor: report.summary.spending_change_percentage > 0 ? '#fff3cd' : '#d4edda',
              borderRadius: '4px',
              marginBottom: '20px'
            }}>
              <strong>
                {report.summary.spending_change_percentage > 0 ? '📈' : '📉'} 
                {' '}
                {Math.abs(report.summary.spending_change_percentage).toFixed(1)}% 
                {report.summary.spending_change_percentage > 0 ? ' increase' : ' decrease'}
              </strong>
              {' '}compared to previous period
            </div>
          )}

          {/* Category Breakdown */}
          <div style={{ marginBottom: '20px' }}>
            <h5>Category Breakdown</h5>
            {Object.entries(report.category_breakdown).map(([category, data]) => (
              <div key={category} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '8px 0',
                borderBottom: '1px solid #eee'
              }}>
                <div>
                  <span style={{ fontWeight: '500' }}>
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </span>
                  <span style={{ fontSize: '12px', color: '#666', marginLeft: '10px' }}>
                    ({data.count} transactions)
                  </span>
                </div>
                <div>
                  <span style={{ fontWeight: 'bold', marginRight: '10px' }}>
                    ₹{data.amount.toFixed(2)}
                  </span>
                  <span style={{ 
                    fontSize: '12px', 
                    color: '#666',
                    backgroundColor: '#f8f9fa',
                    padding: '2px 6px',
                    borderRadius: '10px'
                  }}>
                    {data.percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Top Expenses */}
          {report.top_expenses && report.top_expenses.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h5>Top Expenses</h5>
              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {report.top_expenses.slice(0, 5).map((expense, index) => (
                  <div key={index} className="expense-item">
                    <div>
                      <div style={{ fontWeight: '500' }}>{expense.description}</div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {expense.category} • {expense.date}
                      </div>
                    </div>
                    <div style={{ fontWeight: 'bold', color: '#dc3545' }}>
                      ₹{expense.amount.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Summary */}
          {report.ai_summary && (
            <div style={{ 
              marginTop: '20px',
              padding: '15px',
              backgroundColor: '#e3f2fd',
              borderRadius: '4px',
              borderLeft: '4px solid #2196f3'
            }}>
              <h5 style={{ color: '#1976d2', marginBottom: '10px' }}>
                🤖 AI Analysis
              </h5>
              <div style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>
                {report.ai_summary}
              </div>
            </div>
          )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportGenerator;