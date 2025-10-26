import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../Landing.css';

export default function Landing() {
  const [aboutData, setAboutData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch about us data from backend
    fetch('http://localhost:8000/api/about')
      .then(res => res.json())
      .then(data => {
        setAboutData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching about data:', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="landing-loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header className="landing-hero">
        <div className="hero-content">
          <h1>Give & Get</h1>
          <p className="hero-tagline">
            Connecting generosity with need through smart matching
          </p>
          <div className="hero-buttons">
            <button 
              className="btn-hero btn-get-help"
            >
              Get Help
            </button>
            <button 
              className="btn-hero btn-give-help" 
              onClick={() => navigate('/login')}
            >
              Give Help
            </button>
          </div>
        </div>
      </header>

      {/* Mission Card */}
      <section className="landing-card mission-card">
        <div className="card-container">
          <div className="card-icon">🎯</div>
          <h2>Our Mission</h2>
          <p className="card-text">
            {aboutData?.mission?.description || 
            "Give and Get connects people in need with shelters and charities, while efficiently matching donors with organizations that need their contributions. We use smart matching algorithms to ensure resources reach those who need them most."}
          </p>
        </div>
      </section>

      {/* Core Values Card */}
      <section className="landing-card values-card">
        <div className="card-container">
          <div className="card-icon">💎</div>
          <h2>Our Core Values</h2>
          <div className="values-grid-landing">
            {aboutData?.values?.map((value, index) => (
              <div key={index} className="value-item">
                <div className="value-icon-small">{value.icon}</div>
                <div>
                  <h3>{value.title}</h3>
                  <p>{value.description}</p>
                </div>
              </div>
            )) || (
              <>
                <div className="value-item">
                  <div className="value-icon-small">🔍</div>
                  <div>
                    <h3>Transparency</h3>
                    <p>Every match comes with a detailed explanation of why it was made.</p>
                  </div>
                </div>
                <div className="value-item">
                  <div className="value-icon-small">⚙️</div>
                  <div>
                    <h3>Efficiency</h3>
                    <p>Smart algorithms ensure resources go where they're needed most.</p>
                  </div>
                </div>
                <div className="value-item">
                  <div className="value-icon-small">🌟</div>
                  <div>
                    <h3>Accessibility</h3>
                    <p>Easy-to-use platform that works for everyone.</p>
                  </div>
                </div>
                <div className="value-item">
                  <div className="value-icon-small">✅</div>
                  <div>
                    <h3>Verification</h3>
                    <p>All organizations are verified to ensure legitimacy.</p>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Contact Us Card */}
      <section className="landing-card contact-card">
        <div className="card-container">
          <div className="card-icon">📧</div>
          <h2>Contact Us</h2>
          <p className="card-text">
            {aboutData?.contact?.description || 
            "Want to partner with us or learn more about our mission?"}
          </p>
          <div className="contact-info-landing">
            <div className="contact-item-landing">
              <strong>Email:</strong>{' '}
              <a href={`mailto:${aboutData?.contact?.email || 'contact@giveandget.org'}`}>
                {aboutData?.contact?.email || 'contact@giveandget.org'}
              </a>
            </div>
            {aboutData?.contact?.social && (
              <div className="social-links-landing">
                {aboutData.contact.social.twitter && (
                  <a 
                    href={`https://twitter.com/${aboutData.contact.social.twitter.replace('@', '')}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="social-link"
                  >
                    Twitter
                  </a>
                )}
                {aboutData.contact.social.linkedin && (
                  <a 
                    href={`https://linkedin.com/company/${aboutData.contact.social.linkedin}`}
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="social-link"
                  >
                    LinkedIn
                  </a>
                )}
              </div>
            )}
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

