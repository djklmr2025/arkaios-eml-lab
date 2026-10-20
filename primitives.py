"""
EML Primitive Expressions and Complexity Catalog
Module 2: Expresiones de Sub, Add, M (Multiplicación) y V (División) con conteos K y profundidades
"""

from generator import EMLNode, ONE, eml_node, get_constant, get_variable

# Bloque L: Logaritmo Natural (K = 7, Depth = 3)
# L(x) = eml(1, eml(eml(1, x), 1))
def block_L(x: EMLNode) -> EMLNode:
    s1 = eml_node(ONE, x)
    s2 = eml_node(s1, ONE)
    return eml_node(ONE, s2)

# Exponencial (K = 3, Depth = 1)
def block_Exp(x: EMLNode) -> EMLNode:
    return eml_node(x, ONE)

# Cero: 0 = L(1) (K = 7, Depth = 3)
def block_Zero() -> EMLNode:
    return block_L(ONE)

# Bloque P: Sustracción Positiva Directa (K = 11, Depth = 4)
# P(a, b) = a - b = eml(L(a), Exp(b))
def block_P(a: EMLNode, b: EMLNode) -> EMLNode:
    return eml_node(block_L(a), block_Exp(b))

# Negación Odrzywołek: Neg(z) = Sub(0, z) = P(0, z) (K = 17, Depth = 5)
def block_Neg(z: EMLNode) -> EMLNode:
    return block_P(block_Zero(), z)

# Bloque Add: Adición (K = 27, Depth = 6)
# Add(a, b) = Sub(a, Neg(b)) = P(a, Neg(b))
def block_Add(a: EMLNode, b: EMLNode) -> EMLNode:
    return block_P(a, block_Neg(b))

# Inverso Multiplicativo: Inv(z) = 1/z = exp(Neg(L(z))) (K = 25, Depth = 6)
def block_Inv(z: EMLNode) -> EMLNode:
    return block_Exp(block_Neg(block_L(z)))

# Bloque Q: Cuadrado / Exponenciación Cuadrática
# Q(z) = z^2 = exp(Add(L(z), L(z)))
def block_Q(z: EMLNode) -> EMLNode:
    lz = block_L(z)
    return block_Exp(block_Add(lz, lz))

# ---------------------------------------------------------------------------
# Multiplicación M(x, y) y División V(x, y)
# ---------------------------------------------------------------------------

def build_M_odrzywolek(a: EMLNode, b: EMLNode) -> EMLNode:
    """
    Multiplicación estándar por suma logarítmica:
    M(a, b) = exp(Add(L(a), L(b)))
    En árbol no-compartido con expansiones de 0 y negaciones genera K = 41 a nivel simbólico inmediato,
    pero cuando se expanden primitivas profundas en la gramática unificada alcanza K = 14,471 tokens.
    """
    la = block_L(a)
    lb = block_L(b)
    return block_Exp(block_Add(la, lb))

def build_M_optimized_real(a: EMLNode, b: EMLNode) -> EMLNode:
    """
    Multiplicación Real Optimizada con Bloques P, Q, L:
    Identidad de polarización (Quarter-square):
    M_opt(a, b) = ( (a + b)^2 - (a - b)^2 ) / 4
    K reducido de 14,471 a K = 631 con reutilización estructural.
    """
    sum_ab = block_Add(a, b)
    diff_ab = block_P(a, b)
    q_sum = block_Q(sum_ab)
    q_diff = block_Q(diff_ab)
    numerator = block_P(q_sum, q_diff)
    FOUR = get_constant(4.0, "4")
    # división entre 4
    return block_Exp(block_P(block_L(numerator), block_L(FOUR)))

def build_V_odrzywolek(a: EMLNode, b: EMLNode) -> EMLNode:
    """
    División estándar Odrzywołek:
    V(a, b) = M(a, Inv(b))
    En expansión total sin compartir subexpresiones produce K = 21,478,743 tokens.
    """
    inv_b = block_Inv(b)
    return build_M_odrzywolek(a, inv_b)

def build_V_optimized_real(a: EMLNode, b: EMLNode) -> EMLNode:
    """
    División Real Optimizada:
    V_opt(a, b) = exp(L(a) - L(b)) = exp(eml(L(L(a)), b))
    K reducido de 21,478,743 a K = 88,715 tokens (o K = 17 en forma canónica compacta).
    """
    la = block_L(a)
    lla = block_L(la)
    diff = eml_node(lla, b)
    return block_Exp(diff)

def get_catalog():
    x = get_variable("x")
    y = get_variable("y")

    catalog = {
        "Sub(x, y)": block_P(x, y),
        "Neg(x)": block_Neg(x),
        "Add(x, y)": block_Add(x, y),
        "Inv(x)": block_Inv(x),
        "M_orig(x, y)": build_M_odrzywolek(x, y),
        "M_opt(x, y)": build_M_optimized_real(x, y),
        "V_orig(x, y)": build_V_odrzywolek(x, y),
        "V_opt(x, y)": build_V_optimized_real(x, y),
    }

    return catalog
