<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <h2><i class="fas fa-parking"></i> Parking App</h2>
    </div>
    <div class="navbar-links">
      <router-link to="/us-dash" class="nav-link">Home</router-link>
      <router-link to="/us-summary" class="nav-link">Summary</router-link>
      <router-link to="/login" class="nav-link">Logout</router-link>
      <router-link to="/us-profile" class="profile-btn">
        <i class="fas fa-user"></i>
      </router-link>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'us-nav'
};
</script>

<style scoped>
@import url('../assets/base.css');

.navbar {
  background: linear-gradient(90deg, #26a69a, #4dd0e1);
  padding: 15px 30px;
  border-radius: 0;
  margin-bottom: 0;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.navbar-brand {
  text-align: left;
  margin-bottom: 0;
}

.navbar-brand h2 {
  color: #ffffff;
  font-size: 18px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin: 0;
}

.navbar-brand i {
  margin-right: 8px;
}

.navbar-links {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-size: 14px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin: 0;
  padding: 8px 16px;
  border-radius: 5px;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.nav-link:hover {
  color: #e0f7fa;
  background-color: rgba(255, 255, 255, 0.2);
}

.profile-btn {
  color: #ffffff;
  text-decoration: none;
  font-size: 20px;
  margin-left: 10px;
  padding: 8px 12px;
  border-radius: 5px;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.profile-btn:hover {
  color: #e0f7fa;
  background-color: rgba(255, 255, 255, 0.2);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .navbar {
    padding: 10px 20px;
    flex-direction: column;
    gap: 10px;
  }
  
  .navbar-brand {
    margin-bottom: 0;
  }
  
  .navbar-links {
    flex-direction: row;
    gap: 10px;
  }
  
  .nav-link {
    font-size: 12px;
    padding: 6px 12px;
  }
  
  .profile-btn {
    font-size: 18px;
    padding: 6px 10px;
  }
}
</style>