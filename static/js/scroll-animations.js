// Custom Scroll Animation System
// Lightweight alternative to AOS with better performance

class ScrollAnimations {
    constructor() {
        this.elements = [];
        this.observer = null;
        this.init();
    }

    init() {
        // Find all elements that should be animated
        this.elements = document.querySelectorAll('.scroll-animate, .card-animate, .text-reveal');
        
        // Use Intersection Observer for better performance
        this.createObserver();
        
        // Observe all elements
        this.elements.forEach(element => {
            this.observer.observe(element);
        });

        // Fallback for older browsers
        if (!window.IntersectionObserver) {
            this.fallbackScrollHandler();
        }
    }

    createObserver() {
        const options = {
            threshold: 0.1, // Trigger when 10% of element is visible
            rootMargin: '0px 0px -50px 0px' // Start animation 50px before element enters viewport
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateElement(entry.target);
                    // Stop observing once animated (optional - remove if you want reverse animations)
                    this.observer.unobserve(entry.target);
                }
            });
        }, options);
    }

    animateElement(element) {
        // Add a small delay for smoother effect
        setTimeout(() => {
            element.classList.add('visible');
        }, 50);
    }

    // Fallback for browsers without Intersection Observer
    fallbackScrollHandler() {
        const checkVisibility = () => {
            this.elements.forEach(element => {
                if (!element.classList.contains('visible')) {
                    const rect = element.getBoundingClientRect();
                    const windowHeight = window.innerHeight;
                    
                    // Element is visible if its top is within the viewport
                    if (rect.top < windowHeight - 100) {
                        this.animateElement(element);
                    }
                }
            });
        };

        // Throttle scroll events for better performance
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    checkVisibility();
                    ticking = false;
                });
                ticking = true;
            }
        });

        // Check on load
        checkVisibility();
    }

    // Method to manually trigger animations
    triggerAnimation(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => this.animateElement(element));
    }

    // Method to reset animations (useful for dynamic content)
    resetAnimations(selector) {
        const elements = document.querySelectorAll(selector || '.scroll-animate, .card-animate, .text-reveal');
        elements.forEach(element => {
            element.classList.remove('visible');
            if (this.observer) {
                this.observer.observe(element);
            }
        });
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.scrollAnimations = new ScrollAnimations();
});

// Add staggered animations helper
function addStaggeredAnimations(selector, baseDelay = 100) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((element, index) => {
        element.style.transitionDelay = `${index * baseDelay}ms`;
    });
}

// Export for manual use if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScrollAnimations;
}
