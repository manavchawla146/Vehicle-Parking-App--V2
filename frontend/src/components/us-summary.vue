<template>
  <div class="page-container">
    <Navbar />
    <div class="profile-container">
      <div class="profile-card">
        <div class="dashboard-header">
          <h2><i class="fas fa-chart-pie"></i> Parking Summary</h2>
        </div>
        <div class="summary-card">
          <h3>Summary on Already Used Parking Spots</h3>
          <!-- Chart 1: Bar - Parking Spots Used per Location -->
          <div class="chart-container">
            <h4>Parking Spots Used per Location</h4>
            <canvas id="chart1"></canvas>
          </div>
          <!-- Chart 2: Bar - Total Cost by Vehicle -->
          <div class="chart-container">
            <h4>Total Cost by Vehicle</h4>
            <canvas id="chart2"></canvas>
          </div>
          <!-- Chart 3: Pie - Parking Status -->
          <div class="chart-container">
            <h4>Parking Status</h4>
            <canvas id="chart3"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from './us-nav.vue';
import Chart from 'chart.js/auto';

export default {
  name: 'SummaryPage',
  components: {
    Navbar
  },
  data() {
    return {
      chart1: null,
      chart2: null,
      chart3: null,
      loading: true,
      error: null,
      parkingHistory: []
    };
  },
  async mounted() {
    await this.loadParkingHistory();
  },
  methods: {
    async loadParkingHistory() {
      try {
        const response = await fetch('/api/user/parking-history');
        const data = await response.json();
        this.parkingHistory = data;
        // Fetch parking status summary for the pie chart
        const statusRes = await fetch('/api/user/parking-status-summary');
        const statusData = await statusRes.json();
        this.createCharts(statusData);
        this.loading = false;
      } catch (err) {
        this.error = 'Failed to load parking history.';
        this.loading = false;
        // Create charts with empty data if API fails
        this.createCharts({active: 0, completed: 0});
      }
    },
    
    createCharts(statusData) {
      // Process data for charts
      const locationData = this.processLocationData();
      const vehicleData = this.processVehicleData();
      
      // Chart 1: Parking Spots Used per Location
      this.chart1 = new Chart(document.getElementById('chart1'), {
        type: 'bar',
        data: {
          labels: locationData.labels,
          datasets: [{
            label: 'Spots Used',
            data: locationData.data,
            backgroundColor: ['#4dd0e1', '#81c784', '#ef5350', '#ffd54f', '#9575cd'],
            borderColor: ['#26a69a', '#66bb6a', '#e57373', '#ffb300', '#7e57c2'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 10,
              bottom: 10,
              left: 10,
              right: 10
            }
          },
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
          }
        }
      });

      // Chart 2: Total Cost by Vehicle
      this.chart2 = new Chart(document.getElementById('chart2'), {
        type: 'bar',
        data: {
          labels: vehicleData.labels,
          datasets: [{
            label: 'Total Cost ($)',
            data: vehicleData.data,
            backgroundColor: ['#4dd0e1', '#81c784', '#ef5350', '#ffd54f', '#9575cd'],
            borderColor: ['#26a69a', '#66bb6a', '#e57373', '#ffb300', '#7e57c2'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 10,
              bottom: 10,
              left: 10,
              right: 10
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Cost ($)'
              }
            }
          },
          plugins: {
            legend: {
              labels: {
                color: '#333'
              }
            }
          }
        }
      });

      // Chart 3: Pie - Parking Status
      const active = statusData.active || 0;
      const completed = statusData.completed || 0;
      this.chart3 = new Chart(document.getElementById('chart3'), {
        type: 'pie',
        data: {
          labels: ['Active', 'Parked Out'],
          datasets: [{
            data: [active, completed],
            backgroundColor: ['#4dd0e1', '#ef5350'],
            borderColor: ['#26a69a', '#e57373'],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 10,
              bottom: 10,
              left: 10,
              right: 10
            }
          },
          plugins: {
            legend: {
              labels: {
                color: '#333'
              }
            }
          }
        }
      });
    },
    
    processLocationData() {
      const locationCount = {};
      this.parkingHistory.forEach(item => {
        const location = item.location || 'Unknown';
        locationCount[location] = (locationCount[location] || 0) + 1;
      });
      
      return {
        labels: Object.keys(locationCount),
        data: Object.values(locationCount)
      };
    },
    
    processVehicleData() {
      const vehicleCost = {};
      this.parkingHistory.forEach(item => {
        if (item.total_cost) {
          const vehicle = item.vehicle_no || 'Unknown';
          vehicleCost[vehicle] = (vehicleCost[vehicle] || 0) + parseFloat(item.total_cost);
        }
      });
      
      return {
        labels: Object.keys(vehicleCost),
        data: Object.values(vehicleCost)
      };
    },
    
    processMonthlyUsageData() {
      const monthlyUsage = {};
      
      // Get last 6 months
      const months = [];
      for (let i = 5; i >= 0; i--) {
        const date = new Date();
        date.setMonth(date.getMonth() - i);
        const monthKey = date.toLocaleString('default', { month: 'short', year: '2-digit' });
        months.push(monthKey);
        monthlyUsage[monthKey] = 0;
      }
      
      // Count parking sessions per month
      this.parkingHistory.forEach(item => {
        if (item.timestamp) {
          const date = new Date(item.timestamp + 'Z');
          const monthKey = date.toLocaleString('default', { month: 'short', year: '2-digit' });
          if (monthlyUsage.hasOwnProperty(monthKey)) {
            monthlyUsage[monthKey]++;
          }
        }
      });
      
      return {
        labels: months,
        data: months.map(month => monthlyUsage[month] || 0)
      };
    },

    processStatusData() {
      let active = 0;
      let completed = 0;

      this.parkingHistory.forEach(item => {
        if (item.status === 'active') {
          active++;
        } else if (item.status === 'completed') {
          completed++;
        }
      });

      return {
        active: active,
        completed: completed
      };
    }
  },
  
  beforeDestroy() {
    if (this.chart1) this.chart1.destroy();
    if (this.chart2) this.chart2.destroy();
    if (this.chart3) this.chart3.destroy();
  }
};
</script>

<style>
@import url('../assets/base.css');
@import url('../assets/summary-styles.css');

/* Override conflicting styles from summary-styles.css */
.container {
  display: block !important;
  justify-content: initial !important;
  align-items: initial !important;
  min-height: initial !important;
  background-color: initial !important;
  padding: initial !important;
}

.summary-container {
  width: initial !important;
  max-width: initial !important;
}

.summary-header {
  background: initial !important;
  color: initial !important;
  padding: initial !important;
  border-radius: initial !important;
  margin-bottom: initial !important;
  text-align: initial !important;
}

.summary-header h2 {
  font-size: initial !important;
  font-family: initial !important;
  font-weight: initial !important;
  margin: initial !important;
  color: initial !important;
}

/* Chart container styles */
.chart-container {
  height: 400px !important;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
}

.chart-container h4 {
  margin-bottom: 15px;
  color: #333;
  font-weight: 600;
  font-size: 16px;
  height: 20px;
  overflow: hidden;
}

/* Canvas wrapper to ensure proper sizing */
.chart-container > div {
  height: calc(100% - 50px);
  position: relative;
  overflow: hidden;
}

/* Canvas container to prevent overflow */
.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
  max-width: 100% !important;
  max-height: 100% !important;
  display: block;
  margin: 0 auto;
}

/* Override specific chart IDs */
#chart1, #chart2, #chart3 {
  width: 100% !important;
  height: 100% !important;
  max-width: 100% !important;
  max-height: 100% !important;
}

/* Summary card styles */
.summary-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  overflow: hidden;
}

.summary-card h3 {
  margin-bottom: 25px;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

/* Responsive design */
@media (max-width: 768px) {
  .chart-container {
    height: 350px !important;
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .chart-container > div {
    height: calc(100% - 40px);
  }
  
  .summary-card {
    padding: 20px;
  }
  
  .summary-card h3 {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .chart-container {
    height: 300px !important;
    padding: 10px;
  }
  
  .chart-container > div {
    height: calc(100% - 30px);
  }
  
  .summary-card {
    padding: 15px;
  }
}
</style>