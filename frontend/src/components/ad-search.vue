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
      <div v-if="(filteredParkingLots.length || searchBy === 'primeLocation' || searchBy === 'pricePerHour') && (searchBy === 'primeLocation' || searchBy === 'pricePerHour')" class="parking-lots">
        <div v-for="lot in filteredParkingLots" :key="lot.id" class="parking-card">
          <h4>{{ lot.primeLocation }} (Occupied: {{ lot.occupied }}/{{ lot.total }}) <button class="action-btn" @click="openEditModal(lot)">Edit</button> <button class="action-btn delete-btn" @click="deleteLot(lot)">Delete</button></h4>
          <div class="parking-grid">
            <span v-for="n in lot.total" :key="n" :class="['parking-spot', { occupied: lot.occupiedSpots.includes(n) }]" @click="openSlotModal(lot, n)">
              {{ lot.occupiedSpots.includes(n) ? 'O' : 'A' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Modal for Editing Parking Lot -->
      <div v-if="editModalVisible" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Edit Parking Lot</h3>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Prime Location Name :</label>
              <input v-model="editLotData.primeLocation" type="text" class="modal-input" />
            </div>
            <div class="form-group">
              <label>Address :</label>
              <textarea v-model="editLotData.address" class="modal-textarea"></textarea>
            </div>
            <div class="form-group">
              <label>Pin code :</label>
              <input v-model="editLotData.pinCode" type="text" class="modal-input" />
            </div>
            <div class="form-group">
              <label>Price(per hour):</label>
              <input v-model.number="editLotData.pricePerHour" type="number" class="modal-input" />
            </div>
            <div class="form-group">
              <label>Maximum spots :</label>
              <input v-model.number="editLotData.total" type="number" class="modal-input" @input="updateEditOccupiedSpots" />
            </div>
            <div class="form-group">
              <label>Occupied spots :</label>
              <input v-model.number="editLotData.occupied" type="number" class="modal-input" :max="editLotData.total" @input="updateEditOccupiedSpots" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="action-btn modal-update-btn" @click="updateLot">Update</button>
            <button class="action-btn modal-cancel-btn" @click="closeEditModal">Cancel</button>
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
            <p>Slot Number: {{ selectedSlot }}</p>
            <p>Status: {{ selectedLot.occupiedSpots.includes(selectedSlot) ? 'Occupied' : 'Available' }}</p>
          </div>
          <div class="modal-footer">
            <button v-if="selectedLot.occupiedSpots.includes(selectedSlot)" class="action-btn modal-detail-btn" @click="openDetailModal">Detail</button>
            <button v-else class="action-btn modal-delete-btn" @click="deleteSlot">Delete</button>
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
              <input v-model="selectedLot.primeLocation" type="text" class="modal-input" readonly />
            </div>
            <div class="form-group">
              <label>Address:</label>
              <textarea v-model="selectedLot.address" class="modal-textarea" readonly></textarea>
            </div>
            <div class="form-group">
              <label>Pin Code:</label>
              <input v-model="selectedLot.pinCode" type="text" class="modal-input" readonly />
            </div>
            <div class="form-group">
              <label>Price (per hour):</label>
              <input v-model.number="selectedLot.pricePerHour" type="number" class="modal-input" readonly />
            </div>
            <div class="form-group">
              <label>Maximum Spots:</label>
              <input v-model.number="selectedLot.total" type="number" class="modal-input" readonly />
            </div>
            <div class="form-group">
              <label>Occupied Spots:</label>
              <input v-model.number="selectedLot.occupied" type="number" class="modal-input" readonly />
            </div>
            <p>Slot Number: {{ selectedSlot }}</p>
            <p>Status: {{ selectedLot.occupiedSpots.includes(selectedSlot) ? 'Occupied' : 'Available' }}</p>
          </div>
          <div class="modal-footer">
            <button class="action-btn modal-cancel-btn" @click="closeDetailModal">Close</button>
          </div>
        </div>
      </div>

      <p v-if="!filteredUsers.length && !filteredParkingLots.length && searchString">No results found matching your search.</p>
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
        occupied: '',
        occupiedSpots: [],
        location: ''
      },
      selectedLot: {},
      selectedSlot: null,
      users: JSON.parse(localStorage.getItem('users')) || [
        { id: 1, name: 'John Doe', email: 'john.doe@example.com', status: 'Active' },
        { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', status: 'Active' },
        { id: 3, name: 'Bob Johnson', email: 'bob.johnson@example.com', status: 'Banned' },
      ],
      parkingLots: JSON.parse(localStorage.getItem('parkingLots')) || [
        { id: 1, primeLocation: 'Velachery Lot', address: '123 Velachery St', pinCode: '600042', pricePerHour: 20, total: 15, occupied: 3, occupiedSpots: [2, 5, 10], location: 'Velachery' },
        { id: 2, primeLocation: 'Anna Nagar Lot', address: '456 Anna Nagar Rd', pinCode: '600040', pricePerHour: 25, total: 10, occupied: 4, occupiedSpots: [1, 3, 6, 8], location: 'Anna Nagar' },
      ],
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
    searchItems() {
      console.log('Searching for:', this.searchBy, this.searchString);
    },
    updateSearch() {
      this.searchString = '';
      this.searchItems();
    },
    openEditModal(lot) {
      console.log('Opening edit modal for:', lot);
      this.editLotData = {
        id: lot.id,
        primeLocation: lot.primeLocation,
        address: lot.address,
        pinCode: lot.pinCode,
        pricePerHour: lot.pricePerHour,
        total: lot.total,
        occupied: lot.occupied,
        occupiedSpots: [...lot.occupiedSpots],
        location: lot.primeLocation
      };
      this.editModalVisible = true;
    },
    closeEditModal() {
      console.log('Closing edit modal');
      this.editModalVisible = false;
      this.resetEditData();
    },
    resetEditData() {
      this.editLotData = {
        id: null,
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        total: '',
        occupied: '',
        occupiedSpots: [],
        location: ''
      };
    },
    updateEditOccupiedSpots() {
      const occupied = parseInt(this.editLotData.occupied) || 0;
      const total = parseInt(this.editLotData.total) || 0;
      
      if (occupied > total) {
        this.editLotData.occupied = total;
      }
      
      this.editLotData.occupiedSpots = Array.from(
        { length: parseInt(this.editLotData.occupied) || 0 }, 
        (_, i) => i + 1
      );
    },
    updateLot() {
      console.log('Update button clicked');
      
      if (!this.validateEditForm()) {
        console.log('Validation failed');
        return;
      }
      
      const index = this.parkingLots.findIndex(l => l.id === this.editLotData.id);
      console.log('Found lot at index:', index);
      
      if (index !== -1) {
        const updatedLot = {
          id: this.editLotData.id,
          primeLocation: this.editLotData.primeLocation,
          address: this.editLotData.address,
          pinCode: this.editLotData.pinCode,
          pricePerHour: parseInt(this.editLotData.pricePerHour),
          total: parseInt(this.editLotData.total),
          occupied: parseInt(this.editLotData.occupied),
          occupiedSpots: [...this.editLotData.occupiedSpots],
          location: this.editLotData.primeLocation
        };
        
        console.log('Updating with:', updatedLot);
        
        this.parkingLots.splice(index, 1, updatedLot);
        this.saveParkingLots();
        this.closeEditModal();
        
        console.log('Updated lot:', updatedLot.primeLocation);
        alert('Parking lot updated successfully!');
      } else {
        console.log('Lot not found');
        alert('Error: Parking lot not found');
      }
    },
    validateEditForm() {
      const { primeLocation, address, pinCode, pricePerHour, total, occupied } = this.editLotData;
      
      if (!primeLocation.trim() || !address.trim() || !pinCode.trim() || !pricePerHour || !total || occupied === '') {
        alert('Please fill all fields');
        return false;
      }
      
      if (isNaN(pinCode) || parseInt(pricePerHour) <= 0 || parseInt(total) <= 0 || parseInt(occupied) < 0) {
        alert('Please enter valid numbers for all numeric fields');
        return false;
      }
      
      if (parseInt(occupied) > parseInt(total)) {
        alert('Occupied spots cannot exceed maximum spots');
        return false;
      }
      
      return true;
    },
    deleteLot(lot) {
      if (confirm(`Are you sure you want to delete ${lot.primeLocation}?`)) {
        this.parkingLots = this.parkingLots.filter(l => l.id !== lot.id);
        this.saveParkingLots();
        console.log('Deleted lot:', lot.primeLocation);
      }
    },
    saveParkingLots() {
      localStorage.setItem('parkingLots', JSON.stringify(this.parkingLots));
    },
    openSlotModal(lot, slot) {
      this.selectedLot = { ...lot };
      this.selectedSlot = slot;
      this.slotModalVisible = true;
    },
    closeSlotModal() {
      this.slotModalVisible = false;
      this.selectedLot = {};
      this.selectedSlot = null;
    },
    openDetailModal() {
      this.slotModalVisible = false;
      this.detailModalVisible = true;
    },
    closeDetailModal() {
      this.detailModalVisible = false;
      this.selectedLot = {};
      this.selectedSlot = null;
    },
    deleteSlot() {
      if (this.selectedLot.occupiedSpots.includes(this.selectedSlot)) {
        alert('Cannot delete an occupied slot!');
        return;
      }
      const index = this.parkingLots.findIndex(l => l.id === this.selectedLot.id);
      if (index !== -1) {
        const lot = this.parkingLots[index];
        lot.occupiedSpots = lot.occupiedSpots.filter(s => s !== this.selectedSlot);
        lot.occupied = lot.occupiedSpots.length;
        this.parkingLots.splice(index, 1, lot);
        this.saveParkingLots();
        this.closeSlotModal();
        console.log(`Deleted slot ${this.selectedSlot} from ${lot.primeLocation}`);
        alert('Slot deleted successfully!');
      }
    },
  },
  created() {
    window.addEventListener('beforeunload', () => {
      localStorage.removeItem('users');
      localStorage.removeItem('parkingLots');
    });
  },
};
</script>

<style scoped>
@import url('../assets/ad-dash.css');
</style>