# ARKAIOS Relational Core + GLYPH Specification (v0.1.0)

**Project:** ARKAIOS–EML Experimental Laboratory  
**Status:** Experimental Controlled Implementation  
**Standard:** ARKAIOS Governance & Mathematical Integrity Framework  

---

## 1. Mathematical Foundation: The EML Primitive

The system is founded on the continuous two-argument elementary operator:
$$E(a, b) = e^a - \ln(b)$$
with domain:
$$a \in \mathbb{R}, \quad b > 0$$

All arithmetic and algebraic operations are derived strictly through compositions of $E(a, b)$:
- **Logarithm:** $L(x) = E(0, E(x, 1)) = \ln(x)$
- **Exponential:** $\text{Exp}(x) = E(x, 1) = e^x$
- **Subtraction:** $\text{Sub}(a, b) = E(L(a), \text{Exp}(b)) = a - b$
- **Negation:** $\text{Neg}(z) = \text{Sub}(0, z) = -z$
- **Addition:** $\text{Add}(a, b) = \text{Sub}(a, \text{Neg}(b)) = a + b$

---

## 2. ARKAIOS Relational Core Architecture

The Relational Core implements five distinct processing and semantic capabilities:

1. **`COMBINE`**: Aggregates independent inputs (e.g., addition, multivariable union).
2. **`REINFORCE`**: Amplifies compatible contributions (constructive interference or scaling).
3. **`CANCEL`**: Resolves opposing contributions into a null result without destroying inputs.
4. **`TRANSFORM`**: Maps symbolic and algebraic expressions according to verified transformation rules.
5. **`TRACE`**: Queries immutable provenance and reconstructs complete causal lineages.

### Mandatory Invariant: Non-Destruction of Cancelled Inputs
A null result does **not** imply physical or computational deletion of inputs:
$$\text{combine}([5, -5]) \to 0$$
Generates the record:
```json
{
  "inputs": [5, -5],
  "operation": "ADD",
  "result": 0,
  "relation": "CANCELLATION",
  "is_null": true
}
```
All inputs and causal parent hashes remain intact in the provenance store.

---

## 3. Five-Signal Convergent Model

A central hub coordinates five independent complex signal inputs:
$$z_k(u) = A_k \cdot e^{i (\omega_k \cdot u + \phi_k)}, \quad k \in \{0, 1, 2, 3, 4\}$$
with central sum:
$$S(u) = \sum_{k=0}^4 z_k(u)$$

### Verified Test Cases:
- **Case A (Reinforcement):** $A_k = 1, \omega_k = \omega_0, \phi_k = \phi_0 \implies |S(u)| = 5.0$.
- **Case B (Cancellation):** $A_k = 1, \omega_k = \omega_0, \phi_k = \frac{2\pi k}{5} \implies |S(u)| \approx 0$ ($< 10^{-14}$).
- **Case C (General Composition):** Heterogeneous $A_k, \omega_k, \phi_k$ validated against reference Euler sum.
- **Case D (Traceability):** Even when $|S(u)| = 0$, all 5 individual components and their exact parameters are preserved.
- **Case E (Return Mapping):** Reconstructing 5 inputs from 1 central scalar is an underdetermined, lossy projection unless component parameter dictionaries are preserved in provenance.

---

## 4. ARKAIOS-GLYPH Intermediate Representation (IR)

GLYPH models symbolic and operational pipelines as typed, cycle-free Directed Acyclic Graphs (DAGs).

### Node Types:
- `CONSTANT`: Real or complex scalar constant.
- `VARIABLE`: Named input parameter.
- `EML`: Binary continuous operator $E(a, b)$.
- `COMBINE`: Aggregation node.
- `TRANSFORM`: Rule-applied mutation.
- `SIGNAL`: Parameterized waveform emitter.
- `RESULT`: Sunk evaluation output.
- `PROVENANCE`: Causal marker.

### Strict Decoupling:
- **Visual Representation:** Glyphs, shapes, and SVG geometry are strictly non-semantic visual projections.
- **Symbolic Structure:** DAG topology and operator nodes.
- **Mathematical Semantics:** Continuous evaluation rules and domain boundary checks.
- **Provenance:** SHA-256 Merkle-like causal lineage.

---

## 5. Symbolic Optimizer

The `GlyphOptimizer` applies verified rewrite rules:
- **`CONSTANT_FOLDING`:** EML subtrees with constant inputs are evaluated at compile time.
- **`EML_ONE_REDUCTION`:** $E(x, 1) = e^x - \ln(1) = e^x$, saving log calls.
- **Dead Code Elimination (DCE):** Unreachable orphan nodes are pruned from the optimized root.
- **Preservation Guarantee:** The original graph is always preserved alongside the optimized graph for auditability.
