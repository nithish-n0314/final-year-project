import React from 'react';
import Navbar from '../components/Navbar';
import ReportGenerator from '../components/ReportGenerator';

const ReportsPage = () => {
  return (
    <div>
      <Navbar />
      <div className="container">
        <h2>Financial Reports</h2>
        <p style={{ marginBottom: '30px', color: '#666' }}>
          Generate detailed financial reports with AI analysis and download as PDF
        </p>

        <ReportGenerator />
      </div>
    </div>
  );
};

export default ReportsPage;