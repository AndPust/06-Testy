let cart = [];

function addToCart(productId) {
    fetch(`/product/${productId}`)
        .then(response => response.json())
        .then(product => {
            const existingItem = cart.find(item => item.id === product.id);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({...product, quantity: 1});
            }
            updateCart();
        });
}

function updateCart() {
    const cartItems = document.getElementById('cart-items');
    const buyButton = document.getElementById('buy-button');
    cartItems.innerHTML = '';
    cart.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="cart-item-buttons">
                <button onclick="decreaseQuantity(${item.id})" name="minus_button" ${item.quantity === 1 ? 'disabled' : ''}>-</button>
                <span class="item-quantity">${item.quantity}</span>
                <button onclick="increaseQuantity(${item.id})" name="plus_button">+</button>
                <button class="remove-btn" onclick="removeItem(${item.id})">Remove</button>
            </div>
            <div class="cart-item-details">
                ${item.name} - $${(item.price * item.quantity).toFixed(2)}
            </div>
        `;
        cartItems.appendChild(li);
    });

    updateTotal();
    
    // Update buy button state
    buyButton.disabled = cart.length === 0;
}

function updateTotal() {
    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    document.getElementById('cart-total').textContent = total.toFixed(2);
}

function increaseQuantity(productId) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity += 1;
        updateCart();
    }
}

function decreaseQuantity(productId) {
    const item = cart.find(item => item.id === productId);
    if (item && item.quantity > 1) {
        item.quantity -= 1;
        updateCart();
    }
}

function removeItem(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCart();
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.product').forEach(product => {
        product.addEventListener('click', (event) => {
            // Prevent the click from triggering on child elements
            if (event.target.tagName.toLowerCase() === 'button') return;
            
            const productId = product.dataset.id;
            fetch(`/product/${productId}`)
                .then(response => response.json())
                .then(product => {
                    document.getElementById('detail-name').textContent = product.name;
                    document.getElementById('detail-description').textContent = product.description;
                    document.getElementById('product-details').style.display = 'block';
                })
                .catch(error => console.error('Error:', error));
        });
    });

    const buyButton = document.getElementById('buy-button');
    buyButton.addEventListener('click', buyItems);

    // Initial cart update to set button state
    updateCart();
});

function closeDetails() {
    document.getElementById('product-details').style.display = 'none';
}

// Close the modal if the user clicks outside of it
window.onclick = function(event) {
    let modal = document.getElementById('product-details');
    let modalContent = document.querySelector('#product-details .modal-content');
    
    if (modal && modalContent) {
        if (!modalContent.contains(event.target) && event.target !== modal && !event.target.closest('.product')) {
            modal.style.display = 'none';
        }
    }
}

function buyItems() {
    if (cart.length === 0) {
        return; // Do nothing if cart is empty
    }

    // Prepare the data to send
    const transactionData = cart.map(item => ({
        id: item.id,
        quantity: item.quantity
    }));

    // Send POST request to /transaction_request
    fetch('/transaction_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Transaction successful!");
            // Clear the cart
            cart = [];
            updateCart();
        } else {
            alert("Transaction failed: " + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert("An error occurred during the transaction.");
    });
}