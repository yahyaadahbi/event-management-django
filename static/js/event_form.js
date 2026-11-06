/**
 * EventHub — Event Form JS
 * Multi-step form: navigation, validation, dynamic ticket types
 */

let currentStep = 1;
const totalSteps = 3;

function goToStep(step) {
  if (step > currentStep && !validateStep(currentStep)) return;

  document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
  document.getElementById(`step${step}`).classList.add('active');

  document.querySelectorAll('.step').forEach((el, i) => {
    el.classList.toggle('active', i + 1 === step);
    el.classList.toggle('completed', i + 1 < step);
  });

  currentStep = step;

  if (step === 3) buildReviewSummary();

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateStep(step) {
  if (step === 1) {
    const title = document.querySelector('[name="title"]');
    const eventDate = document.querySelector('[name="event_date"]');
    const loc   = document.querySelector('[name="location"]');

    let valid = true;

    [title, eventDate, loc].forEach(field => {
      if (field && !field.value.trim()) {
        field.classList.add('is-invalid');
        valid = false;
      } else if (field) {
        field.classList.remove('is-invalid');
      }
    });

    return valid;
  }
  return true;
}

function buildReviewSummary() {
  const title   = document.querySelector('[name="title"]')?.value || '—';
  const eventDate = document.querySelector('[name="event_date"]')?.value || '—';
  const loc     = document.querySelector('[name="location"]')?.value || '—';
  const cap     = document.querySelector('[name="capacity_max"]')?.value || '—';
  const price   = document.querySelector('[name="price"]')?.value || '0';
  const status  = document.querySelector('[name="status"]')?.value || '—';

  const el = document.getElementById('reviewSummary');
  if (!el) return;

  el.innerHTML = `
    <div class="row g-3">
      <div class="col-md-6">
        <div class="review-field">
          <span class="filter-label">Title</span>
          <strong>${escapeHtml(title)}</strong>
        </div>
      </div>
      <div class="col-md-6">
        <div class="review-field">
          <span class="filter-label">Status</span>
          <span class="event-status-badge status-${status}">${status}</span>
        </div>
      </div>
      <div class="col-md-6">
        <div class="review-field">
          <span class="filter-label">Date</span>
          <strong>${eventDate}</strong>
        </div>
      </div>
      <div class="col-md-6">
        <div class="review-field">
          <span class="filter-label">Location</span>
          <strong>${escapeHtml(loc)}</strong>
        </div>
      </div>
      <div class="col-md-3">
        <div class="review-field">
          <span class="filter-label">Capacity</span>
          <strong>${cap}</strong>
        </div>
      </div>
      <div class="col-md-3">
        <div class="review-field">
          <span class="filter-label">Price</span>
          <strong>${parseFloat(price) === 0 ? 'Free' : '$' + price}</strong>
        </div>
      </div>
    </div>
  `;
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(text));
  return d.innerHTML;
}

/* ── Dynamic ticket type forms ──────────────────────── */
document.addEventListener('DOMContentLoaded', () => {

  const addBtn = document.getElementById('addTicketType');
  if (!addBtn) return;

  const container = document.getElementById('ticketFormsContainer');
  const totalFormsInput = document.getElementById('id_tickettype_set-TOTAL_FORMS');

  addBtn.addEventListener('click', () => {
    const formCount = parseInt(totalFormsInput.value, 10);
    const templateRow = container.querySelector('.ticket-type-form-row');
    if (!templateRow) return;

    const newRow = templateRow.cloneNode(true);
    newRow.id = `ticketForm${formCount}`;
    newRow.querySelector('h6').textContent = `Ticket Tier ${formCount + 1}`;

    // Update field indices
    newRow.querySelectorAll('input, select, textarea').forEach(field => {
      field.name  = field.name.replace(/-\d+-/, `-${formCount}-`);
      field.id    = field.id.replace(/-\d+-/, `-${formCount}-`);
      field.value = '';
    });

    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-sm btn-ghost text-danger remove-ticket-form';
    removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
    removeBtn.addEventListener('click', () => newRow.remove());
    newRow.querySelector('.d-flex').appendChild(removeBtn);

    container.appendChild(newRow);
    totalFormsInput.value = formCount + 1;
  });

  // Remove existing forms
  container.addEventListener('click', (e) => {
    if (e.target.closest('.remove-ticket-form')) {
      const row = e.target.closest('.ticket-type-form-row');
      const deleteInput = row.querySelector('input[name$="-DELETE"]');
      if (deleteInput) {
        deleteInput.checked = true;
        row.style.opacity = '0.4';
        row.style.pointerEvents = 'none';
      } else {
        row.remove();
      }
    }
  });

});
