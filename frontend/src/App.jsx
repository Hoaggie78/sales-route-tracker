import { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate, useSearchParams } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import WeekView from './components/WeekView';
import { authService, syncService } from './services/api';
import { Download, Upload, LogOut, Menu, X, Database, Settings, Calendar, ChevronRight, Loader2 } from 'lucide-react';
import './styles/App.css';

function AuthSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      localStorage.setItem('token', token);
      navigate('/');
    }
  }, [searchParams, navigate]);

  return <div className="loading">Authenticating...</div>;
}

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Default to true now
  const [currentUser, setCurrentUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedWeek, setSelectedWeek] = useState(1);
  const [selectedDay, setSelectedDay] = useState('MONDAY');
  const [syncStatus, setSyncStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Check for existing token just in case, but prioritize app flow
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    fetchSyncStatus();
  }, []);

  const fetchSyncStatus = async () => {
    try {
      const status = await syncService.getStatus();
      setSyncStatus(status.data);
    } catch (err) {
      console.error('Failed to fetch sync status:', err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    try {
      await syncService.uploadFile(file);
      await fetchSyncStatus();
      alert('Successfully uploaded route plan!');
    } catch (err) {
      console.error('UPLOAD ERROR FULL:', err);
      if (err.response) {
        console.error('UPLOAD ERROR DATA:', err.response.data);
        setError(`Upload failed: ${err.response.data.detail || 'Server error'}`);
      } else {
        setError('Failed to upload route plan. Please check the file format or server connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileDownload = async () => {
    setLoading(true);
    try {
      await syncService.downloadFile();
    } catch (err) {
      alert('Failed to download tracking data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    // No longer needed but kept for minimal changes
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(true); // Don't actually gate anymore
  };

  const renderDashboard = () => (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="user-profile">
          <div className="avatar">KH</div>
          <div className="user-info">
            <h2>Kaleb's Sales Route</h2>
            <p>Ready for your daily route</p>
          </div>
        </div>
        <button onClick={handleLogout} className="icon-button" title="Settings">
          <Settings size={20} />
        </button>
      </header>

      <section className="sync-section card">
        <div className="card-content">
          <div className="sync-info">
            <div className="sync-icon">
              <Database size={24} color="#6366f1" />
            </div>
            <div>
              <h3>Route Plan Management</h3>
              <p>
                {syncStatus?.has_data
                  ? `${syncStatus.total_customers} customers loaded in Supabase`
                  : 'No route data loaded yet'}
              </p>
            </div>
          </div>

          <div className="sync-actions">
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".xlsx,.xls"
              onChange={handleFileUpload}
            />
            <button
              onClick={() => fileInputRef.current.click()}
              disabled={loading}
              className="sync-button primary"
            >
              {loading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <Upload size={20} />
              )}
              <span>Upload Route Plan</span>
            </button>

            <button
              onClick={handleFileDownload}
              disabled={loading || !syncStatus?.has_data}
              className="sync-button secondary"
            >
              <Download size={20} />
              <span>Download Tracking Data</span>
            </button>
          </div>

          {error && <p className="error-text">{error}</p>}
        </div>
      </section>

      <section className="weeks-section">
        <h3>Choose Your Week</h3>
        <div className="week-grid">
          {[1, 2, 3, 4].map(num => (
            <button
              key={num}
              className="week-card"
              onClick={() => {
                setSelectedWeek(num);
                setCurrentView('week');
              }}
            >
              <Calendar size={28} />
              <span>Week {num}</span>
              <ChevronRight size={16} />
            </button>
          ))}
        </div>
      </section>

      {syncStatus?.has_data && (
        <section className="stats-section card">
          <h3>Collection Overview</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{syncStatus.total_customers}</span>
              <span className="stat-label">Total Stops</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{syncStatus.total_visits}</span>
              <span className="stat-label">Visits Tracked</span>
            </div>
          </div>
        </section>
      )}
    </div>
  );

  // Return the main layout directly, bypassing the login gate
  return (
    <div className="app-container">
      <main className="main-content">
        {currentView === 'dashboard' ? (
          renderDashboard()
        ) : currentView === 'week' ? (
          <WeekView
            weekNumber={selectedWeek}
            onBack={() => setCurrentView('dashboard')}
            onDaySelect={(day) => {
              setSelectedDay(day);
              setCurrentView('day');
            }}
          />
        ) : (
          <DayView
            weekNumber={selectedWeek}
            dayName={selectedDay}
            onBack={() => setCurrentView('week')}
          />
        )}
      </main>
    </div>
  );
};

export default function AppWrapper() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/auth/success" element={<AuthSuccess />} />
      </Routes>
    </Router>
  );
}
