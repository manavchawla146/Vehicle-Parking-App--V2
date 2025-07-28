import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../components/login.vue';
import SignupPage from '../components/signup.vue';
import UserDashboard from '../components/us-dash.vue';
import SummaryPage from '../components/us-summary.vue';
import AdminDashboard from '../components/ad-dash.vue';
import AdminSummary from '../components/ad-summary.vue';
import AdminSearch from '../components/ad-search.vue';
import AdminUsers from '../components/ad-users.vue';
import UserProfile from '../components/us-profile.vue';

const routes = [
  { path: '/login', component: LoginPage },
  { path: '/signup', component: SignupPage },
  { path: '/us-dash', component: UserDashboard, meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/us-summary', component: SummaryPage, meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/ad-dash', component: AdminDashboard, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/ad-users', component: AdminUsers, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/ad-search', component: AdminSearch, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/ad-summary', component: AdminSummary, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/us-profile', component: UserProfile, meta: { requiresAuth: true, roles: ['user'] } },
  { path: '/users', component: { template: '<div>Users Page (Placeholder)</div>' } },
  { path: '/search', component: { template: '<div>Search Page (Placeholder)</div>' } },
  { path: '/', redirect: '/login' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const isProtected = to.meta.requiresAuth;
  if (isProtected || to.path.startsWith('/ad-') || to.path.startsWith('/us-')) {
    try {
      const res = await fetch('/api/session', { credentials: 'include' });
      const data = await res.json();
      if (res.ok && data.logged_in) {
        const userRole = data.role;
        const allowedRoles = to.meta.roles || [];
        if (allowedRoles.length === 0 || allowedRoles.includes(userRole)) {
          next();
        } else if (userRole === 'admin') {
          next('/ad-dash');
        } else if (userRole === 'user') {
          next('/us-dash');
        } else {
          next('/login');
        }
      } else {
        next('/login');
      }
    } catch (error) {
      console.error('Session check failed:', error);
      next('/login');
    }
  } else {
    next();
  }
});

export default router;
