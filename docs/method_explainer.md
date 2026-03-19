# Method Explainer

## Title

Adaptive Evidence-Graph Retrieval for Structure-Aware Document Intelligence

**Method name:** SAGER  
**Expanded form:** Structure-Aware Graph Evidence Retrieval

## Purpose of this document

This file explains:

- what our experiment was trying to prove
- what the main method is
- how the system flow works step by step
- what the important terms mean
- what level of granularity our evidence graph uses

## 1. What our experiment was about

The goal of our experiment was to test whether **evidence-graph retrieval** is a better foundation for document intelligence than plain flat chunking.

Most document AI systems still do something like this:

1. extract text from a PDF
2. split the text into chunks
3. run vector search or RAG over those chunks

That works sometimes, but it often breaks when documents contain:

- headings
- tables
- footnotes
- figures
- citations
- multi-page context
- long documents with mixed structure

So our experiment asked:

**Can we represent documents as smaller evidence units with structure, then retrieve over those units more intelligently than basic chunking?**

## 1.1 What this method is not

This method is **not** a keyword-based extraction pipeline.

It is also **not**:

- a plain keyword matching system
- a fixed chunk retrieval system
- a naive RAG pipeline over raw text blocks

Even though some prototype components used heuristic or lexical signals, the actual method is not conceptually based on keyword extraction.

The core of the method is:

- semantic retrieval over evidence atoms
- structure-aware ranking
- graph-assisted context expansion
- support-linked evidence assembly

## 2. What our main method is

Our method is:

**Adaptive Evidence-Graph Retrieval for Structure-Aware Document Intelligence**

We call the method:

**SAGER** = **Structure-Aware Graph Evidence Retrieval**

The main idea is:

- do not treat the document as one long text stream
- do not rely only on fixed chunks
- break the document into smaller **evidence atoms**
- connect these atoms using lightweight structure
- retrieve the best evidence plus its local neighborhood
- return support-linked results instead of isolated text matches

In simple words:

Instead of saying:

> "Give me the best chunk"

our method says:

> "Find the most relevant evidence units, understand their local structure, connect them, and return supported context."

That is why **evidence-graph retrieval** is the right conceptual name, and **SAGER** is the formal method name we use for the system.

## 3. Core terminologies

## 3.1 What is an evidence atom?

An **evidence atom** is the smallest usable retrieval unit in our system.

In the current prototype, an atom is usually close to a **line-level** or **short span-level** extracted unit from a page.

An atom stores information such as:

- `doc_id`
- `page`
- `text`
- `reading_order`
- `parser_source`
- `confidence`
- `atom_type`
- `role_label`

Examples of atoms:

- a heading line
- a sentence-like extracted line
- a footnote line
- a caption line
- a table-like row

Important:

An atom is **not word-specific** in our current method.

It is usually closer to:

- a line
- a phrase
- a sentence fragment
- a short document unit

So the atom granularity is **smaller than chunking, but larger than individual words**.

## 3.2 What is an evidence graph?

An **evidence graph** is a graph where:

- nodes are evidence atoms
- edges represent relationships between atoms

In the current prototype, the graph is lightweight. It mainly includes:

- **adjacency edges**
  Meaning one atom comes before or after another in reading order
- **containment edges**
  Meaning a heading is connected to the content that follows it

So the graph is currently **atom-specific**, not word-specific.

The graph is also not purely sentence-specific in a strict NLP sense, because the extracted units are based on PDF text structure and line-level parsing, not perfect sentence segmentation.

A better way to say it is:

**The evidence graph is built over small document evidence units, roughly line/span level, with document-structure relationships.**

## 3.3 What is context?

**Context** is the set of evidence atoms that the system assembles for a given query.

Context is not just “top matching text.”

It is the result of:

- semantic ranking
- atom selection
- graph expansion
- support assembly

So context means:

> the set of evidence units and nearby supporting units that the system believes are sufficient to answer the query

## 3.4 What is a context program?

A **context program** is the retrieval policy used for one query.

It decides things like:

- what kind of query this is
- which atoms to prioritize
- which graph edges to expand
- how many hops to expand
- what support checks to apply

So it is like a small retrieval strategy selected at query time.

## 3.5 What is structure-aware retrieval?

Structure-aware retrieval means the system is not blind to the type of text it is searching.

It knows that:

- a heading is different from body text
- a footnote is different from a title
- a caption is different from a paragraph
- a table row is different from a citation

That helps it retrieve more grounded evidence.

## 3.6 What is support-linked retrieval?

Support-linked retrieval means the returned answer or document hit is tied back to:

- supporting atom ids
- supporting pages
- supporting evidence text

So the result is inspectable.

That is one of the main strengths of our approach.

## 4. Is our evidence graph word-specific, sentence-specific, or chunk-specific?

This is an important question.

The answer is:

**It is primarily atom-specific, where atoms are line/span-level evidence units.**

That means:

- not word-specific
- not classical sentence-specific
- not large chunk-specific either

More precisely:

- words are too small and too noisy for our current graph
- large chunks are too coarse and lose structure
- atoms are meant to be a middle layer: fine-grained enough for evidence, but large enough to be meaningful

So the graph granularity is:

**fine-grained document evidence units**

In future versions, atoms could become more sophisticated, such as:

- sentence atoms
- table-cell atoms
- figure-caption atoms
- citation atoms
- clause atoms
- region atoms

But in the current prototype they are mostly line-level evidence units enriched with structure labels.

## 5. Full system flow

## Step 1: Receive the PDF

A document enters the system.

## Step 2: Extract text page by page

We extract content from each page while preserving:

- page identity
- reading order
- source provenance

At this stage, the document is still raw extracted material.

## Step 3: Create evidence atoms

The extracted content is split into small units called evidence atoms.

Each atom becomes an object in the system.

This is a major difference from plain chunking.

Instead of one long body of text, we now have a set of smaller evidence units.

## Step 4: Normalize atoms and infer structure

Each atom is enriched with labels such as:

- `heading`
- `footnote`
- `citation`
- `table_caption`
- `figure_caption`
- `table_row`
- `body`

This makes the document representation more meaningful.

## Step 5: Build the evidence graph

Atoms are connected using lightweight relationships:

- adjacency
- containment

This creates local structure around the evidence.

## Step 6: Build the persistent corpus index

We build:

- a document-level semantic index
- an atom-level semantic index
- metadata for support inspection

This is what allows repeated queries over the corpus without rebuilding everything from scratch.

## Step 7: Receive a user query

Examples:

- `humanitarian data governance`
- `data responsibility guidelines`
- `table revenue amount`
- `figure results confidence`

## Step 8: Build a context program

The system decides how to retrieve for this query.

It determines:

- what kind of query this is
- which evidence types matter
- how much graph expansion to use

## Step 9: Rank candidate documents

The system uses the persistent semantic index to find promising documents.

This is not a keyword-only search stage.

It is a semantic evidence-retrieval stage.

## Step 10: Rank candidate atoms

Inside those documents, the system finds the most relevant atoms.

## Step 11: Expand context through the graph

The system adds nearby or connected evidence atoms based on graph relationships.

This helps avoid isolated retrieval and adds supporting local structure.

## Step 12: Produce a support-linked result

The system returns:

- top document hits
- support atom ids
- supporting pages
- evidence text snippet

## Step 13: Verify support

The system checks whether the result is sufficiently supported.

In the current prototype, this is support-presence verification rather than full truth verification.

## Step 14: Reprocess if support is weak

The architecture supports selective reprocessing of uncertain regions.

This is more of an architectural capability right now than a fully developed module, but it is an important part of the method.

## 6. Why this method is stronger than plain chunking

Plain chunking has these problems:

- it loses structure
- it mixes headings and body text together
- it hides provenance
- it makes support inspection harder
- it often retrieves context that is too broad or too coarse

Our method improves this because:

- evidence units are smaller and more precise
- structure is preserved
- graph neighbors can be added for support
- outputs are linked to evidence atoms
- retrieval is more inspectable

## 6.1 Why this is not keyword-based extraction

Keyword-based extraction usually means:

- detect a word or phrase
- pull nearby text
- treat that local match as the result

That is not what our method does.

Our method instead:

- represents the document as evidence atoms
- semantically ranks candidate evidence
- uses structure labels such as heading, footnote, caption, and table row
- expands through graph relationships
- assembles support-linked context

So the correct framing is:

**This is evidence-graph retrieval, not keyword-based extraction.**

## 7. What our experiment proved

The experiment showed that:

- a large noisy PDF corpus can be processed into reusable evidence artifacts
- structure-aware atoms are practical
- persistent semantic indexing works over the corpus
- support-linked evidence retrieval works
- the architecture outperformed a simpler lexical baseline on representative queries

## 8. What our experiment did not prove

The experiment did not yet prove:

- state-of-the-art document intelligence
- strong multimodal layout-native parsing
- legal- or finance-specialized precision
- benchmark superiority over strong modern RAG systems

So the honest conclusion is:

**The experiment validated the architecture and method direction, but not the final production-grade system.**

## 9. Short summary

If someone asks what our method is in one paragraph:

> Our method represents documents as small evidence atoms instead of large chunks, connects those atoms into a lightweight evidence graph, and retrieves structure-aware context from that graph using persistent semantic indexing. This makes document retrieval more grounded, more inspectable, and more suitable for complex documents than plain chunk-based retrieval.

An even shorter version is:

> Our method is an evidence-graph retrieval system that semantically retrieves structure-aware evidence units, expands through lightweight document relationships, and returns support-linked context rather than relying on keywords or large fixed chunks.
