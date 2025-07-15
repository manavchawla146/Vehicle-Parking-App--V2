<template>
  <nav class="admin-nav">
    <div class="nav-header">
      <span class="welcome-text">Welcome to Admin</span>
      <button class="menu-toggle" @click="toggleMenu">
        <span></span><span></span><span></span>
      </button>
    </div>
    <ul :class="{ 'show-menu': isMenuOpen }">
      <li><router-link to="/ad-dash" class="nav-link">Home</router-link></li>
      <li><router-link to="/ad-users" class="nav-link">Users</router-link></li>
      <li><router-link to="/ad-search" class="nav-link">Search</router-link></li>
      <li><router-link to="/ad-summary" class="nav-link">Summary</router-link></li>
      <li><router-link to="/login" class="nav-link">Logout</router-link></li>
    </ul>
  </nav>
</template>

<script>
export default {
  data() {
    return { isMenuOpen: false };
  },
  methods: {
    toggleMenu() { 
      this.isMenuOpen = !this.isMenuOpen;
    }
  }
}
</script>

<style>
.admin-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  padding: 1rem;
  background: #2c3e50;
  color: white;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}

.menu-toggle span {
  display: block;
  width: 25px;
  height: 3px;
  background: white;
  margin: 5px 0;
}

ul {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  width: 100%;
}

li {
  margin: 0 0.5rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  display: block;
}

.nav-link:hover {
  text-decoration: underline;
  color: #1abc9c;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }
  
  ul {
    display: none;
    flex-direction: column;
    width: 100%;
    text-align: center;
  }
  
  ul.show-menu {
    display: flex;
  }
  
  li {
    margin: 0.5rem 0;
  }
}
</style>