<template>
  <div class="container">
    <div class="dash-box">
      <h2><i class="fas fa-users"></i> Admin Users</h2>
      <AdminNavbar />
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
              <td>{{ user.status }}</td>
              <td>
                <button class="action-btn ban-btn" @click="banUser(user)">
                  {{ user.status === 'Active' ? 'Ban' : 'Unban' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
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
      users: JSON.parse(localStorage.getItem('users')) || [
        { id: 1, name: 'John Doe', email: 'john.doe@example.com', status: 'Active' },
        { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com', status: 'Active' },
        { id: 3, name: 'Bob Johnson', email: 'bob.johnson@example.com', status: 'Banned' },
      ],
    };
  },
  methods: {
    banUser(user) {
      if (user.status === 'Active' && confirm(`Are you sure you want to ban ${user.name}?`)) {
        user.status = 'Banned';
        this.saveUsers();
        console.log('Banned user:', user.name);
      } else if (user.status === 'Banned' && confirm(`Are you sure you want to unban ${user.name}?`)) {
        user.status = 'Active';
        this.saveUsers();
        console.log('Unbanned user:', user.name);
      }
    },
    saveUsers() {
      localStorage.setItem('users', JSON.stringify(this.users));
    },
  },
  created() {
    window.addEventListener('beforeunload', () => {
      localStorage.removeItem('users');
    });
  },
};
</script>

<style>
@import url('../assets/ad-dash.css');

/* Additional styles for users table */
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
  border: none;
  border-radius: 5px;
  font-size: 12px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  cursor: pointer;
  margin-right: 5px;
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.ban-btn {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
  color: white;
}

.ban-btn:hover {
  background: linear-gradient(90deg, #c0392b, #e74c3c);
  transform: translateY(-1px);
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