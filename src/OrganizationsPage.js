import React, { useState } from "react";
import "./OrganizationsPage.css";

/* ===============================================================
   🧱 Base Template (matches backend JSON schema)
================================================================*/
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

/* ===============================================================
   🎛️ Dropdown options for Hours of Operation
================================================================*/
const HOUR_OPTIONS = [
  { label: "Closed", value: "closed" },
  { label: "24 Hours", value: "0000-2359" },
  { label: "8 AM - 5 PM", value: "0800-1700" },
  { label: "9 AM - 6 PM", value: "0900-1800" },
  { label: "10 AM - 7 PM", value: "1000-1900" },
  { label: "Custom", value: "custom" },
];

/* ===============================================================
   🧩 Component
================================================================*/
function OrganizationsPage() {
  const [org, setOrg] = useState(BASE_ORG_TEMPLATE);
  const [submitted, setSubmitted] = useState([]);
  const [needsList, setNeedsList] = useState([]);
  const [customHours, setCustomHours] = useState({});

  /* ---------------------------------------------------------------
   🔄 Handle Input Changes (generic + nested fields)
  ----------------------------------------------------------------*/
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

  /* ---------------------------------------------------------------
   🕐 Handle Dropdown for Hours
  ----------------------------------------------------------------*/
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

  /* ---------------------------------------------------------------
   📦 Needs Management
  ----------------------------------------------------------------*/
  const addNeed = () => {
    setNeedsList([...needsList, { item: "", category: "", needed: 0, have: 0, urgency: "medium" }]);
  };

  const updateNeed = (index, field, value) => {
    const newNeeds = [...needsList];
    newNeeds[index][field] = value;
    setNeedsList(newNeeds);
  };

  const removeNeed = (index) => {
    setNeedsList(needsList.filter((_, i) => i !== index));
  };

  /* ---------------------------------------------------------------
   🚀 Submit to /api/org/validate
  ----------------------------------------------------------------*/
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!org.type.shelter && !org.type.charity) {
      alert("Please select at least one organization type.");
      return;
    }

    // Convert languages to array
    if (typeof org.ammenities.languages === "string") {
      org.ammenities.languages = org.ammenities.languages
        .split(",")
        .map((lang) => lang.trim());
    }

    // Convert needs list to JSON object
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

  /* ---------------------------------------------------------------
   🧾 UI
  ----------------------------------------------------------------*/
  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <p className="subtitle">Complete all required fields below</p>

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
          <input name="EIN" placeholder="EIN" value={org.EIN} onChange={handleChange} />
          <input name="name" placeholder="Organization Name" value={org.name} onChange={handleChange} />
          <input name="address" placeholder="Full Address" value={org.address} onChange={handleChange} />
          <input name="image_address_url" placeholder="Image URL" value={org.image_address_url} onChange={handleChange} />
          <textarea name="description" placeholder="Description" value={org.description} onChange={handleChange} />
        </fieldset>

        {/* ---------- CONTACT ---------- */}
        <fieldset>
          <legend>Contact Information</legend>
          <input name="phone" placeholder="Phone" value={org.contact.phone} onChange={handleChange} />
          <input name="email" placeholder="Email" value={org.contact.email} onChange={handleChange} />
          <input name="website" placeholder="Website" value={org.contact.website} onChange={handleChange} />
        </fieldset>

        {/* ---------- HOURS ---------- */}
        <fieldset>
          <legend>Hours of Operation</legend>
          {Object.keys(org.hours).map((day) => (
            <div key={day} className="hour-row">
              <label className="hour-label">
                {day.charAt(0).toUpperCase() + day.slice(1)}:
              </label>
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
            </div>
          ))}
        </fieldset>

        {/* ---------- AMMENITIES ---------- */}
        <fieldset>
          <legend>Amenities</legend>
          <div className="checkbox-grid">
            {Object.entries(org.ammenities).map(([key, val]) => (
              <label key={key}>
                {typeof val === "boolean" ? (
                  <>
                    <input
                      type="checkbox"
                      name={key}
                      checked={val}
                      onChange={handleChange}
                    />{" "}
                    {key.replaceAll("_", " ")}
                  </>
                ) : (
                  <input
                    type="text"
                    name={key}
                    value={val}
                    onChange={handleChange}
                    placeholder={key}
                  />
                )}
              </label>
            ))}
          </div>
        </fieldset>

        {/* ---------- NEEDS ---------- */}
        <fieldset>
          <legend>Needs</legend>
          {needsList.map((need, index) => (
            <div key={index} className="need-row">
              <input
                type="text"
                placeholder="Item Name"
                value={need.item}
                onChange={(e) => updateNeed(index, "item", e.target.value)}
              />
              <input
                type="text"
                placeholder="Category"
                value={need.category}
                onChange={(e) => updateNeed(index, "category", e.target.value)}
              />
              <input
                type="number"
                placeholder="Needed"
                value={need.needed}
                onChange={(e) => updateNeed(index, "needed", e.target.value)}
              />
              <input
                type="number"
                placeholder="Have"
                value={need.have}
                onChange={(e) => updateNeed(index, "have", e.target.value)}
              />
              <select
                value={need.urgency}
                onChange={(e) => updateNeed(index, "urgency", e.target.value)}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              <button type="button" onClick={() => removeNeed(index)}>Remove</button>
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

      {/* ---------- SUBMITTED ---------- */}
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
