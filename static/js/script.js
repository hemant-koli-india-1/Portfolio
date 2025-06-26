// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80, // Adjust for fixed header
                behavior: 'smooth'
            });
            
            // Update active link
            document.querySelectorAll('nav a').forEach(link => {
                link.classList.remove('active');
            });
            this.classList.add('active');
        }
    });
});

// Add active class to current section in navigation
window.addEventListener('scroll', () => {
    const scrollPosition = window.scrollY;
    
    document.querySelectorAll('section').forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            document.querySelectorAll('nav a').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});

// Add animation on scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.timeline-item, .project-card, .skill-category, .certifications-list li');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// Set initial styles for animation
window.addEventListener('load', () => {
    const elements = document.querySelectorAll('.timeline-item, .project-card, .skill-category, .certifications-list li');
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    });
    
    // Trigger initial animation
    setTimeout(animateOnScroll, 300);
});

window.addEventListener('scroll', animateOnScroll);

// Add current year to footer
const currentYear = new Date().getFullYear();
document.querySelector('footer p').innerHTML = `&copy; ${currentYear} Hemant Koli. All rights reserved.`;

// Chat Widget Functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.querySelector('.chat-widget');
    const chatToggle = document.querySelector('.chat-toggle');
    const chatHeader = document.querySelector('.chat-header');
    const chatMessages = document.querySelector('.chat-messages');
    const chatInput = document.querySelector('.chat-input');
    const sendButton = document.querySelector('.send-button');
    
    // Toggle chat window
    chatHeader.addEventListener('click', () => {
        chatWidget.classList.toggle('collapsed');
    });
    
    // Send message on button click
    sendButton.addEventListener('click', sendMessage);
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage('user', message);
        chatInput.value = '';
        
        // Show typing indicator
        const typingId = 'typing-' + Date.now();
        showTypingIndicator(typingId);
        
        try {
            // Call the Python backend using the configurable URL
            const response = await fetch(API_CONFIG.getUrl('CHAT'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: [{
                        role: 'user',
                        content: message
                    }]
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            removeTypingIndicator(typingId);
            addMessage('bot', data.response);
            
        } catch (error) {
            console.error('Error calling chatbot API:', error);
            removeTypingIndicator(typingId);
            addMessage('bot', "I'm having trouble connecting to the server. Please try again later.");
        }
    }
    
    function showTypingIndicator(id) {
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function removeTypingIndicator(id) {
        const typingElement = document.getElementById(id);
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom of chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // This function is no longer needed as we're using the Python backend
    // for generating responses
});
