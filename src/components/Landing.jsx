import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../Landing.css';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header 
        className="landing-hero"
        style={{
          background: `
            linear-gradient(135deg, rgba(246, 248, 251, 0.85) 0%, rgba(255, 255, 255, 0.85) 100%),
            url(${process.env.PUBLIC_URL}/assets/imgs/hero-background.jpg) center/cover no-repeat
          `
        }}
      >
        <div className="hero-content">
          <h1>Give & Get</h1>
          <p className="hero-tagline">
            Connecting generosity with need through smart matching
          </p>
          <div className="hero-buttons">
            <button 
              className="btn-hero btn-primary-action"
              onClick={() => navigate('/get-help')}
            >
              Get Help
            </button>
            <button 
              className="btn-hero btn-primary-action" 
              onClick={() => navigate('/login')}
            >
              Give Help
            </button>
          </div>
        </div>
      </header>

      {/* Mission Card */}
      <section className="landing-card mission-card">
        <div className="mission-content">
          <div className="mission-text-card">
            <h2>
              <svg width="40" height="40" viewBox="0 -1 32 32" xmlns="http://www.w3.org/2000/svg" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '12px' }}>
                <path d="M126,882 C122.667,882 119.982,883.842 117.969,886.235 C116.013,883.76 113.333,882 110,882 C105.306,882 102,886.036 102,890.438 C102,892.799 102.967,894.499 104.026,896.097 L116.459,911.003 C117.854,912.312 118.118,912.312 119.513,911.003 L131.974,896.097 C133.22,894.499 134,892.799 134,890.438 C134,886.036 130.694,882 126,882" fill="#2ee079" transform="translate(-102, -882)" />
              </svg>
              Our Mission
            </h2>
            <p className="card-text">
              Give and Get connects people in need with shelters and charities, while efficiently matching donors with organizations that need their contributions. We use smart matching algorithms to ensure resources reach those who need them most.
            </p>
          </div>
          <div className="mission-image-card">
            <img src="/assets/imgs/mission_image.jpg" alt="Our Mission" />
          </div>
        </div>
      </section>

      {/* Core Values Card */}
      <section className="landing-card values-card">
        <div className="values-content">
          <div className="values-image-card">
            <img src="/assets/imgs/papaioannou-kostas-tysecUm5HJA-unsplash.jpg" alt="Our Core Values" />
          </div>
          <div className="values-text-card">
            <h2>
              <svg width="40" height="40" viewBox="0 0 360 360" xmlns="http://www.w3.org/2000/svg" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: '12px' }}>
                <path d="M289.879,21.713H70.121C25.785,21.713,0,53.106,0,91.833c0,38.725,31.391,70.122,70.121,70.122c4.133,0,8.175-0.383,12.111-1.071c12.633-3.485,21.939-15.072,21.939-28.799c0-16.479-13.404-29.884-29.883-29.884V82.923c27.108,0,49.16,22.055,49.16,49.162c0,21.877-14.367,40.442-34.159,46.798v159.405h42.999v-101.02c0-7.588,6.149-13.74,13.737-13.74c7.583,0,13.731,6.152,13.731,13.74v101.02h40.484v-101.02c0-7.588,6.148-13.74,13.732-13.74c7.587,0,13.736,6.152,13.736,13.74v101.02h42.999V178.979c-20.262-6.071-35.073-24.876-35.073-47.089c0-27.107,22.053-49.16,49.159-49.16v19.28c-16.478,0-29.88,13.404-29.88,29.88c0,13.99,9.663,25.761,22.665,28.993v-0.027c3.993,0.708,8.101,1.098,12.298,1.098c38.73,0,70.121-31.397,70.121-70.122C360,53.106,334.215,21.713,289.879,21.713z" fill="#2ee079" />
              </svg>
              Our Core Values
            </h2>
            <div className="values-list">
              <div className="value-item">
                <h3>Transparency</h3>
                <p>Every match comes with a detailed explanation of why it was made.</p>
              </div>
              <div className="value-item">
                <h3>Efficiency</h3>
                <p>Smart algorithms ensure resources go where they're needed most.</p>
              </div>
              <div className="value-item">
                <h3>Accessibility</h3>
                <p>Easy-to-use platform that works for everyone.</p>
              </div>
              <div className="value-item">
                <h3>Verification</h3>
                <p>All organizations are verified to ensure legitimacy.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Us Card */}
      <section className="landing-card contact-card">
        <div className="contact-container">
          <h2 className="contact-title">Contact Information</h2>
          
          <p className="contact-description">
            Reach out for partnerships, questions, or to learn more about our mission.
          </p>

          <div className="contact-items">
            <div className="contact-item-new">
              <div className="contact-icon instagram-icon">
                <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </div>
              <span className="contact-text">
                @_giveandget
              </span>
            </div>

            <div className="contact-item-new">
              <div className="contact-icon email-icon">
                <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                  <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
              </div>
              <span className="contact-text">
              giveandgetcontact@gmail.com              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Card */}
      <section className="landing-card cta-card">
        <div className="card-container">
          <h2>Ready to Make a Difference?</h2>
          <p className="cta-text">
            Join our community of givers and receivers making an impact every day.
          </p>
          <button 
            className="btn-cta-large" 
            onClick={() => navigate('/login')}
          >
            Start Helping Today
          </button>
        </div>
      </section>
    </div>
  );
}

