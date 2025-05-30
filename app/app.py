import os

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session handling

def calculate_efc(parent_income, student_income, assets, household_size, in_college):
    try:
        if in_college > household_size:
            return None

        parent_contribution = max(0, (parent_income - 25000) * 0.22)
        student_contribution = max(0, student_income * 0.5)
        asset_contribution = max(0, assets * 0.12)
        total_efc = parent_contribution + student_contribution + asset_contribution

        session['breakdown'] = {
            'parent_contribution': round(parent_contribution, 2),
            'student_contribution': round(student_contribution, 2),
            'asset_contribution': round(asset_contribution, 2)
        }

        return round(total_efc / max(in_college, 1), 2)
    except:
        return None

def calculate_pell(efc, coa):
    try:
        pell_amount = round(max(0, min(7395, coa - efc)), 2)
        return pell_amount
    except:
        return None

def calculate_loan_payment(amount, interest_rate, years):
    try:
        monthly_rate = interest_rate / 12 / 100
        n_payments = years * 12
        payment = (amount * monthly_rate) / (1 - (1 + monthly_rate) ** -n_payments)

        schedule = []
        remaining = amount
        total_interest = 0

        for i in range(1, n_payments + 1):
            interest_payment = remaining * monthly_rate
            principal_payment = payment - interest_payment
            remaining -= principal_payment
            total_interest += interest_payment

            if i % 12 == 0:
                schedule.append({
                    'year': i // 12,
                    'principal_paid': round(amount - remaining, 2),
                    'interest_paid': round(total_interest, 2),
                    'remaining_balance': round(max(0, remaining), 2)
                })

        session['loan_schedule'] = schedule
        session['loan_details'] = {
            'monthly_payment': round(payment, 2),
            'total_payments': round(payment * n_payments, 2),
            'total_interest': round(payment * n_payments - amount, 2)
        }

        return round(payment, 2)
    except:
        return None


def calculate_college_savings(target_amount, years, interest_rate, initial_deposit, additional_contribution=0,
                              contribution_frequency="monthly"):
    try:
        monthly_rate = interest_rate / 12 / 100
        n_payments = years * 12

        # Convert yearly contributions to monthly for calculation purposes
        monthly_contribution = additional_contribution if contribution_frequency == "monthly" else additional_contribution / 12

        balance = initial_deposit
        yearly_data = []

        for year in range(1, years + 1):
            for month in range(1, 13):
                interest = balance * monthly_rate
                balance += interest + monthly_contribution

            yearly_data.append({
                'year': year,
                'balance': round(balance, 2),
                'contributions': round(initial_deposit + monthly_contribution * year * 12, 2),
                'earnings': round(balance - initial_deposit - monthly_contribution * year * 12, 2)
            })

        # Calculate how much MORE they would need to contribute monthly to reach the target
        remaining_target = target_amount - balance

        if remaining_target <= 0:
            additional_needed = 0  # They'll exceed their target
        elif monthly_rate == 0:
            additional_needed = remaining_target / n_payments
        else:
            additional_needed = remaining_target * monthly_rate / ((1 + monthly_rate) ** n_payments - 1)

        # Convert to yearly if needed
        if contribution_frequency == "yearly":
            additional_needed *= 12

        session['savings_data'] = yearly_data
        session['monthly_contribution'] = round(additional_needed, 2)
        session['additional_contribution'] = additional_contribution
        session['contribution_frequency'] = contribution_frequency

        return round(additional_needed, 2)
    except:
        return None

@app.route('/')
def index():
    session.clear()  # Clear session to avoid stale data
    return render_template("index.html")

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.form
        parent_income = float(data['parent_income'])
        student_income = float(data['student_income'])
        assets = float(data['assets'])
        household_size = int(data['household_size'])
        in_college = int(data['in_college'])

        efc = calculate_efc(parent_income, student_income, assets, household_size, in_college)

        if efc is None:
            return render_template("index.html", error="Invalid input. Please check your values.")

        session['efc'] = efc
        session['coa'] = None  # clear previous
        session['pell_grant'] = None
        session['aid_gap'] = None

        return redirect(url_for('summary'))
    except:
        return render_template("index.html", error="Invalid input. Please check your values.")


@app.route('/pell', methods=['GET', 'POST'])
def pell():
    grant = None
    error = None
    if request.method == 'POST':
        try:
            efc = float(request.form['efc'])
            coa = float(request.form['coa'])
            grant = calculate_pell(efc, coa)
            session['pell_grant'] = grant
            session['coa'] = coa
            session['aid_gap'] = round(max(0, coa - grant), 2)
            return redirect(url_for('summary'))
        except:
            error = "Invalid input. Please check your values."
    return render_template("pell.html", grant=grant, error=error)

@app.route('/summary')
def summary():
    efc = session.get('efc')
    grant = session.get('pell_grant')
    coa = session.get('coa')
    aid_gap = session.get('aid_gap')
    breakdown = session.get('breakdown')

    total_aid = round(grant, 2) if efc is not None and grant is not None else None

    chart_data = {
        'efc_breakdown': breakdown,
        'aid_coverage': {
            'covered': grant,
            'gap': aid_gap
        } if coa and grant else None
    }

    return render_template(
        "summary.html",
        efc=efc,
        grant=grant,
        coa=coa,
        total_aid=total_aid,
        chart_data=chart_data
    )


@app.route('/loan', methods=['GET', 'POST'])
def loan():
    payment = None
    error = None
    loan_details = None
    loan_schedule = None

    if request.method == 'POST':
        try:
            loan_amount = float(request.form['loan_amount'])
            interest_rate = float(request.form['interest_rate'])
            term_years = int(request.form['term_years'])

            payment = calculate_loan_payment(loan_amount, interest_rate, term_years)
            loan_details = session.get('loan_details')
            loan_schedule = session.get('loan_schedule')
        except Exception as e:
            error = "Invalid input. Please check your values."
            print(f"Error calculating loan payment: {e}")  # For debugging

    return render_template(
        "loan.html",
        payment=payment,
        error=error,
        loan_details=loan_details,
        loan_schedule=json.dumps(loan_schedule) if loan_schedule else None
    )

@app.route('/college-savings', methods=['GET', 'POST'])
def college_savings():
    monthly_contribution = None
    error = None
    additional_contribution = 0
    contribution_frequency = "monthly"

    if request.method == 'POST':
        try:
            target_amount = float(request.form['target_amount'])
            years = int(request.form['years'])
            interest_rate = float(request.form['interest_rate'])
            initial_deposit = float(request.form['initial_deposit'])
            additional_contribution = float(request.form['additional_contribution'])
            contribution_frequency = request.form['contribution_frequency']

            monthly_contribution = calculate_college_savings(
                target_amount, years, interest_rate, initial_deposit,
                additional_contribution, contribution_frequency
            )

            savings_data = session.get('savings_data')
            contribution_frequency = session.get('contribution_frequency')
            additional_contribution = session.get('additional_contribution')

            return render_template(
                "college_savings.html",
                monthly_contribution=monthly_contribution,
                error=error,
                savings_data=savings_data,
                contribution_frequency=contribution_frequency,
                additional_contribution=additional_contribution
            )
        except:
            error = "Invalid input. Please check your values."

    return render_template("college_savings.html",
                          monthly_contribution=monthly_contribution,
                          error=error,
                          contribution_frequency=contribution_frequency)

@app.route('/tips')
def tips():
    return render_template("tips.html")

@app.route('/api/efc-breakdown')
def efc_breakdown_api():
    return jsonify(session.get('breakdown', {}))

@app.route('/api/loan-schedule')
def loan_schedule_api():
    return jsonify(session.get('loan_schedule', []))

@app.route('/api/savings-data')
def savings_data_api():
    return jsonify(session.get('savings_data', []))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
