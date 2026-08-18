// Universal Mobile Navigation Hamburger Handler
document.addEventListener('DOMContentLoaded', function () {
  const hamburger = document.getElementById('navbar-hamburger');
  const navLinks = document.getElementById('nav-links');

  if (hamburger && navLinks) {
    function toggleNav() {
      const isOpen = navLinks.classList.toggle('open');
      hamburger.classList.toggle('active', isOpen);
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      if (isOpen) {
        document.body.classList.add('nav-open');
        document.body.style.overflow = 'hidden';
      } else {
        document.body.classList.remove('nav-open');
        document.body.style.overflow = '';
      }
    }

    function closeNav() {
      navLinks.classList.remove('open');
      hamburger.classList.remove('active');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('nav-open');
      document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleNav();
    });

    // Close when clicking any link inside the mobile menu
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        closeNav();
      });
    });

    // Close when clicking outside of the open menu
    document.addEventListener('click', function (e) {
      if (navLinks.classList.contains('open') && !navLinks.contains(e.target) && !hamburger.contains(e.target)) {
        closeNav();
      }
    });

    // Close with Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) {
        closeNav();
      }
    });

    // Reset when resizing above mobile/tablet breakpoint
    window.addEventListener('resize', function () {
      if (window.innerWidth > 992) {
        closeNav();
      }
    });
  }
});
