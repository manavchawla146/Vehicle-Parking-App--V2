<template>
  <div class="container">
    <div class="dash-box">
      <h2><i class="fas fa-shield-alt"></i> Admin Dashboard</h2>
      <AdminNavbar />
      <!-- Parking Lots Section -->
      <h3>Parking Lots</h3>
      <div class="parking-lots">
        <div v-for="lot in parkingLots" :key="lot.id" class="parking-card">
          <h4>{{ lot.primeLocation }} <span>(Occupied: {{ lot.occupied }}/{{ lot.total }})</span></h4>
          <div class="button-group">
            <button class="action-btn edit-btn" @click="openEditModal(lot)">Edit</button>
            <button class="action-btn delete-btn" @click="deleteLot(lot)">Delete</button>
          </div>
          <div class="parking-grid">
            <span v-for="n in lot.total" :key="n" :class="['parking-spot', { occupied: lot.occupiedSpots.includes(n) }]" @click="openSlotModal(lot, n)">
              {{ lot.occupiedSpots.includes(n) ? 'O' : 'A' }}
            </span>
          </div>
        </div>
        <button class="add-btn" @click="showModal = true">+ Add Lot</button>
      </div>

      <!-- Modal for Adding New Parking Lot -->
      <div v-if="showModal" class="modal-overlay" @click.self="closeAddModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>New Parking Lot</h3>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Prime Location Name :</label>
              <input v-model="newLot.primeLocation" type="text" class="modal-input" placeholder="Enter location name" />
            </div>
            <div class="form-group">
              <label>Address :</label>
              <textarea v-model="newLot.address" class="modal-textarea" placeholder="Enter address"></textarea>
            </div>
            <div class="form-group">
              <label>Pin code :</label>
              <input v-model="newLot.pinCode" type="text" class="modal-input" placeholder="Enter pin code" />
            </div>
            <div class="form-group">
              <label>Price(per hour):</label>
              <input v-model.number="newLot.pricePerHour" type="number" class="modal-input" placeholder="Enter price" />
            </div>
            <div class="form-group">
              <label>Maximum spots :</label>
              <input v-model.number="newLot.maxSpots" type="number" class="modal-input" placeholder="Enter maximum spots" @input="updateNewOccupiedSpots" />
            </div>
            <div class="form-group">
              <label>Occupied spots :</label>
              <input v-model.number="newLot.occupied" type="number" class="modal-input" :max="newLot.maxSpots" @input="updateNewOccupiedSpots" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="action-btn modal-add-btn" @click="addNewLot">Add</button>
            <button class="action-btn modal-cancel-btn" @click="closeAddModal">Cancel</button>
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

      <!-- Occupied Slot Modal -->
      <div v-if="occupiedSlotModalVisible" class="modal-overlay" @click.self="closeOccupiedSlotModal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Occupied Slot Details</h3>
          </div>
          <div class="modal-body">
            <p>Parking Lot: {{ selectedLot.primeLocation }}</p>
            <p>Slot Number: {{ selectedSlot }}</p>
            <p>Status: Occupied</p>
            <div class="form-group">
              <label>Vehicle ID:</label>
              <input v-model="getSlotDetails(selectedSlot).vehicleId" type="text" class="modal-input" readonly />
            </div>
            <div class="form-group">
              <label>Occupation Time:</label>
              <input v-model="getSlotDetails(selectedSlot).occupationTime" type="text" class="modal-input" readonly />
            </div>
          </div>
          <div class="modal-footer">
            <button class="action-btn modal-cancel-btn" @click="closeOccupiedSlotModal">Close</button>
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
            <p>Parking Lot: {{ selectedLot.primeLocation }}</p>
            <p>Slot Number: {{ selectedSlot }}</p>
            <p>Status: Available</p>
          </div>
          <div class="modal-footer">
            <button class="action-btn modal-delete-btn" @click="deleteSlot(selectedLot, selectedSlot); closeAvailableSlotModal()">Delete</button>
            <button class="action-btn modal-cancel-btn" @click="closeAvailableSlotModal">Close</button>
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
          <div class="modal-footer">
            <button class="action-btn modal-cancel-btn" @click="closeDeletionRestrictionModal">Close</button>
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
    AdminNavbar,
  },
  data() {
    return {
      showModal: false,
      editModalVisible: false,
      occupiedSlotModalVisible: false,
      availableSlotModalVisible: false,
      deletionRestrictionModalVisible: false,
      newLot: {
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        maxSpots: '',
        occupied: '',
      },
      editLotData: {
        id: null,
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        total: '',
        occupied: '',
        occupiedSpots: []
      },
      selectedLot: {},
      selectedSlot: null,
      parkingLots: JSON.parse(localStorage.getItem('parkingLots')) || [
        { id: 1, primeLocation: 'Velachery Lot', address: '123 Velachery St', pinCode: '600042', pricePerHour: 20, total: 15, occupied: 3, occupiedSpots: [2, 5, 10], location: 'Velachery', slotDetails: { 2: { vehicleId: 'VH001', occupationTime: '2025-07-15 14:00' }, 5: { vehicleId: 'VH002', occupationTime: '2025-07-15 14:30' }, 10: { vehicleId: 'VH003', occupationTime: '2025-07-15 15:00' } } },
        { id: 2, primeLocation: 'Anna Nagar Lot', address: '456 Anna Nagar Rd', pinCode: '600040', pricePerHour: 25, total: 10, occupied: 4, occupiedSpots: [1, 3, 6, 8], location: 'Anna Nagar', slotDetails: { 1: { vehicleId: 'AN001', occupationTime: '2025-07-15 13:00' }, 3: { vehicleId: 'AN002', occupationTime: '2025-07-15 13:30' }, 6: { vehicleId: 'AN003', occupationTime: '2025-07-15 14:00' }, 8: { vehicleId: 'AN004', occupationTime: '2025-07-15 14:30' } } },
      ],
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
        occupied: lot.occupied,
        occupiedSpots: [...lot.occupiedSpots]
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
        occupied: '',
        occupiedSpots: []
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
    updateNewOccupiedSpots() {
      const occupied = parseInt(this.newLot.occupied) || 0;
      const maxSpots = parseInt(this.newLot.maxSpots) || 0;
      
      if (occupied > maxSpots) {
        this.newLot.occupied = maxSpots;
      }
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
          location: this.editLotData.primeLocation,
          slotDetails: this.parkingLots[index].slotDetails || {}
        };
        
        console.log('Updating with:', updatedLot);
        
        this.parkingLots.splice(index, 1, updatedLot);
        this.saveParkingLots();
        this.closeEditModal();
      } else {
        console.log('Lot not found');
      }
    },
    deleteLot(lot) {
      // Prevent deletion if there are occupied slots
      if (lot.occupied > 0) {
        this.deletionRestrictionModalVisible = true;
        return;
      }
      
      this.parkingLots = this.parkingLots.filter(l => l.id !== lot.id);
      this.saveParkingLots();
      console.log('Deleted lot:', lot.primeLocation);
    },
    addNewLot() {
      if (!this.validateForm()) return;
      
      const newId = this.parkingLots.length > 0 ? Math.max(...this.parkingLots.map(l => l.id)) + 1 : 1;
      const occupiedCount = Math.min(parseInt(this.newLot.occupied) || 0, parseInt(this.newLot.maxSpots) || 0);
      
      this.parkingLots.push({
        id: newId,
        primeLocation: this.newLot.primeLocation,
        address: this.newLot.address,
        pinCode: this.newLot.pinCode,
        pricePerHour: parseInt(this.newLot.pricePerHour),
        total: parseInt(this.newLot.maxSpots),
        occupied: occupiedCount,
        occupiedSpots: Array.from({ length: occupiedCount }, (_, i) => i + 1),
        location: this.newLot.primeLocation,
        slotDetails: {}
      });
      
      this.saveParkingLots();
      this.closeAddModal();
      console.log('New lot added:', this.parkingLots[this.parkingLots.length - 1]);
    },
    resetNewLot() {
      this.newLot = {
        primeLocation: '',
        address: '',
        pinCode: '',
        pricePerHour: '',
        maxSpots: '',
        occupied: ''
      };
    },
    validateForm() {
      const { primeLocation, address, pinCode, pricePerHour, maxSpots, occupied } = this.newLot;
      
      if (!primeLocation.trim() || !address.trim() || !pinCode.trim() || !pricePerHour || !maxSpots || occupied === '') {
        console.log('Please fill all fields');
        return false;
      }
      
      if (isNaN(pinCode) || parseInt(pricePerHour) <= 0 || parseInt(maxSpots) <= 0 || parseInt(occupied) < 0) {
        console.log('Please enter valid numbers for all numeric fields');
        return false;
      }
      
      if (parseInt(occupied) > parseInt(maxSpots)) {
        console.log('Occupied spots cannot exceed maximum spots');
        return false;
      }
      
      return true;
    },
    validateEditForm() {
      const { primeLocation, address, pinCode, pricePerHour, total, occupied } = this.editLotData;
      
      if (!primeLocation.trim() || !address.trim() || !pinCode.trim() || !pricePerHour || !total || occupied === '') {
        console.log('Please fill all fields');
        return false;
      }
      
      if (isNaN(pinCode) || parseInt(pricePerHour) <= 0 || parseInt(total) <= 0 || parseInt(occupied) < 0) {
        console.log('Please enter valid numbers for all numeric fields');
        return false;
      }
      
      if (parseInt(occupied) > parseInt(total)) {
        console.log('Occupied spots cannot exceed maximum spots');
        return false;
      }
      
      return true;
    },
    saveParkingLots() {
      localStorage.setItem('parkingLots', JSON.stringify(this.parkingLots));
      console.log('Saved parking lots to localStorage');
    },
    openSlotModal(lot, slot) {
      this.selectedLot = { ...lot };
      this.selectedSlot = slot;
      if (lot.occupiedSpots.includes(slot)) {
        this.occupiedSlotModalVisible = true;
      } else {
        this.availableSlotModalVisible = true;
      }
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
    deleteSlot(lot, slot) {
      if (lot.occupiedSpots.includes(slot)) {
        console.log('Cannot delete an occupied slot!');
        return;
      }

      const index = this.parkingLots.findIndex(l => l.id === lot.id);
      if (index !== -1) {
        const updatedLot = { ...lot };
        updatedLot.total -= 1; // Decrease total count
        updatedLot.occupiedSpots = updatedLot.occupiedSpots.filter(s => s !== slot && s <= updatedLot.total); // Adjust occupied spots
        updatedLot.occupied = updatedLot.occupiedSpots.length; // Update occupied count
        updatedLot.slotDetails = Object.fromEntries(
          Object.entries(updatedLot.slotDetails || {}).filter(([key]) => parseInt(key) !== slot)
        );
        this.parkingLots.splice(index, 1, updatedLot);
        this.saveParkingLots();
        console.log(`Deleted slot ${slot} from ${lot.primeLocation}`);
      }
    },
    closeDeletionRestrictionModal() {
      this.deletionRestrictionModalVisible = false;
    },
    getSlotDetails(slot) {
      return this.selectedLot.slotDetails?.[slot] || { vehicleId: 'N/A', occupationTime: 'N/A' };
    },
  },
  created() {
    console.log('Component created, parking lots:', this.parkingLots);
  },
};
</script>

<style scoped>
@import url('../assets/ad-dash.css');
</style>  