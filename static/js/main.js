/**
 * EventHub — Main JavaScript
 * Handles: dark mode, counter animations, bookmark AJAX,
 *          toast notifications, mark notifications, nav scroll
 */

/* ── CSRF Helper ────────────────────────────────────── */
function getCsrf() {
  return document.cookie.split(';')
    .map(c => c.trim().split('='))
    .find(([k]) => k === 'csrftoken')?.[1] || '';
}

/* ── Dark Mode ──────────────────────────────────────── */
(function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
})();

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeIcon');
  if (!icon) return;
  icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
}

document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('themeToggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }

  /* ── Animated Counters ────────────────────────────── */
  const counters = document.querySelectorAll('.counter');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => observer.observe(el));

  function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    if (isNaN(target)) return;
    const duration = 1800;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target.toLocaleString();
        clearInterval(timer);
      } else {
        el.textContent = Math.floor(current).toLocaleString();
      }
    }, 16);
  }

  /* ── Navbar scroll effect ─────────────────────────── */
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.style.boxShadow = window.scrollY > 30
        ? '0 4px 20px rgba(0,0,0,0.08)'
        : 'none';
    }, { passive: true });
  }

  /* ── Toast auto-dismiss ───────────────────────────── */
  document.querySelectorAll('.toast.show').forEach(toast => {
    setTimeout(() => {
      const bsToast = bootstrap.Toast.getOrCreateInstance(toast);
      bsToast.hide();
    }, 4000);
  });

  /* ── Bookmark buttons (card-level) ───────────────── */
  document.querySelectorAll('.bookmark-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const eventId = btn.dataset.event;
      try {
        const res = await fetch(`/events/${eventId}/bookmark/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrf(),
            'X-Requested-With': 'XMLHttpRequest',
          },
        });
        const data = await res.json();
        const icon = btn.querySelector('i');
        if (data.bookmarked) {
          icon.className = 'bi bi-bookmark-fill';
          btn.classList.add('active');
          showToast('Event saved to bookmarks!', 'success');
        } else {
          icon.className = 'bi bi-bookmark';
          btn.classList.remove('active');
          showToast('Removed from bookmarks.', 'info');
        }
      } catch (err) {
        console.error('Bookmark error:', err);
      }
    });
  });

  /* ── Mark notifications read ──────────────────────── */
  const markAllBtn = document.getElementById('markAllRead');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', async () => {
      await fetch('/accounts/notifications/read/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrf(),
          'X-Requested-With': 'XMLHttpRequest',
        },
      });
      document.querySelectorAll('.notification-item.unread').forEach(el => el.classList.remove('unread'));
      const badge = document.querySelector('.notification-badge');
      if (badge) badge.remove();
      markAllBtn.textContent = 'All read ✓';
    });
  }

  /* ── List/Grid view toggle ────────────────────────── */
  document.querySelectorAll('.view-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.view-toggle').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const grid = document.getElementById('eventsGrid');
      if (!grid) return;
      if (btn.dataset.view === 'list') {
        grid.classList.add('list-view');
        grid.querySelectorAll('.event-col').forEach(col => {
          col.classList.remove('col-md-6', 'col-xl-4');
          col.classList.add('col-12');
        });
      } else {
        grid.classList.remove('list-view');
        grid.querySelectorAll('.event-col').forEach(col => {
          col.classList.remove('col-12');
          col.classList.add('col-md-6', 'col-xl-4');
        });
      }
    });
  });

  /* ── Capacity bars animation ──────────────────────── */
  document.querySelectorAll('.capacity-bar-fill, .seats-fill').forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => { bar.style.width = target; }, 300);
  });

  /* ── Image preview on event form ──────────────────── */
  const imageInput = document.querySelector('input[name="image"]');
  if (imageInput) {
    imageInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const wrap = document.getElementById('imagePreviewWrap');
      const img = document.getElementById('imagePreview');
      if (wrap && img) {
        const reader = new FileReader();
        reader.onload = ev => { img.src = ev.target.result; wrap.style.display = 'block'; };
        reader.readAsDataURL(file);
      }
    });
  }

  /* ── Star rating interaction ──────────────────────── */
  initStarRating();

});

/* ── Toast helper (global) ──────────────────────────── */
function showToast(message, type = 'info') {
  const container = document.querySelector('.toast-container');
  if (!container) return;

  const icons = {
    success: 'bi-check-circle-fill text-success',
    danger: 'bi-x-circle-fill text-danger',
    warning: 'bi-exclamation-triangle-fill text-warning',
    info: 'bi-info-circle-fill text-info',
  };

  const toast = document.createElement('div');
  toast.className = `toast show align-items-center border-0 toast-${type}`;
  toast.role = 'alert';
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi ${icons[type] || icons.info}"></i>
        ${message}
      </div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;

  container.appendChild(toast);
  new bootstrap.Toast(toast, { autohide: true, delay: 4000 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

/* ── Star rating ────────────────────────────────────── */
function initStarRating() {
  const groups = document.querySelectorAll('.star-rating-group');
  groups.forEach(group => {
    const labels = group.querySelectorAll('.star-label');
    const inputs = group.querySelectorAll('.star-input');

    labels.forEach((label, idx) => {
      label.addEventListener('mouseenter', () => {
        labels.forEach((l, i) => {
          l.querySelector('.star-icon').style.color = i <= idx ? '#f59e0b' : '';
        });
      });
      label.addEventListener('mouseleave', () => {
        labels.forEach((l, i) => {
          const checked = Array.from(inputs).findIndex(inp => inp.checked);
          l.querySelector('.star-icon').style.color = (checked >= 0 && i <= checked) ? '#f59e0b' : '';
        });
      });
      label.querySelector('.star-input').addEventListener('change', () => {
        labels.forEach((l, i) => {
          l.querySelector('.star-icon').style.color = i <= idx ? '#f59e0b' : '';
        });
      });
    });
  });
}
