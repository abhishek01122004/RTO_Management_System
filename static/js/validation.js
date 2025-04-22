// Validation.js - Form validation for RTO Management System

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    setupFormValidation();
    
    // Set up custom input masks
    setupInputMasks();
    
    console.log('Form validation initialized successfully!');
});

// Setup form validation
function setupFormValidation() {
    // Get all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop through forms and prevent submission if there are invalid fields
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Perform custom validations first
            const isCustomValid = performCustomValidations(this);
            
            if (!this.checkValidity() || !isCustomValid) {
                event.preventDefault();
                event.stopPropagation();
                
                // Find first invalid field and focus it
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    
                    // Scroll to the invalid element
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Add shake animation to the invalid element
                    firstInvalid.classList.add('shake');
                    setTimeout(() => {
                        firstInvalid.classList.remove('shake');
                    }, 500);
                }
            }
            
            // Add 'was-validated' class to show validation styles
            this.classList.add('was-validated');
        }, false);
        
        // Add live validation for each input
        setupLiveValidation(form);
    });
}

// Setup live validation as the user types
function setupLiveValidation(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Check validity when input changes
        input.addEventListener('input', function() {
            const isValid = this.checkValidity();
            
            // Get the validation message element if it exists
            let feedbackElement = this.nextElementSibling;
            if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback')) {
                // Create feedback element if it doesn't exist
                feedbackElement = document.createElement('div');
                feedbackElement.className = 'invalid-feedback';
                this.parentNode.insertBefore(feedbackElement, this.nextSibling);
            }
            
            // Update validation message based on validity
            if (!isValid) {
                feedbackElement.textContent = this.validationMessage;
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            }
        });
    });
}

// Perform custom validations that extend browser's built-in validation
function performCustomValidations(form) {
    let isValid = true;
    
    // Password confirmation validation
    const password = form.querySelector('input[name="password1"]');
    const confirmPassword = form.querySelector('input[name="password2"]');
    
    if (password && confirmPassword) {
        if (password.value !== confirmPassword.value) {
            setInvalidState(confirmPassword, 'Passwords do not match');
            isValid = false;
        } else {
            setValidState(confirmPassword);
        }
    }
    
    // Aadhaar number validation (12 digits)
    const aadhaar = form.querySelector('input[name="aadhaar_number"]');
    if (aadhaar && aadhaar.value) {
        const aadhaarRegex = /^\d{12}$/;
        if (!aadhaarRegex.test(aadhaar.value)) {
            setInvalidState(aadhaar, 'Aadhaar number must be exactly 12 digits');
            isValid = false;
        } else {
            setValidState(aadhaar);
        }
    }
    
    // Phone number validation
    const phone = form.querySelector('input[name="phone_number"]');
    if (phone && phone.value) {
        const phoneRegex = /^[6-9]\d{9}$/;
        if (!phoneRegex.test(phone.value)) {
            setInvalidState(phone, 'Please enter a valid 10-digit Indian mobile number');
            isValid = false;
        } else {
            setValidState(phone);
        }
    }
    
    // Vehicle registration number validation
    const vehicleRegNo = form.querySelector('input[name="vehicle_number"]');
    if (vehicleRegNo && vehicleRegNo.value) {
        // Format: XX 00 XX 0000 (state code, RTO code, series, number)
        const regNoRegex = /^[A-Z]{2}\s\d{2}\s[A-Z]{1,2}\s\d{1,4}$/;
        if (!regNoRegex.test(vehicleRegNo.value)) {
            setInvalidState(vehicleRegNo, 'Please enter a valid vehicle registration number (e.g., KA 01 AB 1234)');
            isValid = false;
        } else {
            setValidState(vehicleRegNo);
        }
    }
    
    // License number validation
    const licenseNo = form.querySelector('input[name="license_number"]');
    if (licenseNo && licenseNo.value) {
        // Format: DL12345678901234 (DL followed by 14 digits)
        const licenseRegex = /^(DL|dl)[0-9A-Z]{14}$/i;
        if (!licenseRegex.test(licenseNo.value)) {
            setInvalidState(licenseNo, 'Please enter a valid driving license number');
            isValid = false;
        } else {
            setValidState(licenseNo);
        }
    }
    
    // Chassis number validation
    const chassisNo = form.querySelector('input[name="chassis_number"]');
    const confirmChassisNo = form.querySelector('input[name="confirm_chassis_number"]');
    
    if (chassisNo && confirmChassisNo) {
        if (chassisNo.value !== confirmChassisNo.value) {
            setInvalidState(confirmChassisNo, 'Chassis numbers do not match');
            isValid = false;
        } else {
            setValidState(confirmChassisNo);
        }
    }
    
    // File size validation
    const fileInputs = form.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        if (input.files && input.files.length > 0) {
            const file = input.files[0];
            const maxSize = parseInt(input.getAttribute('data-max-size') || 5) * 1024 * 1024; // Default 5MB
            
            if (file.size > maxSize) {
                const maxSizeMB = maxSize / (1024 * 1024);
                setInvalidState(input, `File size must not exceed ${maxSizeMB}MB`);
                isValid = false;
            } else {
                setValidState(input);
            }
            
            // Check for allowed file types
            const allowedTypes = input.getAttribute('data-allowed-types');
            if (allowedTypes) {
                const types = allowedTypes.split(',').map(type => type.trim());
                const fileExt = file.name.split('.').pop().toLowerCase();
                
                if (!types.includes(fileExt)) {
                    setInvalidState(input, `Only ${allowedTypes} files are allowed`);
                    isValid = false;
                } else {
                    setValidState(input);
                }
            }
        }
    });
    
    // Date validations
    validateDateFields(form, isValid);
    
    return isValid;
}

// Validate date related fields
function validateDateFields(form, isValid) {
    // Date of birth validation (must be at least 18 years old for license)
    const dob = form.querySelector('input[name="date_of_birth"]');
    if (dob && dob.value) {
        const dobDate = new Date(dob.value);
        const today = new Date();
        let age = today.getFullYear() - dobDate.getFullYear();
        const monthDiff = today.getMonth() - dobDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dobDate.getDate())) {
            age--;
        }
        
        // Check if it's a license application form
        const isLicenseForm = form.getAttribute('id') === 'licenseApplicationForm';
        const minAge = isLicenseForm ? 18 : 0;
        
        if (age < minAge) {
            setInvalidState(dob, `You must be at least ${minAge} years old`);
            isValid = false;
        } else {
            setValidState(dob);
        }
    }
    
    // Insurance validity date validation (must be a future date)
    const insuranceValidity = form.querySelector('input[name="insurance_validity"]');
    if (insuranceValidity && insuranceValidity.value) {
        const validityDate = new Date(insuranceValidity.value);
        const today = new Date();
        
        if (validityDate <= today) {
            setInvalidState(insuranceValidity, 'Insurance validity date must be in the future');
            isValid = false;
        } else {
            setValidState(insuranceValidity);
        }
    }
    
    // Purchase date validation (cannot be in future)
    const purchaseDate = form.querySelector('input[name="purchase_date"]');
    if (purchaseDate && purchaseDate.value) {
        const pDate = new Date(purchaseDate.value);
        const today = new Date();
        
        if (pDate > today) {
            setInvalidState(purchaseDate, 'Purchase date cannot be in the future');
            isValid = false;
        } else {
            setValidState(purchaseDate);
        }
    }
    
    return isValid;
}

// Set invalid state for an input element
function setInvalidState(element, message) {
    element.classList.add('is-invalid');
    element.classList.remove('is-valid');
    
    // Find or create the feedback element
    let feedback = element.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        element.parentNode.insertBefore(feedback, element.nextSibling);
    }
    
    feedback.textContent = message;
}

// Set valid state for an input element
function setValidState(element) {
    element.classList.add('is-valid');
    element.classList.remove('is-invalid');
}

// Setup input masks for common fields
function setupInputMasks() {
    // Phone number mask
    const phoneInputs = document.querySelectorAll('input[name="phone_number"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) {
                value = value.substring(0, 10);
            }
            e.target.value = value;
        });
    });
    
    // Aadhaar number mask
    const aadhaarInputs = document.querySelectorAll('input[name="aadhaar_number"]');
    aadhaarInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 12) {
                value = value.substring(0, 12);
            }
            
            // Add spaces for readability
            if (value.length >= 4 && value.length < 8) {
                value = value.substring(0, 4) + ' ' + value.substring(4);
            } else if (value.length >= 8) {
                value = value.substring(0, 4) + ' ' + value.substring(4, 8) + ' ' + value.substring(8);
            }
            
            e.target.value = value;
        });
    });
    
    // Vehicle registration number mask
    const regNoInputs = document.querySelectorAll('input[name="vehicle_number"]');
    regNoInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.toUpperCase();
            
            // Remove any characters that aren't letters, numbers, or spaces
            value = value.replace(/[^A-Z0-9\s]/g, '');
            
            // Format as XX 00 XX 0000
            if (value.length > 0) {
                let formattedValue = '';
                let parts = value.split(' ').join(''); // Remove existing spaces
                
                // Add first space after 2 characters
                if (parts.length > 2) {
                    formattedValue = parts.substring(0, 2) + ' ';
                    parts = parts.substring(2);
                    
                    // Add second space after next 2 characters
                    if (parts.length > 2) {
                        formattedValue += parts.substring(0, 2) + ' ';
                        parts = parts.substring(2);
                        
                        // Add third space after next 2 characters
                        if (parts.length > 2) {
                            formattedValue += parts.substring(0, 2) + ' ';
                            parts = parts.substring(2);
                            
                            // Add remaining characters
                            formattedValue += parts.substring(0, 4);
                        } else {
                            formattedValue += parts;
                        }
                    } else {
                        formattedValue += parts;
                    }
                } else {
                    formattedValue = parts;
                }
                
                value = formattedValue;
            }
            
            e.target.value = value;
        });
    });
}

// Validate email address
function isValidEmail(email) {
    const regex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    return regex.test(email);
}

// Validate a strong password
function isStrongPassword(password) {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
}

// Get password strength
function getPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 1;
    if (password.match(/[a-z]+/)) strength += 1;
    if (password.match(/[A-Z]+/)) strength += 1;
    if (password.match(/[0-9]+/)) strength += 1;
    if (password.match(/[^a-zA-Z0-9]+/)) strength += 1;
    
    return strength;
}

// Update password strength meter
function updatePasswordStrengthMeter(password, meterElement) {
    if (!meterElement) return;
    
    const strength = getPasswordStrength(password);
    
    // Update the width of the strength meter
    const percentage = (strength / 5) * 100;
    meterElement.style.width = percentage + '%';
    
    // Update the color based on strength
    if (strength < 2) {
        meterElement.className = 'password-strength-meter bg-danger';
        meterElement.setAttribute('aria-valuenow', 20);
    } else if (strength < 4) {
        meterElement.className = 'password-strength-meter bg-warning';
        meterElement.setAttribute('aria-valuenow', 60);
    } else {
        meterElement.className = 'password-strength-meter bg-success';
        meterElement.setAttribute('aria-valuenow', 100);
    }
}

// Initialize password strength meter
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[name="password1"]');
    const strengthMeter = document.getElementById('passwordStrengthMeter');
    
    if (passwordInput && strengthMeter) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrengthMeter(this.value, strengthMeter);
        });
    }
});
