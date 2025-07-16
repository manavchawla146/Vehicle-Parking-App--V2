<template>
  <div class="container">
    <div class="dash-box">
      <h2><i class="fas fa-search"></i> Admin Search</h2>
      <AdminNavbar />
      <!-- Search Section -->
      <div class="search-section">
        <div class="search-container">
          <select v-model="searchBy" class="filter-dropdown" @change="updateSearch">
            <option value="userId">User ID</option>
            <option value="name">Name</option>
            <option value="email">Email</option>
            <option value="primeLocation">Parking Lot by Name</option>
            <option value="pricePerHour">Parking Lot by Price</option>
          </select>
          <input
            type="text"
            v-model="searchString"
            class="search-input"
            placeholder="Enter search term"
            @keyup="searchItems"
          />
        </div>
      </div>

      <!-- Users Table -->
      <div class="users-table-wrapper" v-if="(filteredUsers.length || searchBy === 'userId' || searchBy === 'name' || searchBy === 'email') && searchBy !== 'primeLocation' && searchBy !== 'pricePerHour'">
        <table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.name }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Parking Lots Section -->
      <div v-if="filteredParkingLots.length && (searchBy === 'primeLocation' || searchBy === 'pricePerHour')" class="parking-lots">
        <div v-for="lot in filteredParkingLots" :key="lot.id" class="lot-card">
          <h4>
            {{ lot.primeLocation }} (Occupied: {{ lot.slots.filter(s => s.status === 'O').length }}/{{ lot.slots.length }})
          </h4>
          <div class="button-group">
            <button class="action-btn edit-btn" @click="openEditModal(lot)">Edit</button>
            <button class="action-btn delete-btn" @click="deleteLot(lot.id)">Delete</button>
          </div>
          <div class="parking-grid">
            <span
              v-for="slot in lot.slots"
              :key="slot.slot_number"
              :class="['parking-spot', { occupied: slot.status === 'O' }]"
              @click="openSlotModal(lot, slot)"
              style="cursor:pointer"
            >
              {{ slot.status }}
            </span>
          </div>
        </div>
      </div>
      <p v-if="!filteredParkingLots.length && (searchBy === 'primeLocation' || searchBy === 'pricePerHour') && searchString">No parking lots found matching your search.</p>

      <!-- Modal for Editing Parking Lot -->
      <div v-if="editModalVisible" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Edit Parking Lot</h3>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Prime Location Name:</label>
              <input v-model="editLotData.primeLocation" type="text" class="profile-input" />
            </div>
            <div class="form-group">
              <label>Address:</label>
              <input v-model="editLotData.address" type="text" class="profile-input" />
            </div>
            <div class="form-group">
              <label>Pin Code:</label>
              <input v-model="editLotData.pinCode" type="text" class="profile-input" />
            </div>
            <div class="form-group">
              <label>Price (per hour):</label>
              <input v-model.number="editLotData.pricePerHour" type="number" class="profile-input" />
            </div>
            <div class="form-group">
              <label>Maximum Spots:</label>
              <input v-model.number="editLotData.total" type="number" class="profile-input" @input="updateEditOccupiedSpots" />
            </div>
          </div>
          <div class="button-group">
            <button class="action-btn save-btn" @click="updateLot">Save</button>
            <button class="action-btn cancel-btn" @click="closeEditModal">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Slot Modal -->
      <div v-if="slotModalVisible" class="modal-overlay" @click.self="closeSlotModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Slot Details</h3>
          </div>
          <div class="modal-body">
            <p>Parking Lot: {{ selectedLot.primeLocation }}</p>
            <p>Slot Number: {{ selectedSlot.slot_number }}</p>
            <p>Status: {{ selectedSlot.status === 'O' ? 'Occupied' : 'Available' }}</p>
            <p v-if="selectedSlot.status === 'O'">Vehicle: {{ selectedSlot.vehicle_id || 'N/A' }}</p>
            <p v-if="selectedSlot.status === 'O'">User: {{ selectedSlot.username || 'N/A' }}</p>
          </div>
          <div class="button-group">
            <button v-if="selectedSlot.status === 'A'" class="action-btn modal-delete-btn" @click="deleteSlot(selectedLot.id, selectedSlot.slot_number)">Delete</button>
            <button class="action-btn modal-cancel-btn" @click="closeSlotModal">Close</button>
          </div>
        </div>
      </div>

      <!-- Detail Modal -->
      <div v-if="detailModalVisible" class="modal-overlay" @click.self="closeDetailModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Slot Details</h3>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Prime Location:</label>
              <input v-model="selectedLot.primeLocation" type="text" class="profile-input" readonly />
            </div>
            <div class="form-group">
              <label>Address:</label>
              <input v-model="selectedLot.address" type="text" class="profile-input" readonly />
            </div>
            <div class="form-group">
              <label>Pin Code:</label>
              <input v-model="selectedLot.pinCode" type="text" class="profile-input" readonly />
            </div>
            <div class="form-group">
              <label>Price (per hour):</label>
              <input v-model.number="selectedLot.pricePerHour" type="number" class="profile-input" readonly />
            </div>
            <div class="form-group">
              <label>Maximum Spots:</label>
              <input v-model.number="selectedLot.total" type="number" class="profile-input" readonly />
            </div>
            <p>Slot Number: {{ selectedSlot.slot_number }}</p>
            <p>Status: {{ selectedSlot.status === 'O' ? 'Occupied' : 'Available' }}</p>
          </div>
          <div class="button-group">
            <button class="action-btn modal-cancel-btn" @click="closeDetailModal">Close</button>
          </div>
        </div>
      </div>

      <!-- Deletion Restriction Modal -->
      <div v-if="deletionRestrictionModalVisible" class="modal-overlay" @click.self="deletionRestrictionModalVisible = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Deletion Restricted</h3>
          </div>
          <div class="modal-body">
            <p>You can't delete parking lot as it has an occupied parking slot.</p>
          </div>
          <div class="button-group">
            <button class="action-btn modal-cancel-btn" style="width: 100%; background: linear-gradient(90deg, #26a69a, #4dd0e1); color: #fff; font-size: 18px; font-weight: 500; border-radius: 8px; padding: 10px 0; margin-top: 10px;" @click="deletionRestrictionModalVisible = false">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbar from './ad-nav.vue';

export default {
  name: 'AdminSearch',
  components: {
    AdminNavbar,
  },
  data() {
    return {
      searchBy: 'userId',
      searchString: '',
      editModalVisible: false,
      slotModalVisible: false,
      detailModalVisible: false,
      editLotData: {
        id: null,
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        total: '',
        occupiedSpots: [],
      },
      selectedLot: {},
      selectedSlot: null,
      users: [],
      parkingLots: [],
      deletionRestrictionModalVisible: false,
    };
  },
  computed: {
    filteredUsers() {
      if (this.searchBy === 'primeLocation' || this.searchBy === 'pricePerHour') return [];
      if (!this.searchString.trim()) return this.users;
      const searchTerm = this.searchString.toLowerCase();
      if (this.searchBy === 'userId') {
        return this.users.filter(user => user.id.toString().includes(searchTerm));
      } else if (this.searchBy === 'name') {
        return this.users.filter(user => user.name.toLowerCase().includes(searchTerm));
      } else if (this.searchBy === 'email') {
        return this.users.filter(user => user.email.toLowerCase().includes(searchTerm));
      }
      return [];
    },
    filteredParkingLots() {
      if (this.searchBy !== 'primeLocation' && this.searchBy !== 'pricePerHour') return [];
      if (!this.searchString.trim()) return this.parkingLots;
      const searchTerm = this.searchString.toLowerCase();
      if (this.searchBy === 'primeLocation') {
        return this.parkingLots.filter(lot => lot.primeLocation.toLowerCase().includes(searchTerm));
      } else if (this.searchBy === 'pricePerHour') {
        return this.parkingLots.filter(lot => lot.pricePerHour.toString().includes(searchTerm));
      }
      return [];
    },
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await fetch('/api/admin/users', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
          this.users = data;
        } else {
          console.error('Failed to fetch users:', data.error);
        }
      } catch (err) {
        console.error('Error fetching users:', err);
      }
    },
    async fetchLots() {
      try {
        const response = await fetch('/api/admin/lots', { credentials: 'include' });
        const data = await response.json();
        if (response.ok) {
          this.parkingLots = data;
          // Fetch slots for each lot
          await Promise.all(this.parkingLots.map(async lot => {
            const res = await fetch(`/api/admin/lots/${lot.id}/slots`, { credentials: 'include' });
            lot.slots = await res.json();
          }));
        } else {
          console.error('Failed to fetch lots:', data.error);
        }
      } catch (err) {
        console.error('Error fetching lots:', err);
      }
    },
    searchItems() {
      console.log('Searching for:', this.searchBy, this.searchString);
    },
    updateSearch() {
      this.searchString = '';
      this.searchItems();
    },
    openEditModal(lot) {
      this.editLotData = {
        id: lot.id,
        primeLocation: lot.primeLocation,
        address: lot.address,
        pinCode: lot.pinCode,
        pricePerHour: lot.pricePerHour,
        total: lot.total
      };
      this.editModalVisible = true;
    },
    closeEditModal() {
      this.editModalVisible = false;
      this.editLotData = {};
    },
    resetEditData() {
      this.editLotData = {
        id: null,
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        total: '',
        occupiedSpots: [],
      };
    },
    updateEditOccupiedSpots() {
      const occupied = this.editLotData.occupiedSpots.length;
      const total = parseInt(this.editLotData.total) || 0;
      if (occupied > total) {
        this.editLotData.occupiedSpots = this.editLotData.occupiedSpots.slice(0, total);
      }
    },
    async updateLot() {
      if (!this.validateEditForm()) return;

      try {
        const response = await fetch(`/api/admin/lots/${this.editLotData.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            primeLocation: this.editLotData.primeLocation.trim(),
            address: this.editLotData.address.trim(),
            pinCode: this.editLotData.pinCode.trim(),
            pricePerHour: parseInt(this.editLotData.pricePerHour),
            maxSpots: parseInt(this.editLotData.total),
          }),
          credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
          const index = this.parkingLots.findIndex(l => l.id === this.editLotData.id);
          if (index !== -1) {
            this.parkingLots.splice(index, 1, data);
          }
          this.closeEditModal();
          await this.fetchLots();
          console.log('Lot updated:', data);
          alert('Parking lot updated successfully!');
        } else {
          alert(data.error || 'Failed to update lot');
        }
      } catch (err) {
        alert('Server error: ' + err.message);
      }
    },
    validateEditForm() {
      const { primeLocation, address, pinCode, pricePerHour, total } = this.editLotData;
      if (!primeLocation.trim() || !address.trim() || !pinCode.trim() || !pricePerHour || !total) {
        alert('Please fill all fields with valid data');
        return false;
      }
      if (isNaN(parseInt(pinCode)) || parseInt(pinCode) <= 0 || parseInt(pricePerHour) <= 0 || parseInt(total) <= 0) {
        alert('Pin Code, Price, and Maximum Spots must be positive numbers');
        return false;
      }
      return true;
    },
    async deleteLot(lotId) {
      try {
        const response = await fetch(`/api/admin/lots/${lotId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
          this.parkingLots = this.parkingLots.filter(l => l.id !== lotId);
          // Optionally refresh lots
          await this.fetchLots();
        } else {
          if (response.status === 400 && data.error === 'Cannot delete lot with occupied slots') {
            this.deletionRestrictionModalVisible = true;
          } else {
            alert(data.error || 'Failed to delete lot');
          }
        }
      } catch (err) {
        alert('Server error');
      }
    },
    async addSlot(lotId) {
      try {
        const response = await fetch(`/api/admin/lots/${lotId}/slots`, { method: 'POST', credentials: 'include' });
        const data = await response.json();
        if (response.ok) {
          const lot = this.parkingLots.find(l => l.id === lotId);
          lot.total += 1;
          await this.fetchLots();
          console.log('Slot added:', data);
          alert('Slot added successfully!');
        } else {
          alert(data.error || 'Failed to add slot');
        }
      } catch (err) {
        alert('Server error: ' + err.message);
      }
    },
    async deleteSlot(lotId, slotNumber) {
      try {
        const response = await fetch(`/api/admin/lots/${lotId}/slots/${slotNumber}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
          this.closeSlotModal();
          await this.fetchLots(); // Refresh lots and slots
        } else {
          alert(data.error || 'Failed to delete slot');
        }
      } catch (err) {
        alert('Server error');
      }
    },
    openSlotModal(lot, slot) {
      this.selectedLot = lot;
      this.selectedSlot = slot;
      this.slotModalVisible = true;
    },
    closeSlotModal() {
      this.slotModalVisible = false;
      this.selectedLot = {};
      this.selectedSlot = null;
    },
    openDetailModal() {
      this.detailModalVisible = true;
    },
    closeDetailModal() {
      this.detailModalVisible = false;
      this.selectedLot = {};
      this.selectedSlot = null;
    },
  },
  created() {
    this.fetchUsers();
    this.fetchLots();
  },
};
</script>

<style scoped>
@import url('../assets/ad-dash.css');

.search-section {
  margin-top: 20px;
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-dropdown {
  padding: 8px;
  border: 1px solid #bfc9d1;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Roboto', sans-serif;
  background: #f7fafc;
  cursor: pointer;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #bfc9d1;
  border-radius: 6px;
  font-size: 14px;
  font-family: 'Roboto', sans-serif;
  background: #f7fafc;
  flex: 1;
}

.search-input:focus {
  border-color: #3498db;
  outline: none;
}

.users-table-wrapper {
  overflow-x: auto;
  margin-top: 20px;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.users-table th,
.users-table td {
  padding: 10px;
  text-align: left;
  font-size: 14px;
  font-family: 'Roboto', sans-serif;
  border-bottom: 1px solid #ddd;
}

.users-table th {
  background-color: #ecf0f1;
  color: #333;
  text-transform: uppercase;
  font-weight: 500;
}

.users-table td {
  background-color: #fff;
}

.users-table tr:nth-child(even) td {
  background-color: #f9fbfd;
}
</style>