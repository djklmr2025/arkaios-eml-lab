/**
 * EML Node.js Multi-Representation Benchmark
 * Verified across Tree (AST), DAG (Memoized), and Algebraic Reference.
 */

class EmlCounter {
  constructor() {
    this.exp = 0;
    this.ln = 0;
  }
}

class ConstNode {
  constructor(val, name) {
    this.val = Number(val);
    this.name = name || String(val);
    this.key = `C(${this.name})`;
  }
  size() { return 1; }
  depth() { return 0; }
  collect(set) { set.add(this.key); }
  evalTree(env, counter) { return this.val; }
  evalDag(env, memo, counter) { return this.val; }
}

class VarNode {
  constructor(name) {
    this.name = name;
    this.key = `V(${name})`;
  }
  size() { return 1; }
  depth() { return 0; }
  collect(set) { set.add(this.key); }
  evalTree(env, counter) { return env[this.name]; }
  evalDag(env, memo, counter) { return env[this.name]; }
}

class EmlNode {
  constructor(left, right) {
    this.left = left;
    this.right = right;
    this.key = `E(${left.key},${right.key})`;
  }
  size() { return 1 + this.left.size() + this.right.size(); }
  depth() { return 1 + Math.max(this.left.depth(), this.right.depth()); }
  collect(set) {
    if (!set.has(this.key)) {
      set.add(this.key);
      this.left.collect(set);
      this.right.collect(set);
    }
  }
  _op(l, r, counter, mode) {
    counter.exp++;
    counter.ln++;
    if (mode === "stabilized") {
      const lClamped = Math.max(-20, Math.min(20, l));
      const rFloored = Math.max(1e-300, r);
      return Math.exp(lClamped) - Math.log(rFloored);
    }
    // IEEE 754 float64
    let expL = l === -Infinity ? 0 : Math.exp(l);
    let lnR = r === 0 ? -Infinity : Math.log(r);
    return expL - lnR;
  }
  evalTree(env, counter, mode = "float64") {
    const l = this.left.evalTree(env, counter, mode);
    const r = this.right.evalTree(env, counter, mode);
    return this._op(l, r, counter, mode);
  }
  evalDag(env, memo, counter, mode = "float64") {
    if (this.key in memo) return memo[this.key];
    const l = this.left.evalDag(env, memo, counter, mode);
    const r = this.right.evalDag(env, memo, counter, mode);
    const val = this._op(l, r, counter, mode);
    memo[this.key] = val;
    return val;
  }
}

const ONE = new ConstNode(1.0, "1");
const eml = (a, b) => new EmlNode(a, b);
const emlExp = (z) => eml(z, ONE);
const emlLog = (z) => eml(ONE, emlExp(eml(ONE, z)));
const emlSub = (a, b) => eml(emlLog(a), emlExp(b));
const emlDivOpt = (a, b) => emlExp(eml(emlLog(emlLog(a)), b));
const emlSinhOpt = (z) => {
  const ez = emlExp(z);
  const invEz = emlDivOpt(ONE, ez);
  const num = eml(z, emlExp(invEz));
  return emlDivOpt(num, new ConstNode(2.0, "2"));
};

function runNodeSuite() {
  const x = new VarNode("x");
  const y = new VarNode("y");

  const tests = [
    { name: "exp(x)", node: emlExp(x), env: { x: 2.0 }, ref: (env) => Math.exp(env.x) },
    { name: "ln(x)", node: emlLog(x), env: { x: 2.0 }, ref: (env) => Math.log(env.x) },
    { name: "sub(x, y)", node: emlSub(x, y), env: { x: 5.0, y: 2.0 }, ref: (env) => env.x - env.y },
    { name: "div_opt(x, y)", node: emlDivOpt(x, y), env: { x: 8.0, y: 2.0 }, ref: (env) => env.x / env.y },
    { name: "sinh_opt(x)", node: emlSinhOpt(x), env: { x: 1.5 }, ref: (env) => Math.sinh(env.x) },
  ];

  console.log("=== Node.js EML Multi-Representation Benchmark ===");
  tests.forEach((t) => {
    const symbols = t.node.size();
    const set = new Set();
    t.node.collect(set);
    const dagNodes = set.size;

    const cTree = new EmlCounter();
    const valTree = t.node.evalTree(t.env, cTree);

    const cDag = new EmlCounter();
    const valDag = t.node.evalDag(t.env, {}, cDag);

    const ref = t.ref(t.env);
    const err = Math.abs(valTree - ref) / Math.max(1e-15, Math.abs(ref));

    console.log(`${t.name.padEnd(16)} | Symb: ${String(symbols).padEnd(4)} | DAG: ${String(dagNodes).padEnd(4)} | TreeOps: ${String(cTree.exp).padEnd(4)} | DAGOps: ${String(cDag.exp).padEnd(4)} | RelErr: ${err.toExponential(2)}`);
  });
}

runNodeSuite();
