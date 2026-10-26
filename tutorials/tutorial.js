// Shared behaviour for the chart walkthroughs in /tutorials.
//
// Page markup this script expects:
//   <div class="code-block">                  a code block, optionally with Vega-Lite and Altair versions
//     <pre data-lang="vl">…</pre>              (omit data-lang for single-language blocks)
//     <pre data-lang="altair">…</pre>
//   <div class="chart" data-spec="x.json" data-modify="name">   a chart, embedded when the page loads
//   <details class="full-code" data-vl="x.json" data-altair="x.py">   full code, fetched when opened
//   <nav class="toc"><a href="#id">…</a></nav> sidebar links, highlighted for the section in view
//
// Pages can register spec modifiers on window.specModifiers, keyed by data-modify, and extra
// vegaEmbed options on window.embedOptions, keyed by data-options.

(function () {
    const LANG_KEY = "tutorial-code-lang";
    const LANGS = { vl: "Vega-Lite", altair: "Altair" };
    // GitHub's 'copy' icon (Octicons, MIT licence)
    const COPY_ICON =
        '<svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" aria-hidden="true">' +
        '<path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"></path>' +
        '<path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"></path>' +
        "</svg>";
    const EMBED_OPTIONS = {
        renderer: "svg",
        actions: { export: true, source: false, compiled: false, editor: true },
    };

    // ---------- Code language (Vega-Lite or Altair) ----------

    function readLang() {
        try {
            return localStorage.getItem(LANG_KEY) || "vl";
        } catch (e) {
            return "vl";
        }
    }

    function setLang(lang) {
        document.body.dataset.lang = lang;
        document.querySelectorAll("[data-lang-btn]").forEach((btn) => {
            btn.setAttribute("aria-pressed", String(btn.dataset.langBtn === lang));
        });
        try {
            localStorage.setItem(LANG_KEY, lang);
        } catch (e) {
            // Storage can be blocked (private windows); the toggle still works for this visit
        }
    }

    // Add a header with language tabs and a copy button to each code block
    function decorateCodeBlock(block) {
        if (block.querySelector(".code-head")) return;
        const head = document.createElement("div");
        head.className = "code-head";

        const title = document.createElement("span");
        title.className = "code-title";
        title.textContent = block.dataset.title || "";
        head.appendChild(title);

        if (block.querySelector('[data-lang="altair"]')) {
            Object.entries(LANGS).forEach(([lang, label]) => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.dataset.langBtn = lang;
                btn.textContent = label;
                btn.setAttribute("aria-pressed", String(document.body.dataset.lang === lang));
                btn.addEventListener("click", () => setLang(lang));
                head.appendChild(btn);
            });
        }

        const copy = document.createElement("button");
        copy.type = "button";
        copy.className = "copy-btn";
        copy.innerHTML = COPY_ICON;
        copy.title = "Copy code";
        copy.setAttribute("aria-label", "Copy code");
        copy.addEventListener("click", () => {
            const visible = [...block.querySelectorAll("pre")].find((pre) => pre.offsetParent !== null);
            if (!visible) return;
            navigator.clipboard.writeText(visible.textContent).then(() => {
                copy.textContent = "Copied";
                setTimeout(() => (copy.innerHTML = COPY_ICON), 1500);
            });
        });
        head.appendChild(copy);

        block.prepend(head);
    }

    // ---------- Full code panels ----------

    function codeBlockFor(sources) {
        const block = document.createElement("div");
        block.className = "code-block";
        sources.forEach(({ lang, text, prism }) => {
            const pre = document.createElement("pre");
            if (lang) pre.dataset.lang = lang;
            const code = document.createElement("code");
            code.className = "language-" + prism;
            code.textContent = text;
            pre.appendChild(code);
            block.appendChild(pre);
        });
        return block;
    }

    async function openFullCode(details) {
        if (details.dataset.loaded) return;
        details.dataset.loaded = "true";
        const sources = [];
        if (details.dataset.vl) sources.push({ lang: "vl", url: details.dataset.vl, prism: "json" });
        if (details.dataset.altair) sources.push({ lang: "altair", url: details.dataset.altair, prism: "python" });
        try {
            for (const src of sources) {
                const res = await fetch(src.url);
                if (!res.ok) throw new Error(`${res.status} for ${src.url}`);
                src.text = await res.text();
            }
            const block = codeBlockFor(sources.length > 1 ? sources : sources.map((s) => ({ ...s, lang: null })));
            block.dataset.title = details.dataset.title || "";
            details.appendChild(block);
            decorateCodeBlock(block);
            if (window.Prism) block.querySelectorAll("code").forEach((c) => Prism.highlightElement(c));
        } catch (err) {
            const p = document.createElement("p");
            p.className = "chart-error";
            p.textContent = "Could not load the code (" + err.message + "). If you opened this file directly, serve the folder with `python3 -m http.server`.";
            details.appendChild(p);
        }
    }

    // ---------- Charts ----------

    // Vega measures text when it draws, so wait for the web fonts before embedding
    const fontsReady = Promise.all([
        document.fonts.load('400 1em "Hanken Grotesk"'),
        document.fonts.load('600 1em "Hanken Grotesk"'),
    ]).catch(() => {});

    async function embedChart(el) {
        el.classList.add("loading");
        try {
            const res = await fetch(el.dataset.spec);
            if (!res.ok) throw new Error(`${res.status} for ${el.dataset.spec}`);
            let spec = await res.json();
            const modify = el.dataset.modify && (window.specModifiers || {})[el.dataset.modify];
            if (modify) spec = modify(spec);
            const extra = (el.dataset.options && (window.embedOptions || {})[el.dataset.options]) || {};
            await fontsReady;
            el.classList.remove("loading");
            await vegaEmbed(el, spec, { ...EMBED_OPTIONS, ...extra });
        } catch (err) {
            el.classList.remove("loading");
            el.innerHTML = "";
            const p = document.createElement("p");
            p.className = "chart-error";
            p.textContent = "Could not draw this chart (" + err.message + ").";
            el.appendChild(p);
        }
    }

    // Embed every chart at once (the data file is cached after the first fetch). Charts change the page
    // height as they draw, so a link to #section can land in the wrong place: jump there again once
    // they have all drawn, unless the reader has started scrolling.
    function embedAllCharts() {
        let readerScrolled = false;
        ["wheel", "touchmove", "keydown"].forEach((evt) =>
            window.addEventListener(evt, () => (readerScrolled = true), { once: true, passive: true })
        );
        const charts = [...document.querySelectorAll(".chart[data-spec]")];
        // Wait for the body fonts too: swapping them in reflows the text
        Promise.all([...charts.map(embedChart), document.fonts.ready]).then(() => {
            const target = location.hash && document.querySelector(location.hash);
            if (target && !readerScrolled) {
                requestAnimationFrame(() => target.scrollIntoView({ behavior: "instant" }));
            }
        });
    }

    // ---------- Sidebar: highlight the section in view ----------

    function watchSections() {
        const links = [...document.querySelectorAll(".toc a[href^='#']")];
        const sections = links.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
        function update() {
            const line = window.scrollY + window.innerHeight * 0.3;
            let current = sections[0];
            sections.forEach((s) => {
                if (s.offsetTop <= line) current = s;
            });
            links.forEach((a) => a.classList.toggle("active", current && a.getAttribute("href") === "#" + current.id));
        }
        window.addEventListener("scroll", update, { passive: true });
        window.addEventListener("resize", update);
        update();
    }

    // ---------- Start ----------

    document.addEventListener("DOMContentLoaded", () => {
        setLang(readLang());
        document.querySelectorAll(".lang-switch [data-lang-btn]").forEach((btn) => {
            btn.addEventListener("click", () => setLang(btn.dataset.langBtn));
        });
        document.querySelectorAll(".code-block").forEach(decorateCodeBlock);
        document.querySelectorAll("details.full-code").forEach((d) => {
            d.addEventListener("toggle", () => d.open && openFullCode(d));
        });
        embedAllCharts();
        watchSections();
    });
})();
