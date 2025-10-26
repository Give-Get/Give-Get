import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Main from './Main';
<<<<<<< HEAD
import Landing from './Landing';
=======
import OrganizationsPage from '../OrganizationsPage';
>>>>>>> 1b95c8e19032d277ab340e13359cbb0dbfb96b77

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
<<<<<<< HEAD
      <Route path="/app" element={<RequireAuth><Main /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/" replace />} />
=======
      <Route path="/" element={<RequireAuth><Main /></RequireAuth>} />
      <Route path="/register-organization" element={<OrganizationsPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
>>>>>>> 1b95c8e19032d277ab340e13359cbb0dbfb96b77
    </Routes>
  );
}