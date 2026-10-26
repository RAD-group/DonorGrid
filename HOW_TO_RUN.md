# BLOOD DONATION SYSTEM — COMPLETE SETUP GUIDE
# ================================================================
# ALL ERRORS FIXED. Follow EXACTLY in order.
# ================================================================

## CREDENTIALS (all use password: password123)
- admin         → Super Admin dashboard
- coordinator1  → Camp Coordinator dashboard
- hospitaladmin → Hospital Admin dashboard
- donor1        → Donor dashboard

---

## STEP 1: INSTALL PREREQUISITES (one-time setup)
Install these before anything else:

### Java 17 (JDK)
- Windows: Download from https://adoptium.net → Java 17 → Windows x64 Installer
- After install, verify: open CMD and type: java -version

### Maven
- Download from https://maven.apache.org/download.cgi (Binary zip archive)
- Extract to C:\apache-maven-3.9.x
- Add to PATH: System Properties → Environment Variables → PATH → Add: C:\apache-maven-3.9.x\bin
- Verify: mvn -version

### PostgreSQL
- Download from https://www.postgresql.org/download/
- Install with default settings, remember your postgres password

### Node.js (v18+)
- Download from https://nodejs.org (LTS version)
- Verify: node --version && npm --version

### Python 3.10+
- Download from https://python.org
- IMPORTANT: Check "Add Python to PATH" during install
- Verify: python --version

---

## STEP 2: SETUP DATABASE
Open Command Prompt and run:

    psql -U postgres

When prompted enter your postgres password. Then type:

    CREATE DATABASE bloodbank;
    CREATE USER blooduser WITH PASSWORD 'bloodpass123';
    GRANT ALL PRIVILEGES ON DATABASE bloodbank TO blooduser;
    \c bloodbank
    GRANT ALL ON SCHEMA public TO blooduser;

Then exit psql:
    \q

Now run the schema and seed files:
if inisde database no need : database/schema.sql instead:
    psql -U blooduser -d bloodbank -f schema.sql
    psql -U blooduser -d bloodbank -f seed.sql

You should see INSERT statements confirm the data loaded.

---

## STEP 3: START SPRING BOOT BACKEND
Open a NEW terminal window. The backend reads its secrets from environment
variables (see .env.example); it refuses to start without JWT_SECRET.

On Windows (CMD):

    set DB_PASSWORD=bloodpass123
    set JWT_SECRET=<at least 32 random characters>

On Mac/Linux:

    export DB_PASSWORD=bloodpass123
    export JWT_SECRET="$(openssl rand -base64 48)"

Use the database password you chose in Step 2. Then:

    cd backend
    mvn clean install -DskipTests
    mvn spring-boot:run

Wait until you see: "Started BackendApplication" (takes 30-60 seconds first time)
Backend runs at: http://localhost:8080

### VERIFY IT WORKS:
Open browser and go to: http://localhost:8080/api/public/stats
You should see JSON with donor and camp counts. If you see this, backend is working!

### WHY LOGIN WAS FAILING BEFORE:
The old config had ddl-auto=validate which crashes if tables have any mismatch.
Now it uses ddl-auto=update which auto-creates/updates tables.
Also the security config now allows all roles to access the dashboard data endpoints.

---

## STEP 4: START ML SERVICE (FastAPI)
Open another NEW terminal window:

    cd ml-service
    python -m venv venv

On Windows:
    venv\Scripts\activate

On Mac/Linux:
    source venv/bin/activate

Then install and run:

    pip install -r requirements.txt
    python -m uvicorn main:app --reload --port 8000

Wait until you see: "Application startup complete"
ML Service runs at: http://localhost:8000

### VERIFY IT WORKS:
Go to: http://localhost:8000
You should see: {"status":"Blood Donation ML Service running OK"}

### HUGGINGFACE SETUP (OPTIONAL - chat still works without it):
1. Go to https://huggingface.co → Sign Up (free)
2. Click your profile → Settings → Access Tokens → New Token → Read → Generate
3. Copy token (starts with hf_)
4. Before starting the ML service, set it in that terminal:
   Windows: set HF_API_KEY=hf_...    Mac/Linux: export HF_API_KEY=hf_...
5. Never write the key into main.py or any file in git

---

## STEP 5: START REACT FRONTEND
Open another NEW terminal window:

    cd frontend
    npm install
    npm start

Wait for browser to open automatically at: http://localhost:3000
If it doesn't open, manually go to: http://localhost:3000

---

## STEP 6: LOGIN AND TEST

1. Go to http://localhost:3000
2. Click "Get Started" or "Sign In"
3. Enter: username = admin, password = password123
4. You land on the Super Admin dashboard

### Test each role:
- admin / password123 → Super Admin (all data, user management)
- donor1 / password123 → Donor (eligibility, registration, predictions)
- coordinator1 / password123 → Coordinator (camps, location ML)
- hospitaladmin / password123 → Hospital Admin (blood stock, alerts)

---

## COMMON ERRORS AND FIXES

### "Login failed" / "Username not found"
- Make sure seed.sql was run: psql -U blooduser -d bloodbank -f database/seed.sql
- Verify user exists: psql -U blooduser -d bloodbank -c "SELECT username,role FROM users;"

### Backend won't start — "Unable to acquire JDBC Connection"
- PostgreSQL is not running. Start it:
  Windows: Services → postgresql → Start
  Linux: sudo service postgresql start

### Backend error — "relation does not exist"
- Run schema.sql first: psql -U blooduser -d bloodbank -f database/schema.sql

### "CORS error" in browser console
- Make sure backend is running on port 8080
- Don't change the baseURL in api.js

### ML service "Module not found"
- Make sure you activated venv before pip install
- Run: pip install -r requirements.txt again

### Frontend shows blank page
- Run: npm install (inside frontend folder)
- Then: npm start

---

## RUNNING ORDER (EVERY TIME)
Open 3 terminal windows and run in this order:

Terminal 1 (Backend, after setting DB_PASSWORD and JWT_SECRET as in Step 3):
    cd backend && mvn spring-boot:run

Terminal 2 (ML Service):
    cd ml-service && venv\Scripts\activate && python -m uvicorn main:app --reload --port 8000

Terminal 3 (Frontend):
    cd frontend && npm start

---

## VERSIONS USED
- Java: 17 (JDK 17)
- Spring Boot: 3.2.0
- Maven: 3.9+
- Python: 3.12 (the saved models need scikit-learn 1.9.1, as pinned in requirements.txt)
- Node.js: 18+
- PostgreSQL: 14+
