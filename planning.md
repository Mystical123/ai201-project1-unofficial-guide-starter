# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

CS department professor reviews at Sacramento State University, sourced from Rate My Professors. This knowledge is hard to find otherwise because it is scattered across individual professor pages and never aggregated or searchable by topic — students have to already know which professor to look up before they can find anything useful. This system makes it possible to ask cross-professor questions like "who is best for beginners?" and get a grounded answer.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Reviews for Mamoun Abu-Samaha | https://www.ratemyprofessors.com/professor/2231940 |
| 2 | Rate My Professors | Reviews for Prof. Badruddoja | https://www.ratemyprofessors.com/professor/954619 |
| 3 | Rate My Professors | Reviews for Prof. Gordon | https://www.ratemyprofessors.com/professor/2545657 |
| 4 | Rate My Professors | Reviews for Prof. Jin | https://www.ratemyprofessors.com/professor/626344 |
| 5 | Rate My Professors | Reviews for Prof. Krovetz | https://www.ratemyprofessors.com/professor/2016315 |
| 6 | Rate My Professors | Reviews for Prof. Peng | https://www.ratemyprofessors.com/professor/2463450 |
| 7 | Rate My Professors | Reviews for Prof. Polivka | https://www.ratemyprofessors.com/professor/857674 |
| 8 | Rate My Professors | Reviews for Prof. Sabzevary | https://www.ratemyprofessors.com/professor/679668 |
| 9 | Rate My Professors | Reviews for Prof. Salem | https://www.ratemyprofessors.com/professor/2933307 |
| 10 | Rate My Professors | Reviews for Prof. Tajlil | https://www.ratemyprofessors.com/professor/3089504 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->



**Chunk size:**
Chunk size was updated to 800 characters after testing showed 500-character chunks produced weak retrieval scores (above 0.5). Larger chunks carry more semantic signal per embedding, which improved top results to the 0.31-0.49 range., this is long enough to capture 2-3 reviews and short enough to stay focused on whats given. Fixed character size approach is best because it will handle any format we don't have control over and it will provide us with more efficient chunks that can store multiple reviews.
**Overlap:**
Overlap will be set to 100 characters which will catch the split boundary without too much redunancy. Overlap matters here because Rate My Professor reviews end and start just like that and we need 100 char overalop to ensure that the tail of one chunk and head of the next will share enough context where we don't lose critical meaning. 
**Reasoning:**
The purpose of this would be so we can get the most amount of context from our reviews while also not losing any data or context in the process but still being efficient with our tokens because we dont want to use too much to the point its inefficient. However, we do want enough context so we know what the reviews are about and have 100 characters overlapping to also know a bit more context from previous reviews. Too small of a chunk would be anything less than 200 characters, each chunk is a setnece fragment or a half review. Too large would be anything greater than 1000 characters since this would combine too many reviews together and make it harder to go through. Sweet Spot would be anything around 500 characters because this is where the chunk will capture 1-3 reviews and the chunk will be mroe focused. LLM will also get enough context to genereate a grounded and specific answer.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->


**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers

**Top-k:** 3 to 5 chunks is the sweet spot for the msot context and also not being too overwhelming withtout overwhelming the LLM with too much information. 

**Production tradeoff reflection:** all-MiniLM-L6-v2 runs locally at no cost, which is ideal for this project. However, in a production system I would weigh the following tradeoffs: context length is capped at 256 tokens, which works for short reviews but would be limiting for longer documents; it is English-only, so non-English reviews or queries wouldn't be served well; it is general-purpose and not fine-tuned on academic or review text, so niche terminology may not embed as accurately as a domain-specific model; and running locally means higher latency at scale compared to an API-hosted model. A model like OpenAI's text-embedding-3-small would address latency and accuracy, while multilingual-e5 would add language coverage.


---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which professor should I take for the most useful lectures and best in-person teaching experience? | Scott Gordon is the best option based on reviews — students consistently mention his clear explanations, engaging lectures, and useful in-class examples that directly help with exams. He has a 4.7/5 rating with 89% of students saying they would take him again. |
| 2 | Which professor has the easiest exams that are similar to the homework and study guides? | Holly Tajlil is frequently praised for well-organized classes with a low difficulty rating of 2.4. Reviews indicate her exams align closely with homework and study material, making her one of the most approachable professors in the department. |
| 3 | Which professor is the most helpful with feedback on assignments and responds to emails? | Mamoun Abu-Samaha stands out based on his 4.4/5 rating across 134 reviews, with students noting his responsiveness and genuine care for student success. He is one of the most reviewed professors in the department, suggesting consistent positive experiences. |
| 4 | Which professor has the best reviews for teaching CS courses and keeping class structured? | Scott Gordon receives the highest ratings for structured and effective teaching. Reviews highlight his ability to keep class on track, cover relevant material, and make difficult concepts accessible compared to lower-rated professors. |
| 5 | How quickly does Abu-Samaha typically respond when you need help or are falling behind? | Based on reviews, Mamoun Abu-Samaha is known for being accessible and responsive. Students report he responds within the same day via email and holds useful office hours, making it easy to get help when falling behind. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Missing source attribution: Rate my Professor does not have a clean source to copy and paste from and because of this, many chunks could be missing what professor they are coming from and the system might not return the best possible answer due to lack of information
2. off-topic retrieval: my question might be about how a specific professor's grading is but because I dont know what chunks are going ot be retreieved, the chunk might talk about office hours or how well the professor teaches their class instead of having context for the actual question. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```mermaid
flowchart LR
    A[Raw .txt Files\ndocuments/] --> B[Document Ingestion\npython / open()]
    B --> C[Chunking\n500 chars / 100 overlap]
    C --> D[Embedding\nall-MiniLM-L6-v2]
    D --> E[Vector Store\nChromaDB]
    F[User Query] --> G[Query Embedding\nall-MiniLM-L6-v2]
    G --> E
    E --> H[Top-5 Chunks Retrieved]
    H --> I[Response Generation\nLlama 3.3 via Groq]
    I --> J[Answer + Source Citation]
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
-Input to Claude: Chunking strategy section of planning.md + the structure of my .txt files 
-Expected Output: a python function that laods all 10 .txt files and splits them into 500 char chunks with 100-char overlap 
-how to Verify: check that chunks are right size and professor names are preservred 
**Milestone 4 — Embedding and retrieval:**
-Input to Claude: Retreival Approach section + chunking output 
-Expected Output: code that embeds chunks using all-MiniLM-L6-v2 and stores them into ChromaDB, plus a query function that returns top 5 chunks 
-How to verify: run test query and confirm relevant chunks come back 
**Milestone 5 — Generation and interface:**
Input to Claude: full pipeline spec + Groq API setup
Expected output: code that takes retreieved chunks and sends them to Llama 3.3 via Groq with prompt hat forces groudned, cited answers 
How to verify: ask test qeustion and confirm answer references real professor from documents 