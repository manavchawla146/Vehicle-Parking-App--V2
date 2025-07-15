<template>
  <div class="container">
    <div class="summary-container">
      <Navbar />
      <div class="summary-header">
        <h2>Parking Summary</h2>
      </div>
      <div class="summary-card">
        <h3>Summary on Already Used Parking Spots</h3>
        <!-- Chart 1: Bar - Parking Spots Used per Location -->
        <div class="chart-container">
          <h4>Parking Spots Used per Location</h4>
          <div id="chart1"></div>
        </div>
        <!-- Chart 2: Bar - Total Cost by Vehicle -->
        <div class="chart-container">
          <h4>Total Cost by Vehicle</h4>
          <div id="chart2"></div>
        </div>
        <!-- Chart 3: Line - Parking Duration by Spot -->
        <div class="chart-container">
          <h4>Parking Duration by Spot</h4>
          <div id="chart3"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Navbar from './us-nav.vue';

export default {
  name: 'SummaryPage',
  components: {
    Navbar
  },
  data() {
    return {
      parkingData: [
        { id: 120, vehicleNumber: 'TW318888', parkingTime: '2025-06-18 05:40 AM IST', releasingTime: '2025-06-18 06:12 PM IST', location: 'mumbai' },
        { id: 142, vehicleNumber: 'AP510921', parkingTime: '2025-06-18 08:00 AM IST', releasingTime: '2025-06-18 12:00 PM IST', location: 'delhi' },
        { id: 145, vehicleNumber: 'MH123456', parkingTime: '2025-06-18 09:00 AM IST', releasingTime: '2025-06-18 01:00 PM IST', location: 'mumbai' }
      ],
      parkingLots: [
        { id: 132, address: 'Dadar Road', availability: 6, location: 'mumbai', pincode: '400028' },
        { id: 136, address: 'Mumbai Central', availability: 10, location: 'mumbai', pincode: '400037' },
        { id: 167, address: 'Connaught Place', availability: 15, location: 'delhi', pincode: '110001' }
      ],
      chartConfigs: {
        chart1: {
          type: 'bar',
          data: {
            labels: ['Mumbai', 'Delhi'],
            datasets: [{
              label: 'Spots Used',
              data: [2, 1],
              backgroundColor: ['#4dd0e1', '#81c784'],
              borderColor: ['#26a69a', '#66bb6a'],
              borderWidth: 1
            }]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true
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
        },
        chart2: {
          type: 'bar',
          data: {
            labels: ['TW318888', 'AP510921', 'MH123456'],
            datasets: [{
              label: 'Total Cost ($)',
              data: [1544, 480, 480], // 772, 240, 240 minutes * $2/min
              backgroundColor: ['#4dd0e1', '#81c784', '#ef5350'],
              borderColor: ['#26a69a', '#66bb6a', '#ef5350'],
              borderWidth: 1
            }]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true
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
        },
        chart3: {
          type: 'line',
          data: {
            labels: ['Spot 120', 'Spot 142', 'Spot 145'],
            datasets: [{
              label: 'Duration (minutes)',
              data: [772, 240, 240], // 05:40 AM to 06:12 PM = 772 minutes
              fill: false,
              borderColor: '#26a69a',
              tension: 0.1
            }]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true
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
        }
      }
    };
  },
  mounted() {
    this.calculateDurationsAndCosts();
  },
  methods: {
    calculateDurationsAndCosts() {
      this.parkingData.forEach(spot => {
        const parking = new Date(spot.parkingTime.replace('IST', '').trim());
        const releasing = new Date(spot.releasingTime.replace('IST', '').trim());
        const diffMs = releasing - parking;
        spot.durationMinutes = diffMs / (1000 * 60); // Duration in minutes
        const ratePerMinute = 2; // $2 per minute for simplicity
        spot.totalCost = (spot.durationMinutes * ratePerMinute).toFixed(2); // Cost in dollars
        // Update chart data dynamically
        if (spot.id === 120) {
          this.chartConfigs.chart3.data.datasets[0].data[0] = spot.durationMinutes;
          this.chartConfigs.chart2.data.datasets[0].data[0] = parseFloat(spot.totalCost);
        }
        if (spot.id === 142) {
          this.chartConfigs.chart3.data.datasets[0].data[1] = spot.durationMinutes;
          this.chartConfigs.chart2.data.datasets[0].data[1] = parseFloat(spot.totalCost);
        }
        if (spot.id === 145) {
          this.chartConfigs.chart3.data.datasets[0].data[2] = spot.durationMinutes;
          this.chartConfigs.chart2.data.datasets[0].data[2] = parseFloat(spot.totalCost);
        }
      });
    }
  }
};
</script>

<style>
@import url('../assets/summary-styles.css');
</style>