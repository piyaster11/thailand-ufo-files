/* Thailand UFO Files — client application. All visible numbers are guarded. */
(() => {
  const $ = (id) => document.getElementById(id);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const I18N = {
    en: {
      menu: "Files", random: "Random case", sound: "Sound: off", soundOn: "Sound: on",
      about: "About", filters: "Filters", search: "Search", years: "Year range",
      province: "Province", category: "Category", credibility: "Credibility",
      hasphoto: "Has hosted photo or source media", reset: "Reset filters",
      play: "Play timeline", pause: "Pause", chartYear: "By year", chartCat: "By category",
      chartProv: "By province", heat: "Heatmap", heatOn: "Heatmap: on",
      disclaimer: "Entries are unverified reports from public sources, not proof of alien craft. Many have mundane explanations. Pins are often approximate.",
      cases: "Case files", open: "Open file", fly: "Fly to pin", share: "Copy link",
      source: "Sources", viewSource: "View source", noPhoto: "No photograph is hosted for this file. Follow the source link for any images in the original report.",
      precision: "Coordinate precision", summary: "Summary", explain: "Explanation offered",
      unmapped: "No reliable map pin", illustration: "Illustration — not evidence",
      all: "All", empty: "No files match these filters.",
      statsCases: "Case files", statsMapped: "On the map", statsExplained: "Tagged explained", statsPhotos: "With hosted photo",
      cred_witness_report: "Witness report", cred_media_reported: "Media-reported",
      cred_explained: "Explained", cred_unverified: "Unverified",
      cat_light_orb: "Light / orb", cat_fireball: "Fireball / meteor",
      cat_naga_fireballs: "Naga fireballs", cat_triangle: "Triangle",
      cat_disc: "Disc", cat_formation: "Formation",
      cat_military_aviation: "Military / aviation", cat_rocket_reentry_starlink: "Rocket / Starlink / ISS",
      cat_cylinder_other: "Cylinder / other", cat_unspecified: "Unspecified",
      prec_exact: "Exact", prec_area: "Area", prec_province: "Province centroid", prec_unspecified: "Unspecified",
    },
    th: {
      menu: "แฟ้ม", random: "สุ่มแฟ้ม", sound: "เสียง: ปิด", soundOn: "เสียง: เปิด",
      about: "เกี่ยวกับ", filters: "ตัวกรอง", search: "ค้นหา", years: "ช่วงปี",
      province: "จังหวัด", category: "ประเภท", credibility: "ความน่าเชื่อถือของแหล่งข้อมูล",
      hasphoto: "มีภาพที่โฮสต์หรือสื่อในแหล่งต้นทาง", reset: "ล้างตัวกรอง",
      play: "เล่นไทม์ไลน์", pause: "หยุด", chartYear: "รายปี", chartCat: "รายประเภท",
      chartProv: "รายจังหวัด", heat: "แผนที่ความหนาแน่น", heatOn: "ความหนาแน่น: เปิด",
      disclaimer: "รายการเหล่านี้เป็นรายงานจากแหล่งสาธารณะที่ยังไม่ได้พิสูจน์ ไม่ใช่หลักฐานของยานต่างดาว หลายเหตุการณ์มีคำอธิบายสามัญ จุดบนแผนที่มักเป็นตำแหน่งประมาณ",
      cases: "แฟ้มคดี", open: "เปิดแฟ้ม", fly: "บินไปที่หมุด", share: "คัดลอกลิงก์",
      source: "แหล่งที่มา", viewSource: "ดูแหล่งต้นทาง", noPhoto: "แฟ้มนี้ไม่ได้โฮสต์ภาพถ่าย กรุณาตามลิงก์แหล่งข่าวหากต้นทางมีภาพ",
      precision: "ความละเอียดพิกัด", summary: "สรุป", explain: "คำอธิบายที่มีการเสนอ",
      unmapped: "ไม่มีหมุดที่เชื่อถือได้", illustration: "ภาพประกอบ — ไม่ใช่หลักฐาน",
      all: "ทั้งหมด", empty: "ไม่มีแฟ้มที่ตรงกับตัวกรองนี้",
      statsCases: "แฟ้มคดี", statsMapped: "มีบนแผนที่", statsExplained: "ถูกระบุว่าอธิบายได้", statsPhotos: "มีภาพที่โฮสต์",
      cred_witness_report: "รายงานพยาน", cred_media_reported: "สื่อรายงาน",
      cred_explained: "มีคำอธิบาย", cred_unverified: "ยังไม่ตรวจสอบ",
      cat_light_orb: "แสง / ลูกไฟกลม", cat_fireball: "ลูกไฟ / ดาวตก",
      cat_naga_fireballs: "บั้งไฟพญานาค", cat_triangle: "สามเหลี่ยม",
      cat_disc: "จาน / วงรี", cat_formation: "ขบวน / แถว",
      cat_military_aviation: "ทหาร / การบิน", cat_rocket_reentry_starlink: "จรวด / สตาร์ลิงก์ / สถานีอวกาศ",
      cat_cylinder_other: "ทรงกระบอก / อื่น ๆ", cat_unspecified: "ไม่ระบุรูปทรง",
      prec_exact: "แม่นยำ", prec_area: "ระดับพื้นที่", prec_province: "จุดกลางจังหวัด", prec_unspecified: "ไม่ระบุ",
    },
  };

  const state = {
    lang: "en",
    data: null,
    filtered: [],
    yearMin: 1968,
    yearMax: 2026,
    dataYearMin: 1968,
    dataYearMax: 2026,
    cats: new Set(),
    creds: new Set(),
    map: null,
    cluster: null,
    heat: null,
    heatOn: false,
    markers: new Map(),
    charts: {},
    playTimer: null,
    sound: false,
    timelineIdx: null,
  };

  const t = (k) => (I18N[state.lang] && I18N[state.lang][k]) || I18N.en[k] || k;
  const safe = (v, fallback = "—") => {
    if (v === null || v === undefined || v === "") return fallback;
    if (typeof v === "number" && !Number.isFinite(v)) return fallback;
    return v;
  };
  const hasCoords = (s) => {
    if (s == null || s.lat == null || s.lng == null || s.lat === "" || s.lng === "") return false;
    const lat = Number(s.lat), lng = Number(s.lng);
    return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 5 && lat <= 21 && lng >= 96 && lng <= 106.5;
  };
  const yearOf = (s) => {
    const y = parseInt(String(s.date || s.year || ""), 10);
    return Number.isFinite(y) ? y : null;
  };
  const dateSortVal = (s) => {
    let d = s.date || "0000-00-00";
    if (/^\d{4}-\d{2}$/.test(d)) d += "-15";
    if (/^\d{4}$/.test(d)) d += "-06-30";
    return `${d}T${s.time_local || "00:00"}`;
  };

  function applyI18n() {
    document.querySelectorAll("[data-i]").forEach((el) => {
      const k = el.getAttribute("data-i");
      if (k === "sound") el.textContent = state.sound ? t("soundOn") : t("sound");
      else if (k === "heat") el.textContent = state.heatOn ? t("heatOn") : t("heat");
      else if (k === "play") el.textContent = state.playTimer ? t("pause") : t("play");
      else el.textContent = t(k);
    });
    $("langBtn").textContent = state.lang === "en" ? "TH" : "EN";
    document.documentElement.lang = state.lang === "th" ? "th" : "en";
  }

  /* -------- boot -------- */
  function runBoot() {
    const el = $("boot");
    const pre = $("bootText");
    const skip = () => { el.classList.add("done"); };
    $("skipBoot").addEventListener("click", skip);
    if (reduceMotion || location.hash) { skip(); return; }
    const lines = [
      "THAILAND UFO FILES  //  ACCESSING CLASSIFIED ARCHIVE",
      "-----------------------------------------------",
      "AUTH: PUBLIC TERMINAL",
      "CLEARANCE: OBSERVER",
      "LOADING CASE INDEX ........",
      "GEOCODING PLACE NAMES .....",
      "WARNING: REPORTS ARE UNVERIFIED. MANY HAVE MUNDANE EXPLANATIONS.",
      "THE TRUTH IS OUT THERE.",
    ];
    let i = 0, shown = "";
    const tick = () => {
      if (i >= lines.length) { setTimeout(skip, 500); return; }
      shown += lines[i++] + "\n";
      pre.innerHTML = shown + '<span class="boot-cursor"></span>';
      setTimeout(tick, 280);
    };
    tick();
  }

  /* -------- sound -------- */
  function beep() {
    if (!state.sound) return;
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "square";
      o.frequency.value = 880;
      g.gain.value = 0.03;
      o.connect(g); g.connect(ctx.destination);
      o.start();
      setTimeout(() => { o.frequency.value = 1320; }, 80);
      setTimeout(() => { o.stop(); ctx.close(); }, 160);
    } catch (_) { /* ignore */ }
  }

  /* -------- map -------- */
  function initMap() {
    const map = L.map("map", { scrollWheelZoom: true, worldCopyJump: true, zoomControl: true });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 18,
    }).addTo(map);
    map.setView([13.75, 100.5], 6);
    state.map = map;
    state.cluster = L.markerClusterGroup({
      showCoverageOnHover: false,
      maxClusterRadius: 48,
      iconCreateFunction(cluster) {
        const n = cluster.getChildCount();
        const size = n > 20 ? 48 : n > 8 ? 40 : 34;
        return L.divIcon({
          html: `<div class="marker-cluster-custom" style="width:${size}px;height:${size}px">${n}</div>`,
          className: "",
          iconSize: [size, size],
        });
      },
    });
    map.addLayer(state.cluster);
  }

  function markerIcon(s) {
    const explained = s.credibility === "explained" ? " cat-explained-ring" : "";
    return L.divIcon({
      className: "",
      html: `<div class="ufo-marker cat-${s.category || "unspecified"}${explained}"><span class="pulse-core"></span></div>`,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
    });
  }

  function rebuildMarkers(list) {
    state.cluster.clearLayers();
    state.markers.clear();
    if (state.heat) {
      state.map.removeLayer(state.heat);
      state.heat = null;
    }
    const heatPts = [];
    list.forEach((s) => {
      if (!hasCoords(s)) return;
      const lat = Number(s.lat), lng = Number(s.lng);
      const m = L.marker([lat, lng], { icon: markerIcon(s), title: s.case_no + " " + titleOf(s) });
      m.on("click", () => openCase(s, false));
      m.bindPopup(`<strong>${esc(s.case_no)}</strong><br>${esc(titleOf(s))}<br>${esc(s.date_label || s.date || "")}`);
      state.cluster.addLayer(m);
      state.markers.set(s.id, m);
      heatPts.push([lat, lng, 1]);
    });
    if (state.heatOn && heatPts.length) {
      state.heat = L.heatLayer(heatPts, { radius: 28, blur: 22, maxZoom: 10, gradient: { 0.2: "#003322", 0.5: "#00ff6a", 0.85: "#fff3a0" } });
      state.map.addLayer(state.heat);
    }
  }

  /* -------- filters -------- */
  function setupFilters(items) {
    const years = items.map(yearOf).filter((y) => y !== null);
    state.dataYearMin = Math.min(...years);
    state.dataYearMax = Math.max(...years);
    state.yearMin = state.dataYearMin;
    state.yearMax = state.dataYearMax;
    ["yearMin", "yearMax"].forEach((id) => {
      const el = $(id);
      el.min = state.dataYearMin;
      el.max = state.dataYearMax;
    });
    $("yearMin").value = state.yearMin;
    $("yearMax").value = state.yearMax;

    const provinces = [...new Set(items.map((s) => s.province).filter(Boolean))].sort();
    const sel = $("province");
    sel.innerHTML = `<option value="">${t("all")}</option>` + provinces.map((p) => `<option value="${esc(p)}">${esc(p)}</option>`).join("");

    const cats = [...new Set(items.map((s) => s.category).filter(Boolean))].sort();
    const creds = [...new Set(items.map((s) => s.credibility).filter(Boolean))].sort();
    $("catChecks").innerHTML = cats.map((c) => `<label><input type="checkbox" value="${esc(c)}" checked> <span>${esc(t("cat_" + c))}</span></label>`).join("");
    $("credChecks").innerHTML = creds.map((c) => `<label><input type="checkbox" value="${esc(c)}" checked> <span>${esc(t("cred_" + c))}</span></label>`).join("");
    state.cats = new Set(cats);
    state.creds = new Set(creds);

    const onChange = () => { applyFilters(); };
    $("q").addEventListener("input", onChange);
    $("yearMin").addEventListener("input", () => {
      state.yearMin = num($("yearMin").value, state.dataYearMin);
      if (state.yearMin > state.yearMax) { state.yearMax = state.yearMin; $("yearMax").value = state.yearMax; }
      applyFilters();
    });
    $("yearMax").addEventListener("input", () => {
      state.yearMax = num($("yearMax").value, state.dataYearMax);
      if (state.yearMax < state.yearMin) { state.yearMin = state.yearMax; $("yearMin").value = state.yearMin; }
      applyFilters();
    });
    $("province").addEventListener("change", onChange);
    $("hasPhoto").addEventListener("change", onChange);
    $("catChecks").addEventListener("change", (e) => {
      const boxes = [...$("catChecks").querySelectorAll("input")];
      state.cats = new Set(boxes.filter((b) => b.checked).map((b) => b.value));
      applyFilters();
    });
    $("credChecks").addEventListener("change", () => {
      const boxes = [...$("credChecks").querySelectorAll("input")];
      state.creds = new Set(boxes.filter((b) => b.checked).map((b) => b.value));
      applyFilters();
    });
    $("resetBtn").addEventListener("click", () => {
      $("q").value = "";
      $("province").value = "";
      $("hasPhoto").checked = false;
      state.yearMin = state.dataYearMin;
      state.yearMax = state.dataYearMax;
      $("yearMin").value = state.yearMin;
      $("yearMax").value = state.yearMax;
      $("catChecks").querySelectorAll("input").forEach((b) => { b.checked = true; });
      $("credChecks").querySelectorAll("input").forEach((b) => { b.checked = true; });
      state.cats = new Set(cats);
      state.creds = new Set(creds);
      stopPlay();
      $("timeline").value = $("timeline").max;
      applyFilters();
    });
  }

  function applyFilters() {
    const q = ($("q").value || "").trim().toLowerCase();
    const prov = $("province").value;
    const photo = $("hasPhoto").checked;
    const cut = timelineCutoff();
    $("yearMinLab").textContent = String(state.yearMin);
    $("yearMaxLab").textContent = String(state.yearMax);

    const list = state.data.sightings.filter((s) => {
      const y = yearOf(s);
      if (y !== null && (y < state.yearMin || y > state.yearMax)) return false;
      if (prov && s.province !== prov) return false;
      if (state.cats.size && s.category && !state.cats.has(s.category)) return false;
      if (state.creds.size && s.credibility && !state.creds.has(s.credibility)) return false;
      if (photo && !( (s.photos && s.photos.length) || s.media_in_source )) return false;
      if (q) {
        const blob = [s.case_no, s.id, s.title, s.title_th, s.summary, s.location_name, s.location_name_th, s.province, s.province_th].join(" ").toLowerCase();
        if (!blob.includes(q)) return false;
      }
      if (cut && dateSortVal(s) > cut) return false;
      return true;
    });
    list.sort((a, b) => dateSortVal(b).localeCompare(dateSortVal(a)));
    state.filtered = list;
    renderStats(list);
    renderList(list);
    rebuildMarkers(list);
    renderCharts(list);
  }

  function num(v, fallback) {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  }

  function renderStats(list) {
    const mapped = list.filter(hasCoords).length;
    const explained = list.filter((s) => s.credibility === "explained").length;
    const photos = list.filter((s) => s.photos && s.photos.length).length;
    const cells = [
      [list.length, "statsCases"],
      [mapped, "statsMapped"],
      [explained, "statsExplained"],
      [photos, "statsPhotos"],
    ];
    $("stats").innerHTML = cells.map(([n, k]) => `<div class="stat"><b data-count="${n}">${reduceMotion ? n : 0}</b><span>${t(k)}</span></div>`).join("");
    if (!reduceMotion) {
      $("stats").querySelectorAll("b[data-count]").forEach((el) => {
        const target = num(el.getAttribute("data-count"), 0);
        const start = performance.now();
        const tick = (now) => {
          const p = Math.min(1, (now - start) / 600);
          el.textContent = String(Math.round(target * p));
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    }
    $("listHead").textContent = `${t("cases")} (${list.length})`;
  }

  function titleOf(s) {
    return state.lang === "th" ? (s.title_th || s.title) : s.title;
  }
  function summaryOf(s) {
    return state.lang === "th" ? (s.summary_th || s.summary) : s.summary;
  }
  function locOf(s) {
    return state.lang === "th" ? (s.location_name_th || s.location_name) : s.location_name;
  }

  function renderList(list) {
    const ul = $("caseList");
    if (!list.length) {
      ul.innerHTML = `<li>${t("empty")}</li>`;
      return;
    }
    ul.innerHTML = list.map((s) => `
      <li data-id="${esc(s.id)}">
        <span class="cn">${esc(s.case_no)} // ${esc(s.date_label || s.date || "—")}</span>
        <span class="ct">${esc(titleOf(s))}</span>
        <span class="cm">${esc(locOf(s) || "—")} · ${esc(t("cat_" + s.category))} · ${esc(t("cred_" + s.credibility))}</span>
      </li>`).join("");
    ul.querySelectorAll("li[data-id]").forEach((li) => {
      li.addEventListener("click", () => {
        const s = state.data.sightings.find((x) => x.id === li.getAttribute("data-id"));
        if (s) openCase(s, true);
      });
    });
  }

  /* -------- charts -------- */
  const chartColor = "#00ff6a";
  function chartDefaults() {
    Chart.defaults.color = "#7aa388";
    Chart.defaults.borderColor = "rgba(0,255,106,.2)";
    Chart.defaults.font.family = "'Share Tech Mono', monospace";
    Chart.defaults.font.size = 10;
  }
  function renderCharts(list) {
    chartDefaults();
    const years = {};
    const cats = {};
    const provs = {};
    list.forEach((s) => {
      const y = yearOf(s);
      if (y !== null) years[y] = (years[y] || 0) + 1;
      const c = t("cat_" + s.category);
      cats[c] = (cats[c] || 0) + 1;
      const p = s.province || (state.lang === "th" ? "ไม่ระบุ" : "Unspecified");
      provs[p] = (provs[p] || 0) + 1;
    });
    const yearLabels = Object.keys(years).map(Number).sort((a, b) => a - b).map(String);
    const topProv = Object.entries(provs).sort((a, b) => b[1] - a[1]).slice(0, 8);
    paint("chartYear", "bar", yearLabels, yearLabels.map((y) => years[y] || 0));
    const catEntries = Object.entries(cats).sort((a, b) => b[1] - a[1]);
    paint("chartCat", "bar", catEntries.map((e) => e[0]), catEntries.map((e) => e[1]), true);
    paint("chartProv", "bar", topProv.map((e) => e[0]), topProv.map((e) => e[1]), true);
  }
  function paint(id, type, labels, data, horiz) {
    const canvas = $(id);
    if (!canvas) return;
    if (state.charts[id]) state.charts[id].destroy();
    const safeData = data.map((n) => (Number.isFinite(n) ? n : 0));
    state.charts[id] = new Chart(canvas, {
      type,
      data: {
        labels,
        datasets: [{
          data: safeData,
          backgroundColor: "rgba(0,255,106,.35)",
          borderColor: chartColor,
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: horiz ? "y" : "x",
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#7aa388", maxRotation: 0 }, grid: { color: "rgba(0,255,106,.08)" } },
          y: { ticks: { color: "#7aa388" }, grid: { color: "rgba(0,255,106,.08)" }, beginAtZero: true, precision: 0 },
        },
      },
    });
  }

  /* -------- timeline -------- */
  function setupTimeline(items) {
    const dates = items.map(dateSortVal).sort();
    $("timeline").min = 0;
    $("timeline").max = Math.max(0, dates.length - 1);
    $("timeline").value = dates.length - 1;
    $("timeline").addEventListener("input", () => {
      stopPlay();
      applyFilters();
      updateTlLabel();
    });
    $("playBtn").addEventListener("click", () => {
      if (state.playTimer) { stopPlay(); return; }
      let i = num($("timeline").value, 0);
      if (i >= num($("timeline").max, 0)) i = 0;
      $("timeline").value = i;
      applyFilters();
      state.playTimer = setInterval(() => {
        i = num($("timeline").value, 0) + 1;
        const max = num($("timeline").max, 0);
        if (i > max) { stopPlay(); return; }
        $("timeline").value = i;
        applyFilters();
        updateTlLabel();
      }, reduceMotion ? 80 : 220);
      applyI18n();
    });
    updateTlLabel();
  }
  function stopPlay() {
    if (state.playTimer) clearInterval(state.playTimer);
    state.playTimer = null;
    applyI18n();
  }
  function timelineCutoff() {
    const items = [...state.data.sightings].sort((a, b) => dateSortVal(a).localeCompare(dateSortVal(b)));
    const i = num($("timeline").value, items.length - 1);
    const max = num($("timeline").max, items.length - 1);
    if (i >= max) return null;
    const s = items[Math.min(i, items.length - 1)];
    return s ? dateSortVal(s) : null;
  }
  function updateTlLabel() {
    const items = [...state.data.sightings].sort((a, b) => dateSortVal(a).localeCompare(dateSortVal(b)));
    const i = num($("timeline").value, items.length - 1);
    const s = items[Math.min(i, items.length - 1)];
    $("tlLabel").textContent = s ? safe(s.date_label || s.date) : "—";
  }

  /* -------- case drawer -------- */
  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  function openCase(s, fly) {
    beep();
    const drawer = $("drawer");
    const title = titleOf(s);
    const sum = summaryOf(s);
    const loc = locOf(s) || "—";
    const prec = t("prec_" + (s.coord_precision || "unspecified"));
    const hasPin = hasCoords(s);
    const lat = hasPin ? Number(s.lat) : null, lng = hasPin ? Number(s.lng) : null;
    const photos = (s.photos || []).map((p) => {
      const tag = p.kind === "illustration" ? `<span class="illus-tag">${t("illustration")}</span>` : "";
      return `<figure>${tag}<img src="${esc(p.src)}" alt="${esc(p.alt || title)}" loading="lazy"><figcaption>${esc(p.credit || "")}${p.page ? ` · <a href="${esc(p.page)}" target="_blank" rel="noopener">Commons</a>` : ""}</figcaption></figure>`;
    }).join("");
    const sources = (s.sources || []).map((src) => `<li><a href="${esc(src.url)}" target="_blank" rel="noopener">${esc(src.name || t("viewSource"))}</a></li>`).join("");
    const explain = state.lang === "th" ? (s.explanation_th || s.explanation) : (s.explanation || s.explanation_th);
    drawer.innerHTML = `
      <button class="close-x" type="button" id="closeDrawer" aria-label="Close">×</button>
      <div class="cn" style="color:var(--amber);letter-spacing:.16em">${esc(s.case_no)}</div>
      <h2>${esc(title)}</h2>
      <div class="stamp-row">
        <span class="stamp">${esc(t("cred_" + s.credibility))}</span>
        <span class="stamp green">${esc(t("cat_" + s.category))}</span>
        ${s.media_in_source || (s.photos && s.photos.length) ? `<span class="stamp amber">MEDIA</span>` : ""}
      </div>
      <div class="case-meta">${esc(s.date_label || s.date || "—")} · ${esc(loc)}</div>
      <div class="kv">
        <b>ID</b><span>${esc(s.id)}</span>
        <b>${t("precision")}</b><span class="redact" tabindex="0">${esc(prec)}${s.coord_note ? " — " + esc(s.coord_note) : ""}</span>
        <b>Lat / Lng</b><span>${hasPin ? `${Number(lat).toFixed(4)}, ${Number(lng).toFixed(4)}` : t("unmapped")}</span>
        ${s.shape ? `<b>Shape</b><span>${esc(s.shape)}</span>` : ""}
        ${s.time_local ? `<b>Time</b><span>${esc(s.time_local)}</span>` : ""}
      </div>
      <h3>${t("summary")}</h3>
      <p class="case-summary">${esc(sum)}</p>
      ${explain ? `<h3>${t("explain")}</h3><p class="case-summary">${esc(explain)}</p>` : ""}
      ${s.credibility_note ? `<p class="hint">${esc(s.credibility_note)}</p>` : ""}
      ${photos ? `<div class="photos">${photos}</div>` : `<p class="hint">${t("noPhoto")}</p>`}
      <h3>${t("source")}</h3>
      <ul class="source-list">${sources}</ul>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px">
        ${hasPin ? `<button class="btn" type="button" id="flyBtn">${t("fly")}</button>` : ""}
        <button class="btn btn-ghost" type="button" id="shareBtn">${t("share")}</button>
      </div>
    `;
    drawer.classList.add("open");
    $("backdrop").classList.add("open");
    $("closeDrawer").addEventListener("click", closeCase);
    const flyBtn = $("flyBtn");
    if (flyBtn) flyBtn.addEventListener("click", () => flyTo(s));
    $("shareBtn").addEventListener("click", async () => {
      const url = `${location.origin}${location.pathname}#case=${encodeURIComponent(s.id)}`;
      try { await navigator.clipboard.writeText(url); $("shareBtn").textContent = "OK"; setTimeout(() => { $("shareBtn").textContent = t("share"); }, 1200); }
      catch { prompt("Link", url); }
    });
    location.hash = "case=" + encodeURIComponent(s.id);
    $("caseList").querySelectorAll("li").forEach((li) => li.classList.toggle("active", li.getAttribute("data-id") === s.id));
    if (fly && hasPin) flyTo(s);
  }
  function flyTo(s) {
    const lat = Number(s.lat), lng = Number(s.lng);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
    const z = s.coord_precision === "province" ? 8 : 10;
    state.map.flyTo([lat, lng], z, { duration: reduceMotion ? 0 : 0.8 });
    const m = state.markers.get(s.id);
    if (m) setTimeout(() => { try { m.openPopup(); } catch (_) {} }, reduceMotion ? 0 : 850);
  }
  function closeCase() {
    $("drawer").classList.remove("open");
    $("backdrop").classList.remove("open");
    if (location.hash.startsWith("#case=")) history.replaceState("", "", location.pathname + location.search);
  }
  function openFromHash() {
    const m = location.hash.match(/case=([^&]+)/);
    if (!m) return;
    const id = decodeURIComponent(m[1]);
    const s = state.data.sightings.find((x) => x.id === id || x.case_no === id);
    if (s) openCase(s, true);
  }

  /* -------- random / heat / lang -------- */
  function bindChrome() {
    $("randomBtn").addEventListener("click", () => {
      const pool = state.filtered.length ? state.filtered : state.data.sightings;
      if (!pool.length) return;
      const s = pool[Math.floor(Math.random() * pool.length)];
      openCase(s, true);
    });
    $("langBtn").addEventListener("click", () => {
      state.lang = state.lang === "en" ? "th" : "en";
      applyI18n();
      // re-render labels in lists/charts
      const sel = $("province");
      const cur = sel.value;
      const provinces = [...new Set(state.data.sightings.map((s) => s.province).filter(Boolean))].sort();
      sel.innerHTML = `<option value="">${t("all")}</option>` + provinces.map((p) => `<option value="${esc(p)}">${esc(p)}</option>`).join("");
      sel.value = cur;
      $("catChecks").querySelectorAll("label").forEach((lab) => {
        const val = lab.querySelector("input").value;
        lab.querySelector("span").textContent = t("cat_" + val);
      });
      $("credChecks").querySelectorAll("label").forEach((lab) => {
        const val = lab.querySelector("input").value;
        lab.querySelector("span").textContent = t("cred_" + val);
      });
      applyFilters();
      if ($("drawer").classList.contains("open")) {
        const id = (location.hash.match(/case=([^&]+)/) || [])[1];
        const s = id && state.data.sightings.find((x) => x.id === decodeURIComponent(id));
        if (s) openCase(s, false);
      }
    });
    $("soundBtn").addEventListener("click", () => {
      state.sound = !state.sound;
      $("soundBtn").setAttribute("aria-pressed", String(state.sound));
      applyI18n();
      if (state.sound) beep();
    });
    $("heatBtn").addEventListener("click", () => {
      state.heatOn = !state.heatOn;
      $("heatBtn").classList.toggle("active", state.heatOn);
      applyI18n();
      rebuildMarkers(state.filtered);
    });
    $("backdrop").addEventListener("click", closeCase);
    $("menuBtn").addEventListener("click", () => {
      const sb = $("sidebar");
      const open = !sb.classList.contains("open");
      sb.classList.toggle("open", open);
      $("menuBtn").setAttribute("aria-expanded", String(open));
    });
    window.addEventListener("hashchange", openFromHash);
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeCase(); });
  }

  /* -------- init -------- */
  async function init() {
    runBoot();
    initMap();
    bindChrome();
    applyI18n();
    const res = await fetch("data/sightings.json");
    if (!res.ok) throw new Error("Could not load sightings.json");
    const data = await res.json();
    if (!data || !Array.isArray(data.sightings)) throw new Error("Bad sightings payload");
    // harden against NaN in incoming data
    data.sightings.forEach((s) => {
      if (s.lat != null) { const n = Number(s.lat); s.lat = Number.isFinite(n) ? n : null; }
      if (s.lng != null) { const n = Number(s.lng); s.lng = Number.isFinite(n) ? n : null; }
    });
    state.data = data;
    setupFilters(data.sightings);
    setupTimeline(data.sightings);
    applyFilters();
    // fit map to pins
    const pts = data.sightings.filter(hasCoords).map((s) => [Number(s.lat), Number(s.lng)]);
    if (pts.length) state.map.fitBounds(pts, { padding: [30, 30], maxZoom: 7 });
    openFromHash();
  }

  init().catch((err) => {
    console.error(err);
    $("boot").classList.remove("done");
    $("bootText").textContent = "ARCHIVE ERROR: " + (err && err.message ? err.message : "unknown");
  });
})();
