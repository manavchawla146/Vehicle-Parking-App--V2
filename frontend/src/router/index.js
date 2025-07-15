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
  { path: '/us-dash', component: UserDashboard },
  { path: '/us-summary', component: SummaryPage },
  { path: '/ad-dash', component: AdminDashboard },
  { path: '/ad-users', component: AdminUsers },
  { path: '/ad-search', component: AdminSearch },
  { path: '/ad-summary', component: AdminSummary, meta: { requiresAuth: true, adminOnly: true } },
  { path: '/us-profile', component: UserProfile },
  { path: '/users', component: { template: '<div>Users Page (Placeholder)</div>' } },
  { path: '/search', component: { template: '<div>Search Page (Placeholder)</div>' } },
  { path: '/', redirect: '/login' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;