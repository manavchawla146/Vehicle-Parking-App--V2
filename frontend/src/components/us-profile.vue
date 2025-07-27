<template>
  <div class="page-container">
    <us-nav />
    <div class="profile-container">
      <div class="profile-card">
        <div class="dashboard-header">
          <h2><i class="fas fa-user"></i> User Profile</h2>
        </div>
        <div v-if="!isEditing" class="profile-details">
          <div class="detail-group">
            <label>Name:</label>
            <span>{{ user.name }}</span>
          </div>
          <div class="detail-group">
            <label>Email:</label>
            <span>{{ user.email }}</span>
          </div>
          <div class="detail-group">
            <label>Address:</label>
            <span>{{ user.address }}</span>
          </div>
          <div class="detail-group">
            <label>Pin Code:</label>
            <span>{{ user.pincode }}</span>
          </div>
          <div class="detail-group">
            
          </div>
          <button class="action-btn edit-btn" @click="enableEditing">Edit Profile</button>
        </div>
        <div v-else class="profile-edit">
          <div class="form-group">
            <label>Name:</label>
            <input v-model="user.name" type="text" class="profile-input" />
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input v-model="user.email" type="email" class="profile-input" />
          </div>
          <div class="form-group">
            <label>Address:</label>
            <input v-model="user.address" type="text" class="profile-input" />
          </div>
          <div class="form-group">
            <label>Pin Code:</label>
            <input v-model="user.pincode" type="text" class="profile-input" />
          </div>
          <div class="form-group">
            
          </div>
          <div class="button-group">
            <button class="action-btn save-btn" @click="saveChanges">Save</button>
            <button class="action-btn save-btn" @click="cancelEditing">Cancel</button>
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
      isEditing: false,
      user: {
        name: 'John Doe',
        email: 'user@example.com',
        address: '123 Main St',
        pincode: '12345',
        password: 'password123',
      },
    };
  },
  methods: {
    enableEditing() {
      this.isEditing = true;
    },
    cancelEditing() {
      this.isEditing = false;
      this.loadUserData();
    },
    async saveChanges() {
      if (this.validateForm()) {
        try {
          const response = await fetch('/api/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: this.user.name,
              email: this.user.email,
              address: this.user.address,
              pincode: this.user.pincode
            })
          });
          const data = await response.json();
          if (response.ok) {
            this.isEditing = false;
            // Optionally reload user data from server
            this.loadUserData();
          } else {
            alert(data.error || 'Failed to update profile');
          }
        } catch (err) {
          alert('Server error');
        }
      }
    },
    async loadUserData() {
      try {
        const response = await fetch('/api/profile');
        const data = await response.json();
        if (response.ok) {
          this.user = {
            name: data.name,
            email: data.email,
            address: data.address,
            pincode: data.pincode,
          };
        } else {
          // Handle not logged in or error
          this.$router.push('/login');
        }
      } catch (err) {
        this.$router.push('/login');
      }
    },
    validateForm() {
      if (!this.user.name || !this.user.email || !this.user.address || !this.user.pincode) {
        alert('Please fill all fields');
        return false;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.user.email)) {
        alert('Please enter a valid email address');
        return false;
      }
      const pincodeRegex = /^\d{5,6}$/;
      if (!pincodeRegex.test(this.user.pincode)) {
        alert('Pin Code must be a 5-6 digit number');
        return false;
      }
      return true;
    },
  },
  created() {
    this.loadUserData();
  },
};
</script>

<style scoped>
@import url('../assets/base.css');

/* Profile styles */
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e4f5 100%);
  display: flex;
  flex-direction: column;
}

.profile-container {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.profile-card {
  background: #ffffff;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 30px;
  flex: 1;
  margin: 0;
  width: 100%;
  max-width: none;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 0 16px;
}

.dashboard-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #2c3e50;
}

.dashboard-header h2 i {
  margin-right: 8px;
  color: #3498db;
}

.profile-details, .profile-edit {
  text-align: left;
  position: relative;
  z-index: 1;
}

.detail-group, .form-group {
  margin-bottom: 20px;
}

.detail-group label, .form-group label {
  display: block;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.detail-group span {
  display: block;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 8px;
  color: #333;
  border: 1px solid #e9ecef;
}

.profile-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  background-color: #ffffff;
  color: #333;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.profile-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 8px rgba(52, 152, 219, 0.3);
}

.button-group {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
}

.action-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  width: 48%;
}

.edit-btn {
  background-color: #3498db;
  color: #ffffff;
  width: 100%;
}

.edit-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.save-btn {
  background-color: #27ae60;
  color: #ffffff;
}

.save-btn:hover {
  background-color: #229954;
  transform: translateY(-2px);
}

.cancel-btn {
  background-color: #95a5a6;
  color: #ffffff;
}

.cancel-btn:hover {
  background-color: #7f8c8d;
  transform: translateY(-2px);
}

@media (max-width: 600px) {
  .profile-container {
    padding: 15px;
  }
  
  .profile-card {
    padding: 20px;
  }
  
  .dashboard-header h2 {
    font-size: 20px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 15px;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>