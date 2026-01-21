import { useState } from 'react';
import { visitService } from '../services/api';
import VisitModal from './VisitModal';
import { MapPin, Phone, DollarSign, Calendar } from 'lucide-react';

export default function CustomerCard({ customer, onUpdate }) {
  const [showModal, setShowModal] = useState(false);
  
  const latestVisit = customer.visits && customer.visits.length > 0 
    ? customer.visits[customer.visits.length - 1] 
    : null;

  const statusOptions = {
    'not_visited': { label: 'Not Visited', color: '#9ca3af', emoji: '⭕' },
    'no_contact': { label: 'No Contact', color: '#f59e0b', emoji: '❌' },
    'contact_made': { label: 'Contact Made', color: '#60a5fa', emoji: '💬' },
    'sale_made': { label: 'Sale Made', color: '#10b981', emoji: '✅' },
    'follow_up_required': { label: 'Follow-up', color: '#ef4444', emoji: '🔔' }
  };

  const currentStatus = latestVisit?.status || 'not_visited';
  const statusConfig = statusOptions[currentStatus];

  const handleQuickStatus = async (status) => {
    try {
      if (latestVisit) {
        await visitService.update(latestVisit.id, { 
          status,
          visited_at: new Date().toISOString()
        });
      } else {
        await visitService.create({ 
          customer_id: customer.id, 
          status,
          visited_at: new Date().toISOString()
        });
      }
      onUpdate();
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  return (
    <>
      <div className="customer-card" style={{ borderLeftColor: statusConfig.color }}>
        <div className="customer-header">
          <div className="customer-info">
            <div className="stop-number">#{customer.stop_number}</div>
            <div>
              <h4>{customer.name}</h4>
              <div className="customer-meta">
                <MapPin size={14} />
                <span>{customer.address}</span>
              </div>
              <div className="customer-meta">
                <Phone size={14} />
                <span>Acct: {customer.account_number}</span>
              </div>
            </div>
          </div>
          
          <div 
            className="status-badge" 
            style={{ backgroundColor: statusConfig.color }}
          >
            <span>{statusConfig.emoji}</span>
            <span>{statusConfig.label}</span>
          </div>
        </div>

        {latestVisit && latestVisit.status !== 'not_visited' && (
          <div className="visit-details">
            {latestVisit.sales_amount > 0 && (
              <div className="visit-detail">
                <DollarSign size={14} />
                <span>${latestVisit.sales_amount.toFixed(2)}</span>
              </div>
            )}
            {latestVisit.notes && (
              <div className="visit-notes">{latestVisit.notes}</div>
            )}
            {latestVisit.follow_up_required && (
              <div className="visit-detail follow-up">
                <Calendar size={14} />
                <span>Follow-up needed</span>
              </div>
            )}
          </div>
        )}

        <div className="customer-actions">
          <div className="quick-actions">
            {Object.entries(statusOptions)
              .filter(([key]) => key !== 'not_visited')
              .map(([key, config]) => (
                <button
                  key={key}
                  className={`quick-action ${currentStatus === key ? 'active' : ''}`}
                  onClick={() => handleQuickStatus(key)}
                  title={config.label}
                >
                  {config.emoji}
                </button>
              ))}
          </div>
          <button 
            className="details-button"
            onClick={() => setShowModal(true)}
          >
            Details
          </button>
        </div>
      </div>

      {showModal && (
        <VisitModal
          customer={customer}
          visit={latestVisit}
          onClose={() => setShowModal(false)}
          onUpdate={onUpdate}
        />
      )}
    </>
  );
}
