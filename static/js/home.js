/**
 * EventHub — Home Page JS
 * Hero animations, scroll reveals, category chip hover
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ── Staggered hero reveal ──────────────────────────── */
  const heroElements = document.querySelectorAll('.hero-badge, .hero-title, .hero-subtitle, .hero-cta, .hero-stats');
  heroElements.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, 150 + i * 100);
  });

  /* ── Scroll reveal for event cards ─────────────────── */
  const cards = document.querySelectorAll('.event-card, .event-list-item, .category-chip');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = `opacity 0.5s ease ${(i % 6) * 80}ms, transform 0.5s ease ${(i % 6) * 80}ms`;
    revealObserver.observe(card);
  });

});
