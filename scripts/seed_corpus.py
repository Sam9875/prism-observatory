"""Write the PRISM source documents. Original briefing prose, not copied text."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "corpus"

DOCS = [
    {
        "id": "apollo-11",
        "title": "Apollo 11",
        "archive": "orbital",
        "summary": "Eagle landed on the Sea of Tranquility while Michael Collins stayed in Columbia.",
        "entities": "Neil Armstrong; Buzz Aldrin; Michael Collins; Eagle; Columbia; Sea of Tranquility",
        "text": """
Apollo 11 flew from 16 July to 24 July 1969 with three crew members: Neil Armstrong, Buzz Aldrin, and Michael Collins. The mission is remembered for the first crewed landing on the Moon, but only two of the three astronauts walked on the surface. Armstrong commanded the flight, Aldrin was the lunar module pilot, and Collins was the command module pilot who remained in lunar orbit.

The lunar module was named Eagle. On 20 July 1969 Eagle landed on the Sea of Tranquility. Armstrong and Aldrin descended to the regolith, while Collins stayed aboard the command module Columbia and kept station overhead so the rendezvous would still be possible if the landing party had to leave in a hurry. The sentence Armstrong spoke as he stepped off the footpad, about one small step for a man and one giant leap for mankind, became the line most people still quote.

The surface stay was short. The extravehicular activity lasted about two and a half hours. The crew collected about 21.5 kilograms of lunar samples, photographed the site, and left instruments behind. Eagle then lifted off from the Sea of Tranquility, met Columbia, and was discarded. Columbia was the only part of the spacecraft that returned to Earth. Splashdown was in the Pacific Ocean on 24 July 1969.

For retrieval questions, the split of roles matters. Eagle is the lander. Columbia is the ship that stayed in lunar orbit with Michael Collins. The landing site is the Sea of Tranquility, not a highland site and not the later Apollo valleys. Anyone asking who stayed in orbit wants Collins, not a claim that the whole crew walked together.
""",
    },
    {
        "id": "voyager",
        "title": "The Voyager Grand Tour",
        "archive": "orbital",
        "summary": "Voyager 1 and Voyager 2 used a rare planetary alignment, and both later entered interstellar space.",
        "entities": "Voyager 1; Voyager 2; Golden Record; Grand Tour",
        "text": """
Voyager 1 and Voyager 2 left Earth in 1977 to take advantage of a rare alignment of the outer planets. Voyager 2 launched first. The pair was the practical form of a Grand Tour that could bend one spacecraft past several worlds with gravity assists instead of an impossible amount of propellant.

Voyager 2 flew by Jupiter, Saturn, Uranus, and Neptune, and it remains the only spacecraft to have visited the ice giants. Voyager 1 flew by Jupiter and Saturn, then left the planetary plane on a path toward interstellar space. Both craft still phone home with instruments that measure fields and particles, powered by radioisotope thermoelectric generators because sunlight at those distances is too weak for useful solar arrays.

Each spacecraft carries a Golden Record, a copper disc of sounds, speech, and images intended as a portrait of Earth for any finder. The record is a message, not a navigation tool. The spacecraft themselves became the message's couriers. Voyager 1 crossed into interstellar space in 2012. Voyager 2 followed in 2018. Interstellar space here means the region beyond the heliopause, where the solar wind gives way to the wind of the galaxy, not a sudden arrival at another star.
""",
    },
    {
        "id": "jwst",
        "title": "James Webb Space Telescope",
        "archive": "orbital",
        "summary": "JWST observes infrared light from a halo orbit around Sun-Earth L2 with NIRCam, NIRSpec, MIRI, and NIRISS.",
        "entities": "James Webb Space Telescope; JWST; NIRCam; NIRSpec; MIRI; NIRISS; Sun-Earth L2; Ariane 5",
        "text": """
The James Webb Space Telescope, usually shortened to JWST, launched on 25 December 2021 aboard an Ariane 5 rocket. It does not circle Earth in the way Hubble does. JWST operates in a halo orbit around the Sun-Earth L2 point, about 1.5 million kilometers outward from Earth, so the Sun, Earth, and Moon stay in roughly the same direction and a single sunshield can keep the optics cold.

The primary mirror is 6.5 meters across and is built from 18 gold-coated beryllium segments. Gold is there for infrared reflectivity, not for decoration. A five-layer sunshield, about the size of a tennis court, separates the warm spacecraft bus from the cold telescope. JWST is optimized for infrared light, which is how it studies faint galaxies, dusty nurseries, and the atmospheres of worlds passing in front of their stars.

Four science instruments share that mirror. NIRCam images in the near infrared. NIRSpec takes spectra of many targets at once. MIRI extends coverage into the mid-infrared and needs the coldest part of the observatory. The Fine Guidance Sensor includes NIRISS, which adds imaging and spectroscopic modes. People sometimes call JWST a replacement for Hubble. It is a successor in scientific ambition, not a replacement in orbit: Hubble remains a low Earth orbit telescope, and JWST cannot be serviced by astronauts.

Questions about instruments should name NIRCam, NIRSpec, MIRI, and NIRISS. Questions about location should say Sun-Earth L2 and a halo orbit, not a fixed point and not low Earth orbit.
""",
    },
    {
        "id": "hubble",
        "title": "Hubble Space Telescope",
        "archive": "orbital",
        "summary": "Hubble observes from low Earth orbit and was repaired in 1993 after spherical aberration.",
        "entities": "Hubble Space Telescope; Hubble; COSTAR; WFPC2; low Earth orbit",
        "text": """
The Hubble Space Telescope was released into low Earth orbit in 1990 from the space shuttle Discovery on mission STS-31. The orbit is roughly 535 kilometers up. That closeness is why shuttle astronauts could visit Hubble, and it is also why Earth blocks a large part of the sky on every orbit and why the telescope passes through day and night about every 90 minutes.

Soon after commissioning, images showed that the primary mirror had been polished to the wrong figure. The error is called spherical aberration: light from the edge of the mirror did not focus at the same point as light from the center. The 1993 servicing mission installed COSTAR, a box of corrective mirrors for the original instruments, and replaced the main camera with WFPC2, which carried its own correction. Later servicing missions swapped in newer cameras and spectrographs, and COSTAR itself was eventually removed once the new instruments corrected their own light.

Hubble observes ultraviolet, visible, and near-infrared wavelengths. It is still a low Earth orbit telescope. It is not at Sun-Earth L2, it does not have JWST's sunshield, and it does not fly NIRCam or MIRI. When a question compares Hubble and JWST, the orbit is the cleanest difference: Hubble in low Earth orbit, JWST in a halo orbit around L2, with Hubble reachable by astronauts and JWST not.
""",
    },
    {
        "id": "iss",
        "title": "International Space Station",
        "archive": "orbital",
        "summary": "The ISS has been continuously crewed since November 2000 in an orbit near 400 kilometers.",
        "entities": "International Space Station; ISS; Zarya; Cupola",
        "text": """
The International Space Station is a partnership among NASA, Roscosmos, ESA, JAXA, and the Canadian Space Agency. Assembly began with the first module, Zarya, launched in 1998. Continuous human habitation started in November 2000 and has not been broken since. The station flies in low Earth orbit near 400 kilometers, completing one loop in about 90 minutes, so crews see a sunrise roughly every hour and a half.

The laboratory is there for microgravity. Fluids, flames, alloys, and living cells behave differently when weight does not settle them to the bottom of a container. The station is also a test of keeping people healthy on long flights: radiation, bone loss, and closed-loop life support are operational problems, not only research topics. Power comes from large solar arrays that track the Sun as the truss turns.

The Cupola is the windowed module, a ring of panes used for visiting-vehicle operations and for Earth observation. It is not a science instrument in the JWST sense. It is a workstation with a view. Questions about the station should not confuse it with a telescope at L2 or with a lunar lander. Its facts are the partners, Zarya in 1998, continuous crews since November 2000, the roughly 400 kilometer orbit, the 90 minute period, and the Cupola.
""",
    },
    {
        "id": "artemis",
        "title": "Artemis Program",
        "archive": "orbital",
        "summary": "Artemis uses Orion and the Space Launch System to return crews to the Moon, with Gateway planned in lunar orbit.",
        "entities": "Artemis; Orion; Space Launch System; Gateway",
        "text": """
Artemis is NASA's program to return astronauts to the Moon and to practice the kind of sustained presence Apollo did not attempt. The crew vehicle is Orion. The rocket that lifts Orion off Earth is the Space Launch System. Neither vehicle is a renamed Apollo capsule or a renamed Saturn V, even though the mission shape, a crew leaving Earth for the Moon, invites the comparison.

Gateway is a planned outpost in lunar orbit, a small station where crews can transfer before going down to the surface. It is not the International Space Station and it is not in low Earth orbit. Artemis I, flown in 2022, was the uncrewed test that sent Orion around the Moon and back. Artemis II is the crewed lunar flyby, a dress rehearsal that does not land. Artemis III is the planned crewed landing.

NASA has stated that the landing campaign should put the first woman and the first person of color on the Moon. The archive does not invent a landing date beyond that plan, and it does not treat Artemis as a copy of Apollo 11. The durable hardware names are Orion, the Space Launch System, and Gateway.
""",
    },
    {
        "id": "mars-rovers",
        "title": "Curiosity and Perseverance",
        "archive": "orbital",
        "summary": "Curiosity found an ancient lakebed in Gale Crater, and Perseverance brought Ingenuity to Jezero.",
        "entities": "Curiosity; Perseverance; Ingenuity; Gale Crater; Jezero",
        "text": """
Curiosity landed in Gale Crater in 2012. It is a car-sized rover powered by a radioisotope thermoelectric generator, the right choice for a machine that has to survive dust storms and a Martian winter without depending on sunlight alone. Its lasting result is geological: the rocks of Gale preserve an ancient lakebed that was habitable in the sense that liquid water and the chemical ingredients life uses were present, not in the sense that a fossil was held up to a camera.

Perseverance landed in Jezero Crater in 2021. Jezero was chosen because a river once emptied into a lake there and left a delta, which is a natural filing cabinet for sediments. Perseverance drills rock cores and seals them for a later sample-return campaign. It also carried Ingenuity, a small helicopter.

Ingenuity made the first powered, controlled flight on another planet. That sentence is the one to keep. It did not prove that people can live on Mars, and it was not a science laboratory on the scale of the rover. It proved that rotors can generate enough lift in an atmosphere about one percent as thick as Earth's, which is why later missions can consider aircraft instead of only wheels.
""",
    },
    {
        "id": "orbits",
        "title": "Orbits That Matter",
        "archive": "orbital",
        "summary": "LEO, geostationary orbit, sun-synchronous orbit, and the Sun-Earth L2 halo are different tools.",
        "entities": "low Earth orbit; geostationary orbit; Sun-Earth L2; sun-synchronous orbit",
        "text": """
Low Earth orbit is the neighborhood a few hundred kilometers up. The International Space Station and the Hubble Space Telescope both live there. A vehicle in low Earth orbit circles the planet in roughly ninety minutes. Getting there is the cheapest spaceflight there is, and coming home is still possible, which is why crews and service missions use it.

Navigation constellations such as GPS occupy medium Earth orbit, higher than the station and far below the weather satellites that seem to hang still. Geostationary orbit sits about 35,786 kilometers above the equator. A satellite there matches Earth's rotation, so it stays over the same longitude and makes a convenient radio tower. It is a poor place for a high-resolution Earth imager that wants to be close, and it is a poor place for an infrared telescope that wants to be cold.

Sun-synchronous orbits are tilted polar paths chosen so that a satellite crosses a given latitude at about the same local solar time on every visit. That steadiness is why they are used for Earth observation. Sun-Earth L2 is something else entirely: a balance region 1.5 million kilometers outward, where a telescope can keep the Sun and Earth behind one sunshield. JWST does not sit motionless on the point. It follows a halo orbit around L2. Hubble's low Earth orbit and JWST's halo are the comparison this archive expects.
""",
    },
    {
        "id": "what-is-rag",
        "title": "Retrieval-Augmented Generation",
        "archive": "neural",
        "summary": "RAG retrieves passages first so the answer stays grounded instead of relying on memory alone.",
        "entities": "retrieval-augmented generation; grounding; hallucination",
        "text": """
Retrieval-augmented generation, usually called RAG, answers a question in two movements. First it retrieves passages from a corpus you trust. Then it composes the answer from those passages. The point of the first movement is grounding. A claim should be traceable to a sentence the system actually fetched, which is why PRISM prints citation numbers beside the sentences it kept.

A model that answers only from memory can sound fluent and still invent a date, a name, or a citation. That failure is what people mean by hallucination in this setting: the words arrived without a retrieved source. RAG does not make invention impossible. It makes invention visible, because you can check the passage. If the passage is missing, the honest result is a refusal, not a guess.

PRISM's three archives are the only corpus the dashboard and the Python package read. Orbital covers flight, Neural covers the method itself, and Earth covers a handful of planetary systems. A question about a sports final has no foothold there, so the router abstains. Grounding is a constraint, not a slogan.
""",
    },
    {
        "id": "chunking",
        "title": "How PRISM Chunks Text",
        "archive": "neural",
        "summary": "LangChain's recursive splitter packs about 700 characters with 120 characters of overlap.",
        "entities": "RecursiveCharacterTextSplitter; chunk overlap; LangChain",
        "text": """
PRISM chunks every source document before it builds an index. The splitter is LangChain's RecursiveCharacterTextSplitter. It tries the largest natural break first and only then gives up and cuts finer: paragraphs, then lines, then sentences, then spaces. The target size is about 700 characters, with about 120 characters of overlap so a fact that sits on a boundary still appears in the neighboring chunk.

Overlap costs a little duplication and buys recall. A landing site named in the last sentence of one paragraph and explained in the first sentence of the next would be invisible to a hard cut. The overlap keeps both sentences available to search. Each chunk carries the document id, the title, the archive, and the entity list, so a hit can be cited without losing its origin.

Chunking is not summarization. The words in the chunk are the words of the source. Glass, Crystal, and Aurora all search these chunks. They do not search the raw files as single blobs, because a whole document dilutes a specific name such as NIRCam or Thwaites under paragraphs that are only adjacent.
""",
    },
    {
        "id": "hybrid-search",
        "title": "Hybrid Retrieval",
        "archive": "neural",
        "summary": "PRISM fuses BM25 with TF-IDF cosine using reciprocal rank fusion.",
        "entities": "BM25; TF-IDF; reciprocal rank fusion; InMemoryVectorStore",
        "text": """
PRISM keeps two indexes over the same chunks. The lexical index is BM25, Okapi scoring from the rank_bm25 library. BM25 rewards words that are rare in the corpus and frequent in the chunk, which is how a proper name such as NIRCam, Tranquility, or Ingenuity surfaces even when the rest of the question is ordinary. The dense index is a LangChain Embeddings implementation fit with TF-IDF over those chunks and stored in LangChain's InMemoryVectorStore. Cosine similarity on L2-normalized vectors finds passages that share a pattern of terms even when the ranking of exact rare words would have buried them.

The two ranked lists are not averaged in raw score. BM25 scores and cosine scores do not live on the same scale. PRISM fuses them with reciprocal rank fusion. A chunk at rank r contributes 1/(60+r), and a chunk that appears on both lists adds both contributions. The constant 60 keeps a single first-place hit from drowning out a chunk that both methods liked.

Crystal and Aurora also balance a comparison. If the question names two entities that live in different documents, retrieval must bring back at least one chunk from each document when such a chunk exists. A comparison of Hubble and JWST that only quotes Hubble is a failed comparison, however high the score.
""",
    },
    {
        "id": "corrective-rag",
        "title": "Corrective Retrieval",
        "archive": "neural",
        "summary": "The grader can send a weak retrieval to rewrite, and the rewrite may run at most twice.",
        "entities": "corrective RAG; document grader; query rewrite",
        "text": """
Corrective retrieval is the idea that a bad first search should not be the last search. PRISM takes that pattern from the corrective RAG loop taught with LangGraph. After retrieve, a document grader marks each chunk relevant or not. A chunk is relevant when it shares at least two content words with the question, when it carries an entity the question named, or when a content word from its title appears in the question.

The grade is sufficient when two or more chunks are relevant, or when one relevant chunk covers at least half of the question's content words. If the grade is weak and fewer than two rewrites have already run, the rewrite node appends neighboring entity names from the co-occurrence graph and retrieve runs again. The retry counter stops at two. A third loop would wander.

Rewrite does not call a chat model. It adds names that share a source document with something the question already touched, and it refuses names that are already in the question. If the archive still has nothing relevant, synthesize refuses instead of padding an answer. That refusal is the corrective path's last honest move.
""",
    },
    {
        "id": "langgraph-aurora",
        "title": "The Aurora Graph",
        "archive": "neural",
        "summary": "Aurora is a LangGraph StateGraph that routes, grades, rewrites, synthesizes, and verifies.",
        "entities": "LangGraph; Aurora; StateGraph",
        "text": """
Aurora is the long lens, and it is a real LangGraph StateGraph, not a sketch of one. The nodes are router, planner, retrieve, grade, rewrite, synthesize, verify, and abstain. START enters the router. The router sends a comparative or multi-hop question to the planner, a factual question straight to retrieve, and a question with no foothold in the archives to abstain.

The planner may append neighbor entities, then always goes to retrieve. Retrieve goes to grade. Grade either loops to rewrite or continues to synthesize. Rewrite returns to retrieve, and it may do so only until the retry count hits two. Synthesize goes to verify, and verify ends the graph. Abstain also ends the graph, with the refusal sentence and an empty citation list.

State carries the question, the route, the documents, the grade, the retry count, the answer, the citations, the support flag, and a trace. Every node appends a trace entry so the dashboard can light the nodes that actually ran. Glass and Crystal are not this graph. Glass is one hybrid retrieval plus synthesis. Crystal adds entity-balanced retrieval and one expansion, then stops. Only Aurora loops.
""",
    },
    {
        "id": "langchain-parts",
        "title": "What LangChain Does Here",
        "archive": "neural",
        "summary": "LangChain supplies documents, the splitter, embeddings, and the in-memory vector store.",
        "entities": "LangChain; InMemoryVectorStore; Document",
        "text": """
LangChain is the component layer under PRISM, and LangGraph is the control layer. LangChain provides the Document object that carries page content and metadata, the RecursiveCharacterTextSplitter that cuts the corpus, the Embeddings interface that TfidfEmbeddings implements, and InMemoryVectorStore, which holds the dense index in process. Those are library calls, not renamed copies.

BM25 sits beside that stack. The rank_bm25 library scores the same chunks, and reciprocal rank fusion merges the two rankings in PRISM's own code. LangChain's ensemble helpers are not required for the fusion to be real. What matters is that both lists exist and that a chunk can earn its place from either of them.

PRISM does not call a hosted chat model. Synthesis selects sentences from graded chunks, numbers them, and refuses when nothing relevant survived. The browser twin follows the same refusal and the same citation rules, which is why the dashboard runs without an API key. A later chat model can be placed behind synthesize. It should not be placed in front of the grader or the citation check.
""",
    },
    {
        "id": "evaluation",
        "title": "How a Run Is Judged",
        "archive": "neural",
        "summary": "PRISM reports a support flag, context precision, citation coverage, and latency.",
        "entities": "context precision; faithfulness; support flag",
        "text": """
PRISM reports a few numbers on every run, as proxies in the spirit of RAGAS rather than as the RAGAS library itself. Context precision is the fraction of retrieved chunks the grader kept. A run that fetches six chunks and keeps one is less precise than a run that fetches four and keeps three, even if both eventually answer.

The support flag is stricter than a fluent paragraph. It is true only when the answer cites at least one passage that survived grading, and Aurora's verify node also checks that every citation chunk id exists in the index. Citation coverage counts the distinct documents those citations came from. A comparison that cites only one document can be supported and still be incomplete, which is why the balanced retriever exists.

Latency is the wall time around the lens call, reported in milliseconds. The Bench view runs a fixed set of questions through Glass, Crystal, and Aurora and shows route, support, precision, and latency side by side. The football question is in that set on purpose. A grounded system should refuse it.
""",
    },
    {
        "id": "entity-graph",
        "title": "The Entity Neighborhood",
        "archive": "neural",
        "summary": "Entities that share a document become neighbors, and rewrite uses those neighbors.",
        "entities": "entity graph; co-occurrence; GraphRAG; LightRAG",
        "text": """
PRISM builds a small entity graph while it indexes. Two entities become neighbors when they are listed on the same source document. Eagle and Columbia share the Apollo document, so each can suggest the other. NIRCam and Sun-Earth L2 share the JWST document. The graph is co-occurrence, not a claim that one entity causes the other.

Query rewrite and Crystal's single expansion step use that neighborhood. They look at entities mentioned in the question or sitting on the passages already retrieved, then add a few neighboring names the question did not already contain. The added names give BM25 another exact token to hunt for. They do not invent a new corpus.

This is an original local implementation of a neighborhood idea that also shows up in Microsoft GraphRAG and in HKUDS LightRAG. PRISM does not import those projects, does not build their community summaries, and does not require a model to extract triples. The archive view lets you click an entity and see the other documents that share it, which is the same graph the rewrite node walks.
""",
    },
    {
        "id": "amoc",
        "title": "The AMOC",
        "archive": "earth",
        "summary": "The AMOC is the Atlantic overturning circulation and is not identical to the Gulf Stream.",
        "entities": "AMOC; Atlantic Meridional Overturning Circulation; Gulf Stream",
        "text": """
The AMOC is the Atlantic Meridional Overturning Circulation. Warm, salty surface water moves northward through the Atlantic. At high latitudes it cools, becomes dense, and sinks, and a colder deep flow returns south. That overturning is a basin-scale loop, not a single ribbon on a map.

The Gulf Stream is related and is not the same thing. The Gulf Stream is a strong surface current along the western edge of the North Atlantic. It is part of the upper limb of the story and it is also a wind-driven current. Replacing the name AMOC with the name Gulf Stream, or the reverse, loses the distinction between the whole overturning and one surface jet.

A slowdown is discussed because freshening can weaken the sinking. Meltwater from Greenland adds freshwater, freshwater is less dense than salty water, and less dense water is harder to sink. Researchers connect a weaker overturning with shifted storm tracks and with sea-level effects along the east coast of the United States. This archive does not give a year of collapse. It records the mechanism and the distinction.
""",
    },
    {
        "id": "coral",
        "title": "Coral Bleaching",
        "archive": "earth",
        "summary": "Bleaching is the loss of zooxanthellae under stress, especially heat, and it is not automatic death.",
        "entities": "zooxanthellae; coral bleaching; Great Barrier Reef",
        "text": """
Reef-building corals live with photosynthetic algae called zooxanthellae. The algae sit in the coral's tissue, give the colony most of its color, and hand over a large share of the food they make from sunlight. The partnership is why clear, nutrient-poor water can still support a reef.

Coral bleaching is what happens when that partnership breaks. Under stress, especially marine heat, the coral expels the algae and the tissue turns pale. The coral is not automatically dead. If the heat is short, algae can return and the colony can recover. If the heat stays, the colony starves. Bleaching is an injury with a possible recovery, which is why a single pale season is not the same sentence as a dead reef.

The Great Barrier Reef has lived through repeated mass bleaching. Heatwaves, not a mystery disease, are the stress this archive names. Local pollution and storms matter, and they are not a substitute explanation for a basin-scale heat event. The useful distinction is between bleaching, which is the loss of zooxanthellae, and death, which follows only if the stress does not let up.
""",
    },
    {
        "id": "amazon",
        "title": "The Amazon Basin",
        "archive": "earth",
        "summary": "The Amazon recycles moisture as flying rivers, and deforestation weakens that loop.",
        "entities": "Amazon Basin; flying rivers; Madeira River",
        "text": """
The Amazon Basin holds the largest tropical rainforest. Moisture does not simply fall once and run to the sea. Trees pull water from the soil and release it from their leaves, the air carries that moisture downwind, and it falls again. People call those repeated inland flows flying rivers. A storm over the western basin may contain water that has already passed through several forests.

The rivers on the ground are just as specific. The Madeira is one of the great southern tributaries. The Rio Negro, dark with dissolved organics, meets the sediment-heavy Solimões system near Manaus, and the two run side by side before they mix. Those names are the ones to retrieve, not a generic list of every creek.

The basin stores a vast amount of carbon in trees and soils. Deforestation weakens the moisture recycling, because land that no longer transpires feeds the flying rivers less, and it adds carbon to the air when the cut wood and the disturbed soil oxidize. The archive's claim is that coupling: the forest is not only a store of carbon, it is part of the rain machine.
""",
    },
    {
        "id": "antarctica",
        "title": "Antarctic Ice",
        "archive": "earth",
        "summary": "The Antarctic ice sheet is land ice, and Thwaites drains a vulnerable West Antarctic basin.",
        "entities": "Antarctic ice sheet; Thwaites; sea ice",
        "text": """
The Antarctic ice sheet is land ice, snow compressed over hundreds of thousands of years until it flows under its own weight. Sea ice is frozen ocean. When sea ice melts, it does not raise sea level in the way land ice does, because that water was already afloat. Mixing the two is the most common mistake in a short answer about Antarctica.

The East Antarctic ice sheet is the larger, colder mass, sitting mostly on bedrock above sea level. The West Antarctic ice sheet is smaller and, in important places, rests on bedrock that lies below sea level. Ice on a reverse slope can retreat in a way that is hard to stop once warm water reaches the grounding line, the place where the ice lifts off the bed and begins to float.

Thwaites Glacier is watched because it drains a large portion of that West Antarctic basin. A change at Thwaites is not a change in sea ice extent on a winter map. It is a change in how much land ice can reach the ocean. This archive does not invent a year of collapse. It keeps the distinction between the ice sheet, the sea ice, and the glacier that researchers treat as a hinge.
""",
    },
    {
        "id": "monsoon",
        "title": "Monsoon Systems",
        "archive": "earth",
        "summary": "A monsoon is a seasonal reversal of the wind, and the Indian summer monsoon feeds on the shifted ITCZ.",
        "entities": "monsoon; Intertropical Convergence Zone; Indian summer monsoon",
        "text": """
A monsoon is a seasonal reversal of the winds, not a synonym for heavy rain. Many places have downpours and no monsoon. A monsoon climate reverses the prevailing wind between summer and winter, and the rain follows the wind that comes off the ocean.

The Indian summer monsoon is the clearest case in this archive. In boreal summer the Intertropical Convergence Zone shifts north. Winds blow from the ocean onto the subcontinent, the air rises, and most of South Asia's annual rain falls in that season. Reservoirs, sowing dates, and power from hydroelectric dams are built around that timing. A late onset or a long break is an agricultural event, not only a weather anecdote.

A break in the monsoon is a pause in rainfall inside the wet season, when the rains retreat or weaken for days and then return. It is not the winter reversal. Questions about the monsoon should be ready to say wind reversal, the Intertropical Convergence Zone, and the Indian summer monsoon, and should not treat every flood as a monsoon.
""",
    },
    {
        "id": "urban-heat",
        "title": "Urban Heat Islands",
        "archive": "earth",
        "summary": "Cities run hotter than nearby countryside because of dark surfaces, waste heat, and less evaporation.",
        "entities": "urban heat island; albedo; evapotranspiration",
        "text": """
An urban heat island is the pattern in which a city runs warmer than the countryside around it, especially at night. The causes are local and physical. Dark paving and roofs have a low albedo, so they absorb sunlight instead of reflecting it. Buildings store that heat in masonry and release it after sunset, which is why the difference often peaks at night rather than at noon.

Vegetation cools air by evapotranspiration: water moving from soil through leaves and into the air carries heat with it. A street with little soil and few trees has less of that cooling. Engines, air conditioners, and industry add waste heat. Tall streets can also trap warm air and block wind. None of these requires a change in the planet's greenhouse gases, and none of them cancels that change either. A resident feels the sum.

Mitigation follows the causes. Trees and parks restore evapotranspiration. Reflective roofs raise albedo. The effect is local. Calling a hot neighborhood proof of a global trend, or calling global warming merely an urban heat island, mixes two scales this archive keeps apart.
""",
    },
]


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for doc in DOCS:
        body = doc["text"].strip() + "\n"
        content = (
            "---\n"
            f"id: {doc['id']}\n"
            f"title: {doc['title']}\n"
            f"archive: {doc['archive']}\n"
            f"summary: {doc['summary']}\n"
            f"entities: {doc['entities']}\n"
            "---\n\n"
            f"{body}"
        )
        (ROOT / f"{doc['id']}.md").write_text(content, encoding="utf-8")
    print(f"Wrote {len(DOCS)} documents to {ROOT}")


if __name__ == "__main__":
    main()
