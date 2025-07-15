<template>
  <div class="page-container">
   
    <div class="container">
      <div class="form-box">
        <h2><i class="fas fa-parking"></i> User Login</h2>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label for="email">Registered Email ID</label>
            <input
              type="email"
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
          <button type="submit" class="submit-btn">Login</button>
        </form>
        <p class="redirect-text">
          Create Account?
          <router-link to="/signup" class="redirect-link">Sign Up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import usNav from './us-nav.vue';

export default {
  name: 'LoginPage',
  components: {
    'us-nav': usNav,
  },
  data() {
    return {
      email: '',
      password: '',
      errors: {
        email: '',
        password: '',
      },
    };
  },
  methods: {
    validateForm() {
      this.errors = { email: '', password: '' };
      let isValid = true;

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.email) {
        this.errors.email = 'Email is required';
        isValid = false;
      } else if (!emailRegex.test(this.email)) {
        this.errors.email = 'Please enter a valid email address';
        isValid = false;
      }

      if (!this.password) {
        this.errors.password = 'Password is required';
        isValid = false;
      } else if (this.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters long';
        isValid = false;
      }

      return isValid;
    },
    async handleLogin() {
      if (this.validateForm()) {
        try {
          const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: this.email, password: this.password })
          });
          const data = await response.json();
          if (response.ok) {
            if (data.role === 'admin') {
              this.$router.push('/ad-dash');
            } else {
            this.$router.push('/us-dash');
              }
          } else {
            this.errors.email = data.error || 'Login failed';
            this.errors.password = data.error || 'Login failed';
          }
        } catch (err) {
          this.errors.email = 'Server error';
          this.errors.password = 'Server error';
        }
      }
    },
    async logout() {
      await fetch('/api/logout', { method: 'POST' });
      this.$router.push('/login');
    }
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
  margin-bottom: 80px;
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

.input-field,
.submit-btn {
  width: 100%;
  box-sizing: border-box;
}
</style>