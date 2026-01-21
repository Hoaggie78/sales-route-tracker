import { useState, useEffect } from 'react';
import { customerService } from '../services/api';
import CustomerCard from './CustomerCard';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function WeekView() {
  const [selectedWeek, setSelectedWeek] = useState(1);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedDays, setExpandedDays] = useState({});

  const days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
  const weeks = [1, 2, 3, 4];

  useEffect(() => {
    loadCustomers();
  }, [selectedWeek]);

  const loadCustomers = async () => {
    setLoading(true);
    try {
      const response = await customerService.getAll({ week_number: selectedWeek });
      setCustomers(response.data);
      
      // Initially expand all days
      const expanded = {};
      days.forEach(day => { expanded[day] = true; });
      setExpandedDays(expanded);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleDay = (day) => {
    setExpandedDays(prev => ({ ...prev, [day]: !prev[day] }));
  };

  const getCustomersByDay = (day) => {
    return customers
      .filter(c => c.day_of_week === day)
      .sort((a, b) => a.stop_number - b.stop_number);
  };

  const getStatusColor = (customers) => {
    const visited = customers.filter(c => 
      c.visits.length > 0 && c.visits[0].status !== 'not_visited'
    ).length;
    const percentage = (visited / customers.length) * 100;
    
    if (percentage === 0) return '#e5e7eb';
    if (percentage < 50) return '#fbbf24';
    if (percentage < 100) return '#60a5fa';
    return '#10b981';
  };

  return (
    <div className="week-view">
      <div className="week-selector">
        {weeks.map(week => (
          <button
            key={week}
            className={`week-button ${selectedWeek === week ? 'active' : ''}`}
            onClick={() => setSelectedWeek(week)}
          >
            Week {week}
            {week <= 2 ? ' (Initial)' : ' (Follow-up)'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading">Loading customers...</div>
      ) : (
        <div className="days-container">
          {days.map(day => {
            const dayCustomers = getCustomersByDay(day);
            const isExpanded = expandedDays[day];
            const location = dayCustomers[0]?.location || '';
            const date = dayCustomers[0]?.date || '';

            return (
              <div key={day} className="day-section">
                <div 
                  className="day-header"
                  style={{ borderLeftColor: getStatusColor(dayCustomers) }}
                  onClick={() => toggleDay(day)}
                >
                  <div className="day-info">
                    <h3>{day}</h3>
                    <span className="day-meta">
                      {location} • {new Date(date).toLocaleDateString()} • {dayCustomers.length} stops
                    </span>
                  </div>
                  <button className="expand-button">
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                </div>

                {isExpanded && (
                  <div className="day-content">
                    {dayCustomers.map(customer => (
                      <CustomerCard 
                        key={customer.id} 
                        customer={customer}
                        onUpdate={loadCustomers}
                      />
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
