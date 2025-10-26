import React, { useState, useEffect } from 'react';
import './DonorPage.css';

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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // 🧭 Page startup
  useEffect(() => {
    console.log('%c📄 Donor Registration Page Loaded', 'color: dodgerblue; font-weight: bold;');
  }, []);

  // --- Validation helpers ---
  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validatePhone = (phone) => /^\d{3}-\d{3}-\d{4}$/.test(phone);
  const validatePassword = (password) => password.length >= 8;

  // --- Input change handler ---
  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    console.log(`✏️ Input changed → ${name}:`, value);
    setDonorData({ ...donorData, [name]: value });

    if (errors[name]) setErrors({ ...errors, [name]: '' });
  };

  // --- Validate form ---
  const validateForm = () => {
    const newErrors = {};

    if (!donorData.name.trim()) newErrors.name = 'Name is required';
    if (!donorData.email.trim()) newErrors.email = 'Email is required';
    else if (!validateEmail(donorData.email)) newErrors.email = 'Invalid email format';

    if (!donorData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
    else if (!validatePhone(donorData.phone_number))
      newErrors.phone_number = 'Phone format should be XXX-XXX-XXXX';

    if (!donorData.address.trim()) newErrors.address = 'Address is required';

    if (!donorData.password) newErrors.password = 'Password is required';
    else if (!validatePassword(donorData.password))
      newErrors.password = 'Password must be at least 8 characters';

    if (!donorData.confirmPassword)
      newErrors.confirmPassword = 'Please confirm your password';
    else if (donorData.password !== donorData.confirmPassword)
      newErrors.confirmPassword = 'Passwords do not match';

    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      console.error('%c❌ Validation errors:', 'color: crimson; font-weight: bold;', newErrors);
    }

    return Object.keys(newErrors).length === 0;
  };

  // --- Submit handler ---
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('%c🚀 Form submitted', 'color: green; font-weight: bold;');

    if (!validateForm()) {
      console.warn('⚠️ Form validation failed.');
      return;
    }

    const userPayload = {
      name: donorData.name,
      phone_number: donorData.phone_number,
      email: donorData.email,
      address: donorData.address,
      password: donorData.password,
      charity: donorData.charity,
      shelter: donorData.shelter,
      donor: donorData.donor
    };

    console.log('%c🌐 Sending POST → /api/user/create', 'color: orange; font-weight: bold;', userPayload);

    try {
      const response = await fetch('https://give-get.onrender.com/api/user/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userPayload)
      });

      console.log('📡 Response status:', response.status);

      const result = await response.json();
      console.log('%c📦 Backend Response:', 'color: teal; font-weight: bold;', result);

      if (response.ok && result.status === 'success') {
        console.log('%c✅ Donor successfully registered', 'color: limegreen; font-weight: bold;');
        setIsRegistered(true);
      } else {
        console.error('%c❌ Backend error:', 'color: red; font-weight: bold;', result);
        alert('Registration failed: ' + (result.message || 'Unknown error'));
      }
    } catch (err) {
      console.error('%c🔥 Network / Fetch error:', 'color: red; font-weight: bold;', err);
      alert('Could not connect to backend. Please try again later.');
    }
  };

  // --- Success Page ---
  if (isRegistered) {
    console.log('%c🎉 Registration Success Page Rendered', 'color: green; font-weight: bold;');
    return (
      <div className="donor-page">
        <div className="success-container">
          <div className="success-icon">✓</div>
          <h2>Welcome to Give and Get!</h2>
          <p className="success-subtext">Your donor account has been successfully created.</p>
          <div className="registration-summary">
            <p><strong>{donorData.name}</strong></p>
            <p>{donorData.email}</p>
            <p>{donorData.address}</p>
          </div>
          <button
            className="btn-primary btn-full"
            onClick={() => {
              console.log('%c➡️ Navigating to dashboard...', 'color: dodgerblue;');
              window.location.href = '/dashboard';
            }}
          >
            Continue to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // --- Form Page ---
  return (
    <div className="donor-page">
      <div className="donor-container">
        <header className="donor-header">
          <h1>Give and Get</h1>
          <p>Create your donor account to start making a difference</p>
        </header>

        <form onSubmit={handleSubmit} className="donor-form">
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              autoComplete="name"
              type="text"
              id="name"
              name="name"
              value={donorData.name}
              onChange={handleDonorChange}
              className={errors.name ? 'error' : ''}
              placeholder="Full Name"
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              autoComplete="email"
              type="email"
              id="email"
              name="email"
              value={donorData.email}
              onChange={handleDonorChange}
              className={errors.email ? 'error' : ''}
              placeholder="Email"
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Phone Number</label>
            <input
              autoComplete="tel"
              type="tel"
              id="phone_number"
              name="phone_number"
              value={donorData.phone_number}
              onChange={handleDonorChange}
              className={errors.phone_number ? 'error' : ''}
              placeholder="Phone Number (123-456-7890)"
            />
            {errors.phone_number && <span className="error-message">{errors.phone_number}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="address">Street Address</label>
            <input
              autoComplete="street-address"
              type="text"
              id="address"
              name="address"
              value={donorData.address}
              onChange={handleDonorChange}
              className={errors.address ? 'error' : ''}
              placeholder="Street Address"
            />
            {errors.address && <span className="error-message">{errors.address}</span>}
          </div>

          <div className="form-group password-group">
            <label htmlFor="password">Password</label>
            <input
              autoComplete="new-password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={donorData.password}
              onChange={handleDonorChange}
              className={errors.password ? 'error' : ''}
              placeholder="Password"
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <div className="form-group password-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              autoComplete="new-password"
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={donorData.confirmPassword}
              onChange={handleDonorChange}
              className={errors.confirmPassword ? 'error' : ''}
              placeholder="Confirm Password"
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? 'Hide' : 'Show'}
            </button>
            {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
          </div>

          <button type="submit" className="btn-primary btn-full">
            Sign Up
          </button>

          <p className="login-link">
            Already have an account? <a href="/login">Log in</a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default DonorPage;
