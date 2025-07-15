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
.navbar {
  background: linear-gradient(90deg, #26a69a, #4dd0e1);
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  text-align: center;
  margin-bottom: 10px;
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
  flex-direction: column;
  align-items: center;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-size: 14px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  margin: 5px 0;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.nav-link:hover {
  color: #e0f7fa;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  padding: 5px 10px;
}

.profile-btn {
  color: #ffffff;
  text-decoration: none;
  font-size: 20px;
  margin-left: 10px;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.profile-btn:hover {
  color: #e0f7fa;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  padding: 5px 10px;
}

/* Responsive adjustments */
@media (min-width: 601px) {
  .navbar {
    flex-direction: row;
    justify-content: space-between;
  }
  .navbar-brand {
    margin-bottom: 0;
  }
  .navbar-links {
    flex-direction: row;
  }
  .nav-link {
    margin: 0 15px;
  }
  .profile-btn {
    margin-left: 15px;
  }
}
</style>