# TECH_SPEC.md  

**Project:** build-accelerator  
**Owner:** Axentx OS – Engineering Lead  
**Last Updated:** 2026‑06‑23  

---  

## 1. Overview  

`build-accelerator` is a fast, extensible compiler that transforms JavaScript and TypeScript source trees into optimized bundles ready for execution in Node.js or browsers. It is designed to be used as a drop‑in replacement for existing build pipelines (e.g., Webpack, esbuild, tsc) while providing:

* **Zero‑config fast path** – automatic detection of entry points, module resolution, and output format.  
* **Pluggable transformation pipeline** – support for custom AST passes, linting, and code‑gen plugins.  
* **Incremental compilation** – file‑level caching and dependency graph tracking to rebuild only changed modules.  
* **Typed‑aware optimizations** – leverages the TypeScript type‑checker to perform dead‑code elimination, constant folding, and safe inlining.  

The compiler is delivered as an npm package (`@axentx/build-accelerator`) and also as a CLI binary (`bacc`).  

---  

## 2. Architecture Overview  

```
+-------------------+      +-------------------+      +-------------------+
|   CLI / API Entryp| ---> |   Front‑End       | ---> |   Core Compiler   |
|   point (bacc)    |      |   (Parser,       |      |   Engine          |
|   (Node.js)       |      |    TypeChecker)  |      |   (Scheduler,    |
+-------------------+      +-------------------+      |    Optimizer,    |
                                                     |    CodeGen)      |
                                                     +-------------------+
                                                             |
                                                             v
                                                   +-------------------+
                                                   |   Plugin System   |
                                                   |   (AST, Emit,     |
                                                   |    Watcher)       |
                                                   +-------------------+
                                                             |
                                                             v
                                                   +-------------------+
                                                   |   Cache Layer     |
                                                   |   (FS + Redis)    |
                                                   +-------------------+
                                                             |
                                                             v
                                                   +-------------------+
                                                   |   Output Writer   |
                                                   |   (ESM, CJS,      |
                                                   |    Bundle, Source |
                                                   |    Maps)          |
                                                   +-------------------+
```

* **CLI / API Entrypoint** – Exposes a `bacc` binary and a programmatic Node.js API (`compile(sourcePath, options)`).  
* **Front‑End** – Parses `.js`, `.jsx`, `.ts`, `.tsx` files using the **SWC** parser (fast Rust‑based) and runs the TypeScript type‑checker via the **typescript** compiler API.  
* **Core Compiler Engine** –  
  * **Scheduler** builds a directed acyclic graph (DAG) of module dependencies.  
  * **Optimizer** runs a configurable series of passes (dead‑code elimination, tree‑shaking, constant folding).  
  * **CodeGen** emits JavaScript (ES2022) or bundled assets using **esbuild** as the low‑level emitter for speed.  
* **Plugin System** – Plugins can register AST transformers, custom emitters, or file watchers. Plugins are discovered via the `bacc.plugins` field in `package.json` or via a `plugins/` directory.  
* **Cache Layer** –  
  * **File‑system cache** stores per‑file hash → compiled artifact.  
  * **Optional Redis cache** (enabled via `--cache-redis`) for distributed CI environments.  
* **Output Writer** – Writes final artifacts (individual files, bundles, source maps) to the `dist/` directory. Supports ESM, CommonJS, and IIFE bundle formats.  

---  

## 3. Components & Responsibilities  

| Component | Language / Runtime | Key Responsibilities | Public Interface |
|-----------|--------------------|----------------------|------------------|
| **CLI (`bacc`)** | Node.js (TS) | Argument parsing, config loading, invoke compiler, report diagnostics | `bacc [options] <entry>` |
| **Programmatic API** | Node.js (TS) | `compile(entryPath, opts)` returns `CompilationResult` | `export function compile(...)` |
| **Parser** | Rust (via SWC) | Fast lexical analysis & AST generation for JS/TS | `parse(source: string): AST` |
| **TypeChecker** | TypeScript compiler API | Resolve types, emit diagnostics, provide type info to optimizer | `check(ast: AST): TypeInfo` |
| **Scheduler** | TS | Build module DAG, detect cycles, schedule incremental builds | `schedule(entry: string): BuildPlan` |
| **Optimizer** | TS | Apply transformation passes (configurable) | `optimize(plan: BuildPlan): OptimizedPlan` |
| **CodeGen** | esbuild (Go) wrapped in TS | Emit final JS, source maps, bundle assets | `emit(plan: OptimizedPlan, format: EmitFormat): EmitResult` |
| **Plugin Manager** | TS | Load, validate, and execute plugins in defined lifecycle hooks | `register(plugin: Plugin)` |
| **Cache Manager** | TS + Redis client | Compute file hashes, read/write cached artifacts | `get(key): Artifact | null` |
| **Output Writer** | TS | Persist emitted files, create manifest, clean old builds | `write(result: EmitResult, outDir: string)` |

---  

## 4. Data Model  

### 4.1 Core Types  

```ts
// Unique identifier for a source file
type FileID = string; // e.g., absolute path

// AST node (SWC format)
interface ASTNode {
  type: string;
  start: number;
  end: number;
  children?: ASTNode[];
  // ... additional fields per node type
}

// Type information attached to AST nodes
interface TypeInfo {
  [nodeId: string]: {
    type: string;          // e.g., "string", "Promise<number>"
    isConstant?: boolean; // for constant folding
  };
}

// Module metadata stored in the DAG
interface ModuleMeta {
  id: FileID;
  deps: Set<FileID>;
  hash: string;            // content hash for caching
  lastCompiled: number;   // epoch ms
}

// Build plan produced by Scheduler
interface BuildPlan {
  entry: FileID;
  modules: Map<FileID, ModuleMeta>;
  order: FileID[];         // topological order
}

// Optimized plan after passes
interface OptimizedPlan extends BuildPlan {
  transformedAST: Map<FileID, ASTNode>;
}

// Emit result
interface EmitResult {
  files: Map<string, Uint8Array>; // path → bytes
  sourceMaps: Map<string, Uint8Array>;
  diagnostics: Diagnostic[];
}
```

### 4.2 Cache Keys  

Cache key = `SHA256(content) + compilerVersion + pluginHash`.  

---  

## 5. Key APIs / Interfaces  

### 5.1 Programmatic API  

```ts
export interface CompileOptions {
  outDir?: string;               // default: "./dist"
  format?: "esm" | "cjs" | "iife";
  minify?: boolean;              // default: true
  sourcemap?: boolean;           // default: true
  plugins?: string[];            // plugin package names
  cache?: {
    enabled: boolean;
    redisUrl?: string;
  };
  incremental?: boolean;         // default: true
}

export interface CompilationResult {
  success: boolean;
  emittedFiles: string[];        // relative to outDir
  diagnostics: Diagnostic[];
}

export function compile(entry: string, opts?: CompileOptions): Promise<CompilationResult>;
```

### 5.2 CLI Options  

| Flag | Alias | Description |
|------|-------|-------------|
| `--out-dir` | `-o` | Output directory (default `dist/`). |
| `--format` | `-f` | Output format: `esm`, `cjs`, `iife`. |
| `--no-minify` | | Disable minification. |
| `--sourcemap` | | Force source‑map generation. |
| `--plugin` | `-p` | Load additional plugin (repeatable). |
| `--cache-redis` | | Redis URL for distributed cache. |
| `--no-incremental` | | Force full rebuild. |
| `--watch` | `-w` | Watch mode – recompile on file changes. |

---  

## 6. Tech Stack  

| Layer | Technology | Version (pinned) |
|-------|------------|------------------|
| Runtime | Node.js | >= 20.0.0 |
| Language | TypeScript | 5.4 |
| Parser | SWC (Rust) | 0.2.45 |
| Type‑checking | TypeScript compiler API | 5.4 |
| Code Generation / Bundling | esbuild (Go) | 0.21.3 |
| Cache (optional) | Redis | 7.x |
| CLI Arg Parsing | yargs | 17.7 |
| Testing | Jest + ts-jest | 29.x |
| Linting | ESLint + @typescript-eslint | 8.x |
| Build & Publish | pnpm workspaces | 9.x |
| CI/CD | GitHub Actions | latest |

---  

## 7. Dependencies  

**Production**

```json
{
  "@swc/core": "^0.2.45",
  "esbuild": "^0.21.3",
  "typescript": "^5.4.0",
  "yargs": "^17.7.2",
  "redis": "^4.6.7"
}
```

**Dev**

```json
{
  "jest": "^29.7.0",
  "ts-jest": "^29.1.1",
  "eslint": "^8.57.0",
  "@typescript-eslint/parser": "^8.0.0",
  "@types/node": "^20.11.0"
}
```

All dependencies are MIT/Apache‑2.0 compatible, matching the company’s licensing policy.

---  

## 8. Deployment & Distribution  

1. **Package Publishing**  
   * Build with `pnpm run build` → produces `dist/` containing compiled JS (CommonJS) and type declarations.  
   * Publish to npm registry under scope `@axentx` using CI token.  

2. **Docker Image (optional for CI)**  

   ```Dockerfile
   FROM node:20-alpine
   WORKDIR /app
   COPY package.json pnpm-lock.yaml ./
   RUN npm i -g pnpm && pnpm i --frozen-lockfile
   COPY . .
   RUN pnpm run build
   ENTRYPOINT ["bacc"]
   ```

   *Image size ≈ 120 MB.*  

3. **CI Integration**  

   * GitHub Action `build-accelerator.yml` runs on push/PR: lint → unit tests → build → npm publish (on `main`).  
   * Cache step uses `actions/cache` for `node_modules` and compiled artifacts.  

---  

## 9. Security & Compliance  

* All third‑party modules are scanned with **Snyk** during CI; any CVE > 7 is blocked.  
* The compiler runs user code in a **sandboxed child_process** with `--no-wasm` and limited memory (max 512 MiB) to mitigate malicious payloads.  
* Output files are signed with an RSA‑2048 key (managed by Axentx secret store) for integrity verification in downstream pipelines.  

---  

## 10. Future Enhancements (Roadmap)  

| Milestone | Feature | ETA |
|-----------|---------|-----|
| v1.1 | WebAssembly backend for ultra‑fast codegen | Q4 2026 |
| v1.2 | Incremental watch mode with HMR for React Native | Q1 2027 |
| v2.0 | Distributed build farm integration (gRPC worker pool) | Q3 2027 |

---  

*Prepared by the Build‑Accelerator Engineering Team – Axentx OS*
