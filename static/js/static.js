// scripts.js

function searchProducts() {
    const product = document.getElementById("product-input").value;
    if (!product) {
        alert("Please enter a product name.");
        return;
    }

    // Make the API request to Flask backend
    fetch(`/api/search?product=${encodeURIComponent(product)}`)
        .then(response => response.json())
        .then(data => {
            const amazonResultsDiv = document.getElementById("amazon-products");
            const flipkartResultsDiv = document.getElementById("flipkart-products");
            amazonResultsDiv.innerHTML = '';  // Clear previous Amazon results
            flipkartResultsDiv.innerHTML = '';  // Clear previous Flipkart results

            // Separate the results into Amazon and Flipkart
            const amazonProducts = data.products.filter(product => product['Product Link'].includes('amazon.in'));
            const flipkartProducts = data.products.filter(product => product['Product Link'].includes('flipkart.com'));

            // Display Amazon results
            if (amazonProducts.length > 0) {
                amazonProducts.forEach(product => {
                    const productDiv = document.createElement("div");
                    productDiv.classList.add("product");

                    productDiv.innerHTML = `
                        <img src="${product['Product Image']}" alt="${product['Product Name']}">
                        <h4>${product['Product Name']}</h4>
                        <p>${product['Description']}</p>
                        <p class="price">₹${product['Price']}</p>
                        <p>Reviews: ${product['Reviews']}</p>
                        <a href="${product['Product Link']}" target="_blank">View on Amazon</a>
                    `;

                    amazonResultsDiv.appendChild(productDiv);
                });
            } else {
                amazonResultsDiv.innerHTML = "<p>No products found on Amazon.</p>";
            }

            // Display Flipkart results
            if (flipkartProducts.length > 0) {
                flipkartProducts.forEach(product => {
                    const productDiv = document.createElement("div");
                    productDiv.classList.add("product");

                    productDiv.innerHTML = `
                        <img src="${product['Product Image']}" alt="${product['Product Name']}">
                        <h4>${product['Product Name']}</h4>
                        <p>${product['Description']}</p>
                        <p class="price">₹${product['Price']}</p>
                        <p>Reviews: ${product['Reviews']}</p>
                        <a href="${product['Product Link']}" target="_blank">View on Flipkart</a>
                    `;

                    flipkartResultsDiv.appendChild(productDiv);
                });
            } else {
                flipkartResultsDiv.innerHTML = "<p>No products found on Flipkart.</p>";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('There was an issue fetching product data.');
        });
}
