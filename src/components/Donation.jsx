import React from 'react';
import '../App.css';

function Donation(props) {
    return (
        <div className="donation-card">
            <div className="card-body">
                <p className="card-title">{props.quantity}x {props.itemName}</p>
                <label className="card-description mb-3">{props.description}</label>
            </div>
        </div>
    );
}

export default Donation;