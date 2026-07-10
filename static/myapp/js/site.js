/*
 * Copyright (c) 2026 Ak-Suu Portal Project Team. All rights reserved.
 * Proprietary software. See LICENSE for terms.
 */

const header = document.querySelector("[data-header]");
const toggle = document.querySelector("[data-menu-toggle]");
const closeButton = document.querySelector("[data-menu-close]");
const menuBackdrop = document.querySelector("[data-menu-backdrop]");
const progress = document.querySelector("[data-progress]");
const languageLinks = document.querySelectorAll("[data-translate-lang]");
const languageSwitch = document.querySelector(".language-switch");

if (header && toggle) {
    const setMenu = (isOpen) => {
        header.classList.toggle("is-open", isOpen);
        document.body.classList.toggle("menu-open", isOpen);
        toggle.setAttribute("aria-expanded", String(isOpen));
    };

    window.akSuuSetMenu = setMenu;

    document.addEventListener("click", (event) => {
        if (event.target.closest("[data-menu-toggle]")) {
            event.preventDefault();
            setMenu(!header.classList.contains("is-open"));
            return;
        }

        if (event.target.closest("[data-menu-close], [data-menu-backdrop]")) {
            event.preventDefault();
            setMenu(false);
        }
    });

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
const lazyBackgrounds = document.querySelectorAll("[data-lazy-bg]");
const isHeroReveal = (element) => element.closest(".home-hero, .page-hero");

const loadLazyBackground = (element) => {
    element.style.setProperty("--band-image", `url('${element.dataset.lazyBg}')`);
    element.removeAttribute("data-lazy-bg");
};

if ("IntersectionObserver" in window) {
    reveals.forEach((element) => {
        if (isHeroReveal(element)) {
            element.classList.add("is-visible");
        }
    });

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        { rootMargin: "160px 0px -24px", threshold: 0.04 }
    );

    reveals.forEach((element) => {
        if (!isHeroReveal(element)) {
            observer.observe(element);
        }
    });

    const backgroundObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    loadLazyBackground(entry.target);
                    backgroundObserver.unobserve(entry.target);
                }
            });
        },
        { rootMargin: "420px 0px" }
    );

    lazyBackgrounds.forEach((element) => backgroundObserver.observe(element));
} else {
    reveals.forEach((element) => element.classList.add("is-visible"));
    lazyBackgrounds.forEach(loadLazyBackground);
}

document.querySelectorAll("[data-accordion]").forEach((accordion) => {
    const trigger = accordion.querySelector("[data-accordion-trigger]");
    trigger?.addEventListener("click", () => {
        const collapsed = accordion.classList.toggle("is-collapsed");
        trigger.setAttribute("aria-expanded", String(!collapsed));
    });
});

document.querySelectorAll("[data-program-card]").forEach((card) => {
    const toggleButton = card.querySelector("[data-program-details-toggle]");
    const toggleLabel = toggleButton?.querySelector("span");
    const details = card.querySelector("[data-program-details]");
    const hiddenDetailsCount = details ? details.children.length - 1 : 0;
    const toggleText = {
        ru: { more: "Больше", less: "Свернуть" },
        ky: { more: "Көбүрөөк", less: "Жыйуу" },
        en: { more: "More", less: "Collapse" }
    };

    if (!toggleButton || hiddenDetailsCount <= 0) {
        toggleButton?.remove();
        return;
    }

    const getToggleText = () => toggleText[document.documentElement.lang] || toggleText.ru;

    const setProgramExpanded = (isExpanded) => {
        card.classList.toggle("is-expanded", isExpanded);
        toggleButton.setAttribute("aria-expanded", String(isExpanded));
        if (toggleLabel) {
            const labels = getToggleText();
            toggleLabel.textContent = isExpanded ? labels.less : labels.more;
        }
    };

    const toggleProgram = () => {
        setProgramExpanded(!card.classList.contains("is-expanded"));
    };

    toggleButton.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleProgram();
    });

    card.addEventListener("click", (event) => {
        if (event.target.closest("a, button, input, textarea, select")) return;
        toggleProgram();
    });

    card.addEventListener("keydown", (event) => {
        if (event.target.closest("a, button, input, textarea, select")) return;
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            toggleProgram();
        }
    });

});

document.querySelectorAll("[data-card-link]").forEach((card) => {
    const openCard = () => {
        const url = card.dataset.cardLink;
        if (url) window.location.href = url;
    };

    card.addEventListener("click", (event) => {
        if (event.target.closest("a, button, input, textarea, select")) return;
        openCard();
    });

    card.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openCard();
        }
    });
});

document.querySelectorAll("[data-news-filter]").forEach((button) => {
    button.addEventListener("click", () => {
        const filter = button.dataset.newsFilter;
        document.querySelectorAll("[data-news-filter]").forEach((item) => {
            item.classList.toggle("is-active", item === button);
        });
        document.querySelectorAll("[data-news-category]").forEach((card) => {
            const visible = filter === "all" || card.dataset.newsCategory === filter;
            card.hidden = !visible;
        });
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

const setActiveLanguage = (lang) => {
    languageLinks.forEach((link) => {
        link.classList.toggle("is-active", link.dataset.translateLang === lang);
    });
    document.documentElement.lang = lang === "ky" ? "ky" : lang;
};

const normalizeText = (text) => text.replace(/\s+/g, " ").trim();

const setTranslationLoading = (isLoading) => {
    document.body.classList.toggle("is-translating", isLoading);
    languageSwitch?.classList.toggle("is-loading", isLoading);
};

const translationCache = { ru: {} };
const translatableTextNodes = [];
const translatableAttributes = [];
const translatableAttributeNames = ["aria-label", "title", "alt", "placeholder", "data-full"];

const collectTranslatableContent = () => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
            if (!node.parentElement) return NodeFilter.FILTER_REJECT;
            if (node.parentElement.closest("script, style, noscript, svg, iframe, .notranslate")) {
                return NodeFilter.FILTER_REJECT;
            }
            return /[\u0400-\u04FF]/.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
        }
    });

    while (walker.nextNode()) {
        const node = walker.currentNode;
        const original = normalizeText(node.nodeValue);
        if (original) {
            translatableTextNodes.push({
                node,
                original,
                leading: node.nodeValue.match(/^\s*/)?.[0] || "",
                trailing: node.nodeValue.match(/\s*$/)?.[0] || ""
            });
        }
    }

    document.querySelectorAll("*").forEach((element) => {
        if (element.closest(".notranslate")) return;
        translatableAttributeNames.forEach((name) => {
            const value = element.getAttribute(name);
            const original = value ? normalizeText(value) : "";
            if (original && /[\u0400-\u04FF]/.test(original)) {
                translatableAttributes.push({ element, name, original });
            }
        });
    });
};

const loadLocalDictionary = async (lang) => {
    if (translationCache[lang]) return translationCache[lang];
    const response = await fetch(`/static/myapp/i18n/${lang}.json`, {
        cache: "force-cache",
        headers: { Accept: "application/json" }
    });
    if (!response.ok) throw new Error(`Missing local dictionary: ${lang}`);
    translationCache[lang] = await response.json();
    return translationCache[lang];
};

const updateLanguageUrl = (lang) => {
    const url = new URL(window.location.href);
    if (lang === "ru") {
        url.searchParams.delete("lang");
    } else {
        url.searchParams.set("lang", lang);
    }
    window.history.replaceState({}, "", url);
};

const applyLanguage = async (lang) => {
    const nextLang = lang === "kg" ? "ky" : lang;
    localStorage.setItem("ak-suu-language", nextLang);
    setActiveLanguage(nextLang);
    setTranslationLoading(true);
    updateLanguageUrl(nextLang);

    try {
        const dictionary = nextLang === "ru" ? {} : await loadLocalDictionary(nextLang);
        translatableTextNodes.forEach((item) => {
            const value = nextLang === "ru" ? item.original : dictionary[item.original] || item.original;
            item.node.nodeValue = `${item.leading}${value}${item.trailing}`;
        });
        translatableAttributes.forEach((item) => {
            const value = nextLang === "ru" ? item.original : dictionary[item.original] || item.original;
            item.element.setAttribute(item.name, value);
        });
    } catch (error) {
        console.warn(error);
    } finally {
        window.setTimeout(() => setTranslationLoading(false), 120);
    }
};

languageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
        event.preventDefault();
        applyLanguage(link.dataset.translateLang);
    });
});

collectTranslatableContent();

const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
const savedLanguage = requestedLanguage || localStorage.getItem("ak-suu-language") || "ru";
applyLanguage(["ru", "ky", "kg", "en"].includes(savedLanguage) ? savedLanguage : "ru");
