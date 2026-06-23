# Build‑Accelerator PRD  

**Document Owner:** Senior Product/Engineering Lead  
**Date:** 2026‑06‑23  
**Repository:** `build-accelerator` (simple JavaScript/TypeScript compiler)  
**Status:** Draft → Review → Approved → Development  

---  

## 1. Problem Statement  

Modern JavaScript/TypeScript projects increasingly rely on heavyweight toolchains (Babel, Webpack, esbuild, tsc) that add significant install time, configuration overhead, and runtime bloat. Small‑to‑medium teams, internal tooling groups, and CI pipelines often need a **fast, zero‑config compiler** that can:

* Convert modern JS/TS (ES2023+, JSX, TS) to clean ES5/ES6 output.  
* Run deterministically in CI/CD with sub‑second startup.  
* Provide accurate source‑maps and type‑checking without pulling in a full Node ecosystem.  

Current solutions either:

| Solution | Startup Cost | Config Overhead | Bundle Size | Type‑checking |
|----------|--------------|----------------|-------------|---------------|
| Babel + preset-env | High (npm install, .babelrc) | Medium | Large | No |
| tsc (TypeScript) | Medium (npm install) | Low (tsconfig) | Large | Yes |
| esbuild | Low | Low | Small | Partial |
| **Build‑Accelerator** (prototype) | **Very Low** | **Zero** | **Tiny** | **Full** |

The market gap is a **single‑binary, drop‑in compiler** that delivers full TypeScript type safety, modern syntax support, and production‑ready output with **<200 ms cold start** and **no external dependencies**.

---  

## 2. Target Users  

| Persona | Pain Points | Value Proposition |
|---------|-------------|-------------------|
| **Frontend Engineer (SMB)** | Long `npm install` times, config drift across projects | One‑click compile, consistent output |
| **CI/CD Engineer** | Slow build steps, flaky environment setup | Deterministic binary, cache‑friendly |
| **Internal Tooling Team** | Need to compile small scripts quickly, avoid pulling full Node toolchain | Tiny binary, embeddable as a library |
| **Open‑source Library Maintainer** | Want to ship pre‑compiled JS without bundling heavy dev deps | Provide pre‑built artifacts, reduce package size |

---  

## 3. Goals & Success Metrics  

| Goal | Metric | Target (12 weeks) |
|------|--------|-------------------|
| **Performance** | Cold‑start latency (binary exec) | ≤ 150 ms for a 10 k LOC project |
| **Correctness** | Type‑checking pass rate vs. `tsc` | ≥ 99.5 % parity |
| **Adoption** | Number of npm installs (first month) | 1 k installs |
| **Developer Experience** | Avg. time to first successful compile (new repo) | ≤ 30 seconds |
| **Footprint** | Binary size (Linux x86_64) | ≤ 8 MB (compressed) |
| **Reliability** | CI build failure rate due to compiler | < 0.5 % |

---  

## 4. Scope  

### 4.1 In‑Scope (Must‑Have)  

1. **Core Compiler Engine**  
   * Parse JavaScript (ES2023+) and TypeScript (including JSX/TSX).  
   * Emit ES5/ES6 JavaScript with source‑maps.  
   * Full TypeScript type‑checking (leveraging the official `typescript` type checker library).  

2. **Zero‑Config CLI**  
   * `build-accelerator [input-dir] -o [output-dir]`  
   * Auto‑detect `tsconfig.json` if present; otherwise use sensible defaults.  

3. **Binary Distribution**  
   * Pre‑compiled static binaries for Linux, macOS, Windows (x86_64 & arm64).  
   * Single‑file installer via GitHub Releases.  

4. **CI Integration**  
   * Exit codes compatible with existing CI pipelines.  
   * Optional `--watch` mode for local development.  

5. **Documentation & Samples**  
   * README with quick‑start, configuration guide, and benchmark results.  
   * Example repo demonstrating migration from `tsc`/`babel`.  

### 4.2 Out‑of‑Scope (Will Not Be Delivered in this Release)  

| Feature | Reason |
|---------|--------|
| **Bundling / Tree‑shaking** | Handled by downstream bundlers (esbuild, rollup). |
| **Custom Plugin System** | Planned for v2 after core stability. |
| **WebAssembly target** | Future roadmap, not needed for initial market. |
| **IDE language server** | Separate product (Axentx‑LS). |
| **Hot‑module replacement** | Outside compiler’s responsibility. |

---  

## 5. Key Features (Prioritized)  

| Priority | Feature | Description | Acceptance Criteria |
|----------|---------|-------------|---------------------|
| **P1** | **Fast Parsing & Emission** | Use `swc`‑style lexer + `vLLM`‑backed codegen for sub‑ms parsing. | • Parse 10 k LOC in ≤ 30 ms.<br>• Emit identical output to `tsc` (ignoring comments). |
| **P1** | **Full TypeScript Type‑Checking** | Embed the official `typescript` compiler API; run in‑process without external `tsc`. | • All type errors reported match `tsc` output.<br>• No false‑positives on 100+ open‑source projects. |
| **P2** | **Zero‑Config CLI** | Auto‑detect entry points, output directory, and tsconfig defaults. | • `build-accelerator ./src` works out‑of‑the‑box.<br>• `--help` displays all flags. |
| **P2** | **Static Binary Packaging** | Build with `musl` + `upx` to produce <8 MB compressed binaries. | • Release assets pass checksum verification.<br>• Binary runs on clean Docker `alpine` image. |
| **P3** | **Source‑Map Generation** | Emit accurate `.map` files for debugging. | • `source-map` aligns with original TS line numbers in Chrome DevTools. |
| **P3** | **Watch Mode** | Incremental recompilation on file changes (optional). | • `--watch` rebuilds changed files < 100 ms. |
| **P4** | **Benchmark Dashboard** | Auto‑generated HTML benchmark comparing to `tsc`/`esbuild`. | • Dashboard included in release notes. |

---  

## 6. User Stories  

1. **As a frontend engineer**, I want to run `build-accelerator src -o dist` and get a compiled bundle instantly, so I can iterate faster without configuring Babel.  
2. **As a CI engineer**, I need a deterministic compiler binary that I can cache in Docker layers, so my pipeline builds complete in under 2 minutes.  
3. **As an internal tooling team lead**, I want to embed the compiler as a library (`require('build-accelerator')`) to compile user‑provided scripts safely, so I avoid pulling the whole TypeScript package.  

---  

## 7. Technical Approach  

1. **Language & Runtime**  
   * Implement core in **Rust** for safety and performance.  
   * Leverage `swc` crates for parsing, `serde_json` for config handling.  

2. **Type‑Checking**  
   * Bind to the official `typescript` npm package via **Node‑FFI** (embedding a minimal Node runtime) or use the `deno` TypeScript compiler as a library. Evaluate both for binary size.  

3. **Code Generation**  
   * Reuse `swc_ecma_codegen` with custom passes to match `tsc` output semantics (e.g., down‑leveling async/await).  

4. **Packaging**  
   * Use `cross` + `musl` to produce static binaries.  
   * Compress with `upx` and sign releases.  

5. **Testing**  
   * Regression suite: 200 open‑source projects (React, Vue, Node libs).  
   * Property‑based tests for AST round‑trip.  

---  

## 8. Milestones & Timeline  

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1‑2 | Project Kickoff & Architecture | Design docs, repo scaffold |
| 3‑4 | Parser & Codegen MVP | Binary that parses & emits ES5 |
| 5‑6 | Type‑Checking Integration | Passes all `tsc` type tests |
| 7 | CLI & Zero‑Config | Full command‑line interface |
| 8 | Binary Packaging & CI pipelines | Release assets for Linux/macOS |
| 9 | Source‑Map & Watch Mode | Feature complete |
| 10 | Benchmark Dashboard & Docs | HTML report, updated README |
| 11‑12 | Beta Release, Feedback Loop, Final QA | Public GitHub release, success metric tracking |

---  

## 9. Risks & Mitigations  

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Embedding TypeScript** may inflate binary size > 8 MB | Release fails performance goal | Evaluate Deno’s TS compiler (smaller) or compile only type‑checker portion. |
| **Parsing edge‑cases** (decorators, experimental syntax) | Incorrect output → user distrust | Adopt `swc`’s latest parser and maintain a compatibility matrix. |
| **Cross‑platform binary issues** (Windows vs. Linux) | Adoption barrier | Use CI matrix to build/test on all target OSes each commit. |
| **License compliance** (using `typescript` under Apache‑2.0) | Legal risk | Verify compatibility with our MIT‑compatible distribution policy. |

---  

## 10. Success Evaluation  

At the end of the 12‑week cycle, we will evaluate:

1. **Quantitative**: All success metrics met or exceeded.  
2. **Qualitative**: Positive feedback from at least 5 beta users (internal & external).  
3. **Business**: Demonstrated market interest via GitHub stars (>500) and npm install trend.  

If any metric falls short, we will iterate on the offending feature (e.g., binary size) before moving to v2 (plugin system, bundling).  

---  

## 11. Appendices  

### A. Benchmark Baseline (Current `tsc`)  

| Project | Lines of Code | `tsc` compile time | Binary size (tsc) |
|---------|---------------|--------------------|-------------------|
| React App | 12 k | 2.8 s | 45 MB (node_modules) |
| Node CLI | 8 k | 1.9 s | 38 MB |
| Library (TS) | 5 k | 1.2 s | 30 MB |

*Target for Build‑Accelerator: ≤ 0.3 s compile, ≤ 8 MB binary.*

### B. Glossary  

* **CLI** – Command‑Line Interface  
* **CI** – Continuous Integration  
* **AST** – Abstract Syntax Tree  
* **Source‑Map** – Mapping from generated code back to original source  

---  

*Prepared for review by the Axentx product council. Comments and approvals should be added as GitHub PR reviews.*
