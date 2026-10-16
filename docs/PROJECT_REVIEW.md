# Project review and verification scope

The Groq capstone keeps Kraivor's developer workspace idea and replaces the
active AI flow with one Groq key plus local embeddings. This review covers the
paths needed for that demonstration; it is not an exhaustive security audit of
every legacy collaboration or administration feature.

## Issues corrected

| Area | Problem | Result |
| --- | --- | --- |
| AI configuration | Legacy provider routes and model selections required other keys | Central inference policy enforces the Groq endpoint and configured Groq models |
| Retrieval | Uploaded knowledge and analyzed code were not consistently available to chat | Shared chunk ingestion, local embeddings, and scoped hybrid retrieval |
| Grounding | Answers lacked consistent source references | Source labels, filenames, line ranges, and citation normalization |
| Conversation access | Reusing a conversation could bypass ownership checks | User and workspace are checked before loading or appending history |
| Workspace access | AI and analysis paths lacked live membership checks | Requests verify workspace access through Core |
| Streaming | Workflow output did not provide reliable final token streaming | Groq final answer streams over SSE and is persisted |
| Capacity controls | Concurrency slots did not reliably cover stream lifetime | Slots stay held until streaming finishes or fails |
| JWT verification | AI key rotation handling and analysis runtime cryptography were incomplete | Key-ID selection and RSA verification dependencies corrected |
| ZIP analysis | Upload job IDs, file records, multipart requests, and artifact storage were inconsistent | Matching job IDs, bounded extraction, corrected frontend upload, local persistent reports |
| GenAI analysis | Finding explanations used legacy provider setup | Groq enriches findings and generates the executive summary |
| Frontend routing | Broad API rewrite intercepted dynamic AI routes | Core rewrite runs as fallback after AI routes |
| Auth proxy | Slash normalization caused POST redirects and loops | Django URLs retain trailing slashes and automatic frontend slash redirects are disabled |
| Frontend runtime | Production omitted the TypeScript config loader | The Docker image includes the loader without installing packages on startup |
| Session expiry | AI fetch calls did not refresh expired sessions | Shared refresh-and-retry for chat, analysis, and document upload |
| Local startup | Docker dependencies, signing keys, migrations, and DynamoDB volume access blocked startup | Reproducible Groq Compose override and setup script |

## Remaining limitations

- The installed Next.js 15.5.26 production dependency has a moderate cache
  poisoning advisory. `npm audit --omit=dev` identifies 15.5.27 as the patched
  version. Update and retest before public deployment.
- Legacy provider implementation files and historical model database rows
  remain for compatibility. The active inference client and normal model
  selector enforce Groq; this is not a complete removal of every historical
  provider reference from the repository.
- Private GitHub repositories, OAuth providers, push notifications, and other
  optional external integrations retain their separate setup requirements.
- The local deployment uses development infrastructure and local storage. It
  is intended for a capstone demonstration; deployment hardening and the whole
  platform's legacy backend test suites are outside the verified scope.
- The small RAG evaluation measures expected facts and citation references.
  It does not establish general accuracy, resistance to every prompt injection,
  or equivalence to a comprehensive retrieval benchmark.

See [GROQ_CAPSTONE.md](GROQ_CAPSTONE.md) for architecture, limits, setup, and
reproducible live checks.
