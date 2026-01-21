# Sales Route Tracker - Setup Guide

## Step 1: Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: Sales Route Tracker
   - **Supported account types**: Accounts in any organizational directory and personal Microsoft accounts
   - **Redirect URI**: 
     - Platform: Web
     - URI: `http://localhost:8000/auth/callback`
5. Click **Register**

### Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add these permissions:
   - `Files.ReadWrite.All`
   - `User.Read`
   - `offline_access`
6. Click **Grant admin consent** (if you're an admin)

### Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description (e.g., "Sales Route Tracker Secret")
4. Choose an expiration period (recommended: 24 months)
5. Click **Add**
6. **IMPORTANT**: Copy the secret value immediately - you won't be able to see it again!

### Copy Your Credentials

You'll need these three values:
- **Application (client) ID** - from the Overview page
- **Client secret** - the value you just copied
- **Directory (tenant) ID** - from the Overview page (you can use "common" for multi-tenant)

## Step 2: Upload Excel File to OneDrive

1. Log into OneDrive
2. Create a folder structure (e.g., `/Sales/`)
3. Upload your Excel file: `KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx`
4. Note the full path (e.g., `/Sales/KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx`)

## Step 3: Configure the Application

1. Clone or download this project
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` file with your values:

```env
# Database Configuration (you can keep these defaults)
POSTGRES_USER=salesroute
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=salesroute
DATABASE_URL=postgresql://salesroute:your_secure_password_here@db:5432/salesroute

# Microsoft Graph API Configuration (from Azure Portal)
MICROSOFT_CLIENT_ID=your_client_id_from_azure
MICROSOFT_CLIENT_SECRET=your_client_secret_from_azure
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/callback

# OneDrive File Path (the path to your Excel file)
ONEDRIVE_FILE_PATH=/Sales/KalebHogelandJanuary19thStart4WeekSalesRoutePlan__1_.xlsx

# Backend Security (generate a secure key)
SECRET_KEY=run_this_command_to_generate: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

4. Generate a secure SECRET_KEY:
   ```bash
   openssl rand -hex 32
   ```
   Copy the output and paste it as your SECRET_KEY value

## Step 4: Run the Application

Make sure you have Docker and Docker Compose installed, then:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check if everything is running
docker-compose ps
```

You should see three services running:
- `db` (PostgreSQL)
- `backend` (FastAPI)
- `frontend` (React)

## Step 5: Access the Application

1. Open your browser and go to: http://localhost:5173
2. Click **Connect to OneDrive**
3. Sign in with your Microsoft account
4. Grant permissions to the app
5. You'll be redirected back to the app
6. Click **Sync from OneDrive** to import your route plan

## Step 6: Start Tracking!

You're all set! You can now:
- View your 4-week route plan
- Track customer visits
- Record sales and notes
- Set follow-up reminders
- Export tracking data back to OneDrive

## Troubleshooting

### Issue: "Failed to sync from OneDrive"

**Solution**: 
- Check that your file path in `.env` matches exactly with the file in OneDrive
- Make sure the file name matches (including the double underscores)
- Verify your Microsoft credentials are correct

### Issue: "Authentication failed"

**Solution**:
- Double-check your Azure App credentials (Client ID, Client Secret)
- Ensure the redirect URI in Azure matches exactly: `http://localhost:8000/auth/callback`
- Make sure you granted the necessary API permissions

### Issue: "Database connection failed"

**Solution**:
- Make sure Docker is running
- Check if the database container is healthy: `docker-compose ps`
- Verify your DATABASE_URL matches your POSTGRES credentials

### Issue: "Cannot access the app on mobile"

**Solution**:
- Find your computer's local IP address
- Update `.env` VITE_API_URL to use your IP: `http://192.168.x.x:8000`
- Update Azure redirect URI to include: `http://192.168.x.x:8000/auth/callback`
- Restart the containers: `docker-compose restart`
- Access from mobile: `http://192.168.x.x:5173`

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v
```

## Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose up -d --build

# View logs to ensure everything started correctly
docker-compose logs -f
```

## Production Deployment

For production deployment:

1. Use a proper domain name
2. Set up HTTPS/SSL certificates
3. Update redirect URIs in Azure to use your domain
4. Use strong passwords for database
5. Consider using a managed PostgreSQL service
6. Set up proper backup for the database
7. Use environment-specific `.env` files
8. Consider deploying to: AWS, Azure, Google Cloud, or DigitalOcean

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify your `.env` configuration
3. Ensure all Azure permissions are granted
4. Check that your OneDrive file path is correct
