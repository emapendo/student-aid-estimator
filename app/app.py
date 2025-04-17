from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session handling


def calculate_efc(parent_income, student_income, assets, household_size, in_college):
    try:
        parent_contribution = max(0, (parent_income - 25000) * 0.22)
        student_contribution = max(0, student_income * 0.5)
        asset_contribution = max(0, assets * 0.12)
        total_efc = parent_contribution + student_contribution + asset_contribution

        # Save breakdowns for visualization
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

        # Calculate amortization schedule for visualization
        schedule = []
        remaining = amount
        total_interest = 0

        for i in range(1, n_payments + 1):
            interest_payment = remaining * monthly_rate
            principal_payment = payment - interest_payment
            remaining -= principal_payment
            total_interest += interest_payment

            if i % 12 == 0:  # Just store yearly data to keep it manageable
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


def calculate_college_savings(target_amount, years, interest_rate, initial_deposit):
    try:
        monthly_rate = interest_rate / 12 / 100
        n_payments = years * 12

        # PMT formula solved for the periodic payment
        if monthly_rate == 0:
            monthly_contribution = (target_amount - initial_deposit) / n_payments
        else:
            monthly_contribution = (target_amount - initial_deposit * (1 + monthly_rate) ** n_payments) * \
                                   monthly_rate / ((1 + monthly_rate) ** n_payments - 1)

        # Calculate growth over time for visualization
        balance = initial_deposit
        yearly_data = []

        for year in range(1, years + 1):
            for _ in range(12):
                interest = balance * monthly_rate
                balance += interest + monthly_contribution

            yearly_data.append({
                'year': year,
                'balance': round(balance, 2),
                'contributions': round(initial_deposit + monthly_contribution * year * 12, 2),
                'earnings': round(balance - initial_deposit - monthly_contribution * year * 12, 2)
            })

        session['savings_data'] = yearly_data
        session['monthly_contribution'] = round(monthly_contribution, 2)

        return round(monthly_contribution, 2)
    except:
        return None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.form
        efc = calculate_efc(
            float(data['parent_income']),
            float(data['student_income']),
            float(data['assets']),
            int(data['household_size']),
            int(data['in_college'])
        )
        if efc is None:
            raise ValueError("Invalid EFC calculation")

        session['efc'] = efc
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

            # Calculate aid gap for visualization
            net_cost = max(0, coa - grant)
            session['aid_gap'] = round(net_cost, 2)

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

    total_aid = None
    if efc is not None and grant is not None:
        total_aid = round(grant, 2)

    # Convert data for charts
    chart_data = {}
    if breakdown:
        chart_data['efc_breakdown'] = json.dumps(breakdown)

    if coa and grant:
        chart_data['aid_coverage'] = json.dumps({
            'covered': grant,
            'gap': aid_gap
        })

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

    if request.method == 'POST':
        try:
            loan_amount = float(request.form['loan_amount'])
            interest_rate = float(request.form['interest_rate'])
            term_years = int(request.form['term_years'])
            payment = calculate_loan_payment(loan_amount, interest_rate, term_years)
            loan_details = session.get('loan_details')
            loan_schedule = session.get('loan_schedule')

            return render_template(
                "loan.html",
                payment=payment,
                error=error,
                loan_details=loan_details,
                loan_schedule=json.dumps(loan_schedule)
            )
        except:
            error = "Invalid input. Please check your values."

    return render_template("loan.html", payment=payment, error=error)


@app.route('/college-savings', methods=['GET', 'POST'])
def college_savings():
    monthly_contribution = None
    error = None

    if request.method == 'POST':
        try:
            target_amount = float(request.form['target_amount'])
            years = int(request.form['years'])
            interest_rate = float(request.form['interest_rate'])
            initial_deposit = float(request.form['initial_deposit'])

            monthly_contribution = calculate_college_savings(
                target_amount, years, interest_rate, initial_deposit
            )

            savings_data = session.get('savings_data')

            return render_template(
                "college_savings.html",
                monthly_contribution=monthly_contribution,
                error=error,
                savings_data=json.dumps(savings_data)
            )
        except:
            error = "Invalid input. Please check your values."

    return render_template("college_savings.html", monthly_contribution=monthly_contribution, error=error)


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
    app.run(host='0.0.0.0', port=5000)
