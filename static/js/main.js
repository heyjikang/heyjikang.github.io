(() => {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const header = $('.site-header');
  const progress = $('.scroll-progress');
  const menuButton = $('.menu-toggle');
  const mobileNav = $('#mobile-nav');
  const toast = $('.toast');
  let toastTimer;
  let ticking = false;

  function updateScroll() {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (progress) progress.style.transform = `scaleX(${max > 0 ? Math.max(0, Math.min(1, window.scrollY / max)) : 0})`;
    if (header) header.classList.toggle('has-scrolled', window.scrollY > 24);
    ticking = false;
  }
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(updateScroll); ticking = true; }
  }, { passive: true });
  updateScroll();
  $('#year')?.replaceChildren(document.createTextNode(new Date().getFullYear().toString()));

  function setMenu(open) {
    if (!menuButton || !mobileNav) return;
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? '关闭菜单' : '打开菜单');
    mobileNav.inert = !open;
    mobileNav.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);
  }
  menuButton?.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
  $$('#mobile-nav a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') setMenu(false); });
  window.addEventListener('resize', () => { if (window.innerWidth > 820) setMenu(false); });

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 2600);
  }
  async function copyValue(value, message) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
      await navigator.clipboard.writeText(value);
      showToast(message);
    } catch (_) {
      // Clipboard API requires a secure context. Show the value so it can still be copied manually.
      showToast(`请手动复制：${value}`);
    }
  }
  $$('[data-copy]').forEach(button => button.addEventListener('click', () => copyValue(button.dataset.copy, button.dataset.copyLabel || '已复制')));
  $$('[data-copy-url]').forEach(button => button.addEventListener('click', () => copyValue(window.location.href, '文章链接已复制')));

  const filters = $('[data-note-filter]');
  if (filters) {
    const chips = $$('[data-category]', $('.filter-group', filters));
    const cards = $$('[data-note-item]', filters);
    const input = $('#notes-search');
    const count = $('#visible-count');
    const empty = $('.archive-empty', filters);
    let current = 'all';
    function filterItems() {
      const query = (input?.value || '').trim().toLocaleLowerCase();
      let visible = 0;
      cards.forEach(card => {
        const match = (current === 'all' || card.dataset.category === current) && (!query || (card.dataset.search || '').toLocaleLowerCase().includes(query));
        card.hidden = !match;
        if (match) visible++;
      });
      if (count) count.textContent = String(visible);
      if (empty) empty.hidden = visible !== 0;
    }
    chips.forEach(chip => chip.addEventListener('click', () => {
      current = chip.dataset.category;
      chips.forEach(c => c.classList.toggle('is-active', c === chip));
      filterItems();
    }));
    input?.addEventListener('input', filterItems);
  }

  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const animated = $$('.section-heading, .project-feature, .note-row, .about-photo-wrap, .about-content, .contact-inner, .archive-card');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) { entry.target.classList.add('revealed'); observer.unobserve(entry.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -25px 0px' });
    animated.forEach(el => { el.classList.add('reveal-ready'); observer.observe(el); });
  }
})();
