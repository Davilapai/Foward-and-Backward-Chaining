"""
Ya que se construyó la base de datos utilizando herramientas de inteligencia artificial (Claude Sonnet 5.5)
hemos decidido construir una forma de verificar las 3 restricciones logicas que se estipulan en el proyecto
"""
import json
from collections import defaultdict # El default dict es dios, como el de cpp

ruta = "base_conocimiento.json"
reglas = json.load(open(ruta, encoding="utf-8"))["reglas"]
errores = []

# Cantidad y unicidad de las reglas, verificamos q no sea la misma regla con antecedentes en desorden
firmas = {(frozenset(r["antecedentes"]), r["consecuente"]) for r in reglas}

if len(firmas) < 50: 
    errores.append(f"Solo {len(firmas)} reglas distintas (min 50)")

ids = [r["id"] for r in reglas]

if len(ids) != len(set(ids)): 
    errores.append("IDs repetidos")

# Restriccion de horn
for r in reglas:
    if not isinstance(r["consecuente"], str): 
        errores.append(f"{r['id']}: consecuente no es unico") # un unico consecuente

    if not r["antecedentes"] or len(r["antecedentes"]) != len(set(r["antecedentes"])):
        errores.append(f"{r['id']}: antecedentes vacios o duplicados") # antecedentes unicos y no vaciso

    if r["consecuente"] in r["antecedentes"]: 
        errores.append(f"{r['id']}: se autoreferencia")

consecuentes = {r["consecuente"] for r in reglas}
antecedentes = {a for r in reglas for a in r["antecedentes"]}
base = antecedentes - consecuentes            # sintomas/hechos base
finales = consecuentes - antecedentes         # diagnosticos/alertas terminales

# Aciclicidad, q no tenga ciclos JAJAJA
grafo = defaultdict(set)

for r in reglas:
    for a in r["antecedentes"]: grafo[a].add(r["consecuente"])

color = {}

def dfs(n, pila):
    color[n] = 1
    
    for m in grafo[n]:
        if color.get(m) == 1: 
            errores.append("Ciclo: " + " -> ".join(pila + [n, m]))
            continue
        
        if m not in color: 
            dfs(m, pila + [n])
    
    color[n] = 2

for n in list(grafo):
    if n not in color: dfs(n, [])

# Alcanzabilidad, q no haya islas sin conexion
mem = set(base)
disparadas = set()
cambio = True

while cambio:
    cambio = False
    for r in reglas:
        if r["id"] not in disparadas and set(r["antecedentes"]) <= mem:
            disparadas.add(r["id"]); mem.add(r["consecuente"])
            cambio = True

for r in reglas:
    if r["id"] not in disparadas: 
        errores.append(f"{r['id']}: regla inalcanzable")

# Profundidad de los hechos, se nos pedia 4 niveles
dmin, dmax = {b: 0 for b in base}, {b: 0 for b in base}
cambio = True

while cambio:
    cambio = False
    for r in reglas:
        if all(a in dmin for a in r["antecedentes"]):
            lo = 1 + max(dmin[a] for a in r["antecedentes"])
            hi = 1 + max(dmax[a] for a in r["antecedentes"])
            c = r["consecuente"]
            nlo = lo if c not in dmin else min(dmin[c], lo)
            nhi = hi if c not in dmax else max(dmax[c], hi)
            
            if dmin.get(c) != nlo or dmax.get(c) != nhi:
                dmin[c], dmax[c] = nlo, nhi; cambio = True

for f in sorted(finales):
    if dmin[f] < 4: 
        errores.append(f"Final '{f}' con profundidad minima {dmin[f]} (<4)")

niveles_declarados = {r["nivel"] for r in reglas}
for r in reglas:
    nivel_calculado = dmin.get(r["consecuente"])
    if nivel_calculado is not None and r["nivel"] != nivel_calculado:
        errores.append(
            f"{r['id']}: nivel declarado {r['nivel']} "
            f"pero nivel calculado {nivel_calculado}"
        )

niveles_logicos = sorted({0, *dmin.values()})
total_niveles = max(niveles_logicos, default=0)
if niveles_declarados != set(range(1, total_niveles + 1)):
    errores.append(
        "Niveles declarados inconsistentes: "
        f"{sorted(niveles_declarados)} (esperados del 1 al {total_niveles})"
    )

print(f"Reglas: {len(reglas)} | Hechos base: {len(base)} | Intermedios: {len(consecuentes & antecedentes)} | Finales: {len(finales)}")
print(
    f"Niveles lógicos de reglas: {total_niveles} "
    f"(reglas del 1 al {total_niveles}; hechos base en nivel 0)"
)
print("Profundidad de finales (min/max):")

for f in sorted(finales): 
    print(f"  {f:38s} {dmin[f]}/{dmax[f]}")

print("\nRESULTADO:", "KB VALIDA" if not errores else "ERRORES"); [print(" -", e) for e in errores]