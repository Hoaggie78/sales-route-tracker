import { useState } from 'react';
import { visitService } from '../services/api';
import { X, Save } from 'lucide-react';

export default function VisitModal({ customer, visit, onClose, onUpdate }) {
  const [formData, setFormData] = useState({
    status: visit?.status || 'not_visited',
    notes: visit?.notes || '',
    sales_amount: visit?.sales_amount || 0,
    follow_up_required: visit?.follow_up_required || false,
    follow_up_date: visit?.follow_up_date ? new Date(visit.follow_up_date).toISOString().slice(0, 16) : '',
    follow_up_notes: visit?.follow_up_notes || ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        sales_amount: parseFloat(formData.sales_amount) || 0,
        follow_up_date: formData.follow_up_date ? new Date(formData.follow_up_date).toISOString() : null,
        visited_at: formData.status !== 'not_visited' ? new Date().toISOString() : null
      };

      if (visit) {
        await visitService.update(visit.id, submitData);
      } else {
        await visitService.create({
          customer_id: customer.id,
          ...submitData
        });
      }

      onUpdate();
      onClose();
    } catch (error) {
      console.error('Failed to save visit:', error);
      alert('Failed to save visit. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{customer.name}</h2>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          <div className="customer-summary">
            <p><strong>Address:</strong> {customer.address}</p>
            <p><strong>Account:</strong> {customer.account_number}</p>
            <p><strong>Date:</strong> {new Date(customer.date).toLocaleDateString()}</p>
            <p><strong>Location:</strong> {customer.location}</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="status">Visit Status *</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
                required
              >
                <option value="not_visited">Not Visited</option>
                <option value="no_contact">Visited - No Contact</option>
                <option value="contact_made">Visited - Contact Made</option>
                <option value="sale_made">Sale Made</option>
                <option value="follow_up_required">Follow-up Required</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="sales_amount">Sales Amount ($)</label>
              <input
                type="number"
                id="sales_amount"
                name="sales_amount"
                value={formData.sales_amount}
                onChange={handleChange}
                step="0.01"
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="notes">Visit Notes</label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows="4"
                placeholder="Add notes about the visit..."
              />
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="follow_up_required"
                  checked={formData.follow_up_required}
                  onChange={handleChange}
                />
                <span>Follow-up Required</span>
              </label>
            </div>

            {formData.follow_up_required && (
              <>
                <div className="form-group">
                  <label htmlFor="follow_up_date">Follow-up Date</label>
                  <input
                    type="datetime-local"
                    id="follow_up_date"
                    name="follow_up_date"
                    value={formData.follow_up_date}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="follow_up_notes">Follow-up Notes</label>
                  <textarea
                    id="follow_up_notes"
                    name="follow_up_notes"
                    value={formData.follow_up_notes}
                    onChange={handleChange}
                    rows="3"
                    placeholder="What needs to be done on follow-up?"
                  />
                </div>
              </>
            )}

            <div className="modal-actions">
              <button type="button" className="cancel-button" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="save-button" disabled={loading}>
                <Save size={18} />
                <span>{loading ? 'Saving...' : 'Save'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
