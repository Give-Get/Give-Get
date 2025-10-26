import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Main from './Main';
import OrganizationsPage from '../OrganizationsPage';

/** Simple auth guard using localStorage flag 'auth' (replace with real auth) */
function RequireAuth({ children }) {
  const isAuth = !!localStorage.getItem('auth');
  return isAuth ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RequireAuth><Main /></RequireAuth>} />
      <Route path="/register-organization" element={<OrganizationsPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}