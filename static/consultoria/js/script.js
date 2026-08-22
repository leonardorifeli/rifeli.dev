/* rifeli.dev/consultoria */
(function () {
    'use strict';

    var WHATSAPP = '5548988215325';
    var root = document.documentElement;

    /* --- Tema ------------------------------------------------------------ */
    /* Aplicado cedo por um script inline no <head> pra evitar flash. Aqui so
       ligamos o botao e persistimos a escolha. */
    function initTheme() {
        var btn = document.querySelector('.theme-toggle');
        if (!btn) return;

        function label() {
            var dark = root.getAttribute('data-theme') === 'dark' ||
                (!root.getAttribute('data-theme') &&
                    window.matchMedia('(prefers-color-scheme: dark)').matches);
            btn.setAttribute('aria-label', dark ? 'Mudar para tema claro' : 'Mudar para tema escuro');
            btn.setAttribute('aria-pressed', String(dark));
        }

        btn.addEventListener('click', function () {
            var dark = root.getAttribute('data-theme') === 'dark' ||
                (!root.getAttribute('data-theme') &&
                    window.matchMedia('(prefers-color-scheme: dark)').matches);
            var next = dark ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            try { localStorage.setItem('tema', next); } catch (e) {}
            label();
        });

        label();
    }

    /* --- Menu mobile ----------------------------------------------------- */
    function initNav() {
        var toggle = document.querySelector('.menu-toggle');
        var nav = document.querySelector('.nav');
        if (!toggle || !nav) return;

        function close() {
            nav.classList.remove('active');
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', function () {
            var open = nav.classList.toggle('active');
            toggle.setAttribute('aria-expanded', String(open));
        });

        nav.addEventListener('click', function (e) {
            if (e.target.closest('a')) close();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && nav.classList.contains('active')) {
                close();
                toggle.focus();
            }
        });

        document.addEventListener('click', function (e) {
            if (!nav.classList.contains('active')) return;
            if (!nav.contains(e.target) && !toggle.contains(e.target)) close();
        });
    }

    /* --- Header e botao flutuante ---------------------------------------- */
    /* Sentinela + IntersectionObserver: zero trabalho por evento de scroll. */
    function initScrollState() {
        var header = document.querySelector('.header');
        var wa = document.querySelector('.wa-float');
        if (!header && !wa) return;

        var sentinel = document.createElement('div');
        sentinel.setAttribute('aria-hidden', 'true');
        sentinel.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:64px;pointer-events:none';
        document.body.prepend(sentinel);

        if (!('IntersectionObserver' in window)) {
            if (wa) wa.classList.add('is-visible');
            return;
        }

        new IntersectionObserver(function (entries) {
            var past = !entries[0].isIntersecting;
            if (header) header.classList.toggle('is-stuck', past);
            if (wa) wa.classList.toggle('is-visible', past);
        }, { threshold: 0 }).observe(sentinel);
    }

    /* --- Revelacao no scroll --------------------------------------------- */
    function initReveal() {
        var items = document.querySelectorAll('.reveal');
        if (!items.length) return;

        var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (reduced || !('IntersectionObserver' in window)) {
            items.forEach(function (el) { el.classList.add('is-in'); });
            return;
        }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('is-in');
                io.unobserve(entry.target);
            });
        }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

        items.forEach(function (el) { io.observe(el); });
    }

    /* --- Notificacoes ---------------------------------------------------- */
    function notify(message, type) {
        var box = document.querySelector('.notification-container');
        if (!box) {
            box = document.createElement('div');
            box.className = 'notification-container';
            box.setAttribute('role', 'status');
            box.setAttribute('aria-live', 'polite');
            document.body.appendChild(box);
        }

        var item = document.createElement('div');
        item.className = 'notification' + (type === 'error' ? ' error' : '');

        var icon = type === 'error' ? 'i-alert-circle' : 'i-check-circle';
        item.innerHTML =
            '<svg class="icon" aria-hidden="true"><use href="/img/icons.svg#' + icon + '"></use></svg>' +
            '<p></p>' +
            '<button type="button" class="notification-close" aria-label="Fechar aviso">' +
            '<svg class="icon" aria-hidden="true"><use href="/img/icons.svg#i-close"></use></svg></button>';
        item.querySelector('p').textContent = message;

        function dismiss() {
            item.classList.add('is-leaving');
            item.addEventListener('animationend', function () { item.remove(); }, { once: true });
        }

        item.querySelector('.notification-close').addEventListener('click', dismiss);
        box.appendChild(item);
        setTimeout(function () { if (item.isConnected) dismiss(); }, 6000);
    }

    /* --- Formulario ------------------------------------------------------ */
    function initForm() {
        var form = document.getElementById('consultoria-form');
        if (!form) return;

        function setError(field, on) {
            var group = field.closest('.form-group');
            if (group) group.classList.toggle('has-error', on);
            field.setAttribute('aria-invalid', String(on));
        }

        form.addEventListener('input', function (e) {
            var f = e.target;
            if (f.matches('input, select, textarea') && f.value.trim()) setError(f, false);
        });

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var fields = form.querySelectorAll('[required]');
            var first = null;

            fields.forEach(function (field) {
                var ok = field.value.trim() !== '' && field.checkValidity();
                setError(field, !ok);
                if (!ok && !first) first = field;
            });

            if (first) {
                notify('Faltou preencher alguma coisa. Confere os campos marcados.', 'error');
                first.focus();
                return;
            }

            var data = new FormData(form);
            var linhas = [
                '*Contato via rifeli.dev/consultoria*',
                '',
                '*Nome:* ' + (data.get('nome') || ''),
                '*E-mail:* ' + (data.get('email') || ''),
                '*WhatsApp:* ' + (data.get('whatsapp') || 'nao informado'),
                '*Assunto:* ' + (data.get('assunto') || ''),
                '',
                '*Descricao:*',
                (data.get('descricao') || '')
            ];

            var url = 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(linhas.join('\n'));

            /* window.open pode voltar null se o navegador bloquear o popup.
               Sem esse fallback o clique morre em silencio e o lead se perde. */
            var win = window.open(url, '_blank', 'noopener');
            if (win) {
                win.focus();
                notify('Abri o WhatsApp numa aba nova. Se nao apareceu, libere popups.', 'success');
            } else {
                window.location.href = url;
            }
        });
    }

    /* --- Rolagem suave com compensacao do header fixo -------------------- */
    function initAnchors() {
        document.addEventListener('click', function (e) {
            var link = e.target.closest('a[href^="#"]');
            if (!link) return;

            var id = link.getAttribute('href');
            if (!id || id === '#') return;

            var target = document.querySelector(id);
            if (!target) return;

            e.preventDefault();
            var header = document.querySelector('.header');
            var offset = header ? header.offsetHeight + 12 : 12;
            var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
            var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

            window.scrollTo({ top: top, behavior: reduced ? 'auto' : 'smooth' });
            history.replaceState(null, '', id);

            /* mantem o teclado em sincronia com a rolagem */
            target.setAttribute('tabindex', '-1');
            target.focus({ preventScroll: true });
        });
    }

    /* --- FAQ: so uma aberta por vez -------------------------------------- */
    function initFaq() {
        var items = document.querySelectorAll('.faq-item');
        items.forEach(function (item) {
            item.addEventListener('toggle', function () {
                if (!item.open) return;
                items.forEach(function (other) {
                    if (other !== item) other.open = false;
                });
            });
        });
    }

    function boot() {
        initTheme();
        initNav();
        initScrollState();
        initReveal();
        initForm();
        initAnchors();
        initFaq();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
