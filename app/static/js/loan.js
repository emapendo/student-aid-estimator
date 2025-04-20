document.addEventListener('DOMContentLoaded', function() {
  // Get the loan schedule data from the data attribute
  const loanScheduleElement = document.getElementById('loan-schedule-data');
  if (!loanScheduleElement) return;

  const loanSchedule = JSON.parse(loanScheduleElement.dataset.schedule);

  const ctx = document.getElementById('loanBalanceChart').getContext('2d');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: loanSchedule.map(item => `Year ${item.year}`),
      datasets: [{
        label: 'Remaining Balance',
        data: loanSchedule.map(item => item.remaining_balance),
        borderColor: 'rgba(220, 53, 69, 1)',
        backgroundColor: 'rgba(220, 53, 69, 0.1)',
        fill: true
      }, {
        label: 'Principal Paid',
        data: loanSchedule.map(item => item.principal_paid),
        borderColor: 'rgba(40, 167, 69, 1)',
        backgroundColor: 'rgba(40, 167, 69, 0.1)',
        fill: true
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              let label = context.dataset.label || '';
              if (label) label += ': ';
              label += '$' + context.raw.toLocaleString();
              return label;
            }
          }
        }
      }
    }
  });
});
