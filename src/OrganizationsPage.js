import React, { useState } from 'react';
import './OrganizationsPage.css';

// ✅ Base organization JSON structure (mirrors MongoDB + backend OrganizationModel)
const baseOrgTemplate = {
  _id: "0",
  image_url: "",
  type: { shelter: false, charity: false },
  EIN: "",
  name: "",
  address: "",
  location: { lat: 0, lng: 0 },
  ammenities: {
    accessible: false,
    lgbtq_only: false,
    male_only: false,
    female_only: false,
    all_gender: false,
    pet_friendly: false,
    languages: ["english"],
    family_rooming: false,
    beds_available: 0,
    medical_support: false,
    counseling_support: false,
    fees: 0,
    age_minimum: 0,
    age_maximum: 0,
    veteran_only: false,
    immigrant_only: false,
    refugee_only: false,
    good_criminal_record_standing: false,
    sobriety_required: false,
    showers: false,
    id_required: false
  },
  needs: {},
  hours: {
    monday: "0000-2359",
    tuesday: "0000-2359",
    wednesday: "0000-2359",
    thursday: "0000-2359",
    friday: "0000-2359",
    saturday: "0000-2359",
    sunday: "0000-2359"
  },
  description: "",
  contact: {
    phone: "",
    email: "",
    website: ""
  },
  verified: false,
  timestamp: ""
};

function OrganizationsPage() {
  const [organization, setOrganization] = useState(baseOrgTemplate);
  const [organizations, setOrganizations] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // Determine if field belongs to nested object
    if (name in organization.ammenities) {
      setOrganization({
        ...organization,
        ammenities: {
          ...organization.ammenities,
          [name]: type === 'checkbox' ? checked : value
        }
      });
    } else if (name in organization.contact) {
      setOrganization({
        ...organization,
        contact: { ...organization.contact, [name]: value }
      });
    } else if (name in organization.hours) {
      setOrganization({
        ...organization,
        hours: { ...organization.hours, [name]: value || "0000-2359" }
      });
    } else {
      setOrganization({
        ...organization,
        [name]: type === 'checkbox' ? checked : value
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate org type
    if (!organization.type.shelter && !organization.type.charity) {
      alert('Please select at least one organization type (Shelter or Charity)');
      return;
    }

    // Normalize languages (comma-separated input)
    if (typeof organization.ammenities.languages === "string") {
      organization.ammenities.languages = organization.ammenities.languages
        ? organization.ammenities.languages.split(',').map(lang => lang.trim())
        : ['english'];
    }

    // Timestamp
    const updatedOrg = { ...organization, timestamp: new Date().toISOString() };

    try {
      // ✅ Call validation API (not create)
      const response = await fetch('http://localhost:8000/api/org/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedOrg)
      });

      const result = await response.json();

      if (result.success) {
        const verifiedOrg = {
          ...updatedOrg,
          verified: result.verification_status.verified,
          trust_score: result.verification_status.trust_score,
          trust_level: result.verification_status.trust_level
        };

        setOrganizations([...organizations, verifiedOrg]);

        alert(
          `✅ Organization validated successfully!\n\n` +
          `Organization ID: ${result.organization_id}\n` +
          `Verification Status: ${result.verification_status.status}\n` +
          `Trust Score: ${result.verification_status.trust_score}/100\n` +
          `Trust Level: ${result.verification_status.trust_level}\n` +
          `Verified: ${result.verification_status.verified ? 'Yes' : 'No'}\n\n` +
          `${result.verification_status.status === 'pending_review' ?
            'Your organization will be reviewed by an administrator.' :
            result.verification_status.verified ?
            'Your organization has been verified and approved!' :
            'Your organization has been approved but requires additional verification.'}`
        );
      } else {
        alert('❌ Validation Error: ' + (result.message || 'Unknown error'));
      }

    } catch (error) {
      console.error('Backend error:', error);
      alert(
        '⚠️ Could not connect to backend validator.\n\n' +
        'Please make sure FastAPI is running:\n' +
        'uvicorn api:app --reload'
      );
    }

    // Reset form to base template
    setOrganization(baseOrgTemplate);
  };

  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <p className="subtitle">Complete ALL fields below to register your organization</p>

      {/* FORM */}
      <form onSubmit={handleSubmit} className="org-form">
        <fieldset>
          <legend>Organization Type *</legend>
          <label>
            <input
              type="checkbox"
              name="shelter"
              checked={organization.type.shelter}
              onChange={(e) =>
                setOrganization({
                  ...organization,
                  type: { ...organization.type, shelter: e.target.checked }
                })
              }
            />
            Shelter
          </label>
          <label>
            <input
              type="checkbox"
              name="charity"
              checked={organization.type.charity}
              onChange={(e) =>
                setOrganization({
                  ...organization,
                  type: { ...organization.type, charity: e.target.checked }
                })
              }
            />
            Charity
          </label>
        </fieldset>

        <fieldset>
          <legend>Basic Information</legend>
          <input
            type="text"
            name="EIN"
            value={organization.EIN}
            placeholder="EIN"
            onChange={handleChange}
          />
          <input
            type="text"
            name="name"
            value={organization.name}
            placeholder="Organization Name"
            onChange={handleChange}
          />
          <input
            type="text"
            name="address"
            value={organization.address}
            placeholder="Full Address"
            onChange={handleChange}
          />
          <textarea
            name="description"
            value={organization.description}
            placeholder="Description"
            onChange={handleChange}
          />
        </fieldset>

        <fieldset>
          <legend>Contact</legend>
          <input
            type="text"
            name="phone"
            value={organization.contact.phone}
            placeholder="Phone"
            onChange={handleChange}
          />
          <input
            type="email"
            name="email"
            value={organization.contact.email}
            placeholder="Email"
            onChange={handleChange}
          />
          <input
            type="text"
            name="website"
            value={organization.contact.website}
            placeholder="Website"
            onChange={handleChange}
          />
        </fieldset>

        <button type="submit" className="submit-btn">
          Validate & Register
        </button>
      </form>

      {/* DISPLAY VALIDATED ORGANIZATIONS */}
      <div className="organizations-list">
        <h2>Validated Organizations ({organizations.length})</h2>
        {organizations.map((org, idx) => (
          <div key={idx} className="org-card">
            <h3>{org.name}</h3>
            <p><strong>EIN:</strong> {org.EIN}</p>
            <p><strong>Address:</strong> {org.address}</p>
            <p><strong>Verified:</strong> {org.verified ? '✅ Yes' : '❌ No'}</p>
            <p><strong>Trust Score:</strong> {org.trust_score}/100</p>
            <p><strong>Trust Level:</strong> {org.trust_level}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OrganizationsPage;
