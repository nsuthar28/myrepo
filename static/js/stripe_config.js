console.log("Sanity Check!");

// Get Stripe publishable key

function connect(price_id){
  console.log("price_id", price_id)
  fetch("/config/")
  .then((result) => result.json())
  .then((data) => { 
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);

    
      
    // Get Checkout Session ID
    fetch("/create-checkout-session/"+price_id)
    // The response result from a fetch request is a "ReadableStream".
    .then((result) => {
        // use result.json() to resolve the promise and obtain data, which happens to have a publickey member in it.
        return result.json();
      })
      .then((data) => { 
        console.log(data);

        // Redirect to Stripe Checkout
        return stripe.redirectToCheckout({ sessionId: data.sessionId });
      })
      .then((res) => {
        console.log(res);
      });
    });
} 
  
      
