import React, { useState } from 'react';
import './OrganizationsPage.css';

function OrganizationsPage() {
  const [formData, setFormData] = useState({
    // Type
    isShelter: false,
    isCharity: false,

    // Basic Info
    ein: '',
    name: '',
    address: '',

    // Amenities
    accessible: false,
    lgbtq_only: false,
    male_only: false,
    female_only: false,
    all_gender: false,
    pet_friendly: false,
    languages: '',
    family_rooming: false,
    beds_available: '',
    medical_support: false,
    counseling_support: false,
    fees: '',
    age_minimum: '',
    age_maximum: '',
    veteran_only: false,
    immigrant_only: false,
    refugee_only: false,
    good_criminal_record_standing: false,
    sobriety_required: false,
    showers: false,
    id_required: false,

    // Hours
    monday: '',
    tuesday: '',
    wednesday: '',
    thursday: '',
    friday: '',
    saturday: '',
    sunday: '',

    // Description
    description: '',

    // Contact
    phone: '',
    email: '',
    website: ''
  });

  const [organizations, setOrganizations] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate that at least one organization type is selected
    if (!formData.isShelter && !formData.isCharity) {
      alert('Please select at least one organization type (Shelter or Charity)');
      return;
    }

    // Parse languages from comma-separated string
    const languagesArray = formData.languages
      ? formData.languages.split(',').map(lang => lang.trim())
      : ['english'];

    // Create new organization object matching your JSON structure
    const newOrg = {
      type: {
        shelter: formData.isShelter,
        charity: formData.isCharity
      },
      EIN: parseInt(formData.ein) || 0,
      name: formData.name,
      address: formData.address,
      ammenities: {
        accessible: formData.accessible,
        lgbtq_only: formData.lgbtq_only,
        male_only: formData.male_only,
        female_only: formData.female_only,
        all_gender: formData.all_gender,
        pet_friendly: formData.pet_friendly,
        languages: languagesArray,
        family_rooming: formData.family_rooming,
        beds_available: parseInt(formData.beds_available) || 0,
        medical_support: formData.medical_support,
        counseling_support: formData.counseling_support,
        fees: parseFloat(formData.fees) || 0,
        age_minimum: parseInt(formData.age_minimum) || 0,
        age_maximum: parseInt(formData.age_maximum) || 0,
        veteran_only: formData.veteran_only,
        immigrant_only: formData.immigrant_only,
        refugee_only: formData.refugee_only,
        good_criminal_record_standing: formData.good_criminal_record_standing,
        sobriety_required: formData.sobriety_required,
        showers: formData.showers,
        id_required: formData.id_required
      },
      needs: {},
      hours: {
        monday: formData.monday || "0000-2359",
        tuesday: formData.tuesday || "0000-2359",
        wednesday: formData.wednesday || "0000-2359",
        thursday: formData.thursday || "0000-2359",
        friday: formData.friday || "0000-2359",
        saturday: formData.saturday || "0000-2359",
        sunday: formData.sunday || "0000-2359"
      },
      description: formData.description,
      contact: {
        phone: formData.phone,
        email: formData.email,
        website: formData.website
      },
      verified: false,
      timestamp: new Date().toISOString()
    };

    try {
      // Send to backend API
      const response = await fetch('http://localhost:5000/api/organizations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newOrg)
      });

      const result = await response.json();

      if (result.success) {
        // Update the organization with verified status from backend
        const updatedOrg = {
          ...newOrg,
          verified: result.verification_status.verified,
          trust_score: result.verification_status.trust_score,
          trust_level: result.verification_status.trust_level
        };

        // Add to local state with updated verification status
        setOrganizations([...organizations, updatedOrg]);

        // Show success message with verification status
        alert(
          `Organization registered successfully!\n\n` +
          `Organization ID: ${result.organization_id}\n` +
          `Verification Status: ${result.verification_status.status}\n` +
          `Trust Score: ${result.verification_status.trust_score}/100\n` +
          `Trust Level: ${result.verification_status.trust_level}\n` +
          `Verified: ${result.verification_status.verified ? 'Yes' : 'No'}\n\n` +
          `${result.verification_status.status === 'pending_review' ?
            'Your organization will be reviewed by an administrator.' :
            result.verification_status.verified ?
            'Your organization has been verified and approved!' :
            'Your organization has been approved but requires additional verification for full trust.'}`
        );

        console.log('Backend response:', result);
      } else {
        alert('Error: ' + result.message);
        return;
      }
    } catch (error) {
      console.error('Error submitting to backend:', error);
      alert(
        'Warning: Could not connect to backend server.\n\n' +
        'Make sure the Python backend is running:\n' +
        'python backend_api.py\n\n' +
        'Data saved locally only.'
      );

      // Still add to local state as fallback
      setOrganizations([...organizations, newOrg]);
    }

    // Reset form (keeping it tedious - they have to fill it all again!)
    setFormData({
      isShelter: false,
      isCharity: false,
      ein: '',
      name: '',
      address: '',
      accessible: false,
      lgbtq_only: false,
      male_only: false,
      female_only: false,
      all_gender: false,
      pet_friendly: false,
      languages: '',
      family_rooming: false,
      beds_available: '',
      medical_support: false,
      counseling_support: false,
      fees: '',
      age_minimum: '',
      age_maximum: '',
      veteran_only: false,
      immigrant_only: false,
      refugee_only: false,
      good_criminal_record_standing: false,
      sobriety_required: false,
      showers: false,
      id_required: false,
      monday: '',
      tuesday: '',
      wednesday: '',
      thursday: '',
      friday: '',
      saturday: '',
      sunday: '',
      description: '',
      phone: '',
      email: '',
      website: ''
    });
  };

  return (
    <div className="organizations-page">
      <h1>Organization Registration</h1>
      <p className="subtitle">Complete ALL fields below to register your organization</p>

      <form onSubmit={handleSubmit} className="org-form">

        {/* ORGANIZATION TYPE */}
        <fieldset>
          <legend>Organization Type *</legend>
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                name="isShelter"
                checked={formData.isShelter}
                onChange={handleChange}
              />
              Shelter
            </label>
            <label>
              <input
                type="checkbox"
                name="isCharity"
                checked={formData.isCharity}
                onChange={handleChange}
              />
              Charity
            </label>
          </div>
        </fieldset>

        {/* BASIC INFORMATION */}
        <fieldset>
          <legend>Basic Information</legend>

          <div className="form-group">
            <label htmlFor="ein">EIN (Employer Identification Number) *</label>
            <input
              type="number"
              id="ein"
              name="ein"
              value={formData.ein}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="name">Organization Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="address">Full Address *</label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              required
              placeholder="123 Main St, City, State ZIP"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="4"
              placeholder="Describe your organization's mission and services..."
            />
          </div>
        </fieldset>

        {/* AMENITIES */}
        <fieldset>
          <legend>Amenities & Services</legend>

          <div className="checkbox-grid">
            <label>
              <input
                type="checkbox"
                name="accessible"
                checked={formData.accessible}
                onChange={handleChange}
              />
              Wheelchair Accessible
            </label>

            <label>
              <input
                type="checkbox"
                name="lgbtq_only"
                checked={formData.lgbtq_only}
                onChange={handleChange}
              />
              LGBTQ+ Only
            </label>

            <label>
              <input
                type="checkbox"
                name="male_only"
                checked={formData.male_only}
                onChange={handleChange}
              />
              Male Only
            </label>

            <label>
              <input
                type="checkbox"
                name="female_only"
                checked={formData.female_only}
                onChange={handleChange}
              />
              Female Only
            </label>

            <label>
              <input
                type="checkbox"
                name="all_gender"
                checked={formData.all_gender}
                onChange={handleChange}
              />
              All Gender
            </label>

            <label>
              <input
                type="checkbox"
                name="pet_friendly"
                checked={formData.pet_friendly}
                onChange={handleChange}
              />
              Pet Friendly
            </label>

            <label>
              <input
                type="checkbox"
                name="family_rooming"
                checked={formData.family_rooming}
                onChange={handleChange}
              />
              Family Rooming
            </label>

            <label>
              <input
                type="checkbox"
                name="medical_support"
                checked={formData.medical_support}
                onChange={handleChange}
              />
              Medical Support
            </label>

            <label>
              <input
                type="checkbox"
                name="counseling_support"
                checked={formData.counseling_support}
                onChange={handleChange}
              />
              Counseling Support
            </label>

            <label>
              <input
                type="checkbox"
                name="showers"
                checked={formData.showers}
                onChange={handleChange}
              />
              Showers Available
            </label>

            <label>
              <input
                type="checkbox"
                name="veteran_only"
                checked={formData.veteran_only}
                onChange={handleChange}
              />
              Veterans Only
            </label>

            <label>
              <input
                type="checkbox"
                name="immigrant_only"
                checked={formData.immigrant_only}
                onChange={handleChange}
              />
              Immigrants Only
            </label>

            <label>
              <input
                type="checkbox"
                name="refugee_only"
                checked={formData.refugee_only}
                onChange={handleChange}
              />
              Refugees Allowed
            </label>

            <label>
              <input
                type="checkbox"
                name="good_criminal_record_standing"
                checked={formData.good_criminal_record_standing}
                onChange={handleChange}
              />
              No Criminal History Required
            </label>

            <label>
              <input
                type="checkbox"
                name="sobriety_required"
                checked={formData.sobriety_required}
                onChange={handleChange}
              />
              Sobriety Required
            </label>

            <label>
              <input
                type="checkbox"
                name="id_required"
                checked={formData.id_required}
                onChange={handleChange}
              />
              ID Required
            </label>
          </div>

          <div className="form-group">
            <label htmlFor="languages">Languages Spoken (comma-separated)</label>
            <input
              type="text"
              id="languages"
              name="languages"
              value={formData.languages}
              onChange={handleChange}
              placeholder="english, spanish, french"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="beds_available">Beds Available</label>
              <input
                type="number"
                id="beds_available"
                name="beds_available"
                value={formData.beds_available}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="fees">Fees ($)</label>
              <input
                type="number"
                step="0.01"
                id="fees"
                name="fees"
                value={formData.fees}
                onChange={handleChange}
                min="0"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="age_minimum">Minimum Age</label>
              <input
                type="number"
                id="age_minimum"
                name="age_minimum"
                value={formData.age_minimum}
                onChange={handleChange}
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="age_maximum">Maximum Age</label>
              <input
                type="number"
                id="age_maximum"
                name="age_maximum"
                value={formData.age_maximum}
                onChange={handleChange}
                min="0"
              />
            </div>
          </div>
        </fieldset>

        {/* HOURS OF OPERATION */}
        <fieldset>
          <legend>Hours of Operation (format: 0000-2359)</legend>

          <div className="form-group">
            <label htmlFor="monday">Monday</label>
            <input
              type="text"
              id="monday"
              name="monday"
              value={formData.monday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>

          <div className="form-group">
            <label htmlFor="tuesday">Tuesday</label>
            <input
              type="text"
              id="tuesday"
              name="tuesday"
              value={formData.tuesday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>

          <div className="form-group">
            <label htmlFor="wednesday">Wednesday</label>
            <input
              type="text"
              id="wednesday"
              name="wednesday"
              value={formData.wednesday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>

          <div className="form-group">
            <label htmlFor="thursday">Thursday</label>
            <input
              type="text"
              id="thursday"
              name="thursday"
              value={formData.thursday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>

          <div className="form-group">
            <label htmlFor="friday">Friday</label>
            <input
              type="text"
              id="friday"
              name="friday"
              value={formData.friday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>

          <div className="form-group">
            <label htmlFor="saturday">Saturday</label>
            <input
              type="text"
              id="saturday"
              name="saturday"
              value={formData.saturday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>

          <div className="form-group">
            <label htmlFor="sunday">Sunday</label>
            <input
              type="text"
              id="sunday"
              name="sunday"
              value={formData.sunday}
              onChange={handleChange}
              placeholder="0900-1700"
            />
          </div>
        </fieldset>

        {/* CONTACT INFORMATION */}
        <fieldset>
          <legend>Contact Information</legend>

          <div className="form-group">
            <label htmlFor="phone">Phone Number *</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              placeholder="123-456-7890"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="info@organization.org"
            />
          </div>

          <div className="form-group">
            <label htmlFor="website">Website</label>
            <input
              type="url"
              id="website"
              name="website"
              value={formData.website}
              onChange={handleChange}
              placeholder="https://www.organization.org"
            />
          </div>
        </fieldset>

        <button type="submit" className="submit-btn">Submit Organization Registration</button>
      </form>

      {/* Display Added Organizations */}
      <div className="organizations-list">
        <h2>Registered Organizations ({organizations.length})</h2>
        {organizations.map((org, index) => (
          <div key={index} className="org-card">
            <h3>{org.name}</h3>
            <p><strong>EIN:</strong> {org.EIN}</p>
            <p><strong>Type:</strong> {org.type.shelter && 'Shelter'} {org.type.charity && 'Charity'}</p>
            <p><strong>Address:</strong> {org.address}</p>
            <p><strong>Phone:</strong> {org.contact.phone}</p>
            <p><strong>Email:</strong> {org.contact.email}</p>
            <p><strong>Verified:</strong> <span style={{color: org.verified ? '#27ae60' : '#e74c3c', fontWeight: 'bold'}}>{org.verified ? '✓ Yes' : '✗ No'}</span></p>
            {org.trust_score !== undefined && (
              <>
                <p><strong>Trust Score:</strong> {org.trust_score}/100</p>
                <p><strong>Trust Level:</strong> {org.trust_level}</p>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default OrganizationsPage;
