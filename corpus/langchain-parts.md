---
id: langchain-parts
title: What LangChain Does Here
archive: neural
summary: LangChain supplies documents, the splitter, embeddings, and the in-memory vector store.
entities: LangChain; InMemoryVectorStore; Document
---

LangChain is the component layer under PRISM, and LangGraph is the control layer. LangChain provides the Document object that carries page content and metadata, the RecursiveCharacterTextSplitter that cuts the corpus, the Embeddings interface that TfidfEmbeddings implements, and InMemoryVectorStore, which holds the dense index in process. Those are library calls, not renamed copies.

BM25 sits beside that stack. The rank_bm25 library scores the same chunks, and reciprocal rank fusion merges the two rankings in PRISM's own code. LangChain's ensemble helpers are not required for the fusion to be real. What matters is that both lists exist and that a chunk can earn its place from either of them.

PRISM does not call a hosted chat model. Synthesis selects sentences from graded chunks, numbers them, and refuses when nothing relevant survived. The browser twin follows the same refusal and the same citation rules, which is why the dashboard runs without an API key. A later chat model can be placed behind synthesize. It should not be placed in front of the grader or the citation check.
