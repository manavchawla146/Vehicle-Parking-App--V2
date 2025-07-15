<template>
  <div class="page-container">
    
    <div class="container">
      <div class="form-box">
        <h2><i class="fas fa-parking"></i> User Signup</h2>
        <form @submit.prevent="handleSignup">
          <div class="form-group">
            <label for="email">Email ID/Username</label>
            <input
              type="text"
              id="email"
              v-model="email"
              class="input-field"
              required
            />
            <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input
              type="password"
              id="password"
              v-model="password"
              class="input-field"
              required
            />
            <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
          </div>
          <div class="form-group">
            <label for="fullname">Fullname</label>
            <input
              type="text"
              id="fullname"
              v-model="fullname"
              class="input-field"
              required
            />
            <p v-if="errors.fullname" class="error-text">{{ errors.fullname }}</p>
          </div>
          <div class="form-group">
            <label for="address">Address</label>
            <input
              type="text"
              id="address"
              v-model="address"
              class="input-field"
              required
            />
            <p v-if="errors.address" class="error-text">{{ errors.address }}</p>
          </div>
          <div class="form-group">
            <label for="pincode">Pin Code</label>
            <input
              type="text"
              id="pincode"
              v-model="pincode"
              class="input-field"
              required
            />
            <p v-if="errors.pincode" class="error-text">{{ errors.pincode }}</p>
          </div>
          <button type="submit" class="submit-btn">Register</button>
        </form>
        <p class="redirect-text">
          Already have an account?
          <router-link to="/login" class="redirect-link">Login here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import usNav from './us-nav.vue';

export default {
  name: 'SignupPage',
  components: {
    'us-nav': usNav,
  },
  data() {
    return {
      email: '',
      password: '',
      fullname: '',
      address: '',
      pincode: '',
      errors: {
        email: '',
        password: '',
        fullname: '',
        address: '',
        pincode: '',
      },
    };
  },
  methods: {
    validateForm() {
      this.errors = { email: '', password: '', fullname: '', address: '', pincode: '' };
      let isValid = true;

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.email) {
        this.errors.email = 'Email ID/Username is required';
        isValid = false;
      } else if (!emailRegex.test(this.email)) {
        this.errors.email = 'Please enter a valid email address (e.g., user@gmail.com)';
        isValid = false;
      }

      if (!this.password) {
        this.errors.password = 'Password is required';
        isValid = false;
      } else if (this.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters long';
        isValid = false;
      }

      if (!this.fullname) {
        this.errors.fullname = 'Fullname is required';
        isValid = false;
      }

      if (!this.address) {
        this.errors.address = 'Address is required';
        isValid = false;
      }

      const pincodeRegex = /^\d{5,6}$/;
      if (!this.pincode) {
        this.errors.pincode = 'Pin Code is required';
        isValid = false;
      } else if (!pincodeRegex.test(this.pincode)) {
        this.errors.pincode = 'Pin Code must be a 5-6 digit number';
        isValid = false;
      }

      return isValid;
    },
    handleSignup() {
      if (this.validateForm()) {
        localStorage.setItem('userEmail', this.email);
        localStorage.setItem('userPassword', this.password);
        localStorage.setItem('userName', this.fullname);
        localStorage.setItem('userAddress', this.address);
        localStorage.setItem('userPincode', this.pincode);
        console.log('Signup successful with:', this.email, this.password, this.fullname, this.address, this.pincode);
        this.$router.push('/us-dash');
      }
    },
  },
};
</script>

<style>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #d9e4f5 100%);
}

.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 60px); /* Adjust for navbar height */
  padding-top: 60px;
}

.form-box {
  background: linear-gradient(90deg, #26a69a, #4dd0e1);
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  text-align: center;
  color: white;
}

.form-box h2 {
  font-size: 26px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin-bottom: 25px;
}

.form-box h2 i {
  margin-right: 10px;
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  display: block;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin-bottom: 8px;
  color: #e0f7fa;
}

.input-field {
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #e0f7fa;
  box-shadow: 0 0 8px rgba(224, 247, 250, 0.5);
}

.error-text {
  color: #ff4444;
  font-size: 12px;
  margin-top: 5px;
  text-align: left;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #26a69a;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  color: #ffffff;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.submit-btn:hover {
  background-color: #4dd0e1;
  transform: translateY(-2px);
}

.redirect-text {
  font-size: 14px;
  margin-top: 15px;
  color: #e0f7fa;
}

.redirect-link {
  color: #ffffff;
  text-decoration: none;
  font-weight: 500;
}

.redirect-link:hover {
  color: #b2ebf2;
  text-decoration: underline;
}

@media (max-width: 600px) {
  .form-box {
    padding: 20px;
    max-width: 90%;
  }
  .form-box h2 {
    font-size: 22px;
  }
}
</style>