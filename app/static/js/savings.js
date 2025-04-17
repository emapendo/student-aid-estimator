document.addEventListener('DOMContentLoaded', function () {
  const ctx = document.getElementById('savingsChart').getContext('2d');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: savingsData.map(item => `Year ${item.year}`),
      datasets: [
        {
          label: 'Balance',
          data: savingsData.map(item => item.balance),
          backgroundColor: 'rgba(13, 110, 253, 0.2)',
          borderColor: 'rgba(13, 110, 253, 1)',
          borderWidth: 2,
          fill: true
        },
        {
          label: 'Contributions',
          data: savingsData.map(item => item.contributions),
          backgroundColor: 'rgba(40, 167, 69, 0.2)',
          borderColor: 'rgba(40, 167, 69, 1)',
          borderWidth: 2,
          fill: true
        }
      ]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function (value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
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
