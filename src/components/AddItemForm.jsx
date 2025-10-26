import React, { useState } from 'react';

function AddItemForm({ onAdd }) {
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
                <div className="col-12">
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

                <div className="col-12 col-md-12">
                    <label htmlFor="itemName" className="form-label small">Item Name</label>
                    <input
                        id="itemName"
                        type="text"
                        className="form-control"
                        required
                        placeholder="e.g., Men's T-shirt"
                        value={itemName}
                        onChange={e => setItemName(e.target.value)}
                    />
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

                <div className="col-6 col-md-8">
                    <label htmlFor="description" className="form-label small">Description</label>
                    <input
                        id="description"
                        type="text"
                        className="form-control"
                        placeholder="Optional - size, condition, notes"
                        value={description}
                        onChange={e => setDescription(e.target.value)}
                    />
                </div>

                <div className="col-12 d-flex justify-content-center mt-2">
                    <button type="submit" className="btn btn-primary add-item-button">Submit</button>
                </div>
            </div>
        </form>
    );
}

export default AddItemForm;