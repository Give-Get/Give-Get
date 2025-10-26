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
    monday: { start: "0900", end: "1700" },
    tuesday: { start: "0900", end: "1700" },
    wednesday: { start: "0900", end: "1700" },
    thursday: { start: "0900", end: "1700" },
    friday: { start: "0900", end: "1700" },
    saturday: { start: "0000", end: "0000" },
    sunday: { start: "0000", end: "0000" },
  },
  description: "",
  contact: { phone: "", email: "", website: "" },
};

const TIME_OPTIONS = [
  "0000", "0100", "0200", "0300", "0400", "0500", "0600", "0700", "0800",
  "0900", "1000", "1100", "1200", "1300", "1400", "1500", "1600",
  "1700", "1800", "1900", "2000", "2100", "2200", "2300", "2359"
];

function OrganizationsPage() {
  const [org, setOrg] = useState(BASE_ORG_TEMPLATE);
  const [needsList, setNeedsList] = useState([]);
  const [submitted, setSubmitted] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : value;

    if (name in org.contact) {
      setOrg({ ...org, contact: { ...org.contact, [name]: val } });
    } else if (name in org.ammenities) {
      setOrg({ ...org, ammenities: { ...org.ammenities, [name]: val } });
    } else {
      setOrg({ ...org, [name]: val });
    }
  };

  const handleHourChange = (day, field, value) => {
    setOrg({
      ...org,
      hours: { ...org.hours, [day]: { ...org.hours[day], [field]: value } },
    });
  };

  const addNeed = () => {
    setNeedsList([
      ...needsList,
      { item: "", category: "", needed: 0, have: 0, urgency: "medium" },
    ]);
  };

  const updateNeed = (i, field, val) => {
    const updated = [...needsList];
    updated[i][field] = val;
    setNeedsList(updated);
  };

  const removeNeed = (i) => setNeedsList(needsList.filter((_, idx) => i !== idx));

  const handleSubmit = async (e) => {
    e.preventDefault();

    const needsObj = {};
    needsList.forEach((n) => {
      if (n.item)
        needsObj[n.item] = {
          category: n.category,
          needed: parseInt(n.needed) || 0,
          have: parseInt(n.have) || 0,
          urgency: n.urgency,
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
        alert("✅ Organization validated successfully!");
        setSubmitted([...submitted, payload]);
        setOrg(BASE_ORG_TEMPLATE);
        setNeedsList([]);
      } else {
        alert("❌ Validation failed: " + result.message);
      }
    } catch (err) {
      alert("⚠️ Could not connect to backend validator.");
    }
  };

  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <p className="subtitle">Complete all fields below</p>

      <form onSubmit={handleSubmit} className="org-form">

        {/* TYPE */}
        <fieldset>
          <legend>Organization Type *</legend>
          <div className="checkbox-group">
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
          </div>
        </fieldset>

        {/* BASIC INFO */}
        <fieldset>
          <legend>Basic Information</legend>

          <div className="form-row">
            <div className="form-group">
              <label>EIN</label>
              <input name="EIN" value={org.EIN} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Organization Name</label>
              <input name="name" value={org.name} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label>Full Address</label>
            <input name="address" value={org.address} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label>Image URL</label>
            <input name="image_address_url" value={org.image_address_url} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={org.description} onChange={handleChange} />
          </div>
        </fieldset>

        {/* CONTACT */}
        <fieldset>
          <legend>Contact Information</legend>
          <div className="form-row">
            <div className="form-group">
              <label>Phone Number</label>
              <input name="phone" value={org.contact.phone} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input name="email" value={org.contact.email} onChange={handleChange} />
            </div>
          </div>
          <div className="form-group">
            <label>Website</label>
            <input name="website" value={org.contact.website} onChange={handleChange} />
          </div>
        </fieldset>

        {/* HOURS */}
        <fieldset>
          <legend>Hours of Operation</legend>
          {Object.keys(org.hours).map((day) => (
            <div key={day} className="form-row">
              <div className="form-group">
                <label>{day.charAt(0).toUpperCase() + day.slice(1)} Start Time</label>
                <select
                  value={org.hours[day].start}
                  onChange={(e) => handleHourChange(day, "start", e.target.value)}
                >
                  {TIME_OPTIONS.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>{day.charAt(0).toUpperCase() + day.slice(1)} End Time</label>
                <select
                  value={org.hours[day].end}
                  onChange={(e) => handleHourChange(day, "end", e.target.value)}
                >
                  {TIME_OPTIONS.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>
          ))}
        </fieldset>

        {/* AMENITIES */}
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
                    {key.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </>
                ) : (
                  <>
                    {key.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    <input
                      type={typeof val === "number" ? "number" : "text"}
                      name={key}
                      value={val}
                      onChange={handleChange}
                    />
                  </>
                )}
              </label>
            ))}
          </div>
        </fieldset>

        {/* NEEDS */}
        <fieldset>
          <legend>Needs</legend>
          {needsList.map((need, i) => (
            <div key={i} className="form-row">
              <div className="form-group">
                <label>Item Name</label>
                <input value={need.item} onChange={(e) => updateNeed(i, "item", e.target.value)} />
              </div>
              <div className="form-group">
                <label>Category</label>
                <input value={need.category} onChange={(e) => updateNeed(i, "category", e.target.value)} />
              </div>
              <div className="form-group">
                <label>Needed</label>
                <input type="number" value={need.needed} onChange={(e) => updateNeed(i, "needed", e.target.value)} />
              </div>
              <div className="form-group">
                <label>Have</label>
                <input type="number" value={need.have} onChange={(e) => updateNeed(i, "have", e.target.value)} />
              </div>
              <div className="form-group">
                <label>Urgency</label>
                <select value={need.urgency} onChange={(e) => updateNeed(i, "urgency", e.target.value)}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <button type="button" onClick={() => removeNeed(i)}>Remove</button>
            </div>
          ))}
          <button type="button" onClick={addNeed}>➕ Add Need</button>
        </fieldset>

        <button type="submit" className="submit-btn">Validate & Submit</button>
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
