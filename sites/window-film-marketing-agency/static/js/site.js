// Window Film Marketing Agency: menu, dropdowns, simulator and lead form.
(function () {
  const body = document.body;

  // Mobile menu
  const menuBtn = document.querySelector(".menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", () => {
      const open = body.classList.toggle("menu-open");
      menuBtn.setAttribute("aria-expanded", open);
      menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  // Dropdowns: click toggles (touch and mobile); hover handles desktop in CSS
  document.querySelectorAll(".has-drop > .nav-top").forEach((btn) => {
    btn.addEventListener("click", () => {
      const li = btn.parentElement;
      const open = !li.classList.contains("open");
      document.querySelectorAll(".has-drop.open").forEach((x) => { x.classList.remove("open"); x.firstElementChild.setAttribute("aria-expanded", "false"); });
      li.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", open);
    });
  });
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".has-drop") && window.matchMedia("(min-width: 1081px)").matches) {
      document.querySelectorAll(".has-drop.open").forEach((x) => { x.classList.remove("open"); x.firstElementChild.setAttribute("aria-expanded", "false"); });
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    document.querySelectorAll(".has-drop.open").forEach((x) => x.classList.remove("open"));
    if (body.classList.contains("menu-open")) menuBtn.click();
  });

  // Simulator
  const sim = document.querySelector("[data-sim]");
  if (sim) {
    const data = JSON.parse(sim.querySelector(".sim-data").textContent);
    const W = { pages: 24, gbp: 20, reviews: 20, projects: 14, listings: 16 };
    const MAPS = { pages: 12, gbp: 34, reviews: 26, projects: 10, listings: 12 };
    let qi = 0, ch = sim.querySelector(".sim-ch.is-on").dataset.ch;
    const $ = (s) => sim.querySelector(s);
    const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

    function render() {
      const q = data.questions[qi];
      const on = {};
      sim.querySelectorAll("[data-sig]").forEach((i) => (on[i.dataset.sig] = i.checked));
      const w = ch === "Google Maps" ? MAPS : W;
      const pct = Math.min(97, 6 + Math.round(Object.keys(w).reduce((a, k) => a + (on[k] ? w[k] : 0), 0) * 0.91));
      $("[data-pct]").textContent = pct + "%";
      $("[data-bar]").style.width = pct + "%";
      const st = $("[data-state]");
      const level = pct >= 85 ? 4 : pct >= 60 ? 3 : pct >= 35 ? 2 : 1;
      st.textContent = ["INVISIBLE", "MENTIONED", "RECOMMENDED", "TOP PICK"][level - 1];
      st.className = "sim-state s" + level;
      $("[data-bar]").className = "s" + level;
      $("[data-ask]").textContent = q.q;

      const reasons = [];
      if (on.reviews) reasons.push(q.review);
      if (on.pages) reasons.push(q.site);
      if (on.projects) reasons.push("photos show similar " + q.film + " jobs in " + q.city);
      if (on.gbp) reasons.push("Google profile lists " + q.film + " as a service");
      if (on.listings) reasons.push("business details match across every source");
      const you = { you: true, name: "Your Window Film Co.", why: reasons.slice(0, 2).join("; ") || "limited information found" };
      const others = [
        { name: "Competitor Tint & Film", why: "many reviews mention " + q.film },
        { name: "Another " + q.city + " Window Tinting", why: "has a dedicated " + q.film + " page" },
        { name: "Regional Glass & Film", why: "listed on manufacturer dealer locator" },
      ];
      let list = others.slice();
      if (level === 4) list = [you, ...others.slice(0, 2)];
      else if (level === 3) list = [others[0], you, others[1]];
      else if (level === 2) list = [...others.slice(0, 2), you];
      else list = others;
      const intro = ch === "Google Maps" ? "Map results for " + q.film + " near " + q.city : "Here are " + q.film + " installers in " + q.city + " worth contacting:";
      $("[data-reply]").innerHTML = `<span class="src">${esc(ch)}</span><p>${esc(intro)}</p><ol>${list
        .map((b, i) => `<li${b.you ? ' class="you"' : ""}><b>${i + 1}. ${esc(b.name)}</b><small>${esc(b.why)}</small></li>`)
        .join("")}</ol>${level === 1 ? "<p><small>Your company isn't mentioned. Not enough clear, consistent information for this question.</small></p>" : ""}`;
    }

    sim.querySelectorAll(".sim-q").forEach((b) => b.addEventListener("click", () => {
      sim.querySelectorAll(".sim-q").forEach((x) => { x.classList.remove("is-on"); x.setAttribute("aria-pressed", "false"); });
      b.classList.add("is-on"); b.setAttribute("aria-pressed", "true");
      qi = +b.dataset.q; render();
    }));
    sim.querySelectorAll(".sim-ch").forEach((b) => b.addEventListener("click", () => {
      sim.querySelectorAll(".sim-ch").forEach((x) => { x.classList.remove("is-on"); x.setAttribute("aria-pressed", "false"); });
      b.classList.add("is-on"); b.setAttribute("aria-pressed", "true");
      ch = b.dataset.ch; render();
    }));
    sim.querySelectorAll("[data-sig]").forEach((i) => i.addEventListener("change", render));
    $("[data-all]").addEventListener("click", () => { sim.querySelectorAll("[data-sig]").forEach((i) => (i.checked = true)); render(); });
    $("[data-reset]").addEventListener("click", () => { sim.querySelectorAll("[data-sig]").forEach((i) => (i.checked = false)); render(); });
    render();
  }

  // Lead forms
  const topic = new URLSearchParams(location.search).get("topic");
  document.querySelectorAll("form.lead").forEach((form) => {
    if (topic === "call") form.querySelector("[name=topic]").value = "Book a call";
    const status = form.querySelector(".f-status");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const fd = new FormData(form);
      const films = fd.getAll("films").join(", ");
      const key = form.dataset.key;
      if (!key) {
        // No form service configured yet: hand off to the visitor's email app.
        const lines = ["Name: " + fd.get("name"), "Company: " + fd.get("company"), "Email: " + fd.get("email"), "Phone: " + fd.get("phone"), "Website: " + fd.get("website"), "Need: " + fd.get("topic"), "Films: " + films, "", fd.get("message")];
        location.href = "mailto:" + form.dataset.email + "?subject=" + encodeURIComponent(fd.get("topic") + " - " + fd.get("company")) + "&body=" + encodeURIComponent(lines.join("\n"));
        status.className = "f-status ok";
        status.textContent = "Opening your email app. If nothing happens, email " + form.dataset.email;
        return;
      }
      const payload = Object.fromEntries(fd.entries());
      payload.films = films;
      const btn = form.querySelector("button[type=submit]");
      btn.disabled = true;
      status.className = "f-status";
      status.textContent = "Sending...";
      try {
        const r = await fetch(form.action, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(payload) });
        const j = await r.json();
        if (!j.success) throw new Error(j.message || "Send failed");
        form.reset();
        status.className = "f-status ok";
        status.textContent = "Thanks! We got it and will be in touch within one business day.";
      } catch (err) {
        status.className = "f-status err";
        status.textContent = "Something went wrong. Please email " + form.dataset.email;
      } finally {
        btn.disabled = false;
      }
    });
  });
  // Homepage reel: swap the poster for the video on tap, with sound
  document.querySelectorAll("[data-reel]").forEach((box) => {
    const btn = box.querySelector(".reel-play");
    btn.addEventListener("click", () => {
      const v = document.createElement("video");
      v.src = btn.dataset.src;
      v.poster = box.querySelector("img").src;
      v.controls = true;
      v.playsInline = true;
      v.setAttribute("playsinline", "");
      box.replaceChildren(v);
      v.play().catch(() => {});
    });
  });
})();
