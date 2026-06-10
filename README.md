# The Unofficial Guide — Project 1

---

## Domain

CS department professor reviews at Sacramento State University, sourced from Rate My Professors. This knowledge is valuable because students making course registration decisions need to know teaching style, exam difficulty, grading fairness, and professor accessibility — none of which appear in official course catalogs or university websites. The only way to find this information through official channels is to already know which professor you are looking for, meaning students who don't have connections to older students are at a disadvantage. This system makes it possible to ask cross-professor questions and get a grounded answer drawn from real student reviews.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2231940 |
| 2 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/954619 |
| 3 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2545657 |
| 4 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/626344 |
| 5 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2016315 |
| 6 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2463450 |
| 7 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/857674 |
| 8 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/679668 |
| 9 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/2933307 |
| 10 | Rate My Professors | Student reviews | https://www.ratemyprofessors.com/professor/3089504 |

---

## Chunking Strategy

**Chunk size:** 800 characters. Initially set to 500 characters but retrieval testing showed cosine distance scores above 0.5, indicating weak semantic matches. Increasing to 800 characters gave each chunk enough review content to carry a meaningful embedding, bringing top retrieval scores into the 0.31–0.49 range.

**Overlap:** 150 characters. Rate My Professors reviews are copy-pasted as continuous text with no consistent separator between individual reviews. Without overlap, a chunk split in the middle of a review would lose the context of that review entirely. A 150-character overlap ensures the tail of one chunk and the head of the next share enough text that neither loses critical meaning at the boundary.

**Why these choices fit your documents:** RMP reviews are short opinion pieces (typically 2–5 sentences) that run together in a single block per professor. Fixed-size chunking was chosen over paragraph-based chunking because the copy-pasted text has inconsistent formatting and no reliable paragraph breaks. The 800/150 configuration captures 2–4 complete reviews per chunk while maintaining boundary context.

**Final chunk count:** 314 chunks across 10 documents.

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers. This model runs locally with no API key and no rate limits, making it practical for a class project. It is optimized for semantic similarity on short sentences, which fits well with short review-style text where meaning matters more than keyword matching.

**Production tradeoff reflection:** For a production system serving real students, I would weigh several tradeoffs. First, context length — all-MiniLM-L6-v2 is capped at 256 tokens, which works for short reviews but would be limiting for longer documents like syllabi or handbooks. Second, cost vs. latency — this model runs locally which is slower at scale; an API-hosted model like OpenAI's text-embedding-3-small would handle higher traffic with lower latency but would add per-token cost. Third, domain specificity — this is a general-purpose model and is not fine-tuned on academic or review text, so a model trained specifically on student-generated content would likely produce more accurate embeddings for this use case. Finally, multilingual support is absent — if serving international students who write reviews in other languages, a model like multilingual-e5 would be necessary.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt explicitly instructs the model: "Answer ONLY using the information provided in the context below. Do not use any outside knowledge or general assumptions. Always cite which source document(s) your answer comes from. If the context does not contain enough information to answer the question, say exactly: 'I don't have enough information on that.'" The temperature is set to 0.2 to reduce the model's tendency to generate creative or speculative content beyond what the retrieved text supports.

**How source attribution is surfaced in the response:** Source attribution is handled two ways. First, the LLM is instructed in the system prompt to cite sources inline in its response. Second, the retrieved source filenames are programmatically appended in a separate "Retrieved from" field in the UI, regardless of what the LLM says — this guarantees attribution even if the model fails to cite sources in its text.

---

## Sample Chunks

The following are 5 representative chunks from the vector store, each labeled with its source document.

**Chunk 1 | Source: prof_badruddoja.txt**
```
Quality: 2.0 | Difficulty: 3.0 | CSC138 | May 25th, 2026
For Credit: Yes | Attendance: Not Mandatory | Grade: A-
The prof is caring & gave points back on the HW and allowed a make-up test since everyone did so bad.
I simply don't like his teaching style. Each class felt 3hrs & the hw q's are long & hard to understand.
Best to not miss class since most hw & exam q's will be based on in class activities.
Exam review is not helpful; basically study everything.
```

**Chunk 2 | Source: prof_jin.txt**
```
Quality: 4.0 | Difficulty: 2.0 | CSC174 | May 25th, 2026
For Credit: Yes | Attendance: Not Mandatory | Grade: A
A lot of in person examples that are on exams, so attendance is important.
Gave 2.5 pages for cheat sheet exam 1 which was mainly on the LLM hw we did.
If you write down and understand the code, it's pretty easy. The LLM unit was really interesting.
No cheat sheet for final, but if you practice given examples and hw it's easy too.
```

**Chunk 3 | Source: prof_tajlil.txt**
```
Quality: 5.0 | Difficulty: 2.0 | CSC28 | May 28th, 2026
For Credit: Yes | Attendance: Mandatory | Grade: A-
She gives you so many resources to succeed that if you fail, it really is on you.
Her lectures are dense in a good way; they cover a lot of material in a way that is easy to follow,
and she incorporates visual learning when possible.
I recommend taking her classes, and I hope to do so in the future.
```

**Chunk 4 | Source: prof_sabzevary.txt**
```
Quality: 4.0 | Difficulty: 3.0 | CSC130 | May 26th, 2026
For Credit: Yes | Attendance: Mandatory | Grade: A-
It is a very straightforward class. There is one midterm and one final exam,
both are VERY similar to the study guide he gives. If you understand everything on them then you WILL pass.
He is a very chill grader, takes student input into consideration
(we skipped zybooks because everyone told prof it wasn't helpful, prof moved due dates around, etc)
```

**Chunk 5 | Source: prof_abu-samaha.txt**
```
Quality: 5.0 | Difficulty: 3.0 | INFO6350 | Apr 10th, 2026
For Credit: Yes | Attendance: Mandatory | Grade: A
Good instructor! Gives good feedback. Knowledgeable in his field.
He gives a lot of information about the industry, especially the current trends.
His lectures are quite interesting. He focuses on the overall learning perspective of the student
and goes beyond textbook knowledge. He is one of the best Professors in the Computer Science Department.
```

---

## Retrieval Test Results

**Query 1: "Which professor has the most useful lectures?"**

Top returned chunks:
- `prof_abu-samaha.txt` (distance: 0.319) — "His lectures are quite interesting. He focuses on the overall learning perspective of the student and goes beyond textbook knowledge."
- `prof_jin.txt` (distance: 0.389) — "Amazing lectures. Helpful."
- `prof_sabzevary.txt` (distance: 0.400) — "lecturer. Funny too. Hilarious. Caring. Respected. Helpful."
- `prof_abu-samaha.txt` (distance: 0.400) — "Lectures are not just informative but professor also has a sense of humour which makes it fun to learn from him."
- `prof_krovetz.txt` (distance: 0.416) — "His lectures are easy to follow, you can check your hw, and you get unlimited quiz attempts."

**Why these chunks are relevant:** The query asks about lecture quality. All returned chunks contain explicit mentions of lectures — either using the word "lectures" directly or describing the professor's in-class teaching style. The top result from Abu-Samaha directly addresses lecture usefulness with the phrase "goes beyond textbook knowledge," which semantically matches the concept of "useful lectures."

---

**Query 2: "Which professor has the easiest exams?"**

Top returned chunks:
- `prof_krovetz.txt` (distance: 0.407) — "It is not the easiest subject to digest. If you come to lecture, you will likely understand a lot of it."
- `prof_krovetz.txt` (distance: 0.407) — "Very knowledgeable professor! But his lectures are really boring and his grading is terrible!"
- `prof_tajlil.txt` (distance: 0.415) — "Has 70% Test rule. Lectures were extremely long and boring. Test heavy."
- `prof_krovetz.txt` (distance: 0.417) — "Clear grading criteria. Test heavy. Helpful."
- `prof_sabzevary.txt` (distance: 0.420) — "Very disorganized but has the easiest 'exams' ever. 4 quizzes over the span of the semester with no cumulative final."

**Why these chunks are relevant:** The query asks about exam difficulty. The retrieved chunks all contain references to exams, tests, or grading. The most directly relevant chunk is the Sabzevary result which uses the exact phrase "easiest exams ever" — this is a strong semantic and keyword match. The Krovetz results appear because they discuss exam grading, even though they describe his exams as hard, demonstrating that retrieval finds topically relevant chunks regardless of sentiment.

---

**Query 3: "Which professor responds fastest to emails?"**

Top returned chunks:
- `prof_tajlil.txt` (distance: 0.488) — "She is a pretty average professor. She is super fast when responding to emails and will often respond as late as 9:00."
- `prof_sabzevary.txt` (distance: 0.552) — "lecturer. Funny too. Hilarious. Caring. Respected. Helpful."
- `prof_tajlil.txt` (distance: 0.553) — "I really liked Professor Tajlil. She's a super nice lady and at times can be a little repetitive lecturing the material."
- `prof_abu-samaha.txt` (distance: 0.594) — "urself everything. Lots of homework. Helpful."
- `prof_abu-samaha.txt` (distance: 0.600) — "Knowledgeable in his field. He gives a lot of information about the industry."

---

## Example Responses

**Response 1 — Query: "Which professor has the easiest exams that are similar to the homework and study guides?"**

> Based on the context, Professor Sabzevary has the easiest "exams" ever, with 4 quizzes over the span of the semester and no cumulative final. Additionally, Professor Tajlil allows a 5x7 card of notes for exams, which may also indicate that her exams are more straightforward.
>
> Sources:
> - [Source: prof_sabzevary.txt]
> - [Source: prof_tajlil.txt]

---

**Response 2 — Query: "Which professor has the best reviews for teaching CS courses and keeping class structured?"**

> Based on the context, Professor Gordon has the best reviews for teaching CS courses and keeping class structured. He is described as having "great lectures", being "one of the better professors at CSUS", and having a "lecture heavy" teaching style. He also has clear grading criteria, is caring, and is helpful. Additionally, one review states that "He explains things very clearly. If you are doing bad in this class then you are not paying attention. Just show up, pay attention and you'll do fine."
>
> Sources:
> 1. prof_gordon.txt
> 2. prof_abu-samaha.txt
> 3. prof_jin.txt

---

**Response 3 (out-of-scope) — Query: "What is the best restaurant near campus?"**

> I don't have enough information on that.
>
> Sources: None of the provided sources (prof_krovetz.txt, prof_polivka.txt, prof_abu-samaha.txt) contain information about restaurants near campus.

---

## Query Interface

**Input field:** A text box labeled "Your question" with a placeholder example: "Which professor has the most useful lectures?" The user types a plain-language question about Sac State CS professors and either clicks the Ask button or presses Enter to submit.

**Output fields:**
- **Answer** — a multi-line text box showing the LLM-generated response. The response is grounded in retrieved review chunks and includes inline source citations naming which document(s) the answer drew from.
- **Retrieved from** — a multi-line text box listing the source filenames of the top-5 retrieved chunks, displayed as a bulleted list. This field is populated programmatically regardless of what the LLM produces.

**Sample interaction transcript:**

*Input:* "How quickly does Abu-Samaha typically respond when you need help or are falling behind?"

*Answer output:*
> According to the context, Professor Abu-Samaha is "always willing to help every student" and is "incredibly communicative with students, even outside regular hours" and "accessible outside class". This suggests that he is responsive and available to help when needed.
>
> Sources:
> [Source: prof_abu-samaha.txt]

*Retrieved from output:*
> • prof_abu-samaha.txt

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which professor should I take for the most useful lectures and best in-person teaching experience? | Scott Gordon based on 4.7/5 rating and reviews praising clear explanations | Named Abu-Samaha as top choice, mentioned Krovetz and Sabzevary. Did not mention Gordon. | Partially relevant — retrieved Abu-Samaha and Sabzevary but missed Gordon | Partially accurate |
| 2 | Which professor has the easiest exams that are similar to the homework and study guides? | Holly Tajlil based on 2.4 difficulty rating and organized class structure | Named Sabzevary as top choice with specific evidence: "3 Exams in total which are easy." Also mentioned Tajlil. | Relevant — returned Sabzevary and Tajlil chunks | Accurate |
| 3 | Which professor is the most helpful with feedback on assignments and responds to emails? | Mamoun Abu-Samaha based on 134 reviews and high responsiveness mentions | Named Tajlil as standout for fast email response, also mentioned Abu-Samaha and Krovetz | Relevant — retrieved Tajlil, Abu-Samaha, Polivka, Sabzevary, Krovetz | Accurate |
| 4 | Which professor has the best reviews for teaching CS courses and keeping class structured? | Scott Gordon based on highest rating and structured teaching reviews | Named Gordon as top choice with direct quote: "He explains things very clearly." Also compared to Abu-Samaha and Jin. | Relevant — retrieved Gordon, Jin, Abu-Samaha | Accurate |
| 5 | How quickly does Abu-Samaha typically respond when you need help or are falling behind? | Same-day email response based on reviews mentioning accessibility | Described Abu-Samaha as "always willing to help" and "accessible outside class" but gave no specific timeframe | Relevant — only retrieved Abu-Samaha chunks | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Which professor should I take for the most useful lectures and best in-person teaching experience?"

**What the system returned:** The system named Abu-Samaha as the top recommendation, citing his "amazing lectures" and ability to explain concepts clearly. It did not mention Scott Gordon, who has the highest overall rating (4.7/5) in the department and whose reviews most consistently praise structured, effective in-person teaching.

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure caused by document size imbalance. Abu-Samaha has 134 reviews on Rate My Professors — significantly more than Gordon's 32 reviews. Because chunk count is proportional to document length, Abu-Samaha has roughly 4x more chunks in the vector store than Gordon. When a query about lectures is submitted, Abu-Samaha's chunks statistically dominate the top-k results simply because there are more of them, not because they are more relevant. Gordon's smaller document gets crowded out even though his reviews more consistently match the query intent.

**What you would change to fix it:** To fix this, I would normalize chunk representation across professors — either by capping the number of chunks per professor or by adding a metadata filter that ensures at least one chunk from each professor is considered during retrieval. Alternatively, a hybrid search approach combining semantic similarity with a per-source diversity constraint would prevent any single professor from dominating the results.

---

## Spec Reflection

**One way the spec helped you during implementation:** The planning.md Chunking Strategy section was directly useful when implementing the chunking function. Having already decided on 500 characters with 100-character overlap before writing any code meant the implementation was a straightforward translation of the spec into Python. When testing revealed that 500-character chunks produced weak retrieval scores, the spec also made it easy to update — I had a clear record of the original decision and the reasoning, so I could update both the code and the planning.md with the new values and the rationale for changing them.

**One way your implementation diverged from the spec, and why:** The spec listed top-k as 5, which stayed constant throughout. However, the distance metric was not specified in planning.md at all — the spec only mentioned using ChromaDB without specifying cosine vs. L2 distance. During implementation, the default L2 distance produced scores above 1.0 which made it impossible to evaluate retrieval quality against the milestone's 0.5 threshold. Switching to cosine distance was a divergence from the (silent) spec assumption that produced meaningfully interpretable scores between 0 and 1. If I were writing the spec again I would explicitly specify the distance metric as a required decision.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from planning.md, a sample of what my cleaned .txt files looked like, and a request to implement a chunk_text() function matching my specified chunk size and overlap.
- *What it produced:* A fixed-character chunking function with a while loop, chunk size and overlap as parameters defaulting to 500 and 100, and source metadata attached to each chunk.
- *What I changed or overrode:* After running retrieval tests, I changed the default chunk size from 500 to 800 and overlap from 100 to 150 because the smaller chunks produced cosine distance scores above 0.5, indicating weak semantic matches. The structure of the function stayed the same but the parameters were tuned based on empirical testing.

**Instance 2**

- *What I gave the AI:* The full pipeline diagram from planning.md, the Retrieval Approach section, and a request to implement the embedding and ChromaDB storage code plus a retrieval function that returns top-5 chunks with source metadata and distance scores.
- *What it produced:* An embed_and_store() function using SentenceTransformer and a ChromaDB collection with cosine distance, and a retrieve() function that embeds the query and returns matching chunks with metadata.
- *What I changed or overrode:* The initial version used L2 distance (ChromaDB default), which produced scores above 1.0. I directed the AI to switch to cosine distance by adding the metadata={"hnsw:space": "cosine"} parameter to the collection creation, which brought scores into the interpretable 0–1 range required by the milestone checkpoint.
