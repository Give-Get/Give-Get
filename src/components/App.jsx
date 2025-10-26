import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import DonorMain from './DonorMain';
import InNeedMain from './InNeedMain';
import Landing from './Landing';
import OrganizationsPage from '../OrganizationsPage';
import DonorPage from './DonorPage';

/** Simple auth guard using localStorage flag 'auth' (replace with real auth) */
function RequireAuth({ children }) {
  const isAuth = !!localStorage.getItem('auth');
  return isAuth ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/app" element={<RequireAuth><DonorMain /></RequireAuth>} />
      <Route path="/get-help" element={<InNeedMain />} />
      <Route path="/register-organization" element={<OrganizationsPage />} />
      <Route path="/register-donor" element={<DonorPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
