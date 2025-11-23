const API_URL = "https://dummy-validation-api.example.com/validate";
const STORE_URL = "https://f8nvend14d.execute-api.us-east-1.amazonaws.com/prod/storeOrder";

const form = document.getElementById("orderForm");
const resultBox = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(form);
  let order = {};

  formData.forEach((value, key) => {
    order[key] = Number(value) || 0;
  });

  resultBox.innerHTML = "Validating order...";

  try {
    // Step 1 — Send to validation API
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(order)
    });

    const data = await response.json();

    if (!data.orderSignature) {
      resultBox.innerHTML = "❌ Order invalid";
      return;
    }

    const finalOrder = {
      items: order,
      timestamp: new Date().toISOString(),
      orderSignature: data.orderSignature
    };

    // Step 2 — Store in database
    await fetch(STORE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(finalOrder)
    });

    resultBox.innerHTML = `✅ Order stored! <br> Signature: <b>${data.orderSignature}</b>`;

  } catch (err) {
    console.error(err);
    resultBox.innerHTML = "❌ Error processing your order.";
  }
});


