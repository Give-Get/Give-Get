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

  // 🪩 Log when the page first mounts
  useEffect(() => {
    console.groupCollapsed('🟢 DonorPage Initialized');
    console.log('🕐 Component mounted at:', new Date().toLocaleTimeString());
    console.log('📄 Initial donorData:', donorData);
    console.groupEnd();
  }, []);

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validatePhone = (phone) => /^\d{3}-\d{3}-\d{4}$/.test(phone);
  const validatePassword = (password) => password.length >= 8;

  // Handle field changes
  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    console.groupCollapsed(`✏️ Input Change Detected`);
    console.log(`📍 Field: ${name}`);
    console.log(`➡️ New Value:`, value);
    console.groupEnd();

    setDonorData((prev) => ({
      ...prev,
      [name]: value
    }));

    if (errors[name]) {
      console.log(`🧹 Clearing previous error for "${name}"`);
      setErrors({ ...errors, [name]: '' });
    }
  };

  // Validation logic
  const validateForm = () => {
    console.group('🔍 Form Validation');
    const newErrors = {};

    if (!donorData.name.trim()) newErrors.name = 'Name is required';
    if (!donorData.email.trim()) newErrors.email = 'Email is required';
    else if (!validateEmail(donorData.email)) newErrors.email = 'Invalid email format';
    if (!donorData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
    else if (!validatePhone(donorData.phone_number)) newErrors.phone_number = 'Format must be XXX-XXX-XXXX';
    if (!donorData.address.trim()) newErrors.address = 'Address is required';
    if (!donorData.password) newErrors.password = 'Password is required';
    else if (!validatePassword(donorData.password)) newErrors.password = 'Must be ≥ 8 characters';
    if (!donorData.confirmPassword) newErrors.confirmPassword = 'Please confirm password';
    else if (donorData.password !== donorData.confirmPassword)
      newErrors.confirmPassword = 'Passwords do not match';

    if (Object.keys(newErrors).length > 0) {
      console.warn('❌ Validation failed with errors:', newErrors);
    } else {
      console.log('✅ Validation passed!');
    }

    console.groupEnd();
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Submit handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.group('🚀 Form Submission');
    console.log('🧾 Current donorData before validation:', donorData);

    if (!validateForm()) {
      console.warn('🛑 Submission halted due to validation errors.');
      console.groupEnd();
      return;
    }

    const { confirmPassword, address, ...formData } = donorData;
    const userPayload = {
      _id: "0",
      name: formData.name || "",
      charity: false,
      shelter: false,
      donor: true,
      phone_number: formData.phone_number,
      email: formData.email,
      password: formData.password
    };

    console.log('📦 Payload ready for backend:', userPayload);

    try {
      console.log('🌐 Sending POST → http://localhost:5000/api/user/create');
      const response = await fetch("http://localhost:5000/api/user/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userPayload)
      });

      console.log('📬 Response status:', response.status, response.statusText);

      if (!response.ok) {
        const errText = await response.text();
        console.error('❌ Server error response:', errText);
        throw new Error(`Server error: ${errText}`);
      }

      const result = await response.json();
      console.groupCollapsed('✅ Backend Success');
      console.log('🧠 API Result:', result);
      console.groupEnd();

      setIsRegistered(true);
      console.log('🎉 User successfully registered → Updating UI.');
    } catch (error) {
      console.error('🚨 Error during submission:', error);
      alert('⚠️ Could not connect to backend. Please try again later.');
    }

    console.groupEnd();
  };

  if (isRegistered) {
    console.groupCollapsed('🟢 Registration Complete');
    console.log('👤 Registered User:', donorData.name);
    console.log('📧 Email:', donorData.email);
    console.log('🏠 Address:', donorData.address);
    console.groupEnd();

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
          <button className="btn-primary btn-full">
            Continue to Dashboard
          </button>
        </div>
      </div>
    );
  }

  console.log('🧭 Rendering registration form...');

  return (
    <div className="donor-page">
      <div className="donor-container">
        <header className="donor-header">
          <h1>Give and Get</h1>
          <p>Create your donor account to start making a difference</p>
        </header>

        <form onSubmit={handleSubmit} className="donor-form" autoComplete="on">
          {/* FULL NAME */}
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={donorData.name}
              onChange={handleDonorChange}
              className={errors.name ? 'error' : ''}
              placeholder="Full Name"
              autoComplete="name"
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          {/* EMAIL */}
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={donorData.email}
              onChange={handleDonorChange}
              className={errors.email ? 'error' : ''}
              placeholder="Email"
              autoComplete="email"
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          {/* PHONE */}
          <div className="form-group">
            <label htmlFor="phone_number">Phone Number</label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={donorData.phone_number}
              onChange={handleDonorChange}
              className={errors.phone_number ? 'error' : ''}
              placeholder="Phone (123-456-7890)"
              autoComplete="tel"
            />
            {errors.phone_number && <span className="error-message">{errors.phone_number}</span>}
          </div>

          {/* ADDRESS */}
          <div className="form-group">
            <label htmlFor="address">Address</label>
            <input
              type="text"
              id="address"
              name="address"
              value={donorData.address}
              onChange={handleDonorChange}
              className={errors.address ? 'error' : ''}
              placeholder="Street Address"
              autoComplete="address-line1"
            />
            {errors.address && <span className="error-message">{errors.address}</span>}
          </div>

          {/* PASSWORD */}
          <div className="form-group password-group">
            <label htmlFor="password">Password</label>
            <input
              type={showPassword ? 'text' : 'password'}
              id="password"
              name="password"
              value={donorData.password}
              onChange={handleDonorChange}
              className={errors.password ? 'error' : ''}
              placeholder="Password"
              autoComplete="new-password"
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => {
                console.log(`👁️ Password visibility toggled → ${!showPassword ? 'Visible' : 'Hidden'}`);
                setShowPassword(!showPassword);
              }}
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          {/* CONFIRM PASSWORD */}
          <div className="form-group password-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              name="confirmPassword"
              value={donorData.confirmPassword}
              onChange={handleDonorChange}
              className={errors.confirmPassword ? 'error' : ''}
              placeholder="Confirm Password"
              autoComplete="new-password"
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => {
                console.log(`👁️ Confirm Password visibility toggled → ${!showConfirmPassword ? 'Visible' : 'Hidden'}`);
                setShowConfirmPassword(!showConfirmPassword);
              }}
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
