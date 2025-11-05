# WareWise - Intelligent Warehouse Optimization Platform

> Transform raw warehouse inventory data into actionable insights through intelligent anomaly detection

WareWise (Ware-Intelligence Engine) is an enterprise-grade SaaS application that helps warehouse managers and logistics professionals identify and resolve operational inefficiencies. Using a sophisticated rule-based analysis system, WareWise automatically detects warehouse problems, optimizes space utilization, and provides data-driven insights for continuous improvement.

## 🎯 Key Features

### Intelligent Inventory Analysis
- **Smart File Upload**: Import inventory data from Excel/CSV files with automatic column mapping
- **Fuzzy Column Matching**: Intelligent field detection that understands variations in column names
- **Advanced Date Parsing**: Automatically detects and parses 20+ date formats
- **Real-time Anomaly Detection**: Immediate identification of warehouse inefficiencies

### Dynamic Rule System
Eight default rules powered by a customizable rule engine:

**FLOW & TIME Rules:**
- **Forgotten Pallets Alert** (VERY_HIGH) - Detects pallets in receiving >10 hours
- **Incomplete Lots Alert** (VERY_HIGH) - Identifies lot stragglers
- **AISLE Stuck Pallets** (HIGH) - Pallets stuck in transit >4 hours

**SPACE Rules:**
- **Overcapacity Alert** (HIGH) - Locations exceeding capacity
- **Invalid Locations Alert** (HIGH) - Pallets in undefined locations
- **Scanner Error Detection** (MEDIUM) - Data integrity issues
- **Location Type Mismatches** (HIGH) - Mapping inconsistencies

**PRODUCT Rules:**
- **Cold Chain Violations** (VERY_HIGH) - Temperature-sensitive storage issues

### Comprehensive Analytics
- Pilot analytics system with immutable cumulative counters
- Time savings calculations and ROI tracking
- Anomaly heatmaps by location and priority
- Performance metrics dashboards
- Historical trend analysis

### Warehouse Configuration
- Define warehouse locations, zones, and capacities
- Set location constraints and compatibility rules
- Smart configuration auto-detection
- Template system for rapid warehouse setup

### Anomaly Management
- Priority-based categorization (VERY_HIGH, HIGH, MEDIUM, LOW)
- Status tracking (New, Acknowledged, In Progress, Resolved)
- Location-based grouping and filtering
- Detailed anomaly investigation tools

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4 + PostCSS
- **UI Components**: Radix UI
- **Charts**: Chart.js, react-chartjs-2, Recharts
- **State Management**: Zustand
- **Form Handling**: react-hook-form
- **Other**: Axios, react-dropzone, date-fns, lucide-react

### Backend
- **Framework**: Flask 3.1.1 (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login + JWT tokens
- **Security**: Werkzeug password hashing
- **Data Processing**: Pandas 2.2.3, openpyxl
- **Utilities**: rapidfuzz (fuzzy matching), python-dateutil
- **Deployment**: Gunicorn WSGI server

### Infrastructure
- **Hosting**: Vercel (frontend), custom backend
- **Database**: PostgreSQL (production)
- **CORS**: Flask-CORS for cross-origin requests

## 📁 Project Structure

```
Ware-Eng/
├── backend/                    # Flask API backend
│   ├── src/
│   │   ├── app.py             # Main Flask application
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── rule_engine.py     # Dynamic rule evaluation system
│   │   ├── rules_api.py       # Rule management endpoints
│   │   ├── warehouse_api.py   # Warehouse configuration API
│   │   ├── location_api.py    # Location management API
│   │   ├── template_api.py    # Template system API
│   │   ├── wins_api.py        # ROI/Wins tracking API
│   │   ├── analytics_service.py  # Analytics engine
│   │   ├── column_matcher.py  # Intelligent column mapping
│   │   ├── date_parser.py     # Smart date format detection
│   │   └── ...                # Additional services
│   ├── migrations/            # Database migrations
│   ├── templates/             # Jinja2 templates
│   ├── requirements.txt       # Python dependencies
│   └── README_DEPLOYMENT.md   # Deployment guide
│
├── frontend/                  # Next.js React frontend
│   ├── app/                   # Next.js 13+ app directory
│   │   ├── page.tsx           # Landing page
│   │   ├── auth/              # Authentication pages
│   │   ├── admin/             # Admin panel
│   │   ├── demo-interfaces/   # Feature demos
│   │   └── track-wins/        # ROI tracking
│   ├── components/
│   │   ├── dashboard/         # Main dashboard components
│   │   ├── analysis/          # File upload/mapping
│   │   ├── rules/             # Rule management UI
│   │   ├── locations/         # Location configuration
│   │   └── ui/                # Reusable UI components
│   ├── lib/
│   │   ├── api.ts             # API client utilities
│   │   ├── auth.ts            # Authentication utilities
│   │   ├── rules-store.ts     # Rules state management
│   │   └── store.ts           # Main app state
│   ├── package.json           # Frontend dependencies
│   └── next.config.ts         # Next.js configuration
│
├── Tests/                     # Test suites
├── Bugs/                      # Issue tracking
└── Descriptions/              # Feature documentation
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18.x or higher
- **Python** 3.9 or higher
- **PostgreSQL** 12 or higher
- **npm** or **yarn**

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/warewise
   JWT_SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   CORS_ORIGINS=http://localhost:3000
   ```

5. **Initialize database**
   ```bash
   python src/app.py
   ```
   The application will automatically create tables on first run.

6. **Run the development server**
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` and set:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   NEXT_PUBLIC_API_ORIGIN=http://localhost:3000
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 📖 Usage

### Quick Start Guide

1. **Create an Account**
   - Navigate to `/auth/signup`
   - Register with your email and password
   - Create your first warehouse

2. **Upload Inventory Data**
   - Go to "New Analysis" in the dashboard
   - Upload an Excel/CSV file with your inventory data
   - Map columns to required fields (pallet ID, location, dates, etc.)
   - Click "Analyze" to run anomaly detection

3. **Review Anomalies**
   - View detected issues in the Action Center
   - Filter by priority, location, or status
   - Acknowledge and track resolution progress

4. **Configure Warehouse**
   - Set up locations in Warehouse Settings
   - Define zones, capacities, and constraints
   - Apply templates for rapid configuration

5. **Customize Rules**
   - Enable/disable rules based on your needs
   - Adjust thresholds and parameters
   - Create custom rules for specific workflows

6. **Track Performance**
   - View analytics dashboard for insights
   - Track time savings and ROI
   - Export reports for stakeholders

## ⚙️ Configuration

### Warehouse Configuration

Define your warehouse structure in the Warehouse Settings view:

- **Locations**: Physical storage locations (e.g., RECEIVING, A-01-01)
- **Zones**: Logical groupings (RECEIVING, STORAGE, AISLE)
- **Capacities**: Maximum pallets per location
- **Product Types**: Compatible product categories

### Rule Configuration

Customize the rule engine to match your operations:

- **Enable/Disable Rules**: Turn rules on/off as needed
- **Adjust Thresholds**: Modify time limits, capacity percentages
- **Set Priorities**: Control alert severity levels
- **Create Custom Rules**: Define business-specific logic

### Data Mapping

The intelligent column matcher automatically detects:

- **Pallet IDs**: pallet_id, pallet, id, palletid, etc.
- **Locations**: location, loc, current_location, storage_location
- **Dates**: received_date, timestamp, date_received, receive_dt
- **Products**: product_code, sku, item_number, product_id
- **Lots**: lot_number, lot, batch, lot_code

## 🔐 Authentication & Security

- **JWT Token-Based Authentication**: Secure session management
- **Password Hashing**: Werkzeug security with salt
- **Multi-Tenancy**: Warehouse-based data isolation
- **Role-Based Access Control**: Admin and user roles
- **CORS Protection**: Configured allowed origins

## 📊 API Documentation

### Core Endpoints

**Authentication**
```
POST /auth/signup          # Create new user
POST /auth/login           # Authenticate user
POST /auth/logout          # End session
GET  /auth/user            # Get current user
```

**Analysis**
```
POST /upload_and_analyze   # Upload inventory file
GET  /analysis_reports     # List reports
GET  /analysis_reports/:id # Get report details
```

**Rules**
```
GET    /rules              # List all rules
POST   /rules              # Create custom rule
PUT    /rules/:id          # Update rule
DELETE /rules/:id          # Delete rule
```

**Locations**
```
GET    /locations          # List warehouse locations
POST   /locations          # Add location
PUT    /locations/:id      # Update location
DELETE /locations/:id      # Delete location
```

**Analytics**
```
GET /pilot-analytics       # Get analytics data
GET /analytics/summary     # Summary metrics
GET /analytics/trends      # Historical trends
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🚢 Deployment

See `backend/README_DEPLOYMENT.md` for detailed deployment instructions.

### Quick Deploy

**Backend (Render/Railway)**
```bash
# Set environment variables
DATABASE_URL=your-postgres-url
JWT_SECRET_KEY=your-secret

# Deploy
git push origin main
```

**Frontend (Vercel)**
```bash
# Connect to Vercel
vercel --prod

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-api.com
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

- Follow TypeScript/Python best practices
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is proprietary software. All rights reserved.

## 🙏 Acknowledgments

- Built with modern frameworks: Next.js, Flask, PostgreSQL
- UI components by Radix UI
- Charts by Chart.js and Recharts
- Icons by Lucide React

## 📧 Contact & Support

For questions, issues, or feature requests, please open an issue on GitHub.

---

**Made with ❤️ by the WareWise Team**
