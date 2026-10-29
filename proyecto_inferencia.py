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
        self.traza_explicacion = []

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
    # PARTE 2: MOTORES DE INFERENCIA
    # ==========================================================
    def ejecutar_inferencia(self, hechos_iniciales, objetivo):
        """
        Motor de Encadenamiento hacia Adelante
        """
        self.memoria_trabajo = set(hechos_iniciales)
        self.traza_explicacion = []  

        if objetivo in self.memoria_trabajo:
            self.traza_explicacion.append(f"El objetivo '{objetivo}' ya se encuentra en los hechos iniciales.")
            print("Es consecuencia logica!!")
            print(self.traza_explicacion[0])
            return True

        hubo_cambios = True
        while hubo_cambios:
            hubo_cambios = False
            for regla in self.reglas:
                if (regla.consecuente not in self.memoria_trabajo
                        and regla.antecedentes <= self.memoria_trabajo):
                    self.memoria_trabajo.add(regla.consecuente)
                    self.traza_explicacion.append(f"Paso {len(self.traza_explicacion) + 1}: {regla}")
                    hubo_cambios = True
                    if objetivo in self.memoria_trabajo:
                        print("Es consecuencia logica!!")
                        print("Reglas utilizadas: ")
                        print(*self.traza_explicacion, sep='\n')
                        return True
        print("No es consecuencia logica...")
        if self.traza_explicacion:
            print("Hechos derivados antes de fallar:")
            print(*self.traza_explicacion, sep='\n')
        return False

    def exportar_traza(self, ruta="traza_explicacion.txt"):
        """Exporta la traza de explicación a un archivo de texto."""
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.traza_explicacion) + '\n')

    def ejecutar_inferencia_atras(self, hechos_iniciales, objetivo):
        """
        Motor de Encadenamiento hacia Atrás (Backward Chaining).
        """
        memoria = set(hechos_iniciales)
        self.traza_explicacion = []
        if objetivo in memoria:
            self.traza_explicacion.append(f"El objetivo '{objetivo}' ya se encuentra en los hechos iniciales.")
            print("Puede ser demostrado!!")
            print(self.traza_explicacion[0])
            return True
        
        historial = []
        visitados = set()
        res = self.rec_inferencia_atras(memoria, objetivo, historial, visitados, 0)
        if res:
            self.traza_explicacion = [f"Paso {i}: {r}" for i, r in enumerate(historial, 1)]
            print("Puede ser demostrado!!")
            print("Reglas utilizadas: ")
            print(*self.traza_explicacion, sep='\n')
        else:
            print("No puede ser demostrado")
        return res

    def rec_inferencia_atras(self, memoria, obj, historial, visitados, prof):
        if obj in memoria:
            return True
        if obj in visitados or prof > 10:
            return False

        visitados.add(obj)
        reglas_utiles = [i for i in self.reglas if i.consecuente == obj]
        for r in reglas_utiles:
            resultado = True
            historial_rama = []
            memoria_rama = memoria.copy()
            for a in r.antecedentes:
                if self.rec_inferencia_atras(memoria_rama, a, historial_rama, visitados, prof + 1):
                    memoria_rama.add(a) 
                else:
                    resultado = False
                    break
            if resultado:
                memoria.update(memoria_rama)
                historial.extend(historial_rama)
                historial.append(r) 
                return True
        visitados.remove(obj)
        return False

if __name__ == "__main__":
    # 1. Inicializar el motor con el archivo de reglas
    motor = MotorInferencia("base_conocimiento.json")

    # 2. Definir los 4 casos clínicos ordenados del 1 al 4
    casos_de_prueba = [
        {
            "nombre": "Caso Clínico 1: Síndrome Respiratorio Alto",
            "sintomas": ["Fiebre", "Tos", "Dolor_Garganta", "Congestion_Nasal"],
            "objetivo": "Sindrome_Respiratorio_Alto"
        },
        {
            "nombre": "Caso Clínico 2: Neumonía (Nivel 3)",
            "sintomas": ["Fiebre", "Tos", "Esputo", "Dolor_Toracico"],
            "objetivo": "Neumonia"
        },
        {
            "nombre": "Caso Clínico 3: Neumonía Grave (Nivel 4)",
            "sintomas": ["Fiebre", "Tos", "Esputo", "Dolor_Toracico", "Dificultad_Respiratoria", "Saturacion_Baja"],
            "objetivo": "Neumonia_Grave"
        },
        {
            "nombre": "Caso Clínico 4: Alerta de Falla Respiratoria Extrema (Nivel 5)",
            "sintomas": ["Fiebre", "Tos", "Esputo", "Dolor_Toracico", "Dificultad_Respiratoria", "Saturacion_Baja", "Cianosis"],
            "objetivo": "Alerta_Falla_Respiratoria"
        },
        {
            "nombre": "Caso Clínico 5:  Fallo en detectar Alerta de Falla Respiratoria Extrema (Nivel 5)",
            "sintomas": ["Fiebre", "Tos", "Dolor_Toracico", "Dificultad_Respiratoria", "Saturacion_Baja", "Cianosis"],
            "objetivo": "Alerta_Falla_Respiratoria"
        }
    ]

    # 3. Ejecutar los casos automáticamente y exportar trazas
    for i, caso in enumerate(casos_de_prueba, 1):
        print(f"\n==============================================")
        print(f"PROBANDO: {caso['nombre']}")
        print(f"==============================================")
        print(f"Síntomas iniciales (Δ): {caso['sintomas']}")
        print(f"Objetivo a verificar (α): {caso['objetivo']}\n")

        # Motor hacia adelante
        print("--- Motor Hacia Adelante ---")
        resultado_adelante = motor.ejecutar_inferencia(caso['sintomas'], caso['objetivo'])
        print(f"¿Es consecuencia lógica?: {resultado_adelante}")
        motor.exportar_traza(f"adelante_traza_caso_{i}.txt")
        
        # Motor hacia atrás
        print("\n--- Motor Hacia Atrás ---")
        resultado_atras = motor.ejecutar_inferencia_atras(caso['sintomas'], caso['objetivo'])
        print(f"¿Es demostrable?: {resultado_atras}")
        motor.exportar_traza(f"atras_traza_caso_{i}.txt")
