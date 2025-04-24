// Payments.js - Handles payment integrations for RTO Management System

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Razorpay payments if on a payment page
    initializeRazorpayPayment();
    
    // Handle payment verification
    setupPaymentVerification();
    
    console.log('Payment system initialized successfully!');
});

// Initialize Razorpay payment
function initializeRazorpayPayment() {
    const paymentForm = document.getElementById('razorpayPaymentForm');
    if (!paymentForm) return; // Not on a payment page
    
    // Get payment details from data attributes
    const orderDetails = {
        key: paymentForm.getAttribute('data-key'),
        order_id: paymentForm.getAttribute('data-order-id'),
        amount: parseInt(paymentForm.getAttribute('data-amount')),
        currency: paymentForm.getAttribute('data-currency') || 'INR',
        name: paymentForm.getAttribute('data-name') || 'RTO Management System',
        description: paymentForm.getAttribute('data-description') || 'Payment for RTO Service',
        image: paymentForm.getAttribute('data-image'),
        prefill: {
            name: paymentForm.getAttribute('data-user-name') || '',
            email: paymentForm.getAttribute('data-user-email') || '',
            contact: paymentForm.getAttribute('data-user-phone') || ''
        },
        theme: {
            color: '#3498db'
        }
    };
    
    // Initialize pay now button
    const payButton = document.getElementById('razorpayButton');
    if (payButton) {
        payButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Show loading state
            payButton.disabled = true;
            payButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Initializing Payment...';
            
            // Launch Razorpay payment screen
            startRazorpayPayment(orderDetails)
                .then(() => {
                    // Payment screen launched, no need to update button as page will redirect
                    console.log('Payment screen opened');
                })
                .catch(error => {
                    // Reset button state on error
                    payButton.disabled = false;
                    payButton.innerHTML = 'Pay Now';
                    
                    // Show error message
                    const errorContainer = document.getElementById('paymentError');
                    if (errorContainer) {
                        errorContainer.innerHTML = `
                            <div class="alert alert-danger fade-in">
                                <i class="fas fa-exclamation-circle me-2"></i> ${error.message || 'Failed to initialize payment. Please try again.'}
                            </div>
                        `;
                    }
                    
                    console.error('Payment initialization error:', error);
                });
        });
    }
}

// Start Razorpay payment
function startRazorpayPayment(options) {
    return new Promise((resolve, reject) => {
        try {
            const razorpay = new Razorpay(options);
            
            // Handle payment failures
            razorpay.on('payment.failed', function(response) {
                // Show error message
                const errorContainer = document.getElementById('paymentError');
                if (errorContainer) {
                    errorContainer.innerHTML = `
                        <div class="alert alert-danger fade-in">
                            <i class="fas fa-exclamation-circle me-2"></i> Payment Failed: ${response.error.description}
                        </div>
                    `;
                }
                
                // Reset button state
                const payButton = document.getElementById('razorpayButton');
                if (payButton) {
                    payButton.disabled = false;
                    payButton.innerHTML = 'Try Again';
                }
                
                reject(new Error(response.error.description));
            });
            
            // Open Razorpay payment form
            razorpay.open();
            resolve();
            
        } catch (error) {
            reject(error);
        }
    });
}

// Handle payment verification
function setupPaymentVerification() {
    const verificationForm = document.getElementById('paymentVerificationForm');
    if (!verificationForm) return; // Not on a payment verification page
    
    // Listen to the form submission that occurs after Razorpay payment completion
    verificationForm.addEventListener('submit', function(e) {
        // Show a loading indicator during form submission
        const submitButton = this.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Verifying Payment...';
        }
    });
}

// Display payment success message
function showPaymentSuccess(message) {
    const container = document.getElementById('paymentStatus');
    if (!container) return;
    
    container.innerHTML = `
        <div class="payment-success-container text-center py-4">
            <div class="payment-success-icon mb-3">
                <i class="fas fa-check-circle text-success fa-5x"></i>
            </div>
            <h3 class="text-success mb-3">Payment Successful!</h3>
            <p class="mb-4">${message || 'Your payment has been processed successfully.'}</p>
            <div class="d-flex justify-content-center">
                <a href="/dashboard/" class="btn btn-primary me-2">
                    <i class="fas fa-tachometer-alt me-2"></i> Go to Dashboard
                </a>
                <button onclick="window.print()" class="btn btn-outline-secondary">
                    <i class="fas fa-print me-2"></i> Print Receipt
                </button>
            </div>
        </div>
    `;
    
    // Add slide-in animation
    container.classList.add('slide-in');
}

// Display payment error message
function showPaymentError(message) {
    const container = document.getElementById('paymentStatus');
    if (!container) return;
    
    container.innerHTML = `
        <div class="payment-error-container text-center py-4">
            <div class="payment-error-icon mb-3">
                <i class="fas fa-times-circle text-danger fa-5x"></i>
            </div>
            <h3 class="text-danger mb-3">Payment Failed</h3>
            <p class="mb-4">${message || 'There was an issue processing your payment. Please try again.'}</p>
            <div>
                <button onclick="window.history.back()" class="btn btn-primary">
                    <i class="fas fa-arrow-left me-2"></i> Go Back and Try Again
                </button>
            </div>
        </div>
    `;
    
    // Add slide-in animation
    container.classList.add('slide-in');
}

// Generate payment receipt
function generatePaymentReceipt(paymentData) {
    const container = document.getElementById('paymentReceipt');
    if (!container) return;
    
    // Format date
    const paymentDate = new Date(paymentData.payment_date);
    const formattedDate = paymentDate.toLocaleDateString('en-IN') + ' ' + paymentDate.toLocaleTimeString('en-IN');
    
    container.innerHTML = `
        <div class="card receipt-card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Payment Receipt</h5>
            </div>
            <div class="card-body">
                <div class="text-center mb-4">
                    <h4 class="mb-1">Regional Transport Office</h4>
                    <p class="text-muted mb-0">Government of India</p>
                </div>
                
                <div class="receipt-details">
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <p><strong>Payment ID:</strong> ${paymentData.transaction_id}</p>
                            <p><strong>Date & Time:</strong> ${formattedDate}</p>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <p><strong>Payment Status:</strong> <span class="badge bg-success">Paid</span></p>
                            <p><strong>Payment Method:</strong> ${paymentData.payment_method}</p>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <h6 class="mb-2">Payment For</h6>
                            <p><strong>${paymentData.payment_for_type}</strong></p>
                            <p>${paymentData.payment_for_details}</p>
                        </div>
                        <div class="col-md-6">
                            <h6 class="mb-2">Paid By</h6>
                            <p><strong>${paymentData.payer_name}</strong></p>
                            <p>${paymentData.payer_email}</p>
                            <p>${paymentData.payer_phone || ''}</p>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <div class="payment-amount text-end">
                        <h6>Amount Paid</h6>
                        <h3 class="text-primary">₹ ${parseFloat(paymentData.amount).toFixed(2)}</h3>
                    </div>
                </div>
            </div>
            <div class="card-footer text-center">
                <p class="text-muted mb-0">Thank you for your payment!</p>
            </div>
        </div>
        
        <div class="text-center">
            <button onclick="window.print()" class="btn btn-outline-primary">
                <i class="fas fa-print me-2"></i> Print Receipt
            </button>
        </div>
    `;
}

// Handle challan payment
function handleChallanPayment() {
    const challanPayButton = document.getElementById('challanPayButton');
    if (!challanPayButton) return;
    
    challanPayButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        const challanNumber = this.getAttribute('data-challan-number');
        const amount = parseFloat(this.getAttribute('data-amount'));
        
        if (!challanNumber || isNaN(amount)) {
            console.error('Invalid challan details');
            return;
        }
        
        // Redirect to payment page
        window.location.href = `/challan/pay/${challanNumber}/`;
    });
}

// Handle license payment
function handleLicensePayment() {
    const licensePayButton = document.getElementById('licensePayButton');
    if (!licensePayButton) return;
    
    licensePayButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        const applicationNumber = this.getAttribute('data-application-number');
        const amount = parseFloat(this.getAttribute('data-amount'));
        
        if (!applicationNumber || isNaN(amount)) {
            console.error('Invalid license application details');
            return;
        }
        
        // Redirect to payment page
        window.location.href = `/license/application/${applicationNumber}/payment/`;
    });
}

// Handle vehicle registration payment
function handleVehiclePayment() {
    const vehiclePayButton = document.getElementById('vehiclePayButton');
    if (!vehiclePayButton) return;
    
    vehiclePayButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        const regNumber = this.getAttribute('data-reg-number');
        const amount = parseFloat(this.getAttribute('data-amount'));
        
        if (!regNumber || isNaN(amount)) {
            console.error('Invalid vehicle registration details');
            return;
        }
        
        // Redirect to payment page
        window.location.href = `/vehicle/registration/${regNumber}/payment/`;
    });
}

// Initialize all payment buttons
document.addEventListener('DOMContentLoaded', function() {
    handleChallanPayment();
    handleLicensePayment();
    handleVehiclePayment();
});
