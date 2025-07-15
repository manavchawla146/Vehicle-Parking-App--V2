<template>
  <div id="app">
    <div class="navbar-container">
      <us-nav></us-nav>
    </div>
    <div class="container">
      <div class="dash-container">
        <!-- Recent Parking History Box -->
        <div class="card">
          <div class="gradient-header">
            <h3>Recent parking history</h3>
          </div>
          <div class="history-box">
            <table class="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Location</th>
                  <th>Vehicle No</th>
                  <th>Timestamp</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="history in parkingHistory" :key="history.id">
                  <td>{{ history.id }}</td>
                  <td>{{ history.location }}</td>
                  <td>{{ history.vehicleNo }}</td>
                  <td>{{ history.timestamp }}</td>
                  <td>
                    <button class="action-btn" :class="history.action === 'Release' ? 'release-btn' : 'parked-btn'" @click="showModal(history.id, history.action)">{{ history.action }}</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Search Box -->
        <div class="card search-card">
          <div class="gradient-header">
            <h3>Search parking @location/pin code :</h3>
          </div>
          <div class="search-container">
            <input type="text" v-model="searchQuery" @keyup.enter="searchParking" placeholder="Enter location" class="input-field">
            <button class="search-btn" @click="searchParking"><i class="fas fa-search"></i> Search</button>
          </div>
        </div>

        <!-- Parking Lots Box -->
        <div class="card">
          <div class="gradient-header">
            <h3>Parking Lots @ {{ searchQuery || 'Enter location' }}</h3>
          </div>
          <div class="lots-box">
            <table class="lots-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Address</th>
                  <th>Availability</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="lot in filteredLots" :key="lot.id">
                  <td>{{ lot.id }}</td>
                  <td>{{ lot.address }}</td>
                  <td>{{ lot.availability }}</td>
                  <td><button class="action-btn book-btn" @click="showModal(lot.id, 'Book')">Book</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Release Modal -->
      <div v-if="showReleaseModal" class="modal">
        <div class="modal-content">
          <div class="form-group">
            <label>Spot ID:</label>
            <input type="text" v-model="releaseModalData.spotId" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Vehicle Number:</label>
            <input type="text" v-model="releaseModalData.vehicleNo" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Parking Time:</label>
            <input type="text" v-model="releaseModalData.parkingTime" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Releasing Time:</label>
            <input type="text" v-model="releaseModalData.releasingTime" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Total Cost:</label>
            <input type="text" v-model="releaseModalData.totalCost" readonly class="form-input prefilled">
          </div>
       
          <div class="form-actions">
            <button class="action-btn release-btn" @click="confirmRelease">Release</button>
            <button class="action-btn cancel-btn" @click="closeReleaseModal">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Book Modal -->
      <div v-if="showBookModal" class="modal">
        <div class="modal-content">
          <div class="form-group">
            <label>Spot ID:</label>
            <input type="text" v-model="bookModalData.spotId" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Lot ID:</label>
            <input type="text" v-model="bookModalData.lotId" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>User ID:</label>
            <input type="text" v-model="bookModalData.userId" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Amount per Hour:</label>
            <input type="text" v-model="bookModalData.amtPerHour" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Vehicle Number:</label>
            <input type="text" v-model="bookModalData.vehicleNo" placeholder="Enter vehicle number" class="form-input">
          </div>
          <div class="form-actions">
            <button class="action-btn reserve-btn" @click="confirmBook">Reserve</button>
            <button class="action-btn cancel-btn" @click="closeBookModal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import usNav from './us-nav.vue';

export default {
  name: 'us-profile',
  components: {
    'us-nav': usNav,
  },
  data() {
    return {
      parkingHistory: [
        { id: 120, location: "xxxxx", vehicleNo: "TW31888", timestamp: "xx-xx-xx 10:00", action: "Release" },
        { id: 142, location: "xxxxx", vehicleNo: "AP310921", timestamp: "xx-xx-xx 12:00", action: "Parked Out" },
        { id: 150, location: "yyyyy", vehicleNo: "MH12AB1234", timestamp: "xx-xx-xx 09:00", action: "Release" },
        { id: 160, location: "zzzzz", vehicleNo: "DL01CD5678", timestamp: "xx-xx-xx 14:00", action: "Parked Out" },
        { id: 170, location: "aaaaa", vehicleNo: "GJ02EF9012", timestamp: "xx-xx-xx 11:00", action: "Release" }
      ],
      parkingLots: [
        { id: 132, address: "K. Gadgil Marg, xxxxx", availability: 6 },
        { id: 136, address: "Wadala, xxxxx, xxxxx", availability: 10 },
        { id: 140, address: "Bandra, yyyyy, yyyyy", availability: 4 },
        { id: 145, address: "Andheri, zzzzz, zzzzz", availability: 8 },
        { id: 150, address: "Colaba, aaaaa, aaaaa", availability: 12 }
      ],
      searchQuery: "",
      showReleaseModal: false,
      showBookModal: false,
      releaseModalData: { spotId: "", vehicleNo: "", parkingTime: "", releasingTime: "", totalCost: "", status: "" },
      bookModalData: { spotId: "", lotId: "", userId: "", amtPerHour: "", vehicleNo: "" },
      selectedHistory: null,
      selectedLot: null
    };
  },
  computed: {
    filteredLots() {
      if (!this.searchQuery) return this.parkingLots;
      return this.parkingLots.filter(lot =>
        lot.address.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    searchParking() {
      console.log("Searching for:", this.searchQuery);
      this.searchQuery = this.searchQuery.trim();
    },
    showModal(id, action) {
      if (action === 'Release') {
        const history = this.parkingHistory.find(h => h.id === id);
        this.selectedHistory = history;
        this.releaseModalData.spotId = id.toString();
        this.releaseModalData.vehicleNo = history ? history.vehicleNo : "";
        this.releaseModalData.parkingTime = history ? history.timestamp : "";
        this.releaseModalData.releasingTime = history ? "xx-xx-xx 12:00" : ""; // Example releasing time
        this.releaseModalData.totalCost = history ? "$10.00" : ""; // Example cost
        this.showReleaseModal = true;
        this.showBookModal = false;
      } else if (action === 'Book') {
        const lot = this.parkingLots.find(l => l.id === id);
        this.selectedLot = lot;
        this.bookModalData.spotId = id.toString();
        this.bookModalData.lotId = lot ? lot.id.toString() : "";
        this.bookModalData.userId = "USER123"; // Example user ID
        this.bookModalData.amtPerHour = "$2.50"; // Example rate
        this.bookModalData.vehicleNo = "";
        this.showBookModal = true;
        this.showReleaseModal = false;
      }
    },
    closeReleaseModal() {
      this.showReleaseModal = false;
      this.selectedHistory = null;
    },
    closeBookModal() {
      this.showBookModal = false;
      this.selectedLot = null;
    },
    confirmRelease() {
      console.log("Release confirmed:", this.releaseModalData);
      this.closeReleaseModal();
    },
    confirmBook() {
      console.log("Reservation confirmed:", this.bookModalData);
      this.closeBookModal();
    }
  }
};
</script>

<style scoped>
@import url('../assets/us-dash.css');
/* Additional scoped styles if needed */
</style>