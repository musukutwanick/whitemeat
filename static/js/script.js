// Gallery filtering
const filterButtons = document.querySelectorAll('.gallery-filter');
const galleryImages = document.querySelectorAll('.gallery-grid img');

filterButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    // Remove active from all
    filterButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.getAttribute('data-filter');
    galleryImages.forEach(img => {
      if (filter === 'all' || img.getAttribute('data-category') === filter) {
        img.style.display = '';
      } else {
        img.style.display = 'none';
      }
    });
  });
});

// Contact form WhatsApp integration
document.addEventListener('DOMContentLoaded', function() {
  const contactForm = document.getElementById('contactForm');
  
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Get form data
      const name = document.getElementById('contactName').value.trim();
      const email = document.getElementById('contactEmail').value.trim();
      const subject = document.getElementById('contactSubject').value;
      const message = document.getElementById('contactMessage').value.trim();
      
      // Validate form data
      if (!name || !email || !subject || !message) {
        alert('Please fill in all required fields.');
        return;
      }
      
      // Get submit button
      const submitBtn = contactForm.querySelector('.contact-btn');
      const originalText = submitBtn.textContent;
      
      // Show loading state
      submitBtn.textContent = 'Opening WhatsApp...';
      submitBtn.disabled = true;
      
      // Get subject text instead of value
      const subjectSelect = document.getElementById('contactSubject');
      const subjectText = subjectSelect.options[subjectSelect.selectedIndex].text;
      
      // Create WhatsApp message
      const whatsappMessage = `Hello! I'm contacting you through your website.

*Name:* ${name}
*Email:* ${email}
*Subject:* ${subjectText}
*Message:* ${message}

I look forward to hearing from you soon!`;
      
      // Encode the message for URL
      const encodedMessage = encodeURIComponent(whatsappMessage);
      
      // WhatsApp number (without + sign for URL)
      const whatsappNumber = '263772333369';
      
      // Create WhatsApp URL
      const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;
      
      // Open WhatsApp
      window.open(whatsappUrl, '_blank');
      
      // Reset button after a short delay
      setTimeout(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        
        // Optional: Clear form after successful submission
        contactForm.reset();
      }, 2000);
    });
  }
});