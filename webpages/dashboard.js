// Dashboard Script
// Replace with your real API Gateway URLs
const ORDERS_URL = "https://f8nvend14d.execute-api.us-east-1.amazonaws.com/prod/orders";
const STATS_URL = "https://f8nvend14d.execute-api.us-east-1.amazonaws.com/prod/stats";

const ordersContainer = document.getElementById("orders");
const statsContainer = document.getElementById("stats");

async function loadOrders() {
  try {
    const response = await fetch(ORDERS_URL);
    const data = await response.json();

    ordersContainer.innerHTML = "";

    data.forEach(order => {
      const div = document.createElement("div");
      div.className = "order-item";
      div.innerHTML = `
        <p><b>Order ID:</b> ${order.orderId}</p>
        <p><b>Timestamp:</b> ${order.timestamp}</p>
        <p><b>Signature:</b> ${order.orderSignature}</p>
        <pre><b>Items:</b> ${JSON.stringify(order.items, null, 2)}</pre>
        <hr />
      `;
      ordersContainer.appendChild(div);
    });
  } catch (error) {
    console.error("Error loading orders:", error);
    ordersContainer.innerHTML = "❌ Failed to load orders.";
  }
}

async function loadStats() {
  try {
    const response = await fetch(STATS_URL);
    const stats = await response.json();

    statsContainer.innerHTML = `
      <p><b>Total Orders:</b> ${stats.totalOrders}</p>
      <p><b>Total Items Ordered:</b> ${stats.totalItems}</p>
      <pre><b>Item Breakdown:</b> ${JSON.stringify(stats.itemBreakdown, null, 2)}</pre>
    `;
  } catch (error) {
    console.error("Error loading stats:", error);
    statsContainer.innerHTML = "❌ Failed to load statistics.";
  }
}

// Auto refresh
loadOrders();
loadStats();
setInterval(() => {
  loadOrders();
  loadStats();
}, 5000);