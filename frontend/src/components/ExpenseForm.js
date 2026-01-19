import React, { useState } from 'react';
import api from '../services/api';

const ExpenseForm = ({ onExpenseAdded }) => {
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    category: '',
    date: new Date().toISOString().split('T')[0]
  });
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('manual');

  const categories = [
    { value: 'food', label: 'Food & Dining' },
    { value: 'transportation', label: 'Transportation' },
    { value: 'shopping', label: 'Shopping' },
    { value: 'entertainment', label: 'Entertainment' },
    { value: 'bills', label: 'Bills & Utilities' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'education', label: 'Education' },
    { value: 'travel', label: 'Travel' },
    { value: 'groceries', label: 'Groceries' },
    { value: 'other', label: 'Other' }
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    setPdfFile(e.target.files[0]);
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.post('/expenses/', formData);
      setSuccess('Expense added successfully!');
      setFormData({
        amount: '',
        description: '',
        category: '',
        date: new Date().toISOString().split('T')[0]
      });
      onExpenseAdded();
    } catch (error) {
      setError('Failed to add expense');
    } finally {
      setLoading(false);
    }
  };

  const handlePdfSubmit = async (e) => {
    e.preventDefault();
    if (!pdfFile) {
      setError('Please select a PDF file');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const formData = new FormData();
      formData.append('pdf_file', pdfFile);

      const response = await api.post('/expenses/upload-pdf/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess(`${response.data.message}`);
      setPdfFile(null);
      document.getElementById('pdf-file').value = '';
      onExpenseAdded();
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to process PDF');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>Add Expenses</h3>
      
      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px', borderBottom: '1px solid #ddd' }}>
        <button
          onClick={() => setActiveTab('manual')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeTab === 'manual' ? '#007bff' : 'transparent',
            color: activeTab === 'manual' ? 'white' : '#007bff',
            cursor: 'pointer',
            marginRight: '10px'
          }}
        >
          Manual Entry
        </button>
        <button
          onClick={() => setActiveTab('pdf')}
          style={{
            padding: '10px 20px',
            border: 'none',
            background: activeTab === 'pdf' ? '#007bff' : 'transparent',
            color: activeTab === 'pdf' ? 'white' : '#007bff',
            cursor: 'pointer'
          }}
        >
          PDF Upload
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {activeTab === 'manual' && (
        <form onSubmit={handleManualSubmit}>
          <div className="form-group">
            <label htmlFor="amount">Amount (₹)</label>
            <input
              type="number"
              id="amount"
              name="amount"
              className="form-control"
              value={formData.amount}
              onChange={handleChange}
              min="0.01"
              step="0.01"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <input
              type="text"
              id="description"
              name="description"
              className="form-control"
              value={formData.description}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              className="form-control"
              value={formData.category}
              onChange={handleChange}
            >
              <option value="">select category</option>
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="date">Date</label>
            <input
              type="date"
              id="date"
              name="date"
              className="form-control"
              value={formData.date}
              onChange={handleChange}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Adding...' : 'Add Expense'}
          </button>
        </form>
      )}

      {activeTab === 'pdf' && (
        <form onSubmit={handlePdfSubmit}>
          <div className="form-group">
            <label htmlFor="pdf-file">Upload PDF Receipt/Statement</label>
            <input
              type="file"
              id="pdf-file"
              className="form-control"
              accept=".pdf"
              onChange={handleFileChange}
              required
            />
            <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
              Upload receipts, bank statements, or expense reports in PDF format.
              AI will extract and categorize expenses automatically.
            </small>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Processing PDF...' : 'Upload & Extract Expenses'}
          </button>
        </form>
      )}
    </div>
  );
};

export default ExpenseForm;