document.addEventListener('DOMContentLoaded', function () {
  if (typeof loanChartData === 'undefined') return;

  const ctx = document.getElementById('loanChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: loanChartData.map((item, i) => `Month ${i + 1}`),
      datasets: [
        {
          label: 'Remaining Balance',
          data: loanChartData.map(item => item.remaining_balance),
          borderColor: '#0d6efd',
          fill: false,
          tension: 0.3
        },
        {
          label: 'Principal Paid',
          data: loanChartData.map(item => item.principal_paid),
          borderColor: '#198754',
          fill: false,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.dataset.label}: $${context.raw.toLocaleString()}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      }
    }
  });
});
