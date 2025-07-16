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
            <input type="text" v-model="searchQuery" @keyup.enter="searchParking" placeholder="Enter location or pin code" class="input-field">
          </div>
        </div>

        <!-- Parking Lots Box -->
        <div class="card">
          <div class="gradient-header">
            <h3>Parking Lots @ {{ searchQuery || 'Enter location or pin code' }}</h3>
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
                  <td><button class="action-btn book-btn" @click="bookSlot(lot.id)">Book</button></td>
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
            <label>Lot Name:</label>
            <input type="text" v-model="bookModalData.lotName" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Username:</label>
            <input type="text" v-model="bookModalData.username" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Price:</label>
            <input type="text" v-model="bookModalData.price" readonly class="form-input prefilled">
          </div>
          <div class="form-group">
            <label>Vehicle Number:</label>
            <input type="text" v-model="bookModalData.vehicleNo" placeholder="Enter vehicle number" class="form-input" required>
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
      parkingLots: [],
      searchQuery: "",
      showReleaseModal: false,
      showBookModal: false,
      releaseModalData: { spotId: "", vehicleNo: "", parkingTime: "", releasingTime: "", totalCost: "", status: "" },
      bookModalData: { spotId: "", lotName: "", username: "", price: "", vehicleNo: "" },
      selectedHistory: null,
      selectedLot: null,
      userProfile: null
    };
  },
  computed: {
    filteredLots() {
      if (!this.searchQuery) return this.parkingLots;
      return this.parkingLots.filter(lot =>
        lot.address.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        lot.pinCode.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    async searchParking() {
      console.log("Searching for:", this.searchQuery);
      this.searchQuery = this.searchQuery.trim();
      await this.fetchParkingLots();
    },
    async fetchParkingLots() {
      try {
        const response = await fetch(`/api/parking/search?query=${encodeURIComponent(this.searchQuery)}`, {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });
        const data = await response.json();
        if (response.ok) {
          this.parkingLots = data.map(lot => ({
            id: lot.id,
            address: lot.address,
            pinCode: lot.pinCode,
            number_of_spots: lot.number_of_spots,
            occupiedSpots: lot.occupiedSpots || [],
            pricePerHour: lot.pricePerHour,
            primeLocation: lot.primeLocation || lot.address,
            availability: lot.availability
          }));
          console.log("Fetched parking lots with availability:", this.parkingLots);
        } else {
          console.error('Failed to fetch parking lots:', data.error);
          this.parkingLots = [];
        }
      } catch (err) {
        console.error('Error fetching parking lots:', err);
        this.parkingLots = [];
      }
    },
    async fetchUserProfile() {
      try {
        const response = await fetch('/api/profile', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });
        const data = await response.json();
        if (response.ok) {
          this.userProfile = data;
        } else {
          console.error('Failed to fetch user profile:', data.error);
          this.userProfile = { name: 'Unknown User' };
        }
      } catch (err) {
        console.error('Error fetching user profile:', err);
        this.userProfile = { name: 'Unknown User' };
      }
    },
    async showModal(id, action) {
      if (action === 'Release') {
        const history = this.parkingHistory.find(h => h.id === id);
        this.selectedHistory = history;
        this.releaseModalData.spotId = id.toString();
        this.releaseModalData.vehicleNo = history ? history.vehicleNo : "";
        this.releaseModalData.parkingTime = history ? history.timestamp : "";
        this.releaseModalData.releasingTime = history ? new Date().toLocaleString() : "";
        this.releaseModalData.totalCost = history ? "$10.00" : "";
        this.showReleaseModal = true;
        this.showBookModal = false;
      } else if (action === 'Book') {
        const lot = this.parkingLots.find(l => l.id === id);
        this.selectedLot = lot;
        if (!this.userProfile) await this.fetchUserProfile();
        const availableSpot = await this.getAvailableSpot(lot.id);
        this.bookModalData.spotId = availableSpot ? availableSpot.id.toString() : "N/A";
        this.bookModalData.lotName = lot ? lot.primeLocation : "N/A";
        this.bookModalData.username = this.userProfile ? this.userProfile.name : "Unknown User";
        this.bookModalData.price = lot ? `$${lot.pricePerHour.toFixed(2)}` : "N/A";
        this.bookModalData.vehicleNo = "";
        this.showBookModal = true;
        this.showReleaseModal = false;
      }
    },
    async getAvailableSpot(lotId) {
      try {
        const response = await fetch(`/api/parking/lot/${lotId}/spots`, {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });
        const data = await response.json();
        if (response.ok) {
          const availableSpots = data.spots.filter(spot => spot.status === 'A');
          console.log(`Available spots for lot ${lotId}:`, availableSpots);
          return availableSpots.length > 0 ? availableSpots[0] : null;
        }
        console.error(`API error for lot ${lotId}:`, data.error);
        return null;
      } catch (err) {
        console.error('Error fetching available spots:', err);
        return null;
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
    async bookSlot(lotId) {
      const lot = this.parkingLots.find(l => l.id === lotId);
      console.log("Attempting to book lot:", lot);
      if (lot && lot.availability > 0) {
        this.selectedLot = lot;
        if (!this.userProfile) await this.fetchUserProfile();
        const availableSpot = await this.getAvailableSpot(lot.id);
        if (availableSpot) {
          this.bookModalData.spotId = availableSpot.id.toString();
          this.bookModalData.lotName = lot.primeLocation;
          this.bookModalData.username = this.userProfile ? this.userProfile.name : "Unknown User";
          this.bookModalData.price = `$${lot.pricePerHour.toFixed(2)}`;
          this.bookModalData.vehicleNo = "";
          this.showBookModal = true;
        } else {
          console.error("No available spots found despite availability:", lot.availability);
          alert("No available spots found despite availability!");
        }
      } else {
        console.warn("No available slots or lot not found:", lot);
        alert("No available slots or lot not found!");
      }
    },
    async confirmBook() {
      if (!this.bookModalData.vehicleNo.trim()) {
        alert("Please enter a vehicle number!");
        return;
      }
      const userId = sessionStorage.getItem('user_id') || "USER123";
      try {
        const response = await fetch('/api/parking/reserve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            lotId: this.selectedLot.id,
            spotId: parseInt(this.bookModalData.spotId),
            userId: userId,
            vehicleNo: this.bookModalData.vehicleNo.trim()
          }),
        });
        const data = await response.json();
        if (response.ok) {
          console.log("Reservation confirmed:", data);
          this.closeBookModal();
          await this.fetchParkingLots(); // Refresh to update availability
          alert("Booking successful!");
        } else {
          console.error("Booking failed:", data.error);
          alert(data.error || "Failed to book slot");
        }
      } catch (err) {
        console.error("Server error during booking:", err.message);
        alert("Server error: " + err.message);
      }
    }
  },
  created() {
    this.fetchParkingLots();
    this.fetchUserProfile();
  }
};
</script>

<style scoped>
@import url('../assets/us-dash.css');
/* Additional scoped styles if needed */
</style>
