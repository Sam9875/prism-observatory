(function (root) {
  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function step(id, title, summary, comes, happens, goes, code, traceNodes, ranIf) {
    return {
      kind: "step",
      id: id,
      title: title,
      summary: summary,
      comes: comes,
      happens: happens,
      goes: goes,
      code: code,
      traceNodes: traceNodes || [],
      ranIf: ranIf || null,
    };
  }

  function didSearch(_trace, lines) {
    return lines.some(function (item) { return String(item.detail).indexOf("does not retrieve") === -1; });
  }

  function factualRoute(trace) {
    return trace.some(function (item) {
      return item.node === "router" && String(item.detail).indexOf("factual") !== -1;
    });
  }

  function wroteWithoutSecondRetry(trace) {
    var wrote = trace.some(function (item) { return item.node === "synthesize"; });
    var second = trace.some(function (item) {
      return item.node === "rewrite" && String(item.detail).indexOf("Retry 2") !== -1;
    });
    return wrote && !second;
  }

  function wroteAfterSecondRetry(trace) {
    var wrote = trace.some(function (item) { return item.node === "synthesize"; });
    var second = trace.some(function (item) {
      return item.node === "rewrite" && String(item.detail).indexOf("Retry 2") !== -1;
    });
    return wrote && second;
  }

  var LANES = {
    system: {
      kicker: "Built once, then used for every question",
      title: "How the desk is wired",
      lede: "Notes are read and indexed before anyone asks. A question then hits a guard, one of three search paths, and a second guard. Nothing is answered from outside the notes.",
      blocks: [
        step("notes", "Notes", "The only source an answer may use.", "Markdown files in corpus/.", "Each file is read with its title, archive, and text.", "A document list. The browser copy of this list is dashboard/archive.json.", "corpus.py", []),
        step("split", "Passages", "Long notes become short pieces.", "One document.", "The text is split on paragraphs. If a piece starts mid-thought, the previous paragraph is kept with it.", "Chunks, each with an id and the document it came from.", "chunking.py", []),
        {
          kind: "split",
          label: "Those passages feed three indexes. A question does not rebuild them.",
          steps: [
            step("words", "Word index", "Exact word overlap.", "The passages.", "BM25 scores how rare and how frequent the question's words are.", "A ranked list of passages.", "index.py", []),
            step("meaning", "Meaning index", "Similar wording, not only the same words.", "The passages.", "A TF-IDF vector is stored for each passage. The question gets a vector of its own.", "A second ranked list.", "embeddings.py", []),
            step("names", "Name graph", "Which names appear together.", "Names listed on each note.", "Names that share a note become neighbors.", "Extra names a thin question can borrow.", "index.py", []),
          ],
        },
        step("ask", "Question", "Someone types a question.", "The text in the box, or the ask command.", "The text is kept as-is. No model rewrites it yet.", "The same question, handed to the guard.", "cli.py ask, or this page", ["input_guard"]),
        step("input_guard", "First guard", "Bad questions stop here.", "The raw question.", "Empty text, more than 400 characters, an attempt to override the instructions, and personal data are refused. Personal data means an email, a phone number, or a card-shaped number.", "Either a refusal and a closed library, or the question continuing.", "rails.py, then input_guard", ["input_guard"]),
        {
          kind: "split",
          label: "If the guard lets it through, one path runs. Open that path for every branch.",
          steps: [
            step("lane-glass", "Glass", "One search, then an answer.", "The question and the two ranked lists.", "Word rank and meaning rank are fused. Passages are graded. Sentences are copied out and cited.", "An answer, or a refusal if nothing matched.", "lenses.py run_glass", ["glass"]),
            step("lane-crystal", "Crystal", "One expansion, no loop.", "The question, plus names on the first hits.", "Search is balanced so each named thing keeps a passage. Neighbor names are added once, then duplicates are merged.", "An answer from the merged passages.", "lenses.py run_crystal", ["crystal"]),
            step("lane-aurora", "Aurora", "The long path, with a retry.", "The question and the indexes.", "Route, maybe plan, search, grade. A thin grade can search again, at most twice. Then write, check the citation ids, and guard the sentences.", "An answer, a refusal, or a stop.", "graph.py", ["router", "retrieve", "rewrite"]),
          ],
        },
        step("show", "On the page", "You see the result of whichever path ran.", "The answer, the passages, and the step list.", "Glass, Crystal, and Aurora all end in the same shape of result.", "The card on Ask: answer, citations, and the steps.", "dashboard/app.js", ["output_guard", "abstain"]),
      ],
    },
    glass: {
      kicker: "Short path",
      title: "Glass, one search",
      lede: "Glass does not plan and does not retry. If the guard passes and the library has a foothold, it searches once, grades, writes, and checks the sentences.",
      blocks: [
        step("g-in", "Question", "The text you submitted.", "A string.", "It is not rewritten.", "The same string.", "Ask box or cli.py", []),
        step("g-guard", "First guard", "Stop before any search.", "The question.", "Empty, too long, an override attempt, or personal data ends the run. The indexes are not opened.", "A refusal, or the question.", "rails.py screen_input", ["input_guard"]),
        step("g-foot", "Foothold", "Is this question even in the library?", "Names in the question, and its content words.", "If no name and no content word appears in the indexes, Glass refuses without searching.", "Continue, or a refusal.", "graph.py classify", ["glass"]),
        step("g-search", "Hybrid search", "Two lists become one.", "The question.", "BM25 and the meaning index each return a ranking. Reciprocal rank fusion, with constant 60, merges them. Six passages are kept.", "Six passages, still ungraded.", "index.py hybrid_search", ["glass"], didSearch),
        step("g-grade", "Grade", "Drop passages that do not match.", "Those six passages and the question.", "A passage is kept when it shares enough of the question, or a named thing in the question.", "The passages marked relevant. The others stay visible but are not used.", "index.py grade", ["glass"], didSearch),
        step("g-write", "Write", "Sentences are copied, not invented.", "Only the passages that were kept.", "Sentences are scored, a diverse few are kept, and each one gets a citation number. If none were kept, the answer is a refusal.", "A draft answer and its citation numbers.", "synthesize.py", ["glass"], didSearch),
        step("g-out", "Second guard", "Every cited sentence must be in its passage.", "The draft and the passages.", "A sentence that does not appear in the passage it cites is removed. If nothing cited remains, the answer becomes a refusal.", "The answer you are allowed to see.", "rails.py screen_output", ["output_guard"]),
      ],
    },
    crystal: {
      kicker: "One expansion",
      title: "Crystal, then stop",
      lede: "Crystal is for questions that name more than one thing. It searches so each name keeps a passage, borrows neighbor names once, and does not loop.",
      blocks: [
        step("c-guard", "First guard", "Same stop as every other path.", "The question.", "Override attempts and personal data never reach search.", "Continue, or a refusal.", "rails.py", ["input_guard"]),
        step("c-balance", "Balanced search", "Each named thing keeps a seat.", "The question and the name graph.", "Hybrid search is balanced across the names in the question, so one name cannot crowd the other out. Six passages are kept.", "A first set of passages.", "index.py search_balanced", ["crystal"], didSearch),
        step("c-expand", "Borrow names", "One expansion, then no more.", "Names on the first passages.", "Up to four neighbor names are added to the question and the balanced search runs again. If there are no neighbors, this step adds nothing.", "A second set of passages, or nothing.", "index.py expand_terms", ["crystal"], didSearch),
        step("c-merge", "Merge", "Duplicates lose.", "Both sets.", "The same passage keeps the better score. The list is cut back to six.", "One list.", "lenses.py run_crystal", ["crystal"], didSearch),
        step("c-grade", "Grade and write", "Same rules as Glass from here.", "The merged list.", "Grade, then copy cited sentences from the passages that survived.", "A draft answer.", "index.py grade, synthesize.py", ["crystal"], didSearch),
        step("c-out", "Second guard", "Cited sentences have to be real.", "The draft.", "Sentences that are not in the cited passage are removed.", "The answer on the page.", "rails.py screen_output", ["output_guard"]),
      ],
    },
    aurora: {
      kicker: "Long path",
      title: "Aurora, with a retry",
      lede: "Aurora is the LangGraph state machine. The grade step can send the question back through search, at most twice. The citation check and the sentence check are two different gates.",
      blocks: [
        step("a-guard", "First guard", "A blocked question never enters the graph past this node.", "The question.", "The same four refusals as the other paths. The route is set to blocked and the walk ends. There is no second guard, because nothing was written from the library.", "Continue into the router, or stop.", "graph.py input_guard", ["input_guard"]),
        step("a-route", "Route", "Decide which kind of question this is.", "The question, the name index, and the word index.", "No name and no content word: outside the library. Words such as compare, versus, differ, difference, or side by side: a comparison. Two names, the word relationship, or a how-does-this-affect question: multi-part. Anything else with a foothold: a direct question.", "One of those four labels.", "graph.py classify, router", ["router"]),
        {
          kind: "split",
          label: "The label picks the next node.",
          steps: [
            step("a-stop", "Outside the library", "Refuse without searching.", "The abstain label.", "The answer is the shared refusal. Citations stay empty.", "The walk ends.", "graph.py abstain", ["abstain"]),
            step("a-plan", "Plan", "Only comparisons and multi-part questions come here.", "The question.", "A short hybrid search looks for neighbor names. Up to four are added onto the question.", "An expanded question. Direct questions skip this box.", "graph.py planner", ["planner"]),
            step("a-direct", "Direct question", "Skip planning.", "The factual label.", "The original question goes straight to search.", "The question, unchanged.", "graph.py after_router", ["router"], factualRoute),
          ],
        },
        step("a-search", "Search", "Six passages.", "The original question, or the expanded one.", "Comparisons and multi-part questions use the balanced search. Direct questions use ordinary hybrid search.", "Six passages on the state.", "graph.py retrieve", ["retrieve"]),
        step("a-grade", "Grade", "How many passages actually match?", "The six passages.", "Each passage is marked relevant or not.", "A count of matches, used by the next choice.", "graph.py grade", ["grade"]),
        {
          kind: "split",
          label: "After the grade. Two matching passages are enough. So is one passage that covers at least half the question's words.",
          steps: [
            step("a-write-ready", "Enough", "Go write.", "Two relevant passages, or one strong one.", "The walk moves to Write.", "The kept passages.", "graph.py after_grade", ["synthesize"], wroteWithoutSecondRetry),
            step("a-retry", "Too thin, retries left", "Search again. At most twice.", "Fewer matches, and the retry count is 0 or 1.", "Neighbor names are added and the retry count goes up. The walk returns to Search.", "A new query and a higher retry count.", "graph.py rewrite", ["rewrite"]),
            step("a-give-up", "Too thin, retries spent", "Write anyway.", "Still thin after two retries.", "It does not search a third time. Write has to say so if the passages are weak.", "The weak passages, forwarded.", "graph.py after_grade", ["synthesize"], wroteAfterSecondRetry),
          ],
        },
        step("a-write", "Write", "Copy sentences and number them.", "Graded passages.", "The same extractive writer as Glass and Crystal. No hosted model.", "A draft and citation ids.", "synthesize.py, graph.py synthesize", ["synthesize"]),
        step("a-verify", "Check the ids", "Every citation number has to exist.", "The citation ids.", "An id that is not in the index fails the check and the answer is marked unsupported.", "Supported, or not.", "graph.py verify", ["verify"]),
        step("a-out", "Second guard", "The sentence itself has to be in the passage.", "The draft.", "This is separate from the id check. A real id with a sentence that was not in the passage still fails. Failed sentences are removed.", "The answer on the page.", "rails.py, graph.py output_guard", ["output_guard"]),
      ],
    },
  };

  function lit(stepItem, trace) {
    var lines = linesFor(stepItem, trace);
    if (stepItem.ranIf) return stepItem.ranIf(trace || [], lines);
    return lines.length > 0;
  }

  function linesFor(stepItem, trace) {
    var wanted = {};
    stepItem.traceNodes.forEach(function (name) { wanted[name] = true; });
    return (trace || []).filter(function (item) { return wanted[item.node]; });
  }

  function findStep(blocks, id) {
    var found = null;
    blocks.forEach(function (block) {
      if (found) return;
      if (block.kind === "step" && block.id === id) found = block;
      if (block.kind === "split") {
        block.steps.forEach(function (item) {
          if (item.id === id) found = item;
        });
      }
    });
    return found;
  }

  function firstStep(blocks) {
    var found = null;
    blocks.some(function (block) {
      if (block.kind === "step") { found = block; return true; }
      if (block.kind === "split" && block.steps.length) { found = block.steps[0]; return true; }
      return false;
    });
    return found;
  }

  function stationButton(item, selected, trace) {
    var classes = "station";
    if (item.id === selected) classes += " on";
    if (lit(item, trace)) classes += " ran";
    return '<button type="button" class="' + classes + '" data-flow-step="' + esc(item.id) + '">' +
      "<b>" + esc(item.title) + "</b><small>" + esc(item.summary) + "</small></button>";
  }

  function render(options) {
    var laneId = options && LANES[options.lane] ? options.lane : "system";
    var lane = LANES[laneId];
    var trace = (options && options.trace) || [];
    var selected = findStep(lane.blocks, options && options.selected) || firstStep(lane.blocks);
    var switches = Object.keys(LANES).map(function (id) {
      var label = { system: "Whole desk", glass: "Glass", crystal: "Crystal", aurora: "Aurora" }[id];
      return '<button type="button" data-flow-lane="' + id + '"' + (id === laneId ? ' class="on"' : "") + ">" + label + "</button>";
    }).join("");
    var body = lane.blocks.map(function (block) {
      if (block.kind === "step") {
        return "<li>" + stationButton(block, selected.id, trace) + "</li>";
      }
      return '<li class="flow-split"><p>' + esc(block.label) + "</p><div class=\"flow-choices\">" +
        block.steps.map(function (item) { return stationButton(item, selected.id, trace); }).join("") +
        "</div></li>";
    }).join("");
    var ranLines = linesFor(selected, trace);
    if (selected.ranIf && !selected.ranIf(trace, ranLines)) ranLines = [];
    var runHtml = ranLines.length
      ? "<h3>This run</h3><ul>" + ranLines.map(function (item) {
        return "<li>" + esc(item.detail) + "</li>";
      }).join("") + "</ul>"
      : (trace.length
        ? "<p class=\"flow-quiet\">This step did not run for the latest question.</p>"
        : "<p class=\"flow-quiet\">Ask a question on Ask, then come back. Steps that ran are marked.</p>");
    return '<p class="kicker">' + esc(lane.kicker) + "</p><h1>" + esc(lane.title) + "</h1>" +
      '<p class="lede">' + esc(lane.lede) + "</p>" +
      '<div class="flow-switch" role="tablist">' + switches + "</div>" +
      '<div class="flow-layout"><ol class="flow-list">' + body + "</ol>" +
      '<article class="flow-detail"><p class="kicker">Selected step</p><h2>' + esc(selected.title) + "</h2>" +
      "<dl><dt>Comes in</dt><dd>" + esc(selected.comes) + "</dd>" +
      "<dt>What happens</dt><dd>" + esc(selected.happens) + "</dd>" +
      "<dt>Goes out</dt><dd>" + esc(selected.goes) + "</dd>" +
      "<dt>In the code</dt><dd>" + esc(selected.code) + "</dd></dl>" +
      runHtml + "</article></div>";
  }

  function traceFor(last, laneId) {
    if (!last) return [];
    var lane = LANES[laneId] ? laneId : "system";
    if (last.lenses) {
      if (lane === "system") {
        var merged = [];
        last.lenses.forEach(function (item) {
          (item.trace || []).forEach(function (entry) { merged.push(entry); });
        });
        return merged;
      }
      var match = null;
      last.lenses.forEach(function (item) { if (item.lens === lane) match = item; });
      return match && match.trace ? match.trace : [];
    }
    if (lane === "system" || lane === last.lens) return last.trace || [];
    return [];
  }

  root.PrismFlow = { render: render, lanes: Object.keys(LANES), traceFor: traceFor };
})(typeof window !== "undefined" ? window : globalThis);
