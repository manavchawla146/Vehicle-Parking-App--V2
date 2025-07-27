<template>
  <div class="page-container">
    <us-nav></us-nav>
    <div class="profile-container">
      <div class="profile-card">
        <div class="dashboard-header">
          <h2><i class="fas fa-car"></i> User Dashboard</h2>
        </div>
        
        <!-- Recent Parking History Box -->
        <div class="card">
          <div class="gradient-header">
            <div style="display: flex; align-items: center; justify-content: space-between;">
              <button class="notification-btn" @click="openNotificationModal">
                <i class="fas fa-bell"></i>
                <span v-if="unreadNotifications > 0" class="notification-badge">{{ unreadNotifications }}</span>
              </button>
              <h3 style="margin: 0; flex-grow: 1; text-align: center;">Recent parking history</h3>
              <div style="display: flex; gap: 10px;">
                <button class="action-btn" @click="exportParkingHistory">Export</button>
              </div>
            </div>
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
                <tr v-for="history in parkingHistory" :key="history.id + history.type">
                  <td>{{ history.id }}</td>
                  <td>{{ history.location }}</td>
                  <td>{{ history.vehicle_no }}</td>
                  <td>
                    {{ history.timestamp ? new Date(history.timestamp).toLocaleString() : '' }}
                  </td>
                  <td>
                    <span v-if="history.type === 'parked_out'" class="status-text">
                      Parked Out<br>
                     </span>
                    <button
                      v-else
                      class="action-btn release-btn"
                      @click="openReleaseModal(history)"
                    >Release</button>
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

      <!-- Booking Modal -->
      <div v-if="showModal" class="modal">
        <div class="modal-content">
          <h3>Available Slots for {{ selectedLot.address }}</h3>
          <div>
            <button
              v-for="slot in slots"
              :key="slot.id"
              :disabled="slot.status !== 'A'"
              @click="bookSlot(slot)"
              :style="{ background: slot.status === 'A' ? '#1abc9c' : '#ccc' }"
            >
              {{ slot.slot_number }} ({{ slot.status }})
            </button>
          </div>
        </div>
      </div>

      <!-- Notification Modal -->
      <div v-if="showNotificationModal" class="modal-overlay" @click.self="closeNotificationModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Notifications</h3>
          </div>
          <div class="modal-body">
            <div v-if="notifications.length === 0" class="no-notifications">No new notifications.</div>
            <ul v-else class="notification-list">
              <li v-for="(notification, index) in notifications" :key="index" class="notification-item">
                <div class="notification-message">{{ notification.message }}</div>
                <div class="notification-timestamp">{{ formatNotificationTime(notification.timestamp) }}</div>
              </li>
            </ul>
          </div>
          <div class="button-group">
            <button class="action-btn modal-cancel-btn" @click="closeNotificationModal">Close</button>
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
      parkingHistory: [], // Remove hardcoded data - will be fetched from database
      parkingLots: [],
      searchQuery: "",
      showReleaseModal: false,
      showBookModal: false,
      releaseModalData: { spotId: "", vehicleNo: "", parkingTime: "", releasingTime: "", totalCost: "", status: "" },
      bookModalData: { spotId: "", lotName: "", username: "", price: "", vehicleNo: "" },
      selectedHistory: null,
      selectedLot: null,
      userProfile: null,
      showModal: false, // boolean for modal visibility
      slots: [],
      showNotificationModal: false,
      notifications: [], // New property for notifications
      unreadNotifications: 0 // New property for unread notifications
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

    async fetchUserParkingHistory() {
      try {
        const response = await fetch('/api/user/parking-history', {
          credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
          this.parkingHistory = data.map(row => ({
            ...row,
            displayTime: row.timestamp ? new Date(row.timestamp).toLocaleString() : ''
          }));
        } else {
          console.error('Failed to fetch parking history:', data.error);
          this.parkingHistory = [];
        }
      } catch (error) {
        console.error('Error fetching parking history:', error);
        this.parkingHistory = [];
      }
    },

    async openReleaseModal(history) {
        this.selectedHistory = history;
      this.releaseModalData.spotId = history.id.toString();
      this.releaseModalData.vehicleNo = history.vehicle_no || '';
      this.releaseModalData.parkingTime = history.displayTime; // Use display time
      
      // Calculate real release time and cost using consistent time methods
      const parkingTime = new Date(history.timestamp); // Use original timestamp
      const releaseTime = new Date(); // Current time
      
      // Debug logging
      console.log('Original timestamp from backend:', history.timestamp);
      console.log('Parking time:', parkingTime);
      console.log('Release time:', releaseTime);
      console.log('Is parking time valid?', !isNaN(parkingTime.getTime()));
      
      // Check if parking time is valid
      if (isNaN(parkingTime.getTime())) {
        console.error('Invalid parking time:', history.timestamp);
        alert('Error: Invalid parking time detected. Please contact support.');
        return;
      }
      
      const durationMs = releaseTime.getTime() - parkingTime.getTime();
      const durationHours = durationMs / (1000 * 60 * 60); // Convert to hours
      
      console.log('Duration in milliseconds:', durationMs);
      console.log('Duration in hours:', durationHours);
      
      // Use dynamic price from the lot
      const pricePerHour = history.pricePerHour || 5; // Fallback to $5 if not available
      
      // Calculate cost with minimum charge of 1 hour
      let totalCost = Math.max(durationHours * pricePerHour, pricePerHour);
      totalCost = totalCost.toFixed(2);
      
      console.log('Price per hour:', pricePerHour);
      console.log('Total cost:', totalCost);
      
      this.releaseModalData.releasingTime = releaseTime.toLocaleString();
      this.releaseModalData.totalCost = `$${totalCost}`;
      
      this.showReleaseModal = true;
      this.showBookModal = false;
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
    async confirmRelease() {
      try {
        const response = await fetch('/api/parking/release', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            spotId: this.releaseModalData.spotId
          })
        });

        const data = await response.json();

        if (response.ok) {
          // Success: update UI, close modal
          await this.fetchParkingLots();
          await this.fetchUserParkingHistory();
          this.closeReleaseModal();
        } else {
          // Only show alert if the backend says it's an error
          alert(data.error || "Failed to release parking spot!");
        }
      } catch (error) {
        alert("Network error releasing parking spot!");
      }
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
          await this.fetchUserParkingHistory(); // Refresh parking history
          alert("Booking successful!");
        } else {
          console.error("Booking failed:", data.error);
          alert(data.error || "Failed to book slot");
        }
      } catch (err) {
        console.error("Server error during booking:", err.message);
        alert("Server error: " + err.message);
      }
    },
    exportParkingHistory() {
      // Simple CSV export example
      const headers = ['ID', 'LOCATION', 'VEHICLE NO', 'TIMESTAMP', 'ACTION'];
      const rows = this.parkingHistory.map(h => [
        h.id,
        h.location,
        h.vehicle_no,
        h.timestamp ? new Date(h.timestamp + 'Z').toLocaleString() : '',
        h.type === 'parked_out' ? 'Parked Out' : 'Reserved'
      ]);
      let csvContent = headers.join(',') + '\n' + rows.map(e => e.join(',')).join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.setAttribute('download', 'parking_history.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    
    // Notification methods
    async fetchNotifications() {
      try {
        const response = await fetch('/api/user/notifications', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        });
        
        if (response.ok) {
          const data = await response.json();
          this.notifications = data.notifications || [];
          this.unreadNotifications = data.unread_count || 0;
          
          // If user has seen notifications, mark them as read
          if (this.notifications.length > 0 && this.unreadNotifications > 0) {
            // Don't automatically mark as read, let user see them first
          }
        } else {
          console.error('Failed to fetch notifications:', response.statusText);
          this.notifications = [];
          this.unreadNotifications = 0;
        }
      } catch (error) {
        console.error('Error fetching notifications:', error);
        this.notifications = [];
        this.unreadNotifications = 0;
      }
    },
    
    openNotificationModal() {
      this.showNotificationModal = true;
      this.markNotificationsAsRead();
    },
    
    closeNotificationModal() {
      this.showNotificationModal = false;
      this.markNotificationsAsRead();
    },
    
    markNotificationsAsRead() {
      this.notifications.forEach(notification => {
        notification.read = true;
      });
      this.unreadNotifications = 0;
    },
    
    formatNotificationTime(timestamp) {
      if (!timestamp) return '';
      try {
        const date = new Date(timestamp + 'Z');
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays > 0) {
          return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        } else if (diffHours > 0) {
          return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        } else {
          return 'Just now';
        }
      } catch (error) {
        return timestamp; // Return original timestamp if parsing fails
      }
    },


  },
  created() {
    this.fetchParkingLots();
    this.fetchUserProfile();
    this.fetchUserParkingHistory();
    this.fetchNotifications(); // Fetch notifications on component creation
  }
};
</script>

<style scoped>
@import url('../assets/base.css');
@import url('../assets/us-dash.css');
/* Additional scoped styles if needed */

.status-text {
  color: #ff3a24;
  font-weight: bold;
  padding: 5px 10px;
  background-color: #fbeee0;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

.action-btn.release-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

.action-btn.release-btn:hover {
  background-color: #388e3c;
}

.export-btn {
  background-color: #2196f3;
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  margin-left: 16px;
  transition: background 0.2s;
}
.export-btn:hover {
  background-color: #1769aa;
}

/* Notification styles */
.notification-btn {
  background: none;
  border: none;
  color: #ffffff;
  font-size: 18px;
  cursor: pointer;
  position: relative;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.notification-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #ff4444;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* Notification Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #26a69a;
  padding-bottom: 10px;
}

.no-notifications {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 20px;
}

.modal-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.modal-content li {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.modal-content li:last-child {
  border-bottom: none;
}

.notification-timestamp {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.modal-actions {
  margin-top: 20px;
  text-align: center;
}
</style>
