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
    };
  },
  mounted() {
    // Initialize Bar Chart: Occupancy by Parking Lot
    this.chart1 = new Chart(document.getElementById('chart1'), {
      type: 'bar',
      data: {
        labels: ["Parking #1", "Parking #2"],
        datasets: [{
          label: "Occupied Spots",
          data: [3, 4],
          backgroundColor: ["#4dd0e1", "#81c784"],
          borderColor: ["#26a69a", "#66bb6a"],
          borderWidth: 1
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Number of Spots"
            }
          }
        },
        plugins: {
          legend: {
            labels: {
              color: "#333"
            }
          }
        },
        maintainAspectRatio: false
      }
    });

    // Initialize Pie Chart: Overall Parking Utilization
    this.chart2 = new Chart(document.getElementById('chart2'), {
      type: 'pie',
      data: {
        labels: ["Occupied", "Available"],
        datasets: [{
          data: [7, 18],
          backgroundColor: ["#ef5350", "#4dd0e1"],
          borderColor: ["#e57373", "#26a69a"],
          borderWidth: 1
        }]
      },
      options: {
        plugins: {
          legend: {
            labels: {
              color: "#333"
            }
          }
        },
        maintainAspectRatio: false
      }
    });

    // Initialize Line Chart: Daily Occupancy Trend
    this.chart3 = new Chart(document.getElementById('chart3'), {
      type: 'line',
      data: {
        labels: ["June 18", "June 19", "June 20"],
        datasets: [{
          label: "Occupied Spots",
          data: [5, 6, 7],
          fill: false,
          borderColor: "#ef5350",
          tension: 0.1,
          pointBackgroundColor: "#e57373"
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Number of Spots"
            }
          }
        },
        plugins: {
          legend: {
            labels: {
              color: "#333"
            }
          }
        },
        maintainAspectRatio: false
      }
    });
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