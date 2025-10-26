import React from 'react';
import '../App.css';

function Donation(props) {
    return (
        <div className="donation-card">
            <div className="card-body">
                <button 
                    className="remove-button" 
                    onClick={props.onClick}
                    aria-label="Remove donation"
                >
                    ×
                </button>
                <p className="card-title">{props.quantity}x {props.itemName}</p>
                <label className="card-description mb-3">{props.description}</label>
            </div>
        </div>
    );
}

export default Donation;