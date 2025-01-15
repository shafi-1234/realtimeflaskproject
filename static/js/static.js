// Ensure the script executes only after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.getElementById("searchForm");
  const searchResults = document.getElementById("searchResults");
  const modal = document.getElementById("priceModal");
  const modalContent = modal.querySelector(".modal-content");
  const closeModalBtn = modal.querySelector(".close");

  // Event listener for the search form submission
  searchForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = document.getElementById("searchQuery").value.trim();

    if (!query) {
      alert("Please enter a search term.");
      return;
    }

    displayLoadingState();

    try {
      const results = await fetchSearchResults(query);
      renderSearchResults(results);
    } catch (error) {
      console.error("Error fetching search results:", error);
      alert("Failed to fetch search results. Please try again later.");
    } finally {
      removeLoadingState();
    }
  });

  // Fetch search results from the server
  async function fetchSearchResults(query) {
    const response = await fetch(`/search?query=${encodeURIComponent(query)}`);

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    return await response.json();
  }

  // Render search results dynamically
  function renderSearchResults(results) {
    searchResults.innerHTML = "";

    if (!results || results.length === 0) {
      searchResults.innerHTML = "<p>No results found.</p>";
      return;
    }

    results.forEach((result) => {
      const resultCard = document.createElement("div");
      resultCard.className = "result-card";

      resultCard.innerHTML = `
        <h3>${result.title}</h3>
        <p>Price: ${result.price}</p>
        <a href="${result.link}" target="_blank">View Product</a>
        <button class="alert-btn" data-product='${JSON.stringify(result)}'>Set Price Alert</button>
      `;

      searchResults.appendChild(resultCard);
    });

    attachAlertButtonHandlers();
  }

  // Attach event handlers to "Set Price Alert" buttons
  function attachAlertButtonHandlers() {
    const alertButtons = document.querySelectorAll(".alert-btn");

    alertButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const productData = JSON.parse(button.getAttribute("data-product"));
        openModal(productData);
      });
    });
  }

  // Display loading state
  function displayLoadingState() {
    searchResults.innerHTML = "<p>Loading...</p>";
  }

  // Remove loading state
  function removeLoadingState() {
    // Placeholder in case further actions are needed
  }

  // Open modal with product details
  function openModal(product) {
    modalContent.innerHTML = `
      <span class="close">&times;</span>
      <h3>Set Price Alert</h3>
      <p>Product: ${product.title}</p>
      <p>Current Price: ${product.price}</p>
      <form id="alertForm">
        <label for="targetPrice">Target Price:</label>
        <input type="number" id="targetPrice" name="targetPrice" required />
        <button type="submit">Set Alert</button>
      </form>
    `;

    modal.style.display = "block";

    const alertForm = document.getElementById("alertForm");
    alertForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const targetPrice = document.getElementById("targetPrice").value;
      setPriceAlert(product, targetPrice);
    });

    const closeBtn = modalContent.querySelector(".close");
    closeBtn.addEventListener("click", closeModal);
  }

  // Close modal
  function closeModal() {
    modal.style.display = "none";
    modalContent.innerHTML = "";
  }

  // Set price alert (stub function for backend integration)
  async function setPriceAlert(product, targetPrice) {
    try {
      const response = await fetch("/set-alert", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product, targetPrice }),
      });

      if (!response.ok) {
        throw new Error("Failed to set price alert.");
      }

      alert("Price alert set successfully!");
      closeModal();
    } catch (error) {
      console.error("Error setting price alert:", error);
      alert("Failed to set price alert. Please try again later.");
    }
  }

  // Close modal on outside click
  window.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
});
