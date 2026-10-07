const assert = require("assert");
require("../dashboard/map.js");

const map = globalThis.PrismMap;
assert.ok(map && map.render);

const html = map.render("guard");
assert.ok(html.includes('class="arch-board"'));
assert.ok(html.includes('class="arch-to"'));
assert.ok(html.includes('class="arch-down"'));
["Notes", "Passages", "Word index", "Meaning index", "Name graph", "Question", "First guard", "Glass", "Crystal", "Aurora", "Second guard", "This page"].forEach(function (title) {
  assert.ok(html.includes(title), "missing " + title);
});
assert.ok(html.includes("indexes stay closed"));
assert.ok(html.includes('data-arch="guard"'));
assert.ok(html.includes("arch-box on"));

const aurora = map.render("aurora");
assert.ok(aurora.includes("at most twice"));
assert.ok(!aurora.includes("indexes stay closed"));

const hostile = map.render("<script>");
assert.ok(!hostile.includes("<script>"));
assert.ok(hostile.includes("indexes stay closed"));
