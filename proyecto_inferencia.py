import json

# ==========================================================
# PARTE 1: ESTRUCTURA DE DATOS (NO MODIFICAR)
# ==========================================================
class Regla:
    def __init__(self, id_regla, antecedentes, consecuente):
        self.id_regla = id_regla
        self.antecedentes = set(antecedentes)  
        self.consecuente = consecuente

    def __str__(self):
        return f"{self.id_regla}: {' AND '.join(self.antecedentes)} -> {self.consecuente}"

class MotorInferencia:
    def __init__(self, ruta_kb):
        self.reglas = self.cargar_kb(ruta_kb)
        self.memoria_trabajo = set()
        self.traza_explicacion = [] # Sugerencia para almacenar el orden de las reglas activadas

    def cargar_kb(self, ruta):
        """Carga las reglas desde un archivo JSON."""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            return [Regla(r.get('id'), r['antecedentes'], r['consecuente']) for r in datos['reglas']]
        except Exception as e:
            print(f"Error al cargar la Base de Conocimiento: {e}")
            return []

    # ==========================================================
    # PARTE 2: MOTORES DE INFERENCIA (A DESARROLLAR)
    # ==========================================================
    def ejecutar_inferencia(self, hechos_iniciales, objetivo):
        """
        Motor de Encadenamiento hacia Adelante (Forward Chaining).
        Retorna True si el objetivo es consecuencia lógica de los hechos
        iniciales y la KB, False en caso contrario.

        Algoritmo de punto fijo:
          1. La memoria de trabajo arranca con los hechos iniciales.
          2. Se recorren las reglas; una regla se dispara solo si TODOS sus
             antecedentes están en memoria y su consecuente aún NO está.
          3. Cada disparo agrega el consecuente a memoria y se registra en
             la traza (orden cronológico).
          4. Se repite hasta que (a) el objetivo aparece en memoria -> True,
             o (b) una pasada completa no agrega nada (punto fijo) -> False.

        Terminación: cada disparo agrega un hecho nuevo y el conjunto de
        consecuentes posibles es finito, así que el ciclo termina siempre,
        incluso si la KB tuviera ciclos.
        """
        self.memoria_trabajo = set(hechos_iniciales)
        self.traza_explicacion = []  # se reinicia en cada ejecución

        # Caso trivial: el objetivo ya es un hecho inicial (cero disparos).
        if objetivo in self.memoria_trabajo:
            return True

        hubo_cambios = True
        while hubo_cambios:  # una iteración = una pasada completa por la KB
            hubo_cambios = False
            for regla in self.reglas:
                # Disparar solo si el consecuente es nuevo y se cumplen
                # todos los antecedentes (subconjunto de la memoria).
                if (regla.consecuente not in self.memoria_trabajo
                        and regla.antecedentes <= self.memoria_trabajo):
                    self.memoria_trabajo.add(regla.consecuente)
                    self.traza_explicacion.append({
                        "paso": len(self.traza_explicacion) + 1,
                        "id": regla.id_regla,
                        "antecedentes": sorted(regla.antecedentes),
                        "consecuente": regla.consecuente,
                    })
                    hubo_cambios = True
                    # Detenerse apenas se alcance el objetivo.
                    if objetivo in self.memoria_trabajo:
                        return True

        # Punto fijo alcanzado sin llegar al objetivo.
        return False

    # ----------------------------------------------------------
    # Traza de explicación (motor hacia adelante)
    # ----------------------------------------------------------
    def traza_a_texto(self):
        """Devuelve la traza como texto legible, un disparo por línea."""
        if not self.traza_explicacion:
            return "(No se disparó ninguna regla)"
        lineas = []
        for t in self.traza_explicacion:
            ants = " AND ".join(t["antecedentes"])
            lineas.append(f"Paso {t['paso']:>2} | {t['id']}: {ants} -> {t['consecuente']}")
        return "\n".join(lineas)

    def imprimir_traza(self):
        """Imprime la traza de la última inferencia hacia adelante."""
        print("Traza de explicación (orden cronológico):")
        print(self.traza_a_texto())

    def exportar_traza(self, ruta):
        """
        Exporta la traza a un archivo.
        Si la ruta termina en .json se guarda como JSON; en otro caso como
        texto plano legible.
        """
        with open(ruta, "w", encoding="utf-8") as f:
            if ruta.lower().endswith(".json"):
                json.dump(self.traza_explicacion, f, ensure_ascii=False, indent=2)
            else:
                f.write(self.traza_a_texto() + "\n")

    def ejecutar_inferencia_atras(self, hechos_iniciales, objetivo):
        """
        Motor de Encadenamiento hacia Atrás (Backward Chaining).
        Debe retornar True si el objetivo puede ser probado, False en caso contrario.
        Debe manejar adecuadamente la recursividad (goal-driven) y los casos base.
        """
        memoria = set(hechos_iniciales)
        if objetivo in memoria:
            return True
        
        historial = []
        res = self.rec_inferencia_atras(memoria, objetivo, historial)
        if res:
            print("Puede ser demostrado!!")
            print("Reglas utilizadas: ")
            print(*[r.id_regla for r in historial], sep=', ')
        else:
            print("No puede ser demostrado")
        return res

    def rec_inferencia_atras(self, memoria, obj, historial):
        if obj in memoria:
            return True

        reglas_utiles = [i for i in self.reglas if i.consecuente == obj]
        for r in reglas_utiles:
            resultado = True
            for a in r.antecedentes:
                if self.rec_inferencia_atras(memoria, a, historial):
                    memoria.add(a) 
                else:
                    resultado = False
                    break
            if resultado:
                historial.append(r) 
                return True
        return False

# ==========================================================
# PARTE 3: EJECUCIÓN (PUEDEN MODIFICAR PARA PRUEBAS)
# ==========================================================
if __name__ == "__main__":
    # 1. Inicializar el motor con el archivo de reglas
    motor = MotorInferencia("base_conocimiento.json")

    # 2. Definir caso clínico de prueba
    sintomas = ["Fiebre", "Tos", "Dolor_Garganta","Congestion_Nasal"] 
    hipotesis = "Sindrome_Respiratorio_Alto"

    print(f"--- Sistema Experto de Diagnóstico ---")
    print(f"Síntomas iniciales: {sintomas}")
    print(f"Objetivo a verificar: {hipotesis}\n")

    # 3. Ejecutar Inferencia hacia Adelante
    print("--- Motor Hacia Adelante ---")
    resultado_adelante = motor.ejecutar_inferencia(sintomas, hipotesis)
    print(f"¿Es consecuencia lógica?: {resultado_adelante}")
    motor.imprimir_traza()
    print()

    # 4. Ejecutar Inferencia hacia Atrás
    print("--- Motor Hacia Atrás ---")
    resultado_atras = motor.ejecutar_inferencia_atras(sintomas, hipotesis)
    print(f"¿Es demostrable?: {resultado_atras}")