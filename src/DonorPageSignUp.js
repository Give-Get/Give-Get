import React, { useState } from 'react';
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

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  const validatePhone = (phone) => /^\d{3}-\d{3}-\d{4}$/.test(phone);
  const validatePassword = (password) => password.length >= 8;

  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    console.log(`📝 Input changed → ${name}:`, value);

    setDonorData({
      ...donorData,
      [name]: value
    });

    if (errors[name]) {
      console.log(`🧹 Clearing error for ${name}`);
      setErrors({ ...errors, [name]: '' });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    console.log('🔍 Running validation...');

    if (!donorData.name.trim()) newErrors.name = 'Name is required';
    if (!donorData.email.trim()) newErrors.email = 'Email is required';
    else if (!validateEmail(donorData.email)) newErrors.email = 'Invalid email format';
    if (!donorData.phone_number.trim()) newErrors.phone_number = 'Phone number is required';
    else if (!validatePhone(donorData.phone_number)) newErrors.phone_number = 'Phone format should be XXX-XXX-XXXX';
    if (!donorData.address.trim()) newErrors.address = 'Address is required';
    if (!donorData.password) newErrors.password = 'Password is required';
    else if (!validatePassword(donorData.password)) newErrors.password = 'Password must be at least 8 characters';
    if (!donorData.confirmPassword) newErrors.confirmPassword = 'Please confirm your password';
    else if (donorData.password !== donorData.confirmPassword)
      newErrors.confirmPassword = 'Passwords do not match';

    if (Object.keys(newErrors).length > 0) {
      console.warn('⚠️ Validation errors found:', newErrors);
    } else {
      console.log('✅ Validation passed.');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 Form submitted.');

    if (!validateForm()) {
      console.warn('❌ Form validation failed. Aborting submission.');
      return;
    }

    console.log('🧱 Building payload for backend...');
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

    console.log('📦 Payload ready to send:', userPayload);

    try {
      console.log('🌐 Sending POST → http://localhost:8000/api/users/create');
      const response = await fetch("http://localhost:8000/api/users/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userPayload)
      });

      console.log('📬 Received response:', response.status, response.statusText);

      if (!response.ok) {
        const errText = await response.text();
        console.error('❌ Server error:', errText);
        throw new Error(`Server error: ${errText}`);
      }

      const result = await response.json();
      console.log('✅ Backend success:', result);

      setIsRegistered(true);
      console.log('🎉 Registration complete. UI updated.');
    } catch (error) {
      console.error('🚨 Error while sending to backend:', error);
      alert('⚠️ Could not connect to backend. Please try again later.');
    }
  };

  if (isRegistered) {
    console.log('🟢 Displaying success screen for new donor.');
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

  console.log('📋 Rendering registration form.');

  return (
    <div className="donor-page">
      <div className="donor-container">
        <header className="donor-header">
          <h1>Give and Get</h1>
          <p>Create your donor account to start making a difference</p>
        </header>

        <form onSubmit={handleSubmit} className="donor-form">
          <div className="form-group">
            <input
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
            <input
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
            <input
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
            <input
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
            <input
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
            <input
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
