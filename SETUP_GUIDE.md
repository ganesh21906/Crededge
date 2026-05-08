# Quick Setup Guide

## Prerequisites
- Node.js (v16 or higher)
- Python (v3.10 or higher)
- npm or yarn

## Step 1: Frontend Setup

1. Open terminal in the project folder
2. Navigate to frontend:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Start the development server:
   ```bash
   npm start
   ```

5. The application will open at `http://localhost:3000`

## Step 2: Backend Setup

1. Open a NEW terminal in the project folder
2. Navigate to backend:
   ```bash
   cd backend
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Activate it:
   # Windows:
   venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the API server:
   ```bash
   python app.py
   ```

6. The API will run at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

## Step 3: Test the Application

1. Open browser to `http://localhost:3000`
2. Navigate through:
   - **Home Page**: Overview of the platform
   - **Individual Application**: Fill the form with sample data
   - **SME Application**: Fill the business loan form
   - **Dashboard**: View application statistics
   - **Admin Panel**: Review submitted applications

## Sample Data to Test With

### Individual Application:
- Name: Rajesh Kumar
- Mobile: 9876543210
- Email: rajesh@email.com
- Monthly Income: 50000
- Loan Amount: 200000
- Check all alternative data checkboxes

### SME Application:
- Business Name: Kumar Traders
- Mobile: 9876543210
- Email: info@kumartraders.com
- Annual Revenue: 5000000
- Loan Amount: 1000000
- GST Number: 29ABCDE1234F1Z5

## What You'll See

### Sample Data Throughout the Application:
- ✅ All forms show **placeholders** indicating what data goes where
- ✅ Dashboard shows **mock statistics** and sample applications
- ✅ Credit score page displays **AI-generated assessment** with factors
- ✅ Admin panel shows **sample pending applications**

### Data Collection Points:
- **Personal/Business Info**: Basic details
- **Financial Info**: Income/Revenue details
- **Alternative Data Checkboxes**: Shows what supporting documents are needed
- **Banking Info**: Account details
- **Loan Requirements**: Amount and purpose

## Important Notes

1. **All data is currently MOCK/SAMPLE** - no real API connections yet
2. **Forms are fully functional** - they collect and display data properly
3. **No database** - submissions are not stored (for now)
4. **Credit scores are randomly generated** - ML model not implemented yet

## Troubleshooting

### Frontend won't start:
```bash
# Delete node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Backend won't start:
```bash
# Ensure Python 3.10+ is installed
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port already in use:
- Frontend (3000): Change in `frontend/package.json` proxy setting
- Backend (8000): Change in `backend/app.py` port parameter

## Next Development Steps

1. **Connect APIs**: Link frontend forms to backend endpoints
2. **Add Database**: Store applications in PostgreSQL/MongoDB
3. **Implement ML Model**: Build actual credit scoring algorithm
4. **Add Authentication**: User login/signup system
5. **Integrate Real APIs**: GST, DigiLocker, utility bill verification

## File Structure
```
Mini project 3rd sem/
├── frontend/                # React application
│   ├── src/
│   │   ├── pages/          # All application pages
│   │   ├── App.js          # Main app component
│   │   └── index.js        # Entry point
│   └── package.json        # Dependencies
├── backend/                # FastAPI application
│   ├── app.py             # Main API server
│   └── requirements.txt    # Python dependencies
├── data/                   # Sample data files
│   ├── sample_applications.json
│   └── alternative_data_sources.json
├── README.md              # Project overview
└── PROJECT_DOCUMENTATION.md # Detailed documentation
```

## Need Help?

Check the following files:
- `README.md` - Project overview
- `PROJECT_DOCUMENTATION.md` - Detailed technical documentation
- `data/alternative_data_sources.json` - See all data sources we use

---
**Happy Coding! 🚀**
