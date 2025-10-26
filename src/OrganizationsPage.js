import React, { useState } from 'react';
import './OrganizationsPage.css';

/* ------------------------------------------------------------------
 🧱 Base JSON Template (matches backend expectation exactly)
-------------------------------------------------------------------*/
const BASE_ORG_TEMPLATE = {
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
  contact: { phone: "", email: "", website: "" }
};

/* ------------------------------------------------------------------
 🧩 React Component
-------------------------------------------------------------------*/
function OrganizationsPage() {
  const [org, setOrg] = useState(BASE_ORG_TEMPLATE);
  const [submitted, setSubmitted] = useState([]);

  /* ---------------------------------------------------------------
   🔄 Handle Input Changes (supports nested JSON fields)
  ----------------------------------------------------------------*/
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : value;

    // Handle nested updates cleanly
    if (name in org.contact) {
      setOrg({ ...org, contact: { ...org.contact, [name]: val } });
    } else if (name in org.hours) {
      setOrg({ ...org, hours: { ...org.hours, [name]: val || "0000-2359" } });
    } else if (name in org.ammenities) {
      setOrg({ ...org, ammenities: { ...org.ammenities, [name]: val } });
    } else {
      setOrg({ ...org, [name]: val });
    }
  };

  /* ---------------------------------------------------------------
   🚀 Submit: POST JSON directly to /api/org/validate
  ----------------------------------------------------------------*/
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!org.type.shelter && !org.type.charity) {
      alert("Please select at least one organization type.");
      return;
    }

    // If languages typed as string, normalize to array
    if (typeof org.ammenities.languages === "string") {
      org.ammenities.languages = org.ammenities.languages
        .split(",")
        .map((lang) => lang.trim());
    }

    // Omit ammenities if not a shelter
    const payload = { ...org };
    if (!org.type.shelter) delete payload.ammenities;

    try {
      const res = await fetch("http://localhost:8000/api/org/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (result.success) {
        alert(`✅ Validation complete! Created ID: ${result.organization_id}`);
        setSubmitted([...submitted, payload]);
        setOrg(BASE_ORG_TEMPLATE);
      } else {
        alert(`❌ Validation failed: ${result.message || "Unknown error"}`);
      }
    } catch (err) {
      console.error(err);
      alert("⚠️ Could not reach backend validation API.");
    }
  };

  /* ---------------------------------------------------------------
   🧾 UI
  ----------------------------------------------------------------*/
  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <p className="subtitle">Fill out all required fields to register your organization</p>

      <form onSubmit={handleSubmit} className="org-form">

        {/* ---------- TYPE ---------- */}
        <fieldset>
          <legend>Organization Type *</legend>
          <label>
            <input
              type="checkbox"
              checked={org.type.shelter}
              onChange={(e) =>
                setOrg({ ...org, type: { ...org.type, shelter: e.target.checked } })
              }
            /> Shelter
          </label>
          <label>
            <input
              type="checkbox"
              checked={org.type.charity}
              onChange={(e) =>
                setOrg({ ...org, type: { ...org.type, charity: e.target.checked } })
              }
            /> Charity
          </label>
        </fieldset>

        {/* ---------- BASIC INFO ---------- */}
        <fieldset>
          <legend>Basic Information</legend>
          <input
            name="EIN"
            placeholder="EIN"
            value={org.EIN}
            onChange={handleChange}
          />
          <input
            name="name"
            placeholder="Organization Name"
            value={org.name}
            onChange={handleChange}
          />
          <input
            name="address"
            placeholder="Full Address"
            value={org.address}
            onChange={handleChange}
          />
          <input
            name="image_address_url"
            placeholder="Image URL"
            value={org.image_address_url}
            onChange={handleChange}
          />
          <textarea
            name="description"
            placeholder="Description"
            value={org.description}
            onChange={handleChange}
          />
        </fieldset>

        {/* ---------- CONTACT ---------- */}
        <fieldset>
          <legend>Contact Information</legend>
          <input
            name="phone"
            placeholder="Phone Number"
            value={org.contact.phone}
            onChange={handleChange}
          />
          <input
            name="email"
            placeholder="Email"
            value={org.contact.email}
            onChange={handleChange}
          />
          <input
            name="website"
            placeholder="Website"
            value={org.contact.website}
            onChange={handleChange}
          />
        </fieldset>

        {/* ---------- HOURS ---------- */}
        <fieldset>
          <legend>Hours of Operation (0000-2359)</legend>
          {Object.keys(org.hours).map((day) => (
            <input
              key={day}
              name={day}
              placeholder={day.charAt(0).toUpperCase() + day.slice(1)}
              value={org.hours[day]}
              onChange={handleChange}
            />
          ))}
        </fieldset>

        {/* ---------- AMMENITIES (only if shelter) ---------- */}
        {org.type.shelter && (
          <fieldset>
            <legend>Amenities (Shelter Only)</legend>
            <div className="checkbox-grid">
              {Object.keys(org.ammenities).map((key) => (
                <label key={key}>
                  {typeof org.ammenities[key] === "boolean" ? (
                    <>
                      <input
                        type="checkbox"
                        name={key}
                        checked={org.ammenities[key]}
                        onChange={handleChange}
                      />{" "}
                      {key.replaceAll("_", " ")}
                    </>
                  ) : (
                    <input
                      type="text"
                      name={key}
                      value={org.ammenities[key]}
                      onChange={handleChange}
                      placeholder={key}
                    />
                  )}
                </label>
              ))}
            </div>
          </fieldset>
        )}

        <button type="submit" className="submit-btn">
          Validate & Submit
        </button>
      </form>

      {/* ---------- SUBMITTED ORGANIZATIONS ---------- */}
      <div className="organizations-list">
        <h2>Submitted Organizations ({submitted.length})</h2>
        {submitted.map((o, i) => (
          <div key={i} className="org-card">
            <h3>{o.name}</h3>
            <p><strong>Type:</strong> {o.type.shelter ? "Shelter" : "Charity"}</p>
            <p><strong>Address:</strong> {o.address}</p>
            <p><strong>Contact:</strong> {o.contact.email}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OrganizationsPage;
