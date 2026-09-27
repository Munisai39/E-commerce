/**
 * MarketNest - Vanilla JavaScript Interactions
 * Mobile navigation, image previews, modals, favorites AJAX, and tabs
 */

document.addEventListener('DOMContentLoaded', function () {
  // --------------------------------------------------------------------------
  // 1. Mobile Navigation Toggle
  // --------------------------------------------------------------------------
  const mobileToggle = document.getElementById('mobileNavToggle');
  const desktopNav = document.getElementById('navDesktopLinks');

  if (mobileToggle && desktopNav) {
    mobileToggle.addEventListener('click', function () {
      desktopNav.classList.toggle('mobile-open');
    });
  }

  // --------------------------------------------------------------------------
  // 2. User Profile Dropdown Menu
  // --------------------------------------------------------------------------
  const userMenuBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');

  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });

    document.addEventListener('click', function (e) {
      if (!userDropdown.contains(e.target) && !userMenuBtn.contains(e.target)) {
        userDropdown.classList.remove('show');
      }
    });
  }

  // --------------------------------------------------------------------------
  // 3. Product Gallery Thumbnail Switching
  // --------------------------------------------------------------------------
  const mainProductImage = document.getElementById('mainProductImage');
  const thumbnails = document.querySelectorAll('.thumb-item');

  thumbnails.forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      thumbnails.forEach(t => t.classList.remove('active'));
      thumb.classList.add('active');
      const newSrc = thumb.getAttribute('data-full-img');
      if (mainProductImage && newSrc) {
        mainProductImage.src = newSrc;
      }
    });
  });

  // --------------------------------------------------------------------------
  // 4. Modal Dialogs (Make Offer, Contact Seller, Report, Delete Confirm)
  // --------------------------------------------------------------------------
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const modalCloseBtns = document.querySelectorAll('[data-modal-close]');

  modalTriggers.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = btn.getAttribute('data-modal-target');
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  modalCloseBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const modal = btn.closest('.modal-backdrop');
      if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
      }
    });
  });

  document.querySelectorAll('.modal-backdrop').forEach(function (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
      }
    });
  });

  // Close modals on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.show').forEach(function (m) {
        m.classList.remove('show');
        document.body.style.overflow = '';
      });
    }
  });

  // --------------------------------------------------------------------------
  // 5. AJAX Favorite / Wishlist Toggle
  // --------------------------------------------------------------------------
  const favoriteButtons = document.querySelectorAll('.card-fav-btn, .btn-fav-toggle');

  favoriteButtons.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const listingId = btn.getAttribute('data-listing-id');
      const url = btn.getAttribute('data-url') || `/listing/${listingId}/favorite/`;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCsrfToken(),
          'Accept': 'application/json',
        },
      })
      .then(response => {
        if (response.redirected) {
          window.location.href = response.url;
          return null;
        }
        return response.json();
      })
      .then(data => {
        if (!data) return;
        if (data.status === 'ok') {
          // Toggle active class
          btn.classList.toggle('active', data.is_favorited);

          // Update header counter badge if present
          const favCounter = document.getElementById('navbarFavCounter');
          if (favCounter) {
            favCounter.textContent = data.favorites_count;
            favCounter.style.display = data.favorites_count > 0 ? 'flex' : 'none';
          }

          // Show floating toast
          showToast(data.message, data.is_favorited ? 'success' : 'info');
        }
      })
      .catch(err => {
        console.error('Error toggling favorite:', err);
      });
    });
  });

  // --------------------------------------------------------------------------
  // 6. Dynamic Subcategory Selector for Listing Form
  // --------------------------------------------------------------------------
  const categorySelect = document.getElementById('id_category');
  const subcategorySelect = document.getElementById('id_subcategory');

  if (categorySelect && subcategorySelect) {
    categorySelect.addEventListener('change', function () {
      const catId = categorySelect.value;
      if (!catId) {
        subcategorySelect.innerHTML = '<option value="">---------</option>';
        return;
      }

      fetch(`/api/subcategories/${catId}/`)
        .then(res => res.json())
        .then(data => {
          let options = '<option value="">Select Subcategory (Optional)</option>';
          data.subcategories.forEach(sub => {
            options += `<option value="${sub.id}">${sub.name}</option>`;
          });
          subcategorySelect.innerHTML = options;
        })
        .catch(err => console.error('Error fetching subcategories:', err));
    });
  }

  // --------------------------------------------------------------------------
  // 7. Image Upload Preview
  // --------------------------------------------------------------------------
  const imageInput = document.getElementById('id_listing_images');
  const previewContainer = document.getElementById('imagePreviews');

  if (imageInput && previewContainer) {
    imageInput.addEventListener('change', function () {
      previewContainer.innerHTML = '';
      const files = Array.from(imageInput.files);

      if (files.length === 0) return;

      files.forEach((file, index) => {
        if (!file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = function (e) {
          const thumbDiv = document.createElement('div');
          thumbDiv.className = 'preview-thumb';
          thumbDiv.innerHTML = `
            <img src="${e.target.result}" alt="Preview ${index + 1}" />
            <div style="position: absolute; bottom: 2px; left: 2px; background: rgba(0,0,0,0.6); color: #fff; font-size: 10px; padding: 1px 4px; border-radius: 2px;">
              ${index === 0 ? 'Primary' : '#' + (index + 1)}
            </div>
          `;
          previewContainer.appendChild(thumbDiv);
        };
        reader.readAsDataURL(file);
      });
    });
  }

  // --------------------------------------------------------------------------
  // 8. Contact Phone Reveal Button
  // --------------------------------------------------------------------------
  const phoneRevealBtn = document.getElementById('phoneRevealBtn');
  const phoneSecret = document.getElementById('phoneSecret');

  if (phoneRevealBtn && phoneSecret) {
    phoneRevealBtn.addEventListener('click', function () {
      phoneSecret.style.display = 'inline';
      phoneRevealBtn.style.display = 'none';
    });
  }

  // --------------------------------------------------------------------------
  // 9. Password Visibility Toggle
  // --------------------------------------------------------------------------
  const passwordToggles = document.querySelectorAll('.password-toggle-btn');
  passwordToggles.forEach(function (toggle) {
    toggle.addEventListener('click', function () {
      const input = toggle.previousElementSibling;
      if (input && (input.type === 'password' || input.type === 'text')) {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        toggle.innerHTML = isPassword
          ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>'
          : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
      }
    });
  });

  // --------------------------------------------------------------------------
  // 10. Auto-Dismiss Toast Messages
  // --------------------------------------------------------------------------
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(function (toast) {
    const dismissBtn = toast.querySelector('.toast-dismiss');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', function () {
        toast.remove();
      });
    }
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(50px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  });

  // --------------------------------------------------------------------------
  // 11. Helper: Dynamic Toast Creator
  // --------------------------------------------------------------------------
  function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">${message}</div>
      <button type="button" class="toast-dismiss">&times;</button>
    `;

    toast.querySelector('.toast-dismiss').addEventListener('click', () => toast.remove());
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(50px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // --------------------------------------------------------------------------
  // 12. Helper: CSRF Token from Cookie
  // --------------------------------------------------------------------------
  function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === 'csrftoken=') {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    // Fallback: check DOM input
    if (!cookieValue) {
      const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfInput) cookieValue = csrfInput.value;
    }
    return cookieValue;
  }
});
