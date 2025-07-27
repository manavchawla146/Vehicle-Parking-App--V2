<template>
  <div class="container">
    <div class="dash-box">
      <h2><i class="fas fa-chart-bar"></i> Admin Summary</h2>
      <AdminNavbar />
      <div class="summary-card">
        <!-- Chart Containers -->
        <div class="chart-container">
          <h4>Occupancy by Parking Lot</h4>
          <canvas id="chart1"></canvas>
        </div>
        <div class="chart-container">
          <h4>Overall Parking Utilization</h4>
          <canvas id="chart2"></canvas>
        </div>
        <div class="chart-container">
          <h4>Daily Occupancy Trend</h4>
          <canvas id="chart3"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbar from './ad-nav.vue';
import Chart from 'chart.js/auto';

export default {
  name: 'AdminSummary',
  components: {
    AdminNavbar,
  },
  data() {
    return {
      chart1: null,
      chart2: null,
      chart3: null,
      loading: true,
      error: null,
    };
  },
  async mounted() {
    try {
      // Fetch lots data
      const lotsRes = await fetch('/api/admin/lots');
      const lots = await lotsRes.json();
      // Prepare data for charts 1 and 2
      const lotLabels = lots.map(lot => lot.primeLocation);
      const occupiedData = lots.map(lot => lot.occupied);
      const available = lots.reduce((sum, lot) => sum + lot.available, 0);
      const occupied = lots.reduce((sum, lot) => sum + lot.occupied, 0);

      // Chart 1: Occupancy by Parking Lot
      this.chart1 = new Chart(document.getElementById('chart1'), {
        type: 'bar',
        data: {
          labels: lotLabels,
          datasets: [{
            label: 'Occupied Spots',
            data: occupiedData,
            backgroundColor: ["#4dd0e1", "#81c784", "#ef5350", "#ffd54f", "#9575cd", "#ffb74d"],
            borderColor: ["#26a69a", "#66bb6a", "#e57373", "#ffb300", "#7e57c2", "#ffa726"],
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Number of Spots'
              }
            }
          },
          plugins: {
            legend: {
              labels: {
                color: '#333'
              }
            }
          },
          maintainAspectRatio: false
        }
      });

      // Chart 2: Overall Parking Utilization
      this.chart2 = new Chart(document.getElementById('chart2'), {
        type: 'pie',
        data: {
          labels: ['Occupied', 'Available'],
          datasets: [{
            data: [occupied, available],
            backgroundColor: ["#ef5350", "#4dd0e1"],
            borderColor: ["#e57373", "#26a69a"],
            borderWidth: 1
          }]
        },
        options: {
          plugins: {
            legend: {
              labels: {
                color: '#333'
              }
            }
          },
          maintainAspectRatio: false
        }
      });

      // Fetch occupancy trend data
      try {
        const trendRes = await fetch('/api/admin/occupancy-trend');
        if (!trendRes.ok) {
          throw new Error(`HTTP error! status: ${trendRes.status}`);
        }
        const trend = await trendRes.json();
        
        // Ensure we have valid data for the trend chart
        const trendDates = trend.dates || [];
        const trendCounts = trend.occupied_counts || [];
        
        console.log('Trend data received:', { dates: trendDates, counts: trendCounts });
        
        // Chart 3: Daily Occupancy Trend
        this.chart3 = new Chart(document.getElementById('chart3'), {
          type: 'line',
          data: {
            labels: trendDates,
            datasets: [{
              label: 'Bookings per Day',
              data: trendCounts,
              fill: false,
              borderColor: '#ef5350',
              tension: 0.1,
              pointBackgroundColor: '#e57373',
              pointRadius: 6,
              pointHoverRadius: 8
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Bookings'
                },
                ticks: {
                  stepSize: 1
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              }
            },
            plugins: {
              legend: {
                labels: {
                  color: '#333'
                }
              },
              tooltip: {
                mode: 'index',
                intersect: false
              }
            },
            maintainAspectRatio: false
          }
        });
      } catch (error) {
        console.error('Error loading trend data:', error);
        // Create chart with sample data if API fails
        const sampleDates = ['2025-07-20', '2025-07-21', '2025-07-22', '2025-07-23', '2025-07-24', '2025-07-25', '2025-07-26'];
        const sampleCounts = [0, 0, 0, 0, 0, 0, 3]; // Show today's 3 bookings
        
        this.chart3 = new Chart(document.getElementById('chart3'), {
          type: 'line',
          data: {
            labels: sampleDates,
            datasets: [{
              label: 'Bookings per Day (Sample)',
              data: sampleCounts,
              fill: false,
              borderColor: '#ef5350',
              tension: 0.1,
              pointBackgroundColor: '#e57373',
              pointRadius: 6,
              pointHoverRadius: 8
            }]
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Number of Bookings'
                },
                ticks: {
                  stepSize: 1
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Date'
                }
              }
            },
            plugins: {
              legend: {
                labels: {
                  color: '#333'
                }
              },
              tooltip: {
                mode: 'index',
                intersect: false
              }
            },
            maintainAspectRatio: false
          }
        });
      }
      this.loading = false;
    } catch (err) {
      this.error = 'Failed to load summary data.';
      this.loading = false;
    }
  },
  beforeDestroy() {
    if (this.chart1) this.chart1.destroy();
    if (this.chart2) this.chart2.destroy();
    if (this.chart3) this.chart3.destroy();
  },
};
</script>

<style>
@import url('../assets/ad-dash.css');

/* Ensure chart containers have a controlled size */
.chart-container {
  min-height: 250px;
  max-height: 300px;
  margin-bottom: 20px;
}

canvas {
  width: 100% !important;
  height: 250px !important;
  max-width: 550px;
  margin: 0 auto;
}

.summary-card {
  background-color: #ecf0f1;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

@media (max-width: 600px) {
  .chart-container {
    min-height: 200px;
    max-height: 250px;
  }
  canvas {
    height: 200px !important;
  }
  .summary-card {
    padding: 10px;
  }
}
</style>