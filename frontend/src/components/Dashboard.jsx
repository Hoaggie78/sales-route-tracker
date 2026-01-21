import { useState, useEffect } from 'react';
import { visitService } from '../services/api';
import { TrendingUp, Users, DollarSign, Calendar } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await visitService.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (!stats) {
    return <div className="error">Failed to load dashboard</div>;
  }

  const statCards = [
    {
      icon: Users,
      label: 'Total Customers',
      value: stats.total_customers,
      color: '#3b82f6'
    },
    {
      icon: TrendingUp,
      label: 'Visited',
      value: stats.visited_count,
      color: '#10b981'
    },
    {
      icon: DollarSign,
      label: 'Sales Made',
      value: stats.sales_made_count,
      subValue: `$${stats.total_sales_amount.toFixed(2)}`,
      color: '#f59e0b'
    },
    {
      icon: Calendar,
      label: 'Follow-ups',
      value: stats.follow_ups_required,
      color: '#ef4444'
    }
  ];

  const weekProgress = [
    { week: 1, progress: stats.week_1_progress },
    { week: 2, progress: stats.week_2_progress },
    { week: 3, progress: stats.week_3_progress },
    { week: 4, progress: stats.week_4_progress }
  ];

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      <div className="stats-grid">
        {statCards.map((stat, index) => (
          <div key={index} className="stat-card" style={{ borderLeftColor: stat.color }}>
            <div className="stat-icon" style={{ color: stat.color }}>
              <stat.icon size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stat.value}</div>
              {stat.subValue && <div className="stat-subvalue">{stat.subValue}</div>}
              <div className="stat-label">{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="week-progress-section">
        <h2>Weekly Progress</h2>
        <div className="week-progress-grid">
          {weekProgress.map((week) => (
            <div key={week.week} className="week-progress-card">
              <div className="week-label">Week {week.week}</div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${week.progress}%` }}
                />
              </div>
              <div className="progress-value">{week.progress.toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
