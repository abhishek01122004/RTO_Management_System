// Animations.js - Handles animations and transitions for the RTO Management System

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    activateAnimations();
    
    // Setup scroll animations
    setupScrollAnimations();
    
    // Add loading states to buttons
    setupLoadingButtons();
    
    // Initialize progress bars
    animateProgressBars();
    
    console.log('Animation system initialized successfully!');
});

// Activate animations for elements on page load
function activateAnimations() {
    // Add timed animations with staggered delay
    const fadeElements = document.querySelectorAll('.fade-in-element');
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, 100 * index);
    });
    
    // Slide in elements
    const slideElements = document.querySelectorAll('.slide-in-element');
    slideElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('slide-in');
        }, 100 * index);
    });
    
    // Scale in elements
    const scaleElements = document.querySelectorAll('.scale-in-element');
    scaleElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('scale-in');
        }, 100 * index);
    });
    
    // Bounce in elements
    const bounceElements = document.querySelectorAll('.bounce-in-element');
    bounceElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('bounce-in');
        }, 100 * index);
    });
    
    // Add hover animations
    addHoverAnimations();
}

// Add hover animations to elements
function addHoverAnimations() {
    // Card hover effects
    const hoverCards = document.querySelectorAll('.hover-card');
    hoverCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('hover-lift');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('hover-lift');
        });
    });
    
    // Button hover effects
    const animatedButtons = document.querySelectorAll('.btn-animated');
    animatedButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.classList.add('pulse');
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.remove('pulse');
        });
    });
}

// Setup animations that trigger on scroll
function setupScrollAnimations() {
    // Get all elements that should animate on scroll
    const scrollAnimElements = document.querySelectorAll('.scroll-anim');
    
    // Do nothing if no elements found
    if (!scrollAnimElements.length) return;
    
    // Create observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // Add animation class when element is in viewport
            if (entry.isIntersecting) {
                const animClass = entry.target.dataset.animation || 'fade-in';
                entry.target.classList.add(animClass);
                
                // Stop observing after animation is applied
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 }); // Trigger when at least 10% of the element is visible
    
    // Observe all elements
    scrollAnimElements.forEach(element => {
        observer.observe(element);
    });
}

// Add loading states to buttons
function setupLoadingButtons() {
    const forms = document.querySelectorAll('form:not(.no-loading-indicator)');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            
            if (submitButton && !submitButton.classList.contains('btn-loading')) {
                // Save original button text
                const originalText = submitButton.innerHTML;
                submitButton.setAttribute('data-original-text', originalText);
                
                // Add spinner and loading text
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
                submitButton.classList.add('btn-loading');
                submitButton.disabled = true;
                
                // Reset button if form submission takes too long (10 seconds)
                setTimeout(() => {
                    if (submitButton.classList.contains('btn-loading')) {
                        submitButton.innerHTML = submitButton.getAttribute('data-original-text');
                        submitButton.classList.remove('btn-loading');
                        submitButton.disabled = false;
                    }
                }, 10000);
            }
        });
    });
}

// Animate progress bars
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('aria-valuenow') + '%';
        
        // Initial state
        bar.style.width = '0%';
        
        // Create animation timeline
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = targetWidth;
        }, 200);
    });
}

// Animation for step indicators
function animateStepIndicator(currentStep) {
    const steps = document.querySelectorAll('.step');
    
    steps.forEach((step, index) => {
        if (index < currentStep) {
            // Mark previous steps as completed
            step.classList.remove('active');
            step.classList.add('completed');
        } else if (index === currentStep) {
            // Mark current step as active
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            // Reset future steps
            step.classList.remove('active', 'completed');
        }
    });
}

// Animated counter for statistics
function animateCounter(element, targetValue, duration = 2000) {
    let startTime = null;
    const startValue = parseInt(element.textContent) || 0;
    
    function updateCounter(timestamp) {
        if (!startTime) startTime = timestamp;
        
        const elapsed = timestamp - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smoother animation
        const easedProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        
        const currentValue = Math.floor(startValue + (targetValue - startValue) * easedProgress);
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = targetValue.toLocaleString();
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Animate all counters on the page
function animateAllCounters() {
    const counterElements = document.querySelectorAll('.counter-element');
    
    counterElements.forEach(counter => {
        const targetValue = parseInt(counter.getAttribute('data-target'));
        if (!isNaN(targetValue)) {
            animateCounter(counter, targetValue);
        }
    });
}

// Add shake animation to an element
function shakeElement(element) {
    element.classList.add('shake-animation');
    
    // Remove animation class after it completes
    setTimeout(() => {
        element.classList.remove('shake-animation');
    }, 500);
}

// Typewriter effect for text
function typewriterEffect(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Add pulse animation to an element
function pulseElement(element, duration = 1000) {
    element.classList.add('pulse-animation');
    
    // Remove animation class after it completes
    setTimeout(() => {
        element.classList.remove('pulse-animation');
    }, duration);
}

// Animate timeline entries
function animateTimeline() {
    const timelineItems = document.querySelectorAll('.timeline-item');
    
    timelineItems.forEach((item, index) => {
        // Create a slight delay for each item to create a staggered effect
        setTimeout(() => {
            item.classList.add('slide-in');
        }, 200 * index);
    });
}

// Add notification popup animation
function animateNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} slide-in-right`;
    
    // Add icon based on notification type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${icon}"></i>
            <p>${message}</p>
        </div>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to notification container or create one if it doesn't exist
    let notificationContainer = document.querySelector('.notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    notificationContainer.appendChild(notification);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.add('slide-out-right');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto close after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('slide-out-right');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, duration);
}

// CSS Animation Keyframes (added via JavaScript)
function addAnimationKeyframes() {
    // If keyframes already exist, don't add them again
    if (document.getElementById('animation-keyframes')) return;
    
    const keyframesStyle = document.createElement('style');
    keyframesStyle.id = 'animation-keyframes';
    
    keyframesStyle.textContent = `
        @keyframes shake-animation {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        
        @keyframes pulse-animation {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        @keyframes slide-in-right {
            0% { transform: translateX(100%); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slide-out-right {
            0% { transform: translateX(0); opacity: 1; }
            100% { transform: translateX(100%); opacity: 0; }
        }
        
        .shake-animation {
            animation: shake-animation 0.5s ease-in-out;
        }
        
        .pulse-animation {
            animation: pulse-animation 0.5s ease-in-out;
        }
        
        .slide-in-right {
            animation: slide-in-right 0.3s ease-in-out forwards;
        }
        
        .slide-out-right {
            animation: slide-out-right 0.3s ease-in-out forwards;
        }
        
        .notification-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 350px;
        }
        
        .notification {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            margin-bottom: 10px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .notification-content {
            padding: 15px;
            display: flex;
            align-items: center;
        }
        
        .notification-content i {
            margin-right: 10px;
            font-size: 1.2rem;
        }
        
        .notification-content p {
            margin: 0;
        }
        
        .notification-close {
            background: transparent;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            color: #999;
            transition: color 0.2s ease;
        }
        
        .notification-close:hover {
            color: #333;
        }
        
        .notification-info {
            border-left: 4px solid #3498db;
        }
        
        .notification-success {
            border-left: 4px solid #2ecc71;
        }
        
        .notification-warning {
            border-left: 4px solid #f39c12;
        }
        
        .notification-error {
            border-left: 4px solid #e74c3c;
        }
        
        .notification-info i {
            color: #3498db;
        }
        
        .notification-success i {
            color: #2ecc71;
        }
        
        .notification-warning i {
            color: #f39c12;
        }
        
        .notification-error i {
            color: #e74c3c;
        }
    `;
    
    document.head.appendChild(keyframesStyle);
}

// Initialize additional animations when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add animation keyframes to document
    addAnimationKeyframes();
    
    // Animate timelines if they exist
    if (document.querySelector('.timeline-item')) {
        animateTimeline();
    }
    
    // Animate all counters
    if (document.querySelector('.counter-element')) {
        animateAllCounters();
    }
});
