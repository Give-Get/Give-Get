import React, { useState } from 'react';
import '../App.css';

const DonorPage = () => {
  const [donorData, setDonorData] = useState({
    name: '',
    phone_number: '',
    email: '',
    address: '',
    password: '',
    confirmPassword: '',
    charity: false,
    shelter: false,
    donor: true
  });

  const [isRegistered, setIsRegistered] = useState(false);
  const [errors, setErrors] = useState({});

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone) => {
    const phoneRegex = /^\d{3}-\d{3}-\d{4}$/;
    return phoneRegex.test(phone);
  };

  const validatePassword = (password) => {
    return password.length >= 8;
  };

  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    setDonorData({
      ...donorData,
      [name]: value
    });

    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!donorData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!donorData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(donorData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!donorData.phone_number.trim()) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!validatePhone(donorData.phone_number)) {
      newErrors.phone_number = 'Phone format should be XXX-XXX-XXXX';
    }

    if (!donorData.address.trim()) {
      newErrors.address = 'Address is required';
    }

    if (!donorData.password) {
      newErrors.password = 'Password is required';
    } else if (!validatePassword(donorData.password)) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!donorData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (donorData.password !== donorData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const { confirmPassword, ...donorRegistration } = donorData;

    console.log('Donor Registration:', donorRegistration);

    // Here you would typically send this data to your backend
    // fetch('/api/register-donor', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(donorRegistration)
    // });

    setIsRegistered(true);
  };

  if (isRegistered) {
    return (
      <div className="App">
        <header className="site-header">
          <h1 className="brand">Give & Get</h1>
        </header>

        <main className="app-main d-flex align-items-center justify-content-center">
          <div className="login-card card shadow-sm">
            <div className="card-body text-center">
              <div style={{ fontSize: '4em', color: 'var(--bs-primary)', marginBottom: '1rem' }}>✓</div>
              <h3 className="card-title mb-3">Welcome to Give & Get!</h3>
              <p className="text-muted mb-4">Your donor account has been successfully created.</p>
              <div className="mb-4">
                <p className="mb-1"><strong>{donorData.name}</strong></p>
                <p className="mb-1 text-muted small">{donorData.email}</p>
                <p className="mb-0 text-muted small">{donorData.address}</p>
              </div>
              <button className="btn btn-primary w-100">
                Continue to Dashboard
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="site-header">
        <h1 className="brand">Give & Get</h1>
      </header>

      <main className="app-main d-flex align-items-center justify-content-center">
        <div className="login-card card shadow-sm">
          <div className="card-body">
            <h3 className="card-title mb-4">Create Donor Account</h3>

            <form onSubmit={handleSubmit}>
                <div className="row g-2 align-items-end">
              <div className="mb-1 col-6 col-md-6">
                <label className="form-label small">Full Name</label>
                <input
                  type="text"
                  className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                  name="name"
                  value={donorData.name}
                  onChange={handleDonorChange}
                  placeholder="John Doe"
                />
                {errors.name && <div className="invalid-feedback d-block">{errors.name}</div>}
              </div>

              <div className="mb-1 col-6 col-md-6">
                <label className="form-label small">Phone Number</label>
                <input
                  type="tel"
                  className={`form-control ${errors.phone_number ? 'is-invalid' : ''}`}
                  name="phone_number"
                  value={donorData.phone_number}
                  onChange={handleDonorChange}
                  placeholder="123-456-7890"
                />
                {errors.phone_number && <div className="invalid-feedback d-block">{errors.phone_number}</div>}
              </div>

              <div className="mb-1">
                <label className="form-label small">Email</label>
                <input
                  type="email"
                  className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                  name="email"
                  value={donorData.email}
                  onChange={handleDonorChange}
                  placeholder="you@example.com"
                />
                {errors.email && <div className="invalid-feedback d-block">{errors.email}</div>}
              </div>

              <div className="mb-1">
                <label className="form-label small">Address</label>
                <input
                  type="text"
                  className={`form-control ${errors.address ? 'is-invalid' : ''}`}
                  name="address"
                  value={donorData.address}
                  onChange={handleDonorChange}
                  placeholder="123 Main St, City, State ZIP"
                />
                {errors.address && <div className="invalid-feedback d-block">{errors.address}</div>}
              </div>

              <div className="mb-1">
                <label className="form-label small">Password</label>
                <input
                  type="password"
                  className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                  name="password"
                  value={donorData.password}
                  onChange={handleDonorChange}
                  placeholder="••••••••"
                />
                {errors.password && <div className="invalid-feedback d-block">{errors.password}</div>}
              </div>

              <div className="mb-4">
                <label className="form-label small">Confirm Password</label>
                <input
                  type="password"
                  className={`form-control ${errors.confirmPassword ? 'is-invalid' : ''}`}
                  name="confirmPassword"
                  value={donorData.confirmPassword}
                  onChange={handleDonorChange}
                  placeholder="••••••••"
                />
                {errors.confirmPassword && <div className="invalid-feedback d-block">{errors.confirmPassword}</div>}
              </div>
              </div>

              <button type="submit" className="btn btn-primary w-100">Sign Up</button>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DonorPage;
