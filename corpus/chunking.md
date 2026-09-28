---
id: chunking
title: How PRISM Chunks Text
archive: neural
summary: LangChain's recursive splitter packs about 700 characters with 120 characters of overlap.
entities: RecursiveCharacterTextSplitter; chunk overlap; LangChain
---

PRISM chunks every source document before it builds an index. The splitter is LangChain's RecursiveCharacterTextSplitter. It tries the largest natural break first and only then gives up and cuts finer: paragraphs, then lines, then sentences, then spaces. The target size is about 700 characters. When a chunk fills up, the next one keeps the previous paragraph, so a fact on a boundary still appears in the neighboring chunk without cutting a word in half.

Overlap costs a little duplication and buys recall. A landing site named in the last sentence of one paragraph and explained in the first sentence of the next would be invisible to a hard cut. The overlap keeps both sentences available to search. Each chunk carries the document id, the title, the archive, and the entity list, so a hit can be cited without losing its origin.

Chunking is not summarization. The words in the chunk are the words of the source. Glass, Crystal, and Aurora all search these chunks. They do not search the raw files as single blobs, because a whole document dilutes a specific name such as NIRCam or Thwaites under paragraphs that are only adjacent.
