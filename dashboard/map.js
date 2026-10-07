(function (root) {
  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  var BOXES = [
    { id: "notes", title: "Notes", line: "The only source.", detail: "Markdown files in corpus/. Three shelves: Orbital, Neural, and Earth. An answer is not allowed to use anything else." },
    { id: "passages", title: "Passages", line: "Notes, cut short.", detail: "Each note is split on paragraphs. If a piece starts mid-thought, the previous paragraph stays with it. The browser copy of this list is archive.json." },
    { id: "words", title: "Word index", line: "Same words rank higher.", detail: "BM25 scores how rare the question's words are, and how often they appear. This list is built once, before anyone asks." },
    { id: "meaning", title: "Meaning index", line: "Similar wording.", detail: "Each passage is stored as a TF-IDF vector. The question gets a vector of its own. This is a second ranked list. It is not a chat model, and it needs no key." },
    { id: "names", title: "Name graph", line: "Names that share a note.", detail: "If two names appear on the same note, they become neighbors. A thin question can borrow a few of those names." },
    { id: "question", title: "Question", line: "What you typed.", detail: "The box on Ask, or the ask command. The text is kept as-is. Nothing rewrites it yet." },
    { id: "guard", title: "First guard", line: "Bad questions stop.", detail: "Empty text, more than 400 characters, a request to ignore the rules, and personal data are refused. Personal data means an email, a phone number, or a card-shaped number. The indexes stay closed." },
    { id: "glass", title: "Glass", line: "Search once.", detail: "The word list and the meaning list are merged. Six passages are graded. Sentences are copied from the ones that match, and each sentence gets a number. There is no retry." },
    { id: "crystal", title: "Crystal", line: "Each name keeps a seat.", detail: "Search is balanced so one named thing cannot crowd the other out. Neighbor names are added once, duplicates are merged, and the path stops. There is no loop." },
    { id: "aurora", title: "Aurora", line: "The long path.", detail: "It labels the question, searches, and grades. A thin grade can search again, at most twice. Then it writes the sentences and checks that each citation number points at a real passage. Open Path to see that walk lit for the last question." },
    { id: "out", title: "Second guard", line: "The sentence must be in the note.", detail: "After an answer is written, every cited sentence has to appear in the passage it cites. A sentence that fails is removed. If nothing cited remains, the answer becomes a refusal. A question that was stopped, or that was outside the library, never reaches this box." },
    { id: "page", title: "This page", line: "Same rules, in the browser.", detail: "Ask shows the answer and the notes it came from. Flow marks the steps that ran. The page does not send the question to a server." },
  ];

  function byId(id) {
    for (var i = 0; i < BOXES.length; i++) if (BOXES[i].id === id) return BOXES[i];
    return null;
  }

  function box(id, selected) {
    var item = byId(id);
    var on = id === selected ? " on" : "";
    return '<button type="button" class="arch-box' + on + '" data-arch="' + esc(id) + '"><b>' +
      esc(item.title) + "</b><small>" + esc(item.line) + "</small></button>";
  }

  function arrow() {
    return '<span class="arch-to" aria-hidden="true"></span>';
  }

  function fan(ids, selected) {
    return '<div class="arch-fan">' + ids.map(function (id) { return box(id, selected); }).join("") + "</div>";
  }

  function chain(ids, selected) {
    return ids.map(function (id) { return box(id, selected); }).join(arrow());
  }

  function lane(label, inner) {
    return '<section class="arch-lane"><p class="arch-label">' + esc(label) + '</p><div class="arch-flow">' + inner + "</div></section>";
  }

  function down() {
    return '<div class="arch-down" aria-hidden="true"></div>';
  }

  function render(selectedId) {
    var selected = byId(selectedId) || byId("guard");
    var board = [
      lane("Built before anyone asks", chain(["notes", "passages"], selected.id) + arrow() + fan(["words", "meaning", "names"], selected.id)),
      lane("A question arrives", chain(["question", "guard"], selected.id)),
      lane("One of these runs", fan(["glass", "crystal", "aurora"], selected.id)),
      lane("After an answer is written", chain(["out", "page"], selected.id)),
    ].join(down());
    return '<div class="arch"><p class="kicker">Architecture</p><h1>The pieces.</h1>' +
      '<p class="lede">Follow the arrows from top to bottom. Click a box to read what happens there. Flow marks these same steps for one question.</p>' +
      '<div class="arch-board" role="group" aria-label="Architecture of the reading desk">' + board + "</div>" +
      '<article class="arch-note" id="arch-note"><h2>' + esc(selected.title) + "</h2><p>" + esc(selected.detail) + "</p></article></div>";
  }

  root.PrismMap = { render: render };
})(typeof globalThis !== "undefined" ? globalThis : this);
