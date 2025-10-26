import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

export default function Login() {
  const [type, setType] = useState('individual');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    // TODO: replace with real authentication call
    // On successful login:
    localStorage.setItem('auth', '1'); // simple flag for RequireAuth
    navigate('/app', { replace: true }); // go to authenticated app
  }

  return (
    <div className="App">
      <header className="site-header">
        <h1 className="brand">Give & Get</h1>
      </header>

      <main className="app-main d-flex align-items-center justify-content-center">
        <div className="login-card card shadow-sm">
          <div className="card-body">
            <h3 className="card-title mb-4">Login</h3>

            <div className="user-type btn-group mb-3" role="group">
              <button
                type="button"
                className={`btn ${type === 'individual' ? 'btn-primary' : 'btn-outline-secondary'}`}
                onClick={() => setType('individual')}
              >
                Individual
              </button>
              <button
                type="button"
                className={`btn ${type === 'center' ? 'btn-primary' : 'btn-outline-secondary'}`}
                onClick={() => setType('center')}
              >
                Center
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label small">Email</label>
                <input type="email" className="form-control" value={email}
                       onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" />
              </div>

              <div className="mb-3">
                <label className="form-label small">Password</label>
                <input type="password" className="form-control" value={password}
                       onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
              </div>

              <div className="d-flex justify-content-between align-items-center">
                <button type="submit" className="btn btn-primary">Sign in</button>
                <a className="text-muted small" href="#forgot">Forgot?</a>
              </div>
            </form>
          </div>

          <div className="card-footer text-center small text-muted">
            Signing in as <strong>{type === 'individual' ? 'Individual' : 'Center'}</strong>
          </div>
        </div>
      </main>
    </div>
  );
}