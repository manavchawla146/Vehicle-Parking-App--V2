<template>
  <div class="page-container">
    <us-nav />
    <div class="profile-container">
      <div class="profile-card">
        <h2><i class="fas fa-user"></i> User Profile</h2>
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
            <label>Password:</label>
            <span>********</span>
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
            <label>Password:</label>
            <input v-model="user.password" type="password" class="profile-input" />
          </div>
          <div class="button-group">
            <button class="action-btn save-btn" @click="saveChanges">Save</button>
            <button class="action-btn cancel-btn" @click="cancelEditing">Cancel</button>
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
    saveChanges() {
      if (this.validateForm()) {
        // Save logic here (removed localStorage for Claude compatibility)
        this.isEditing = false;
        console.log('Profile updated:', this.user);
      }
    },
    loadUserData() {
      // Load user data logic here
      this.user = {
        name: 'John Doe',
        email: 'user@example.com',
        address: '123 Main St',
        pincode: '12345',
        password: 'password123',
      };
    },
    validateForm() {
      if (!this.user.name || !this.user.email || !this.user.address || !this.user.pincode || !this.user.password) {
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
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e4f5 100%);
  padding: 15px;
}

/* Compact navbar styles to match the profile card width */
.page-container :deep(.us-nav),
.page-container :deep(nav),
.page-container :deep(.navbar) {
  position: relative !important;
  width: 120% !important;
  max-width: 520px !important;
  margin: 0 auto 15px auto !important;
  border-radius: 15px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
  top: 0 !important;
  left: auto !important;
  right: auto !important;
  transform: none !important;
  padding: 8px 20px !important;
  height: auto !important;
  min-height: 45px !important;
  max-height: 60px !important;
  box-sizing: border-box !important;
}

/* Compact navbar content */
.page-container :deep(.us-nav *),
.page-container :deep(nav *),
.page-container :deep(.navbar *) {
  font-size: 14px !important;
  padding: 6px 12px !important;
  line-height: 1.2 !important;
}

.page-container :deep(.us-nav .nav-brand),
.page-container :deep(nav .nav-brand),
.page-container :deep(.navbar .nav-brand) {
  font-size: 16px !important;
  font-weight: 600 !important;
  padding: 6px 8px !important;
}

.page-container :deep(.us-nav .nav-links),
.page-container :deep(nav .nav-links),
.page-container :deep(.navbar .nav-links) {
  gap: 15px !important;
}

.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
}

.profile-card {
  background: linear-gradient(90deg, #26a69a, #4dd0e1);
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 450px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.profile-card h2 {
  font-size: 26px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin-bottom: 25px;
  position: relative;
  z-index: 1;
}

.profile-card h2 i {
  margin-right: 10px;
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
  color: #e0f7fa;
}

.detail-group span {
  display: block;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #ffffff;
}

.profile-input {
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  box-sizing: border-box;
}

.profile-input:focus {
  outline: none;
  border-color: #e0f7fa;
  box-shadow: 0 0 8px rgba(224, 247, 250, 0.5);
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
  background-color: #4dd0e1;
  color: #ffffff;
  width: 100%;
}

.edit-btn:hover {
  background-color: #26a69a;
  transform: translateY(-2px);
}

.save-btn {
  background-color: #26a69a;
  color: #ffffff;
}

.save-btn:hover {
  background-color: #4dd0e1;
  transform: translateY(-2px);
}

.cancel-btn {
  background-color: #b2ebf2;
  color: #26a69a;
}

.cancel-btn:hover {
  background-color: #e0f7fa;
  transform: translateY(-2px);
}

.profile-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  z-index: 0;
  animation: rotate 15s linear infinite;
}

@keyframes rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .page-container {
    padding: 10px;
  }
  
  .profile-card {
    padding: 20px;
    max-width: 90%;
  }
  
  .profile-card h2 {
    font-size: 22px;
  }
  
  .button-group {
    flex-direction: column;
    gap: 15px;
  }
  
  .action-btn {
    width: 100%;
  }
  
  /* Even more compact navbar on mobile */
  .page-container :deep(.us-nav),
  .page-container :deep(nav),
  .page-container :deep(.navbar) {
    max-width: 90% !important;
    padding: 6px 15px !important;
    min-height: 40px !important;
    max-height: 50px !important;
  }
  
  .page-container :deep(.us-nav *),
  .page-container :deep(nav *),
  .page-container :deep(.navbar *) {
    font-size: 13px !important;
    padding: 4px 8px !important;
  }
}
</style>