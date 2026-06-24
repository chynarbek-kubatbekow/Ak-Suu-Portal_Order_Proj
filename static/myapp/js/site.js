const header = document.querySelector("[data-header]");
const toggle = document.querySelector("[data-menu-toggle]");
const closeButton = document.querySelector("[data-menu-close]");
const progress = document.querySelector("[data-progress]");
const languageLinks = document.querySelectorAll("[data-translate-lang]");

if (header && toggle) {
    const setMenu = (isOpen) => {
        header.classList.toggle("is-open", isOpen);
        document.body.classList.toggle("menu-open", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
    };

    toggle.addEventListener("click", () => setMenu(!header.classList.contains("is-open")));
    closeButton?.addEventListener("click", () => setMenu(false));

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            setMenu(false);
        }
    });

    document.querySelectorAll("[data-nav] a").forEach((link) => {
        link.addEventListener("click", () => setMenu(false));
    });
}

const reveals = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12 }
    );

    reveals.forEach((element) => observer.observe(element));
} else {
    reveals.forEach((element) => element.classList.add("is-visible"));
}

document.querySelectorAll("[data-accordion]").forEach((accordion) => {
    const trigger = accordion.querySelector("[data-accordion-trigger]");
    trigger?.addEventListener("click", () => {
        const collapsed = accordion.classList.toggle("is-collapsed");
        trigger.setAttribute("aria-expanded", String(!collapsed));
    });
});

const updateProgress = () => {
    if (!progress) return;
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const value = scrollable > 0 ? (window.scrollY / scrollable) * 100 : 0;
    progress.style.width = `${Math.min(100, Math.max(0, value))}%`;
};

window.addEventListener("scroll", updateProgress, { passive: true });
window.addEventListener("resize", updateProgress);
updateProgress();

const getCookieDomain = () => {
    const hostname = window.location.hostname;
    if (hostname === "localhost" || hostname === "127.0.0.1" || !hostname.includes(".")) {
        return "";
    }
    return `;domain=.${hostname}`;
};

const setTranslateCookie = (value) => {
    const maxAge = 60 * 60 * 24 * 365;
    const domain = getCookieDomain();
    document.cookie = `googtrans=${value};path=/;max-age=${maxAge};SameSite=Lax`;
    if (domain) {
        document.cookie = `googtrans=${value};path=/;max-age=${maxAge};SameSite=Lax${domain}`;
    }
};

const clearTranslateCookie = () => {
    const domain = getCookieDomain();
    document.cookie = "googtrans=;path=/;max-age=0;SameSite=Lax";
    if (domain) {
        document.cookie = `googtrans=;path=/;max-age=0;SameSite=Lax${domain}`;
    }
};

const setActiveLanguage = (lang) => {
    languageLinks.forEach((link) => {
        link.classList.toggle("is-active", link.dataset.translateLang === lang);
    });
    document.documentElement.lang = lang === "ky" ? "ky" : lang;
};

const syncSavedLanguage = () => {
    setActiveLanguage(localStorage.getItem("ak-suu-language") || "ru");
};

const chooseGoogleLanguage = (lang) => {
    const combo = document.querySelector(".goog-te-combo");
    if (!combo) return false;
    combo.value = lang;
    combo.dispatchEvent(new Event("change"));
    return true;
};

const applyLanguage = (lang, shouldReload = true) => {
    const nextLang = lang === "kg" ? "ky" : lang;
    localStorage.setItem("ak-suu-language", nextLang);
    setActiveLanguage(nextLang);

    if (nextLang === "ru") {
        clearTranslateCookie();
    } else {
        setTranslateCookie(`/ru/${nextLang}`);
    }

    const changed = nextLang === "ru" ? false : chooseGoogleLanguage(nextLang);
    if (shouldReload && !changed) {
        window.location.reload();
    }
};

languageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
        event.preventDefault();
        applyLanguage(link.dataset.translateLang);
    });
});

const savedLanguage = localStorage.getItem("ak-suu-language") || "ru";
setActiveLanguage(savedLanguage);

window.addEventListener("pageshow", syncSavedLanguage);
window.addEventListener("load", syncSavedLanguage);

window.addEventListener("ak-suu-translate-ready", () => {
    const currentLanguage = localStorage.getItem("ak-suu-language") || "ru";
    setActiveLanguage(currentLanguage);
    if (currentLanguage !== "ru") {
        setTranslateCookie(`/ru/${currentLanguage}`);
        chooseGoogleLanguage(currentLanguage);
    }
});

[250, 800, 1600].forEach((delay) => {
    window.setTimeout(syncSavedLanguage, delay);
});
