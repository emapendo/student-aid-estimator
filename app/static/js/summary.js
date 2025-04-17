document.addEventListener('DOMContentLoaded', function () {
  if (typeof coverageData !== 'undefined') {
    const coverageCtx = document.getElementById('coverageChart').getContext('2d');
    new Chart(coverageCtx, {
      type: 'doughnut',
      data: {
        labels: ['Covered by Grant', 'Remaining Need'],
        datasets: [{
          data: [coverageData.covered, coverageData.gap],
          backgroundColor: ['#198754', '#dc3545'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.label || '';
                const value = context.raw;
                return `${label}: $${value.toLocaleString()}`;
              }
            }
          }
        }
      }
    });
  }

  if (typeof breakdownData !== 'undefined') {
    const breakdownCtx = document.getElementById('breakdownChart').getContext('2d');
    new Chart(breakdownCtx, {
      type: 'bar',
      data: {
        labels: ['Parent Contribution', 'Student Contribution', 'Asset Contribution'],
        datasets: [{
          label: 'Amount ($)',
          data: [
            breakdownData.parent_contribution,
            breakdownData.student_contribution,
            breakdownData.asset_contribution
          ],
          backgroundColor: [
            'rgba(13, 110, 253, 0.7)',
            'rgba(255, 193, 7, 0.7)',
            'rgba(108, 117, 125, 0.7)'
          ],
          borderColor: [
            'rgba(13, 110, 253, 1)',
            'rgba(255, 193, 7, 1)',
            'rgba(108, 117, 125, 1)'
          ],
          borderWidth: 1
        }]
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
        }
      }
    });
  }
});
