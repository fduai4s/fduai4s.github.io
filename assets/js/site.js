// Publication filters: search, type, year group and "high-impact only".
(function () {
  var form = document.getElementById("publication-filters");
  if (!form) return;

  var items = Array.prototype.slice.call(document.querySelectorAll("[data-publication]"));
  var groups = Array.prototype.slice.call(document.querySelectorAll("[data-publication-group]"));
  var count = document.getElementById("publication-count");
  var empty = document.getElementById("publication-empty");
  var clear = document.getElementById("publication-clear");
  var template = count.getAttribute("data-template");

  items.forEach(function (el) {
    el._search = (el.getAttribute("data-search") || el.textContent).toLowerCase();
  });

  function apply() {
    var q = form.q.value.trim().toLowerCase();
    var type = form.type.value;
    var group = form.group.value;
    var hi = form.hi.checked;
    var terms = q ? q.split(/\s+/) : [];
    var shown = 0;

    items.forEach(function (el) {
      var ok = (!type || el.getAttribute("data-type") === type) &&
        (!group || el.getAttribute("data-group") === group) &&
        (!hi || el.hasAttribute("data-high-impact")) &&
        terms.every(function (t) { return el._search.indexOf(t) !== -1; });
      el.hidden = !ok;
      if (ok) shown++;
    });
    groups.forEach(function (g) {
      g.hidden = !g.querySelector("[data-publication]:not([hidden])");
    });

    var filtered = q || type || group || hi;
    count.hidden = !filtered;
    count.textContent = template.replace("{n}", shown).replace("{total}", items.length);
    empty.hidden = shown !== 0;
  }

  // Allow links such as /publications/?q=perovskite&hi=1
  var params = new URLSearchParams(window.location.search);
  if (params.has("q")) form.q.value = params.get("q");
  if (params.has("type")) form.type.value = params.get("type");
  if (params.has("year")) form.group.value = params.get("year");
  if (params.get("hi") === "1") form.hi.checked = true;

  form.hidden = false;
  apply();
  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  form.addEventListener("reset", function () { setTimeout(apply, 0); });
  if (clear) clear.addEventListener("click", function () { form.reset(); });
})();
