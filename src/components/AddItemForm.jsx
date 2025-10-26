import React, { useState } from 'react';

function AddItemForm({ onAdd, onBack }) {
    const [category, setCategory] = useState('Clothing');
    const [itemName, setItemName] = useState('');
    const [quantity, setQuantity] = useState('1');
    const [description, setDescription] = useState('');

    const categories = [
        'Clothing',
        'Household',
        'Food',
        'Toiletries',
        'Other'
    ];

    function handleSubmit(e) {
        e.preventDefault();
        const newItem = {
            category,
            itemName: itemName.trim(),
            quantity: quantity.toString(),
            description: description.trim()
        };

        if (onAdd) onAdd(newItem);

        // reset simple fields
        setCategory('Clothing');
        setItemName('');
        setQuantity('1');
        setDescription('');
    }

    return (
        <form onSubmit={handleSubmit} className="add-item-form card card-body mb-3">
            <div className="row g-2 align-items-end">
                <div className="col-6 col-md-8">
                    <label htmlFor="category" className="form-label small">Category</label>
                    <select
                        id="category"
                        className="form-select"
                        value={category}
                        onChange={e => setCategory(e.target.value)}
                    >
                        {categories.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                        ))}
                    </select>
                </div>

                <div className="col-6 col-md-4">
                    <label htmlFor="quantity" className="form-label small">Quantity</label>
                    <input
                        id="quantity"
                        type="number"
                        min="1"
                        className="form-control"
                        value={quantity}
                        onChange={e => setQuantity(e.target.value)}
                    />
                </div>

                <div className="col-12 col-md-12">
                    <label htmlFor="itemName" className="form-label small">Item Name</label>
                    <input
                        id="itemName"
                        type="text"
                        className="form-control"
                        required
                        placeholder="E.g. Men's T-shirt"
                        value={itemName}
                        onChange={e => setItemName(e.target.value)}
                    />
                </div>

                <div className="col-12 col-md-12">
                    <label htmlFor="description" className="form-label small">Description</label>
                    <input
                        id="description"
                        type="text"
                        className="form-control"
                        placeholder="E.g. size, condition, notes"
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                    />
                </div>

                <div className="col-12 d-flex align-items-center mt-3" style={{ minHeight: '40px', position: 'relative' }}>
                    {onBack && (
                        <button
                            type="button"
                            onClick={onBack}
                            className="back-arrow-btn"
                            aria-label="Back"
                            style={{
                                background: 'none',
                                border: 'none',
                                padding: 0,
                                marginRight: '10px',
                                display: 'flex',
                                alignItems: 'center',
                                cursor: 'pointer',
                                position: 'absolute',
                                left: 0,
                            }}
                        >
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M15 18L9 12L15 6" stroke="#adb5bd" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                    )}
                    <div className="flex-grow-1 d-flex justify-content-center">
                        <button type="submit" className="btn btn-primary add-item-button">Submit</button>
                    </div>
                </div>
            </div>
        </form>
    );
}

export default AddItemForm;

// Add subtle hover effect for the back arrow button
const style = document.createElement('style');
style.innerHTML = `
    .back-arrow-btn svg path {
        transition: stroke 0.2s;
    }
    .back-arrow-btn:hover svg path {
        stroke: #2ee079; /* Bootstrap btn-success green */
    }
`;
if (typeof document !== 'undefined' && !document.getElementById('add-item-form-back-arrow-style')) {
    style.id = 'add-item-form-back-arrow-style';
    document.head.appendChild(style);
}