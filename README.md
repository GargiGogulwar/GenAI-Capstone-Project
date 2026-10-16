## 🐍 Kraivor — developer intelligence Workspace

**Groq-only GenAI capstone:** start with `python scripts/setup_groq.py`.
See [the capstone guide](docs/GROQ_CAPSTONE.md) for setup, the GenAI concept map,
demonstration steps, and end-to-end verification.

<div align="center">

  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/nkswalih/kraivor/dev/docs/assets/kraivor_text_logo.svg">
    <img src="https://raw.githubusercontent.com/nkswalih/kraivor/dev/docs/assets/kraivor_text_logo.svg" alt="Kraivor" width="500">
  </picture>

  <p><strong>One workspace. Infinite codebase memory.</strong></p>

  <br>

  <!-- Badges -->

  <p>
    <a href="https://github.com/nkswalih/kraivor/actions"><img src="https://img.shields.io/github/actions/workflow/status/nkswalih/kraivor/ci.yml?style=flat-square&logo=github&label=build" alt="Build Status"></a>
    <a href="https://github.com/nkswalih/kraivor/blob/dev/LICENSE"><img src="https://img.shields.io/github/license/nkswalih/kraivor?style=flat-square&color=blue" alt="License"></a>
    <!-- <a href="https://github.com/nkswalih/kraivor/releases"><img src="https://img.shields.io/github/v/release/nkswalih/kraivor?style=flat-square&logo=semver" alt="Version"></a> -->
    <a href="https://github.com/nkswalih/kraivor/stargazers"><img src="https://img.shields.io/github/stars/nkswalih/kraivor?style=flat-square&logo=github" alt="Stars"></a>
    <a href="https://github.com/nkswalih/kraivor/graphs/contributors"><img src="https://img.shields.io/github/contributors/nkswalih/kraivor?style=flat-square&logo=contributorcovenant" alt="Contributors"></a>
    <a href="https://github.com/nkswalih/kraivor/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square&logo=github" alt="PRs Welcome"></a>
    <a href="https://discord.gg/rgdV8Uh6D"><img src="https://img.shields.io/badge/chat-discord-5865F2?style=flat-square&logo=discord" alt="Discord"></a>
  </p>
  
  <p>Kraivor is a unified developer intelligence platform that combines a <strong>Repository Analyzer</strong>, <strong>Agentic AI System</strong>, and <strong>Developer Productivity Platform</strong> into a single authenticated workspace — giving engineering teams deep code insights, AI-powered assistance, and a collaborative hub, all out of the box.</p>
</div>

---

## About the Project

Engineering teams today juggle too many tools — repository analysis, AI coding assistants, project management, documentation — all scattered across different platforms with no shared context. Kraivor solves this by bringing everything into **one unified workspace**.

What makes Kraivor different:

- **Deep, structural code analysis** — not just linting, but a full Production Readiness Score with prioritized, actionable reports.
- **Multi-agent AI** — specialized agents for architecture review, security auditing, performance profiling, and code generation that share context and collaborate.
- **Built for scale from day one** — async-first microservices, event-driven architecture, and full observability out of the box. No "we'll fix it in production."

Whether you're a solo developer looking to level up your code quality or a platform team standardizing engineering practices across 100+ repos, Kraivor gives you the intelligence layer your workflow has been missing.

---

## ⚡ What is Kraivor?

Engineering teams today juggle too many disconnected tools — repo analysis in one tab, AI copilots in another, project boards somewhere else, docs scattered across a wiki. **Kraivor collapses all of that into one authenticated workspace.**

It combines three pillars into a single product:

<table>
<tr>
<td width="33%" valign="top">

### 🔍 Repository Analyzer
Deep structural analysis — not linting. Full **Production Readiness Scores** with prioritized, actionable remediation reports.

</td>
<td width="33%" valign="top">

### 🤖 Agentic AI System
Specialized agents — architecture, security, performance, codegen — sharing context via a RAG pipeline, collaborating on your actual codebase.

</td>
<td width="33%" valign="top">

### 📋 Productivity Platform
Notes, projects, Kanban boards, and real-time collaboration — all enriched with live AI context pulled from your repos.

</td>
</tr>
</table>

---

## 🌍 Mission & Vision

### The Vision

Kraivor isn't building another dev tool. It's building the **unified operating system for developer intelligence** — the layer that sits between your code and your team, remembering everything so nobody has to.

Every context switch — tab to tab, tool to tool, Slack thread to stale wiki page — is time your team isn't shipping. Kraivor's vision is a world where a codebase has **infinite memory**: every architectural decision, every security finding, every performance regression, and every conversation about *why* the code looks the way it does, all queryable in one place, forever.

We believe the next generation of engineering orgs won't be defined by how many tools they've integrated — they'll be defined by how little context they lose.

### The Mission

Our mission is **engineering resilience, democratized**:

- 🧪 **Production-grade simulation for everyone** — not just teams with a dedicated platform org. A solo developer should get the same structural rigor as a 200-person engineering team.
- 🤝 **Multi-agent collaboration as a default, not a luxury** — AI agents that specialize, share context, and hand off work the way a real team does.
- 🏗️ **Structural analysis that scales with you** — from a single repo to a 100+ service monorepo sprawl, without losing signal in the noise.

Kraivor exists so that code quality, security posture, and architectural health stop being things you *hope* are fine, and start being things you *know* are fine.

---

## Features

| Area | Description |
|------|-------------|
| **Repository Analyzer** | Deep structural analysis of any codebase. Generates actionable Production Readiness Scores with prioritized remediation reports across security, performance, maintainability, and architecture. |
| **Agentic AI System** | A multi-agent AI workspace where specialized agents (architecture, security, performance, code gen) collaborate on your codebase with full context awareness and a RAG pipeline. |
| **Developer Productivity Platform** | Unified workspace for notes, projects, and tasks — enhanced with AI context from your repositories. Drag-and-drop project boards, real-time collaboration, and rich markdown editing. |
| **Real-Time Collaboration** | WebSocket-powered live updates, chat, presence indicators, and collaborative editing so your team stays in sync without leaving the platform. |
| **Production-Grade Infrastructure** | Async-first design, event-driven communication via Kafka, full observability with correlation IDs and structured logging, and graceful degradation across all services. |

---


Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for more information.

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/nkswalih">Mohammed Swalih N K</a> and the Kraivor community.</sub>
</p>
