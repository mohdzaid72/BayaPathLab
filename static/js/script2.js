// Navbar scroll effect
window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(102, 126, 234, 0.95)';
    } else {
        header.style.background = 'var(--primary)';
    }
});

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Intersection Observer for animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate', 'visible');
            entry.target.classList.add('fade-in', 'visible');
        }
    });
}, { threshold: 0.1 });

// Observe all cards and sections
document.querySelectorAll('.test-card, .feature-item, .contact-item, .admin-section').forEach(el => {
    observer.observe(el);
});

// Form handling
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const btn = form.querySelector('button[type="submit"]');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        btn.disabled = true;
    });
});

// Particle effect for hero
function createParticle() {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: fixed;
        width: 4px;
        height: 4px;
        background: rgba(255,255,255,0.6);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        left: ${Math.random() * 100}vw;
        animation: floatParticle 6s infinite linear;
    `;
    document.body.appendChild(particle);
    
    setTimeout(() => particle.remove(), 6000);
}

function floatParticle() {
    const keyframes = `
        @keyframes floatParticle {
            0% { 
                transform: translateY(100vh) rotate(0deg);
                opacity: 1;
            }
            100% { 
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
    `;
    if (!document.querySelector('style#particles')) {
        const style = document.createElement('style');
        style.id = 'particles';
        style.textContent = keyframes;
        document.head.appendChild(style);
    }
}

// Create particles
setInterval(createParticle, 300);

// Typing effect for hero
function typeWriter(element, text, speed = 100) {
    let i = 0;
    element.innerHTML = '';
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Hero typing effect
    const heroTitle = document.querySelector('.hero h1');
    if (heroTitle) {
        typeWriter(heroTitle, heroTitle.textContent, 80);
    }
});