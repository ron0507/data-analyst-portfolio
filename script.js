(function () {
    "use strict";

    const NAV_OFFSET = 72;

    function smoothScrollToHash(hash) {
        const id = hash && hash.startsWith("#") ? hash : `#${hash}`;
        const el = document.querySelector(id);
        if (!el) return;
        const top = el.getBoundingClientRect().top + window.pageYOffset - NAV_OFFSET;
        window.scrollTo({ top, behavior: "smooth" });
    }

    function initNav() {
        document.querySelectorAll('a[href^="#"]').forEach((link) => {
            link.addEventListener("click", (e) => {
                const href = link.getAttribute("href");
                if (!href || href === "#") return;
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    smoothScrollToHash(href);
                    if (href === "#main") {
                        const main = document.getElementById("main");
                        window.setTimeout(() => {
                            main?.focus({ preventScroll: true });
                        }, 450);
                    }
                }
            });
        });

        const hamburger = document.querySelector(".hamburger");
        const navMenu = document.querySelector(".nav-menu");

        function closeMenu() {
            if (!hamburger || !navMenu) return;
            hamburger.classList.remove("active");
            navMenu.classList.remove("active");
            hamburger.setAttribute("aria-expanded", "false");
            hamburger.setAttribute("aria-label", "Open menu");
        }

        function openMenu() {
            if (!hamburger || !navMenu) return;
            hamburger.classList.add("active");
            navMenu.classList.add("active");
            hamburger.setAttribute("aria-expanded", "true");
            hamburger.setAttribute("aria-label", "Close menu");
        }

        if (hamburger && navMenu) {
            hamburger.addEventListener("click", () => {
                if (navMenu.classList.contains("active")) closeMenu();
                else openMenu();
            });
        }

        document.querySelectorAll(".nav-menu a").forEach((link) => {
            link.addEventListener("click", closeMenu);
        });

        injectMobileNavStyles();

        const navbar = document.querySelector(".navbar");
        window.addEventListener(
            "scroll",
            () => {
                if (!navbar) return;
                if (window.scrollY > 40) {
                    navbar.style.background = "rgba(15, 23, 42, 0.94)";
                } else {
                    navbar.style.background = "rgba(15, 23, 42, 0.82)";
                }
            },
            { passive: true }
        );

        const sections = document.querySelectorAll("section[id]");
        const navItems = document.querySelectorAll(".nav-menu a");

        function highlightNav() {
            let current = "";
            const y = window.scrollY + NAV_OFFSET + 40;
            sections.forEach((section) => {
                const top = section.offsetTop;
                const h = section.offsetHeight;
                if (y >= top && y < top + h) {
                    current = section.getAttribute("id") || "";
                }
            });
            navItems.forEach((item) => {
                item.classList.toggle("active", item.getAttribute("href") === `#${current}`);
            });
        }

        window.addEventListener("scroll", highlightNav, { passive: true });
        highlightNav();
    }

    function injectMobileNavStyles() {
        if (document.getElementById("portfolio-inline-nav-styles")) return;
        const style = document.createElement("style");
        style.id = "portfolio-inline-nav-styles";
        style.textContent = `
            .nav-menu a.active { color: var(--text) !important; }
            .nav-menu a.active::after { width: 100% !important; }
            @media (max-width: 768px) {
                .nav-menu.active {
                    display: flex !important;
                    flex-direction: column;
                    position: absolute;
                    top: 100%;
                    left: 0;
                    right: 0;
                    background: rgba(15, 23, 42, 0.98);
                    border-bottom: 1px solid var(--border);
                    padding: 1rem 1.5rem 1.5rem;
                    gap: 0.25rem;
                    align-items: stretch;
                    z-index: 999;
                }
                .nav-menu.active li { width: 100%; }
                .nav-menu.active a {
                    display: block;
                    padding: 0.65rem 0;
                    border-bottom: 1px solid var(--border);
                }
                .hamburger.active span:nth-child(1) {
                    transform: rotate(-45deg) translate(-5px, 6px);
                }
                .hamburger.active span:nth-child(2) { opacity: 0; }
                .hamburger.active span:nth-child(3) {
                    transform: rotate(45deg) translate(-5px, -6px);
                }
            }
        `;
        document.head.appendChild(style);
    }

    function initRevealAnimations() {
        const observerOptions = { threshold: 0.12, rootMargin: "0px 0px -40px 0px" };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll(".project-card, .certification-item, .timeline-item, .skills-category, .impact-card").forEach((el) => {
            el.classList.add("reveal-on-scroll");
            observer.observe(el);
        });

        if (!document.getElementById("portfolio-reveal-styles")) {
            const s = document.createElement("style");
            s.id = "portfolio-reveal-styles";
            s.textContent = `
                html.js-reveal .reveal-on-scroll {
                    opacity: 0;
                    transform: translateY(18px);
                    transition: opacity 0.55s ease, transform 0.55s ease;
                }
                html.js-reveal .reveal-on-scroll.is-visible {
                    opacity: 1;
                    transform: translateY(0);
                }
                @media (prefers-reduced-motion: reduce) {
                    html.js-reveal .reveal-on-scroll { opacity: 1 !important; transform: none !important; transition: none !important; }
                }
            `;
            document.head.appendChild(s);
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.documentElement.classList.add("js-reveal");
        initNav();
        initRevealAnimations();
    });
})();
