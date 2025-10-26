import React from 'react';
import '../App.css';

function Donation(props) {
    return (
        <div className="donation-card">
            <div className="card-body">
                <p className="card-title mb-3">{props.quantity}x {props.itemName} ({props.size})</p>
            </div>
        </div>
    );
}

export default Donation;