<template>
  <div class="page-container">
    <AdminNavbar />
    <div class="profile-container">
      <div class="profile-card">
        <div class="dashboard-header">
          <h2><i class="fas fa-users"></i> Admin Users</h2>
        </div>
        <!-- Users Table -->
        <div class="users-table-wrapper">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td>
                  <span :class="['status-badge', user.status === 'Active' ? 'active' : 'banned']">
                    {{ user.status }}
                  </span>
                </td>
                <td>
                  <button 
                    :class="['action-btn', user.status === 'Active' ? 'ban-btn' : 'unban-btn']" 
                    @click="showBanModal(user)"
                  >
                    {{ user.status === 'Active' ? 'Ban' : 'Unban' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
         </div>

        <!-- Ban/Unban Confirmation Modal -->
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal-content">
            <h3>{{ modalAction }} Confirmation</h3>
            <p>Are you sure you want to {{ modalAction.toLowerCase() }} {{ selectedUser.name }}?</p>
            <div class="button-group">
              <button class="action-btn confirm-btn" @click="confirmAction">{{ modalAction }}</button>
              <button class="action-btn cancel-btn" @click="closeModal">Cancel</button>
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
  name: 'AdminUsers',
  components: {
    AdminNavbar,
  },
  data() {
    return {
      users: [],
      showModal: false,
      selectedUser: {},
      modalAction: '',
    };
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await fetch('/api/admin/users', {
          headers: { 'Content-Type': 'application/json' },
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
    showBanModal(user) {
      this.selectedUser = { ...user };
      this.modalAction = user.status === 'Active' ? 'Ban' : 'Unban';
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.selectedUser = {};
      this.modalAction = '';
    },
    async confirmAction() {
      try {
        const endpoint = this.modalAction === 'Ban' ? '/ban' : '/unban';
        const response = await fetch(`/api/admin/users/${this.selectedUser.id}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const data = await response.json();
        if (response.ok) {
          const index = this.users.findIndex(u => u.id === this.selectedUser.id);
          if (index !== -1) {
            this.users[index].status = data.status;
          }
          this.closeModal();
          console.log(`${this.modalAction} successful for ${this.selectedUser.name}`);
          // Refresh the users list to ensure consistency
          await this.fetchUsers();
        } else {
          console.error('Failed to update user status:', data.error);
        }
      } catch (err) {
        console.error('Error updating user status:', err);
      }
    },
  },
  created() {
    this.fetchUsers();
  },
};
</script>

<style scoped>
@import url('../assets/base.css');
@import url('../assets/ad-dash.css');

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

.action-btn {
  padding: 6px 12px;
  background: linear-gradient(90deg, #1abc9c, #16a085);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.action-btn:hover {
  background: linear-gradient(90deg, #16a085, #1abc9c);
  transform: translateY(-1px);
}

.ban-btn {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
  color: white;
}

.ban-btn:hover {
  background: linear-gradient(90deg, #c0392b, #e74c3c);
  transform: translateY(-1px);
}

.unban-btn {
  background: linear-gradient(90deg, #27ae60, #2ecc71);
  color: white;
}

.unban-btn:hover {
  background: linear-gradient(90deg, #2ecc71, #27ae60);
  transform: translateY(-1px);
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.banned {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.confirm-btn {
  background: linear-gradient(90deg, #1abc9c, #16a085);
  color: white;
}

.confirm-btn:hover {
  background: linear-gradient(90deg, #16a085, #1abc9c);
  transform: translateY(-1px);
}

.cancel-btn {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
  color: white;
}

.cancel-btn:hover {
  background: linear-gradient(90deg, #c0392b, #e74c3c);
  transform: translateY(-1px);
}

.button-group {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.refresh-btn {
  background: linear-gradient(90deg, #3498db, #2980b9);
  color: white;
  margin-top: 10px;
}

.refresh-btn:hover {
  background: linear-gradient(90deg, #2980b9, #3498db);
  transform: translateY(-1px);
}

.modal-overlay {
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
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  text-align: center;
  color: #333;
  width: 300px;
}

.modal-content h3 {
  margin-bottom: 15px;
  color: #333;
}

.modal-content p {
  margin-bottom: 20px;
  color: #666;
}

@media (max-width: 600px) {
  .users-table {
    min-width: 100%;
    display: block;
  }
  .users-table thead {
    display: none;
  }
  .users-table tr,
  .users-table td {
    display: block;
    width: 100%;
  }
  .users-table td {
    padding: 8px;
    font-size: 12px;
    border-bottom: 1px solid #ddd;
  }
  .users-table td:before {
    content: attr(data-label);
    font-weight: 500;
    color: #1abc9c;
    margin-right: 10px;
    white-space: nowrap;
  }
  .users-table td[data-label="ID"]:before { content: "ID: "; }
  .users-table td[data-label="Name"]:before { content: "Name: "; }
  .users-table td[data-label="Email"]:before { content: "Email: "; }
  .users-table td[data-label="Status"]:before { content: "Status: "; }
  .users-table td[data-label="Actions"]:before { content: "Actions: "; }
  .action-btn {
    width: 100%;
    margin-bottom: 5px;
  }
  .action-btn:last-child {
    margin-bottom: 0;
  }
}
</style>
