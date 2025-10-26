import React, { useState } from "react";
import "./OrganizationsPage.css";

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
    id_required: false,
  },
  needs: {},
  hours: {
    monday: "0000-2359",
    tuesday: "0000-2359",
    wednesday: "0000-2359",
    thursday: "0000-2359",
    friday: "0000-2359",
    saturday: "0000-2359",
    sunday: "0000-2359",
  },
  description: "",
  contact: { phone: "", email: "", website: "" },
};

const HOUR_OPTIONS = [
  { label: "Closed", value: "closed" },
  { label: "24 Hours (0000-2359)", value: "0000-2359" },
  { label: "8 AM - 5 PM (0800-1700)", value: "0800-1700" },
  { label: "9 AM - 6 PM (0900-1800)", value: "0900-1800" },
  { label: "10 AM - 7 PM (1000-1900)", value: "1000-1900" },
  { label: "Custom", value: "custom" },
];

function OrganizationsPage() {
  const [org, setOrg] = useState(BASE_ORG_TEMPLATE);
  const [needsList, setNeedsList] = useState([]);
  const [customHours, setCustomHours] = useState({});
  const [submitted, setSubmitted] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : value;

    if (name in org.contact) {
      setOrg({ ...org, contact: { ...org.contact, [name]: val } });
    } else if (name in org.hours) {
      setOrg({ ...org, hours: { ...org.hours, [name]: val } });
    } else if (name in org.ammenities) {
      setOrg({ ...org, ammenities: { ...org.ammenities, [name]: val } });
    } else {
      setOrg({ ...org, [name]: val });
    }
  };

  const handleHoursChange = (day, value) => {
    if (value === "custom") {
      const custom = prompt(`Enter custom hours for ${day} (e.g. 0900-1700):`);
      if (custom) {
        setOrg({ ...org, hours: { ...org.hours, [day]: custom } });
        setCustomHours({ ...customHours, [day]: custom });
      }
    } else {
      setOrg({ ...org, hours: { ...org.hours, [day]: value } });
    }
  };

  const addNeed = () => {
    setNeedsList([
      ...needsList,
      { item: "", category: "", needed: 0, have: 0, urgency: "medium" },
    ]);
  };

  const updateNeed = (index, field, value) => {
    const updated = [...needsList];
    updated[index][field] = value;
    setNeedsList(updated);
  };

  const removeNeed = (index) => {
    setNeedsList(needsList.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!org.type.shelter && !org.type.charity) {
      alert("Please select at least one organization type.");
      return;
    }

    if (typeof org.ammenities.languages === "string") {
      org.ammenities.languages = org.ammenities.languages
        .split(",")
        .map((l) => l.trim());
    }

    const needsObj = {};
    needsList.forEach((n) => {
      if (n.item)
        needsObj[n.item] = {
          category: n.category || "",
          needed: parseInt(n.needed) || 0,
          have: parseInt(n.have) || 0,
          urgency: n.urgency || "medium",
        };
    });

    const payload = { ...org, needs: needsObj };

    try {
      const res = await fetch("http://localhost:8000/api/org/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await res.json();
      if (result.success) {
        alert(`✅ Validated & Created: ID ${result.organization_id}`);
        setSubmitted([...submitted, payload]);
        setOrg(BASE_ORG_TEMPLATE);
        setNeedsList([]);
      } else {
        alert(`❌ Validation failed: ${result.message}`);
      }
    } catch (err) {
      console.error(err);
      alert("⚠️ Could not connect to backend validator.");
    }
  };

  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <p className="subtitle">Fill out all required fields to register your organization</p>

      <form onSubmit={handleSubmit} className="org-form">
        {/* --- Organization Type --- */}
        <fieldset>
          <legend>Organization Type *</legend>
          <label>
            <input
              type="checkbox"
              checked={org.type.shelter}
              onChange={(e) =>
                setOrg({ ...org, type: { ...org.type, shelter: e.target.checked } })
              }
            />
            Shelter
          </label>
          <label>
            <input
              type="checkbox"
              checked={org.type.charity}
              onChange={(e) =>
                setOrg({ ...org, type: { ...org.type, charity: e.target.checked } })
              }
            />
            Charity
          </label>
        </fieldset>

        {/* --- Basic Info --- */}
        <fieldset>
          <legend>Basic Information</legend>
          <label>
            EIN:
            <input name="EIN" value={org.EIN} onChange={handleChange} />
          </label>
          <label>
            Organization Name:
            <input name="name" value={org.name} onChange={handleChange} />
          </label>
          <label>
            Full Address:
            <input name="address" value={org.address} onChange={handleChange} />
          </label>
          <label>
            Image URL:
            <input name="image_address_url" value={org.image_address_url} onChange={handleChange} />
          </label>
          <label>
            Description:
            <textarea name="description" value={org.description} onChange={handleChange} />
          </label>
        </fieldset>

        {/* --- Contact Info --- */}
        <fieldset>
          <legend>Contact Information</legend>
          <label>
            Phone Number:
            <input name="phone" value={org.contact.phone} onChange={handleChange} />
          </label>
          <label>
            Email:
            <input name="email" value={org.contact.email} onChange={handleChange} />
          </label>
          <label>
            Website:
            <input name="website" value={org.contact.website} onChange={handleChange} />
          </label>
        </fieldset>

        {/* --- Hours --- */}
        <fieldset>
          <legend>Hours of Operation (0000-2359)</legend>
          {Object.keys(org.hours).map((day) => (
            <label key={day}>
              {day.charAt(0).toUpperCase() + day.slice(1)} Hours:
              <select
                value={customHours[day] || org.hours[day]}
                onChange={(e) => handleHoursChange(day, e.target.value)}
              >
                {HOUR_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </fieldset>

        {/* --- Amenities --- */}
        <fieldset>
          <legend>Amenities</legend>

          {Object.entries(org.ammenities).map(([key, val]) => (
            <div key={key}>
              {typeof val === "boolean" ? (
                <label>
                  <input
                    type="checkbox"
                    name={key}
                    checked={val}
                    onChange={handleChange}
                  />
                  {key.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                </label>
              ) : (
                <label>
                  {key.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}:
                  <input
                    type={typeof val === "number" ? "number" : "text"}
                    name={key}
                    value={val}
                    onChange={handleChange}
                  />
                </label>
              )}
            </div>
          ))}
        </fieldset>

        {/* --- Needs --- */}
        <fieldset>
          <legend>Needs</legend>
          {needsList.map((need, i) => (
            <div key={i}>
              <label>
                Item Name:
                <input
                  type="text"
                  value={need.item}
                  onChange={(e) => updateNeed(i, "item", e.target.value)}
                />
              </label>
              <label>
                Category:
                <input
                  type="text"
                  value={need.category}
                  onChange={(e) => updateNeed(i, "category", e.target.value)}
                />
              </label>
              <label>
                Needed:
                <input
                  type="number"
                  value={need.needed}
                  onChange={(e) => updateNeed(i, "needed", e.target.value)}
                />
              </label>
              <label>
                Have:
                <input
                  type="number"
                  value={need.have}
                  onChange={(e) => updateNeed(i, "have", e.target.value)}
                />
              </label>
              <label>
                Urgency:
                <select
                  value={need.urgency}
                  onChange={(e) => updateNeed(i, "urgency", e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </label>
              <button type="button" onClick={() => removeNeed(i)}>
                Remove
              </button>
            </div>
          ))}
          <button type="button" onClick={addNeed}>
            ➕ Add Need
          </button>
        </fieldset>

        <button type="submit" className="submit-btn">
          Validate & Submit
        </button>
      </form>

      <div className="organizations-list">
        <h2>Submitted Organizations ({submitted.length})</h2>
        {submitted.map((o, i) => (
          <div key={i} className="org-card">
            <h3>{o.name}</h3>
            <p><strong>Address:</strong> {o.address}</p>
            <p><strong>Type:</strong> {o.type.shelter ? "Shelter" : "Charity"}</p>
            <p><strong>Contact:</strong> {o.contact.email}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OrganizationsPage;
