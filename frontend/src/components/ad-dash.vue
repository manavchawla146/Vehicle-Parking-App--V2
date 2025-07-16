<template>
  <div class="page-container">
    <AdminNavbar />
    <div class="profile-container">
      <div class="profile-card">
        <div class="dashboard-header">
          <h2><i class="fas fa-shield-alt"></i> Admin Dashboard</h2>
          <button class="action-btn add-btn dashboard-add-btn" @click="showModal = true">+ Add Lot</button>
        </div>
        <h3 v-if="loading">Loading...</h3>
        <h3 v-else-if="parkingLots.length === 0">No Parking Lots Available</h3>
        <h3 v-else>Parking Lots</h3>
        <div v-if="!loading" class="parking-lots">
          <div v-for="lot in parkingLots" :key="lot.id" class="lot-card">
            <h2>
              {{ lot.address }} (Occupied: {{ lot.occupied }}/{{ lot.total }})
            </h2>
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

        <!-- Modal for Adding New Parking Lot -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeAddModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>New Parking Lot</h3>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Prime Location Name:</label>
                <input v-model="newLot.primeLocation" type="text" class="profile-input" placeholder="Enter location name" />
              </div>
              <div class="form-group">
                <label>Address:</label>
                <input v-model="newLot.address" type="text" class="profile-input" placeholder="Enter address" />
              </div>
              <div class="form-group">
                <label>Pin Code:</label>
                <input v-model="newLot.pinCode" type="text" class="profile-input" placeholder="Enter pin code" />
              </div>
              <div class="form-group">
                <label>Price (per hour):</label>
                <input v-model.number="newLot.pricePerHour" type="number" class="profile-input" placeholder="Enter price" />
              </div>
              <div class="form-group">
                <label>Maximum Spots:</label>
                <input v-model.number="newLot.maxSpots" type="number" class="profile-input" placeholder="Enter maximum spots" />
              </div>
            </div>
            <div class="button-group">
              <button class="action-btn save-btn" @click="addNewLot">Save</button>
              <button class="action-btn cancel-btn" @click="closeAddModal">Cancel</button>
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

        <!-- Occupied Slot Modal -->
        <div v-if="occupiedSlotModalVisible" class="modal-overlay" @click.self="closeOccupiedSlotModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Occupied Slot Details</h3>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Parking Lot:</label>
                <span>{{ selectedLot.primeLocation }}</span>
              </div>
              <div class="form-group">
                <label>Slot Number:</label>
                <span>{{ selectedSlot }}</span>
              </div>
              <div class="form-group">
                <label>Status:</label>
                <span>Occupied</span>
              </div>
              <div class="form-group">
                <label>Vehicle ID:</label>
                <input v-model="getSlotDetails(selectedSlot).vehicleId" type="text" class="profile-input" readonly />
              </div>
              <div class="form-group">
                <label>Occupation Time:</label>
                <input v-model="getSlotDetails(selectedSlot).occupationTime" type="text" class="profile-input" readonly />
              </div>
            </div>
            <div class="button-group">
              <button class="action-btn cancel-btn" @click="closeOccupiedSlotModal">Close</button>
            </div>
          </div>
        </div>

        <!-- Available Slot Modal -->
        <div v-if="availableSlotModalVisible" class="modal-overlay" @click.self="closeAvailableSlotModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Available Slot Details</h3>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Parking Lot:</label>
                <span>{{ selectedLot.primeLocation }}</span>
              </div>
              <div class="form-group">
                <label>Slot Number:</label>
                <span>{{ selectedSlot }}</span>
              </div>
              <div class="form-group">
                <label>Status:</label>
                <span>Available</span>
              </div>
            </div>
            <div class="button-group">
              <button class="action-btn delete-btn" @click="deleteSlot(selectedLot.id, selectedSlot.slot_number); closeAvailableSlotModal()">Delete</button>
              <button class="action-btn cancel-btn" @click="closeAvailableSlotModal">Close</button>
            </div>
          </div>
        </div>

        <!-- Deletion Restriction Modal -->
        <div v-if="deletionRestrictionModalVisible" class="modal-overlay" @click.self="closeDeletionRestrictionModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Deletion Restricted</h3>
            </div>
            <div class="modal-body">
              <p>You can't delete parking lot as it has an occupied parking slot.</p>
            </div>
            <div class="button-group">
              <button class="action-btn cancel-btn" @click="closeDeletionRestrictionModal">Close</button>
            </div>
          </div>
        </div>

        <!-- Slot Details Modal -->
        <div v-if="slotModalVisible" class="modal-overlay" @click.self="closeSlotModal">
          <div class="modal-content">
            <div class="modal-header">
              <h3>Slot Details</h3>
            </div>
            <div class="modal-body">
              <p>Parking Lot: {{ selectedLot.primeLocation }}</p>
              <p>Slot Number: {{ selectedSlot.slot_number }}</p>
              <p>Status: {{ selectedSlot.status === 'O' ? 'Occupied' : 'Available' }}</p>
              <p v-if="selectedSlot.status === 'O'">Vehicle: {{ selectedSlot.vehicle_id }}</p>
              <p v-if="selectedSlot.status === 'O'">User: {{ selectedSlot.username }}</p>
            </div>
            <div class="button-group">
              <button v-if="selectedSlot.status === 'A'" class="action-btn modal-delete-btn" @click="deleteSlot(selectedLot.id, selectedSlot.slot_number)">Delete</button>
              <button class="action-btn modal-cancel-btn" @click="closeSlotModal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminNavbar from './ad-nav.vue';

export default {
  name: 'AdminDashboard',
  components: {
    'AdminNavbar': AdminNavbar,
  },
  data() {
    return {
      showModal: false,
      editModalVisible: false,
      occupiedSlotModalVisible: false,
      availableSlotModalVisible: false,
      deletionRestrictionModalVisible: false,
      loading: true,
      newLot: {
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        maxSpots: '',
      },
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
      parkingLots: [],
      slotModalVisible: false,
    };
  },
  methods: {
    openEditModal(lot) {
      console.log('Opening edit modal for:', lot);
      this.editLotData = {
        id: lot.id,
        primeLocation: lot.primeLocation,
        address: lot.address,
        pinCode: lot.pinCode,
        pricePerHour: lot.pricePerHour,
        total: lot.total,
        occupiedSpots: [...lot.occupiedSpots],
      };
      this.editModalVisible = true;
    },
    closeEditModal() {
      console.log('Closing edit modal');
      this.editModalVisible = false;
      this.resetEditData();
    },
    closeAddModal() {
      this.showModal = false;
      this.resetNewLot();
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
    async addNewLot() {
      if (!this.validateForm()) return;

      try {
        const response = await fetch('/api/admin/lots', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            primeLocation: this.newLot.primeLocation.trim(),
            address: this.newLot.address.trim(),
            pinCode: this.newLot.pinCode.trim(),
            pricePerHour: parseInt(this.newLot.pricePerHour),
            maxSpots: parseInt(this.newLot.maxSpots),
          }),
          credentials: 'include'
        });
        const data = await response.json();
        if (response.ok) {
          this.parkingLots.push(data);
          this.closeAddModal();
          await this.fetchLots();
          console.log('New lot added:', data);
          alert('Parking lot added successfully!');
        } else {
          alert(data.error || 'Failed to add lot');
        }
      } catch (err) {
        alert('Server error: ' + err.message);
      }
    },
    resetNewLot() {
      this.newLot = {
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        maxSpots: '',
      };
    },
    validateForm() {
      const { primeLocation, address, pinCode, pricePerHour, maxSpots } = this.newLot;
      if (!primeLocation.trim() || !address.trim() || !pinCode.trim() || !pricePerHour || !maxSpots) {
        alert('Please fill all fields with valid data');
        return false;
      }
      if (isNaN(parseInt(pinCode)) || parseInt(pinCode) <= 0 || parseInt(pricePerHour) <= 0 || parseInt(maxSpots) <= 0) {
        alert('Pin Code, Price, and Maximum Spots must be positive numbers');
        return false;
      }
      return true;
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
    async fetchLots() {
      this.loading = true;
      try {
        const response = await fetch('/api/admin/lots', { credentials: 'include' });
        const data = await response.json();
        if (response.ok) {
          this.parkingLots = data;
          // Fetch slots for each lot and attach them
          await Promise.all(this.parkingLots.map(async lot => {
            const res = await fetch(`/api/admin/lots/${lot.id}/slots`, { credentials: 'include' });
            lot.slots = await res.json();
          }));
        } else {
          console.error('Failed to fetch lots:', data.error);
        }
      } catch (err) {
        console.error('Error fetching lots:', err);
      } finally {
        this.loading = false;
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
    closeOccupiedSlotModal() {
      this.occupiedSlotModalVisible = false;
      this.selectedLot = {};
      this.selectedSlot = null;
    },
    closeAvailableSlotModal() {
      this.availableSlotModalVisible = false;
      this.selectedLot = {};
      this.selectedSlot = null;
    },
    async deleteLot(lotId) {
      try {
        const response = await fetch(`/api/admin/lots/${lotId}`, { method: 'DELETE', credentials: 'include' });
        const data = await response.json();
        if (response.ok) {
          this.parkingLots = this.parkingLots.filter(l => l.id !== lotId);
          console.log('Deleted lot:', lotId);
          alert('Parking lot deleted successfully!');
        } else {
          alert(data.error || 'Failed to delete lot');
          if (response.status === 400 && data.error === 'Cannot delete lot with occupied slots') {
            this.deletionRestrictionModalVisible = true;
          }
        }
      } catch (err) {
        alert('Server error: ' + err.message);
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
    closeDeletionRestrictionModal() {
      this.deletionRestrictionModalVisible = false;
    },
    getSlotDetails(slot) {
      const slotData = this.selectedLot.slots.find(s => s.slot_number === slot);
      return slotData || { vehicleId: 'N/A', occupationTime: 'N/A' };
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
  },
  created() {
    this.fetchLots();
    console.log('Component created, parking lots:', this.parkingLots);
  },
};
</script>

<style scoped>
@import url('../assets/ad-dash.css');
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 16px;
}
.dashboard-add-btn {
  min-width: 120px;
  max-width: 160px;
  padding: 8px 20px;
  font-size: 16px;
  background-color: #1abc9c;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.07);
}
.dashboard-add-btn:hover {
  background-color: #159c86;
}
.occupied {
  background: #e74c3c;
  color: #fff;
}
.available {
  background: #1abc9c;
  color: #fff;
}
</style>