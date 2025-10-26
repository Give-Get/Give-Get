import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './Login';
import Main from './Main';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/main" element={<Main />} />
    </Routes>
  );
}
