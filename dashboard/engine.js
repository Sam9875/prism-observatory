(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.PrismEngine = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const STOP = new Set("the and for with from that this what when where which how does did are was were have has its into about over than then them they their your not but you who why".split(" "));
  const GENERIC = new Set("space telescope earth international station program archive graph search circulation summer island basin sheet system rover crater record orbit module atlantic meridional overturning".split(" "));
  const REFUSAL = "PRISM does not have grounded material for that in the Orbital, Neural, or Earth archives.";

  function tokenize(text, minLen) {
    const out = [];
    const matches = String(text || "").toLowerCase().match(/[a-z0-9]+/g) || [];
    matches.forEach(function (token) {
      if (token.length >= minLen && !STOP.has(token)) out.push(token);
    });
    return out;
  }

  function contentTokens(text) {
    return tokenize(text, 4);
  }

  function entityMentioned(name, query) {
    const folded = String(name || "").toLowerCase().trim();
    if (folded.length < 3) return false;
    const q = String(query || "").toLowerCase();
    if (q.indexOf(folded) !== -1) return true;
    const qTokens = new Set(q.match(/[a-z0-9]+/g) || []);
    const parts = folded.match(/[a-z0-9]+/g) || [];
    for (let i = 0; i < parts.length; i += 1) {
      const token = parts[i];
      if (token.length >= 4 && !GENERIC.has(token) && qTokens.has(token)) return true;
    }
    return false;
  }

  function sentences(text) {
    const parts = String(text || "").split(/(?<=[.!?])\s+/).map(function (part) { return part.trim(); }).filter(Boolean);
    return parts.length ? parts : (String(text || "").trim() ? [String(text).trim()] : []);
  }

  function coverage(query, text) {
    const terms = contentTokens(query);
    if (!terms.length) return 0;
    const present = new Set(tokenize(text, 3));
    let hit = 0;
    terms.forEach(function (term) { if (present.has(term)) hit += 1; });
    return hit / terms.length;
  }

  function chunkDocuments(documents, readyChunks) {
    if (readyChunks && readyChunks.length) {
      return readyChunks.map(function (chunk) {
        return {
          id: chunk.id,
          docId: chunk.doc_id || chunk.docId,
          title: chunk.title,
          archive: chunk.archive,
          entities: chunk.entities || [],
          text: chunk.text,
          index: chunk.index || 0,
        };
      });
    }
    const chunks = [];
    documents.forEach(function (doc) {
      const paragraphs = String(doc.text || "").split(/\n\n+/).map(function (part) { return part.trim(); }).filter(Boolean);
      let buffer = "";
      let index = 0;
      function push(text) {
        const clean = text.trim();
        if (!clean) return;
        chunks.push({
          id: doc.id + "-" + index,
          docId: doc.id,
          title: doc.title,
          archive: doc.archive,
          entities: doc.entities || [],
          text: clean,
          index: index,
        });
        index += 1;
      }
      paragraphs.forEach(function (paragraph) {
        if (buffer && (buffer.length + paragraph.length) > 700) {
          push(buffer);
          const kept = buffer.split(/\n\n/).pop();
          buffer = kept ? kept + "\n\n" + paragraph : paragraph;
        } else {
          buffer = buffer ? buffer + "\n\n" + paragraph : paragraph;
        }
      });
      push(buffer);
    });
    return chunks;
  }

  function buildBm25(tokenized) {
    const count = tokenized.length || 1;
    const df = new Map();
    let total = 0;
    tokenized.forEach(function (tokens) {
      total += tokens.length;
      const seen = new Set(tokens);
      seen.forEach(function (token) { df.set(token, (df.get(token) || 0) + 1); });
    });
    const avg = total / count || 1;
    const k1 = 1.5;
    const b = 0.75;
    return function score(queryTokens) {
      return tokenized.map(function (tokens) {
        const tf = new Map();
        tokens.forEach(function (token) { tf.set(token, (tf.get(token) || 0) + 1); });
        const length = tokens.length || 1;
        let sum = 0;
        queryTokens.forEach(function (token) {
          const freq = tf.get(token) || 0;
          if (!freq) return;
          const docs = df.get(token) || 0;
          const idf = Math.log(1 + (count - docs + 0.5) / (docs + 0.5));
          sum += idf * ((freq * (k1 + 1)) / (freq + k1 * (1 - b + b * length / avg)));
        });
        return sum;
      });
    };
  }

  function fitTfidf(chunks) {
    const docs = chunks.map(function (chunk) { return tokenize(chunk.text, 3); });
    const df = new Map();
    docs.forEach(function (tokens) {
      new Set(tokens).forEach(function (token) { df.set(token, (df.get(token) || 0) + 1); });
    });
    const terms = Array.from(df.keys()).sort();
    const vocab = new Map(terms.map(function (term, index) { return [term, index]; }));
    const n = Math.max(docs.length, 1);
    const idf = terms.map(function (term) { return Math.log((1 + n) / (1 + df.get(term))) + 1; });
    function vector(text) {
      const vec = new Array(Math.max(terms.length, 1)).fill(0);
      if (!terms.length) return vec;
      const counts = new Map();
      tokenize(text, 3).forEach(function (token) { counts.set(token, (counts.get(token) || 0) + 1); });
      let total = 0;
      counts.forEach(function (value) { total += value; });
      total = total || 1;
      counts.forEach(function (value, token) {
        const index = vocab.get(token);
        if (index === undefined) return;
        vec[index] = (value / total) * idf[index];
      });
      let norm = 0;
      vec.forEach(function (value) { norm += value * value; });
      norm = Math.sqrt(norm) || 1;
      return vec.map(function (value) { return value / norm; });
    }
    const matrix = chunks.map(function (chunk) { return vector(chunk.text); });
    return { vector: vector, matrix: matrix };
  }

  function dot(left, right) {
    let sum = 0;
    const width = Math.min(left.length, right.length);
    for (let i = 0; i < width; i += 1) sum += left[i] * right[i];
    return sum;
  }

  function readyFromArchive(archive) {
    if (!archive || !Array.isArray(archive.documents) || !archive.documents.length) {
      throw new Error("Archive has no documents");
    }
    const documents = archive.documents;
    const chunks = chunkDocuments(documents, archive.chunks);
    function indexedText(chunk) {
      return chunk.title + ". " + chunk.text;
    }
    const bm25Tokens = chunks.map(function (chunk) {
      const tokens = tokenize(indexedText(chunk), 2);
      return tokens.length ? tokens : ["empty"];
    });
    const allTokens = new Set();
    bm25Tokens.forEach(function (tokens) {
      tokens.forEach(function (token) { if (token.length > 3) allTokens.add(token); });
    });
    const tfidf = fitTfidf(chunks.map(function (chunk) {
      return { text: indexedText(chunk) };
    }));
    const entityNames = new Map();
    const graph = new Map();
    const entityDocs = new Map();
    documents.forEach(function (doc) {
      const keys = [];
      (doc.entities || []).forEach(function (name) {
        const key = String(name).toLowerCase().trim();
        if (key.length < 3) return;
        if (!entityNames.has(key)) entityNames.set(key, name);
        keys.push(key);
        if (!entityDocs.has(key)) entityDocs.set(key, new Set());
        entityDocs.get(key).add(doc.id);
        if (!graph.has(key)) graph.set(key, new Set());
      });
      keys.forEach(function (left) {
        keys.forEach(function (right) {
          if (left !== right) graph.get(left).add(right);
        });
      });
    });
    return {
      archive: archive,
      documents: documents,
      chunks: chunks,
      bm25: buildBm25(bm25Tokens),
      allTokens: allTokens,
      tfidf: tfidf,
      entityNames: entityNames,
      graph: graph,
      entityDocs: entityDocs,
    };
  }

  function entitiesInQuery(index, query) {
    const found = [];
    const seen = new Set();
    index.entityNames.forEach(function (name, key) {
      if (seen.has(key)) return;
      if (entityMentioned(name, query)) {
        found.push(name);
        seen.add(key);
      }
    });
    return found;
  }

  function hybridSearch(index, query, k) {
    const lexicalScores = index.bm25(tokenize(query, 2));
    const lexical = lexicalScores
      .map(function (score, i) { return { score: score, i: i }; })
      .filter(function (row) { return row.score > 0; })
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, 12);
    const qv = index.tfidf.vector(query);
    const dense = index.tfidf.matrix
      .map(function (vector, i) { return { score: dot(qv, vector), i: i }; })
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, 12);
    const fused = new Map();
    lexical.forEach(function (row, rank) {
      const id = index.chunks[row.i].id;
      const slot = fused.get(id) || { bm25: 0, dense: 0, score: 0, i: row.i };
      const contribution = 1 / (60 + rank + 1);
      slot.bm25 = contribution;
      slot.score += contribution;
      fused.set(id, slot);
    });
    dense.forEach(function (row, rank) {
      const id = index.chunks[row.i].id;
      const slot = fused.get(id) || { bm25: 0, dense: 0, score: 0, i: row.i };
      const contribution = 1 / (60 + rank + 1);
      slot.dense = contribution;
      slot.score += contribution;
      fused.set(id, slot);
    });
    return Array.from(fused.values())
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, k)
      .map(function (slot) {
        const chunk = index.chunks[slot.i];
        return {
          id: chunk.id,
          chunk_id: chunk.id,
          docId: chunk.docId,
          doc_id: chunk.docId,
          title: chunk.title,
          archive: chunk.archive,
          text: chunk.text,
          entities: chunk.entities,
          score: slot.score,
          bm25: slot.bm25,
          dense: slot.dense,
          relevant: false,
        };
      });
  }

  function searchBalanced(index, query, k) {
    const hits = hybridSearch(index, query, k);
    const implied = new Map();
    entitiesInQuery(index, query).forEach(function (name) {
      const docs = index.entityDocs.get(name.toLowerCase());
      if (!docs) return;
      docs.forEach(function (docId) { if (!implied.has(docId)) implied.set(docId, name); });
    });
    if (implied.size < 2) return hits;
    const merged = new Map(hits.map(function (hit) { return [hit.id, hit]; }));
    implied.forEach(function (name, docId) {
      const present = Array.from(merged.values()).some(function (hit) { return hit.docId === docId; });
      if (present) return;
      const extras = hybridSearch(index, name, 2);
      for (let i = 0; i < extras.length; i += 1) {
        if (extras[i].docId === docId) {
          merged.set(extras[i].id, extras[i]);
          break;
        }
      }
    });
    return Array.from(merged.values()).sort(function (a, b) { return b.score - a.score; }).slice(0, Math.max(k, implied.size));
  }

  function expandTerms(index, query, hits, limit) {
    const folded = query.toLowerCase();
    const seeds = new Set();
    entitiesInQuery(index, query).forEach(function (name) { seeds.add(name.toLowerCase()); });
    (hits || []).forEach(function (hit) {
      (hit.entities || []).forEach(function (name) {
        if (entityMentioned(name, query)) seeds.add(name.toLowerCase());
      });
      const blob = hit.text.toLowerCase();
      index.entityNames.forEach(function (_name, key) {
        if (blob.indexOf(key) !== -1) seeds.add(key);
      });
    });
    const neighbors = [];
    const seen = new Set();
    seeds.forEach(function (seed) {
      const links = index.graph.get(seed);
      if (!links) return;
      Array.from(links).sort().forEach(function (neighbor) {
        if (neighbors.length >= (limit || 4) || seen.has(neighbor)) return;
        const display = index.entityNames.get(neighbor) || neighbor;
        if (folded.indexOf(neighbor) !== -1 || folded.indexOf(display.toLowerCase()) !== -1) return;
        neighbors.push(display);
        seen.add(neighbor);
      });
    });
    return neighbors.slice(0, limit || 4);
  }

  function grade(query, hits) {
    const queryTerms = new Set(contentTokens(query));
    return hits.map(function (hit) {
      const shared = contentTokens(hit.text).filter(function (token) { return queryTerms.has(token); });
      const entityHit = (hit.entities || []).some(function (name) { return entityMentioned(name, query); });
      const titleHit = contentTokens(hit.title).some(function (token) { return queryTerms.has(token); });
      const copy = Object.assign({}, hit);
      copy.relevant = shared.length >= 2 || entityHit || titleHit;
      return copy;
    });
  }

  function classify(index, question) {
    const folded = question.toLowerCase();
    const entities = entitiesInQuery(index, question);
    const lexical = contentTokens(question).some(function (token) { return index.allTokens.has(token); });
    if (!entities.length && !lexical) return "abstain";
    if (/compare|versus|\bvs\b|difference|differ|side by side/.test(folded)) return "comparative";
    if (entities.length >= 2 || folded.indexOf("relationship") !== -1 || (folded.indexOf("how does") !== -1 && folded.indexOf("affect") !== -1)) {
      return "multihop";
    }
    return "factual";
  }

  function synthesize(question, hits, route) {
    const relevant = hits.filter(function (hit) { return hit.relevant; });
    if (!relevant.length) return { answer: REFUSAL, citations: [], supported: false };
    const matchedDocs = new Set();
    relevant.forEach(function (hit) {
      if ((hit.entities || []).some(function (name) { return entityMentioned(name, question); })) {
        matchedDocs.add(hit.docId);
      }
    });
    const candidates = [];
    relevant.forEach(function (hit, hitIndex) {
      sentences(hit.text).forEach(function (sentence, sentenceIndex) {
        if (sentence.length < 40 || sentence[0] !== sentence[0].toUpperCase()) return;
        const overlap = contentTokens(sentence).filter(function (token) {
          return contentTokens(question).indexOf(token) !== -1;
        }).length;
        let bonus = 0;
        if (matchedDocs.has(hit.docId)) {
          (hit.entities || []).forEach(function (name) {
            if (name.length >= 4 && sentence.toLowerCase().indexOf(name.toLowerCase()) !== -1) bonus += 3;
          });
        }
        candidates.push({ score: overlap + bonus, hitIndex: hitIndex, sentenceIndex: sentenceIndex, sentence: sentence, hit: hit });
      });
    });
    if (!candidates.length) {
      const fallback = relevant[0];
      return {
        answer: fallback.text.trim() + " [1]\n\nGrounded in 1 passage.",
        citations: [{ n: 1, chunk_id: fallback.id, doc_id: fallback.docId, title: fallback.title, archive: fallback.archive, quote: fallback.text.slice(0, 180) }],
        supported: true,
      };
    }
    candidates.sort(function (a, b) {
      return b.score - a.score || a.hitIndex - b.hitIndex || a.sentenceIndex - b.sentenceIndex;
    });
    const selected = [];
    const covered = new Set();
    const seenSentences = new Set();
    candidates.forEach(function (candidate) {
      if (selected.length >= 5) return;
      const key = candidate.sentence.toLowerCase().replace(/\s+/g, " ").trim();
      if (seenSentences.has(key)) return;
      const tokens = contentTokens(candidate.sentence);
      if (selected.length && tokens.length) {
        const overlap = tokens.filter(function (token) { return covered.has(token); }).length / tokens.length;
        if (overlap > 0.7 && selected.length >= 2) return;
      }
      selected.push(candidate);
      seenSentences.add(key);
      tokens.forEach(function (token) { covered.add(token); });
    });
    selected.sort(function (a, b) { return a.hitIndex - b.hitIndex || a.sentenceIndex - b.sentenceIndex; });
    const numbers = new Map();
    const citations = [];
    const rendered = selected.map(function (candidate) {
      if (!numbers.has(candidate.hit.id)) {
        numbers.set(candidate.hit.id, numbers.size + 1);
        citations.push({
          n: numbers.get(candidate.hit.id),
          chunk_id: candidate.hit.id,
          doc_id: candidate.hit.docId,
          title: candidate.hit.title,
          archive: candidate.hit.archive,
          quote: candidate.hit.text.slice(0, 180),
        });
      }
      return candidate.sentence + " [" + numbers.get(candidate.hit.id) + "]";
    });
    const prefix = route === "comparative" ? "Set side by side, the archives say this. " : "";
    return {
      answer: prefix + rendered.join(" ") + "\n\nGrounded in " + citations.length + " passage(s).",
      citations: citations,
      supported: citations.length > 0,
    };
  }

  function finish(lens, question, route, hits, trace, started, retries) {
    const written = synthesize(question, hits, route);
    const relevant = hits.filter(function (hit) { return hit.relevant; }).length;
    return {
      lens: lens,
      question: question,
      route: route,
      answer: written.answer,
      citations: written.citations,
      chunks: hits,
      trace: trace,
      supported: written.supported,
      metrics: {
        retries: retries || 0,
        relevant: relevant,
        retrieved: hits.length,
        latencyMs: Date.now() - started,
        contextPrecision: hits.length ? relevant / hits.length : 0,
        route: route,
        supported: written.supported,
      },
    };
  }

  function runAurora(index, question) {
    const started = Date.now();
    const trace = [];
    function note(node, detail) { trace.push({ node: node, detail: detail }); }
    const route = classify(index, question);
    note("router", "Classified the question as " + route + ".");
    if (route === "abstain") {
      note("abstain", "The question has no foothold in the three archives.");
      return {
        lens: "aurora",
        question: question,
        route: route,
        answer: REFUSAL,
        citations: [],
        chunks: [],
        trace: trace,
        supported: false,
        metrics: { retries: 0, relevant: 0, retrieved: 0, latencyMs: Date.now() - started, contextPrecision: 0, route: route, supported: false },
      };
    }
    let expanded = question;
    if (route === "comparative" || route === "multihop") {
      const terms = expandTerms(index, question, hybridSearch(index, question, 4), 4);
      if (terms.length) expanded = question + " " + terms.join(" ");
      note("planner", terms.length ? "Added neighbor terms: " + terms.join(", ") : "No extra entity names added.");
    }
    let retries = 0;
    let hits = [];
    for (let pass = 0; pass < 3; pass += 1) {
      const query = expanded || question;
      hits = (route === "comparative" || route === "multihop") ? searchBalanced(index, query, 6) : hybridSearch(index, query, 6);
      note("retrieve", "Retrieval kept " + hits.length + " chunks.");
      hits = grade(question, hits);
      const relevant = hits.filter(function (hit) { return hit.relevant; });
      note("grade", relevant.length + " of " + hits.length + " chunks graded relevant.");
      const enough = relevant.length >= 2 || (relevant.length === 1 && coverage(question, relevant[0].text) >= 0.5);
      if (enough || retries >= 2) break;
      retries += 1;
      const extra = expandTerms(index, question, hits, 4);
      if (extra.length) expanded = question + " " + extra.join(" ");
      note("rewrite", (extra.length ? "Rewrote the query with " + extra.join(", ") : "Rewrote the query without new neighbor names.") + " Retry " + retries + ".");
    }
    const written = synthesize(question, hits, route);
    note("synthesize", "Composed an answer with " + written.citations.length + " citation(s).");
    const known = new Set(index.chunks.map(function (chunk) { return chunk.id; }));
    const missing = written.citations.filter(function (item) { return !known.has(item.chunk_id); });
    let supported = written.supported && !missing.length;
    let answer = written.answer;
    if (missing.length) {
      supported = false;
      answer += " Citation check failed.";
      note("verify", "Citation check failed.");
    } else {
      note("verify", supported ? "Citations resolve to retrieved chunks." : "Answer is unsupported.");
    }
    const relevantCount = hits.filter(function (hit) { return hit.relevant; }).length;
    return {
      lens: "aurora",
      question: question,
      route: route,
      answer: answer,
      citations: written.citations,
      chunks: hits,
      trace: trace,
      supported: supported,
      metrics: {
        retries: retries,
        relevant: relevantCount,
        retrieved: hits.length,
        latencyMs: Date.now() - started,
        contextPrecision: hits.length ? relevantCount / hits.length : 0,
        route: route,
        supported: supported,
      },
    };
  }

  function ask(index, question, lens) {
    const choice = lens || "aurora";
    if (choice === "all") {
      return { lenses: ["glass", "crystal", "aurora"].map(function (name) { return ask(index, question, name); }) };
    }
    if (choice === "aurora") return runAurora(index, question);
    const started = Date.now();
    const route = classify(index, question);
    if (route === "abstain") {
      const trace = [{ node: choice, detail: "No archive foothold, so " + choice + " does not retrieve." }];
      return finish(choice, question, route, [], trace, started, 0);
    }
    if (choice === "glass") {
      const hits = grade(question, hybridSearch(index, question, 6));
      const kept = hits.filter(function (hit) { return hit.relevant; }).length;
      return finish("glass", question, route, hits, [{ node: "glass", detail: "Hybrid retrieval graded " + kept + " chunks relevant." }], started, 0);
    }
    const first = searchBalanced(index, question, 6);
    const terms = expandTerms(index, question, first, 4);
    const second = terms.length ? searchBalanced(index, question + " " + terms.join(" "), 6) : [];
    const merged = new Map();
    first.concat(second).forEach(function (hit) {
      const current = merged.get(hit.id);
      if (!current || hit.score > current.score) merged.set(hit.id, hit);
    });
    const ordered = Array.from(merged.values()).sort(function (a, b) { return b.score - a.score; }).slice(0, 6);
    const hits = grade(question, ordered);
    const trace = [
      { node: "crystal", detail: "Balanced hybrid search on the original question." },
      { node: "crystal", detail: terms.length ? "Expanded once with " + terms.join(", ") + "." : "No neighbor terms to expand." },
      { node: "crystal", detail: "Merged to " + hits.length + " unique chunks." },
    ];
    return finish("crystal", question, route, hits, trace, started, 0);
  }

  return {
    ask: ask,
    chunkDocuments: chunkDocuments,
    readyFromArchive: readyFromArchive,
    tokenize: tokenize,
    REFUSAL: REFUSAL,
  };
});
