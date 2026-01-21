# Sales Route Tracker

A full-stack web application for tracking Kimball Midwest sales routes with OneDrive integration.

## Features

- 📅 4-week route plan visualization
- ✅ Visit tracking with status updates
- 📝 Notes and sales tracking per customer
- 💰 Sales amount recording
- 🔄 Real-time sync with OneDrive Excel file
- 📱 Mobile-friendly responsive design
- 📊 Progress dashboard and statistics

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **Database**: PostgreSQL
- **Integration**: Microsoft Graph API (OneDrive)
- **Deployment**: Docker + Docker Compose

## Setup

### 🚀 Cloud Deployment (Recommended for Mobile Access)

Want to access your sales tracker from your phone anywhere? Deploy to Azure in 5 minutes:

→ **[Azure Deployment Quick Start](AZURE_QUICKSTART.md)**

This will give you:
- ☁️ Cloud-hosted application
- 📱 Mobile access from anywhere
- 🔐 Secure HTTPS connection
- 💾 Automatic database backups
- 🌍 Global access

**Cost**: ~$30-40/month (or use free tier for first month)

### Local Setup (Docker)

#### Prerequisites

- Docker & Docker Compose
- Microsoft Azure App Registration (for OneDrive API)
- OneDrive account with the Excel file

#### Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Name: "Sales Route Tracker"
5. Redirect URI: `http://localhost:8000/auth/callback`
6. Permissions needed:
   - `Files.ReadWrite.All`
   - `User.Read`

#### Environment Variables

Create `.env` file in the root directory:

```env
# Database
POSTGRES_USER=salesroute
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=salesroute
DATABASE_URL=postgresql://salesroute:your_secure_password@db:5432/salesroute

# Microsoft Graph API
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/callback

# OneDrive File Path
ONEDRIVE_FILE_PATH=/Sales/KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx

# Backend
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Frontend
VITE_API_URL=http://localhost:8000
```

### Running the Application

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application at: http://localhost:5173

## Project Structure

```
sales-route-tracker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Microsoft OAuth
│   │   │   ├── customers.py     # Customer endpoints
│   │   │   ├── visits.py        # Visit tracking
│   │   │   └── sync.py          # OneDrive sync
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── customer.py
│   │   │   └── visit.py
│   │   ├── services/
│   │   │   ├── onedrive.py      # OneDrive integration
│   │   │   └── excel_parser.py  # Excel parsing
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── WeekView.jsx
│   │   │   ├── CustomerCard.jsx
│   │   │   └── VisitModal.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## Usage

### First Time Setup

1. Navigate to the app
2. Click "Connect to OneDrive"
3. Authenticate with Microsoft
4. The app will sync your Excel file and populate the database
5. Start tracking visits!

### Tracking Visits

- **Status Options**:
  - Not Visited (default)
  - Visited - No Contact
  - Visited - Contact Made
  - Sale Made
  - Follow-up Required

- **For Each Visit**:
  - Mark status
  - Add notes
  - Record sales amount
  - Set next action date

### Syncing

- Manual sync: Click "Sync with OneDrive" button
- Auto-sync: Happens every 15 minutes in background
- Changes are written back to Excel file in a tracking sheet

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## License

Proprietary - Kaleb Hogeland / Kimball Midwest
