import React, { useState } from 'react';
import './OrganizationsPage.css';

// ✅ Base org template that matches your desired JSON
const baseOrgTemplate = {
  image_address_url: "",
  type: { shelter: false, charity: false },
  EIN: "",
  name: "",
  address: "",
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
  }
};

function OrganizationsPage() {
  const [organization, setOrganization] = useState(baseOrgTemplate);
  const [organizations, setOrganizations] = useState([]);

  // ✅ Handles nested field updates dynamically
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === 'checkbox' ? checked : value;

    if (name in organization.ammenities) {
      setOrganization({
        ...organization,
        ammenities: { ...organization.ammenities, [name]: val }
      });
    } else if (name in organization.contact) {
      setOrganization({
        ...organization,
        contact: { ...organization.contact, [name]: val }
      });
    } else if (name in organization.hours) {
      setOrganization({
        ...organization,
        hours: { ...organization.hours, [name]: val || "0000-2359" }
      });
    } else {
      setOrganization({ ...organization, [name]: val });
    }
  };

  // ✅ Submit sends JSON directly to validator
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!organization.type.shelter && !organization.type.charity) {
      alert('Please select at least one organization type (Shelter or Charity)');
      return;
    }

    // Normalize languages to array
    if (typeof organization.ammenities.languages === 'string') {
      organization.ammenities.languages = organization.ammenities.languages
        .split(',')
        .map(lang => lang.trim());
    }

    try {
      const response = await fetch('http://localhost:8000/api/org/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(organization)
      });

      const result = await response.json();
      if (result.success) {
        alert(`✅ Organization validated & created with ID: ${result.organization_id}`);
        setOrganizations([...organizations, organization]);
      } else {
        alert(`❌ Validation failed: ${result.message}`);
      }
    } catch (err) {
      console.error(err);
      alert('⚠️ Could not connect to validation API.');
    }

    setOrganization(baseOrgTemplate);
  };

  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <form onSubmit={handleSubmit} className="org-form">
        <fieldset>
          <legend>Organization Type *</legend>
          <label>
            <input
              type="checkbox"
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
          <legend>Basic Info</legend>
          <input name="EIN" placeholder="EIN" value={organization.EIN} onChange={handleChange} />
          <input name="name" placeholder="Name" value={organization.name} onChange={handleChange} />
          <input name="address" placeholder="Address" value={organization.address} onChange={handleChange} />
          <input
            name="image_address_url"
            placeholder="Image URL"
            value={organization.image_address_url}
            onChange={handleChange}
          />
          <textarea
            name="description"
            placeholder="Description"
            value={organization.description}
            onChange={handleChange}
          />
        </fieldset>

        <fieldset>
          <legend>Contact</legend>
          <input name="phone" placeholder="Phone" value={organization.contact.phone} onChange={handleChange} />
          <input name="email" placeholder="Email" value={organization.contact.email} onChange={handleChange} />
          <input name="website" placeholder="Website" value={organization.contact.website} onChange={handleChange} />
        </fieldset>

        <button type="submit" className="submit-btn">Validate & Create</button>
      </form>

      <div className="organizations-list">
        <h2>Submitted Organizations ({organizations.length})</h2>
        {organizations.map((org, i) => (
          <div key={i} className="org-card">
            <h3>{org.name}</h3>
            <p>{org.address}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OrganizationsPage;
