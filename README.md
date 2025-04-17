# Student Financial Aid Calculator

A comprehensive financial aid calculator with interactive visualizations to help students plan for college expenses.

## Features

- **EFC Calculator**: Estimate Expected Family Contribution based on income and household information
- **Pell Grant Estimator**: Calculate potential federal grant eligibility 
- **Loan Repayment Calculator**: Visualize monthly payments and loan payoff timeline
- **College Savings Calculator**: Plan ahead with a monthly savings estimator
- **Interactive Visualizations**: Charts and graphs for better understanding
- **Mobile Responsive**: Works on all device sizes

## Technology Stack

- **Backend**: Python with Flask framework
- **Frontend**: HTML, Bootstrap 5, Chart.js
- **Containerization**: Docker
- **Deployment**: Google Cloud Run or Vercel

## Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Visit `http://localhost:5000` in your browser

## Docker Deployment

1. Build the Docker image:
   ```
   docker build -t financial-aid-calculator .
   ```
2. Run the container locally:
   ```
   docker run -p 5000:5000 financial-aid-calculator
   ```

## Cloud Deployment

### Google Cloud Run

1. Build and push the Docker image:
   ```
   gcloud builds submit --tag gcr.io/[PROJECT-ID]/financial-aid-calculator
   ```
2. Deploy to Cloud Run:
   ```
   gcloud run deploy financial-aid-calculator --image gcr.io/[PROJECT-ID]/financial-aid-calculator --platform managed
   ```

### Vercel Deployment

1. Install Vercel CLI:
   ```
   npm i -g vercel
   ```
2. Deploy to Vercel:
   ```
   vercel
   ```

## Usage Notes

- All calculations are estimates and should be used for planning purposes only
- Real financial aid amounts may vary based on institution-specific policies
- Always consult with financial aid offices for official determinations