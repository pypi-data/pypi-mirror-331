# kbanksdk

A Python SDK for integrating with KBank Payment Gateway API endpoints.

## Installation

```

## Usage
```



Below is a comprehensive Markdown documentation that explains how to implement the payment form in both React and Vue.js, along with an example OpenAPI specification for the payment API endpoint. This guide covers the component code, integration details, and API documentation to help other developers replicate and extend the functionality.

---

# Payment Form Integration Documentation

## Overview

This documentation describes the implementation of a dynamic payment form that:
- Creates a `<form>` element with hidden input fields.
- Integrates an external payment script.
- Submits the form data to a payment endpoint.

The guide includes examples for both **React** and **Vue.js** implementations, as well as an **OpenAPI** specification that documents the API endpoint used for processing the payment.

---

## Key Features

- **Dynamic Form Creation:**  
  The component creates a form and appends several hidden input fields (e.g., `orderId`, `userId`, `grandTotal`, `basketId`, and `customerId`).

- **Payment Script Integration:**  
  The external payment script is integrated by appending a `<script>` element with required data attributes (e.g., API key, amount, currency).

- **Lifecycle Cleanup:**  
  The component cleans up the injected form when it is unmounted or destroyed to avoid any stale content or memory leaks.

- **OpenAPI Documentation:**  
  A sample OpenAPI snippet is provided to document the backend payment API endpoint, allowing for clear integration specifications between the frontend and backend.

---

## API Endpoint: OpenAPI Documentation

The payment form submits data to the following endpoint:

**POST** `https://shop.villamarket.com/api/payment3/cardtoken`

Below is an example OpenAPI 3.0 specification snippet documenting this endpoint:

```yaml
openapi: 3.0.3
info:
  title: Payment API
  version: 1.0.0
  description: API endpoint for processing card token payments.
servers:
  - url: https://shop.villamarket.com
paths:
  /api/payment3/cardtoken:
    post:
      summary: Process Payment and Generate Card Token
      description: |
        Submits payment details including order, user, basket, and customer information.
      requestBody:
        required: true
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                orderId:
                  type: string
                  description: Unique order identifier.
                  example: "order_test_abc123xyz"
                userId:
                  type: string
                  description: Identifier of the user making the payment.
                  example: "cust_test_cd785f18d71349bfad9a6d516dcd26ea"
                grandTotal:
                  type: string
                  description: Total amount to be paid.
                  example: "74"
                basketId:
                  type: string
                  description: Unique identifier for the basket.
                  example: "basket_test_def456uvw"
                customerId:
                  type: string
                  description: Identifier of the customer.
                  example: "cust_test_cd785f18d71349bfad9a6d516dcd26ea"
            encoding:
              orderId:
                contentType: text/plain
              userId:
                contentType: text/plain
              grandTotal:
                contentType: text/plain
              basketId:
                contentType: text/plain
              customerId:
                contentType: text/plain
      responses:
        '200':
          description: Payment processed successfully and card token generated.
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    example: true
                  cardToken:
                    type: string
                    description: The generated card token.
                    example: "tok_1Hh1XYZ2abC3deF4gHiJKL5m"
                  message:
                    type: string
                    example: "Payment processed successfully."
        '400':
          description: Invalid request parameters.
        '500':
          description: Server error.
```

---

## Example Implementations

### 1. React Implementation

The React component uses hooks (`useEffect` and `useRef`) to inject the form and script into the DOM after the component mounts.

```tsx
import { useEffect, useRef } from "react";

const PaymentForm = () => {
  // Reference to the container div where the form will be injected
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Clear any previous content in the container
    containerRef.current.innerHTML = "";

    // Create the form element
    const form = document.createElement("form");
    form.method = "POST"; // Set form submission method

    // **Hidden Input Fields**

    // Order ID: dynamically generated order id
    const orderIdInput = document.createElement("input");
    orderIdInput.type = "hidden";
    orderIdInput.name = "orderId";
    orderIdInput.value =
      "order_test_" + Math.random().toString(36).substring(2, 15);
    form.appendChild(orderIdInput);

    // User ID: static customer identifier
    const userIdInput = document.createElement("input");
    userIdInput.type = "hidden";
    userIdInput.name = "userId";
    userIdInput.value = "cust_test_cd785f18d71349bfad9a6d516dcd26ea";
    form.appendChild(userIdInput);

    // Grand Total: static payment amount
    const grandTotalInput = document.createElement("input");
    grandTotalInput.type = "hidden";
    grandTotalInput.name = "grandTotal";
    grandTotalInput.value = "74";
    form.appendChild(grandTotalInput);

    // Basket ID: dynamically generated basket id
    const basketIdInput = document.createElement("input");
    basketIdInput.type = "hidden";
    basketIdInput.name = "basketId";
    basketIdInput.value =
      "basket_test_" + Math.random().toString(36).substring(2, 15);
    form.appendChild(basketIdInput);

    // Customer ID: static value
    const customerIdInput = document.createElement("input");
    customerIdInput.type = "hidden";
    customerIdInput.name = "customerId";
    customerIdInput.value = "cust_test_cd785f18d71349bfad9a6d516dcd26ea";
    form.appendChild(customerIdInput);

    // Set the form action (payment endpoint)
    form.action =
      "https://shop.villamarket.com/api/payment3/cardtoken";

    // **Payment Script Integration**

    // Create the script element for the payment gateway
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src =
      "https://dev-kpaymentgateway.kasikornbank.com/ui/v2/kpayment.min.js";
    // Configure required data attributes
    script.setAttribute("data-apikey", "pkey_test_22211JYBY6Vj43HyQhp2rK7pK3FEQpkwPz7D8");
    script.setAttribute("data-amount", "74.00");
    script.setAttribute("data-currency", "THB");
    script.setAttribute("data-payment-methods", "card");
    script.setAttribute("data-name", "Your Shop Name");
    script.setAttribute("data-mid", "401394788145001");
    script.setAttribute("data-customer-id", "cust_test_cd785f18d71349bfad9a6d516dcd26ea");

    // Append the script to the form
    form.appendChild(script);

    // Append the form to the container
    containerRef.current.appendChild(form);

    // Cleanup: Clear the container when the component unmounts
    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
    };
  }, []); // Runs only once on mount

  // Render the container div
  return <div ref={containerRef} />;
};

export default PaymentForm;
```

---

### 2. Vue.js Implementation

The Vue.js component uses lifecycle hooks (`mounted` and `beforeDestroy`) to inject and later clean up the form.

```vue
<template>
  <!-- The container div where the form will be injected -->
  <div ref="container"></div>
</template>

<script>
export default {
  name: "PaymentForm",
  mounted() {
    // Get a reference to the container element
    const container = this.$refs.container;
    if (!container) return;

    // Clear any previous content in the container
    container.innerHTML = "";

    // Create the form element
    const form = document.createElement("form");
    form.method = "POST"; // Set the form submission method

    // **Hidden Input Fields**

    // Order ID: dynamically generated order id
    const orderIdInput = document.createElement("input");
    orderIdInput.type = "hidden";
    orderIdInput.name = "orderId";
    orderIdInput.value =
      "order_test_" + Math.random().toString(36).substring(2, 15);
    form.appendChild(orderIdInput);

    // User ID: static customer identifier
    const userIdInput = document.createElement("input");
    userIdInput.type = "hidden";
    userIdInput.name = "userId";
    userIdInput.value = "cust_test_cd785f18d71349bfad9a6d516dcd26ea";
    form.appendChild(userIdInput);

    // Grand Total: static payment amount
    const grandTotalInput = document.createElement("input");
    grandTotalInput.type = "hidden";
    grandTotalInput.name = "grandTotal";
    grandTotalInput.value = "74";
    form.appendChild(grandTotalInput);

    // Basket ID: dynamically generated basket id
    const basketIdInput = document.createElement("input");
    basketIdInput.type = "hidden";
    basketIdInput.name = "basketId";
    basketIdInput.value =
      "basket_test_" + Math.random().toString(36).substring(2, 15);
    form.appendChild(basketIdInput);

    // Customer ID: static value
    const customerIdInput = document.createElement("input");
    customerIdInput.type = "hidden";
    customerIdInput.name = "customerId";
    customerIdInput.value = "cust_test_cd785f18d71349bfad9a6d516dcd26ea";
    form.appendChild(customerIdInput);

    // Set the form action (payment endpoint)
    form.action =
      "https://shop.villamarket.com/api/payment3/cardtoken";

    // **Payment Script Integration**

    // Create the script element for the payment gateway
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src =
      "https://dev-kpaymentgateway.kasikornbank.com/ui/v2/kpayment.min.js";
    // Configure required data attributes
    script.setAttribute("data-apikey", "pkey_test_22211JYBY6Vj43HyQhp2rK7pK3FEQpkwPz7D8");
    script.setAttribute("data-amount", "74.00");
    script.setAttribute("data-currency", "THB");
    script.setAttribute("data-payment-methods", "card");
    script.setAttribute("data-name", "Your Shop Name");
    script.setAttribute("data-mid", "401394788145001");
    script.setAttribute("data-customer-id", "cust_test_cd785f18d71349bfad9a6d516dcd26ea");

    // Append the script to the form
    form.appendChild(script);

    // Append the form to the container
    container.appendChild(form);
  },
  beforeDestroy() {
    // Cleanup: Clear the container before the component is destroyed
    if (this.$refs.container) {
      this.$refs.container.innerHTML = "";
    }
  },
};
</script>
```

---

## Explanation for Developers

### Common Steps in Both Implementations

1. **Initialization:**
   - **React:** Uses `useRef` to obtain a reference to the container `<div>` and `useEffect` to manipulate the DOM after the component mounts.
   - **Vue:** Uses the `ref` attribute to reference the container element and the `mounted` hook for DOM manipulation.

2. **Dynamic Form Construction:**
   - A `<form>` element is created and configured with the HTTP method (`POST`) and an action URL pointing to the payment endpoint.
   - **Hidden Inputs:**  
     The form includes hidden `<input>` fields for `orderId`, `userId`, `grandTotal`, `basketId`, and `customerId`. Some values (e.g., `orderId` and `basketId`) are generated dynamically.

3. **Payment Script Integration:**
   - An external `<script>` element is created with its `src` attribute pointing to the payment gateway URL.
   - The script is configured with data attributes (e.g., API key, amount, currency) required for the payment process.
   - The script is appended to the form to enable the payment functionality.

4. **Appending and Cleanup:**
   - The form is appended to the designated container.
   - Cleanup functions (React's `return` in `useEffect` and Vue's `beforeDestroy` hook) ensure that the container is cleared when the component is unmounted/destroyed.

### OpenAPI Specification

The provided OpenAPI snippet documents the backend payment endpoint. Developers should:
- Use this specification as a guide to understand the expected parameters and responses.
- Update the examples and descriptions according to the actual implementation details on the backend.

### How to Replicate

1. **Create the Component:**
   - For **React:** Create a new component file and implement the provided React code.
   - For **Vue:** Create a new `.vue` file and implement the provided Vue code.

2. **Update Values:**
   - Replace static values (e.g., API key, userId, grandTotal) with your actual configuration.
   - Ensure the form’s action attribute points to your production payment endpoint.

3. **Integrate External Script:**
   - Verify that the external script URL and data attributes match your payment provider’s requirements.
   - For a different payment gateway, refer to its documentation for the correct configuration.

4. **Test the Integration:**
   - Confirm that the form is rendered correctly and that the payment process initiates as expected upon form submission.
   - Validate the backend integration using the OpenAPI documentation as a reference.
