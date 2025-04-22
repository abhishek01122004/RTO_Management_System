// Main JavaScript file for RTO Management System

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize popovers
    initializePopovers();
    
    // Handle flash messages dismissal
    setupFlashMessages();
    
    // Add smooth scrolling for anchor links
    setupSmoothScrolling();
    
    // Set up search functionality
    setupSearch();
    
    // Initialize status tracking
    initializeStatusTracking();
    
    // Activate animation for elements
    activateAnimations();
    
    // Setup form validation
    setupFormValidation();
    
    // Initialize dashboard counters animation
    animateCounters();
    
    // Handle notification system
    setupNotifications();
    
    // Add mobile menu functionality
    setupMobileMenu();
    
    console.log('RTO Management System initialized successfully!');
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

// Initialize Bootstrap popovers
function initializePopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

// Set up flash message dismissal
function setupFlashMessages() {
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
        
        // Add fade out animation
        alert.addEventListener('close.bs.alert', function() {
            this.style.transition = 'opacity 0.5s ease';
            this.style.opacity = '0';
        });
    });
}

// Smooth scrolling for anchor links
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]:not([data-bs-toggle])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Set up search functionality
function setupSearch() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[type="search"]');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                // Add shake animation to input
                searchInput.classList.add('shake');
                setTimeout(() => {
                    searchInput.classList.remove('shake');
                }, 500);
            }
        });
    }
}

// Initialize status tracking functionality
function initializeStatusTracking() {
    const trackingForms = document.querySelectorAll('.status-tracking-form');
    trackingForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const applicationNumber = this.querySelector('input[name="application_number"]').value;
            const applicationType = this.querySelector('select[name="application_type"]').value;
            const resultContainer = document.getElementById('trackingResult');
            
            if (!applicationNumber || !applicationType) {
                showError(resultContainer, 'Please provide both application type and number.');
                return;
            }
            
            // Show loading indicator
            resultContainer.innerHTML = '<div class="text-center my-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Fetching status information...</p></div>';
            
            // Fetch application status
            fetch(`/dashboard/status/${applicationType}/${applicationNumber}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Application not found');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    displayApplicationStatus(resultContainer, data.data, applicationType);
                } else {
                    showError(resultContainer, data.error || 'Could not retrieve application status.');
                }
            })
            .catch(error => {
                showError(resultContainer, error.message || 'An error occurred while retrieving the status.');
            });
        });
    });
}

// Display application status information
function displayApplicationStatus(container, data, applicationType) {
    let statusHtml = '';
    
    if (applicationType === 'license') {
        statusHtml = `
            <div class="card slide-in">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">License Application Status</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Application Number:</strong> ${data.application_number}</p>
                            <p><strong>Applicant Name:</strong> ${data.applicant_name}</p>
                            <p><strong>Application Type:</strong> ${data.application_type}</p>
                            <p><strong>License Type:</strong> ${data.license_type}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Application Date:</strong> ${data.application_date}</p>
                            <p><strong>Current Status:</strong> <span class="status-badge status-${data.current_status.toLowerCase()}">${data.current_status}</span></p>
                            <p><strong>Payment Status:</strong> ${data.payment_status}</p>
                        </div>
                    </div>
                    ${data.test_date ? `
                    <hr>
                    <h6 class="mb-3">Test Information</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Test Type:</strong> ${data.test_type}</p>
                            <p><strong>Test Date:</strong> ${data.test_date}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Test Venue:</strong> ${data.test_venue}</p>
                            <p><strong>Test Status:</strong> ${data.test_completed ? (data.test_result || 'Pending Result') : 'Scheduled'}</p>
                        </div>
                    </div>
                    ` : ''}
                    ${data.license_number ? `
                    <hr>
                    <h6 class="mb-3">License Information</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>License Number:</strong> ${data.license_number}</p>
                            <p><strong>Issued Date:</strong> ${data.issued_date}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Valid Until:</strong> ${data.valid_until}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    } else if (applicationType === 'vehicle') {
        statusHtml = `
            <div class="card slide-in">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Vehicle Registration Status</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Application Number:</strong> ${data.application_number}</p>
                            <p><strong>Owner Name:</strong> ${data.owner_name}</p>
                            <p><strong>Registration Type:</strong> ${data.registration_type}</p>
                            <p><strong>Vehicle Category:</strong> ${data.vehicle_category}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Make & Model:</strong> ${data.make_model}</p>
                            <p><strong>Application Date:</strong> ${data.application_date}</p>
                            <p><strong>Current Status:</strong> <span class="status-badge status-${data.current_status.toLowerCase()}">${data.current_status}</span></p>
                            <p><strong>Payment Status:</strong> ${data.payment_status}</p>
                        </div>
                    </div>
                    ${data.inspection_date ? `
                    <hr>
                    <h6 class="mb-3">Inspection Information</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Inspection Date:</strong> ${data.inspection_date}</p>
                            <p><strong>Inspection Venue:</strong> ${data.inspection_venue}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Inspection Status:</strong> ${data.inspection_completed ? (data.inspection_result || 'Pending Result') : 'Scheduled'}</p>
                        </div>
                    </div>
                    ` : ''}
                    ${data.registration_number ? `
                    <hr>
                    <h6 class="mb-3">Registration Information</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Registration Number:</strong> ${data.registration_number}</p>
                            <p><strong>Registration Date:</strong> ${data.registration_date}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Valid Until:</strong> ${data.valid_until}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = statusHtml;
}

// Show error message
function showError(container, message) {
    container.innerHTML = `
        <div class="alert alert-danger fade-in" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i> ${message}
        </div>
    `;
}

// Animate dashboard counters
function animateCounters() {
    const counters = document.querySelectorAll('.counter-value');
    
    counters.forEach(counter => {
        const targetValue = parseInt(counter.getAttribute('data-target'));
        if (isNaN(targetValue)) return;
        
        const duration = 2000; // Animation duration in milliseconds
        const startTime = performance.now();
        let currentValue = 0;
        
        function updateCounter(timestamp) {
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            currentValue = Math.floor(targetValue * progress);
            counter.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = targetValue.toLocaleString();
            }
        }
        
        requestAnimationFrame(updateCounter);
    });
}

// Setup notifications handling
function setupNotifications() {
    const notificationToggle = document.getElementById('notificationToggle');
    if (notificationToggle) {
        notificationToggle.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = document.getElementById('notificationDropdown');
            
            // Mark notifications as read when dropdown is opened
            if (!dropdown.classList.contains('show')) {
                const unreadNotifications = document.querySelectorAll('.notification-item.unread');
                if (unreadNotifications.length > 0) {
                    markNotificationsAsRead();
                }
            }
        });
    }
}

// Mark notifications as read
function markNotificationsAsRead() {
    fetch('/notifications/mark-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelectorAll('.notification-item.unread').forEach(notification => {
                notification.classList.remove('unread');
            });
            
            // Update notification counter
            const notificationBadge = document.getElementById('notificationBadge');
            if (notificationBadge) {
                notificationBadge.style.display = 'none';
            }
        }
    })
    .catch(error => {
        console.error('Error marking notifications as read:', error);
    });
}

// Get CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Setup mobile menu
function setupMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const mobileMenu = document.getElementById('mobileMenu');
            if (mobileMenu) {
                mobileMenu.classList.toggle('show');
                this.setAttribute('aria-expanded', mobileMenu.classList.contains('show'));
            }
        });
    }
}

// Function to toggle password visibility
function togglePasswordVisibility(inputId, toggleBtnId) {
    const passwordInput = document.getElementById(inputId);
    const toggleBtn = document.getElementById(toggleBtnId);
    
    if (passwordInput && toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle icon
            if (type === 'password') {
                this.innerHTML = '<i class="fas fa-eye"></i>';
            } else {
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            }
        });
    }
}

// Document upload preview function
function previewDocument(inputElement, previewElementId) {
    inputElement.addEventListener('change', function() {
        const previewElement = document.getElementById(previewElementId);
        if (!previewElement) return;
        
        const file = this.files[0];
        if (!file) {
            previewElement.innerHTML = '';
            return;
        }
        
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        // Display appropriate preview based on file type
        if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExtension)) {
            // Image preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewElement.innerHTML = `
                    <div class="document-preview-container">
                        <img src="${e.target.result}" alt="Document Preview" class="img-thumbnail">
                        <p class="text-center mt-2">${file.name} (${(file.size / 1024).toFixed(2)} KB)</p>
                    </div>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            // Generic file preview
            let iconClass = 'fas fa-file';
            
            if (['pdf'].includes(fileExtension)) {
                iconClass = 'fas fa-file-pdf';
            } else if (['doc', 'docx'].includes(fileExtension)) {
                iconClass = 'fas fa-file-word';
            } else if (['xls', 'xlsx'].includes(fileExtension)) {
                iconClass = 'fas fa-file-excel';
            }
            
            previewElement.innerHTML = `
                <div class="document-preview-container text-center">
                    <i class="${iconClass} fa-4x mb-3"></i>
                    <p>${file.name} (${(file.size / 1024).toFixed(2)} KB)</p>
                </div>
            `;
        }
    });
}
