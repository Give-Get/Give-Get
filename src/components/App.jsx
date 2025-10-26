import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Main from './Main';
import Landing from './Landing';

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
      <Route path="/app" element={<RequireAuth><Main /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}