"""
Pruebas unitarias del motor hacia adelante (Persona 3).
Ejecutar:  python -m unittest test_motor_adelante -v
Usa una KB de ejemplo de 3 reglas (archivo temporal) y la KB real.
"""
import json
import os
import tempfile
import unittest

from proyecto_inferencia import MotorInferencia

KB_EJEMPLO = {
    "reglas": [
        {"id": "E1", "antecedentes": ["Fiebre", "Tos"], "consecuente": "Infeccion"},
        {"id": "E2", "antecedentes": ["Infeccion", "Dificultad_Respiratoria"], "consecuente": "Neumonia"},
        {"id": "E3", "antecedentes": ["Neumonia", "Saturacion_Baja"], "consecuente": "Alerta_Neumonia_Grave"},
    ]
}

#PROBAR CON python -m unittest test_motor_adelante -v

#python proyecto_inferencia.py

"""
EJEMPLO 7 pasos:
python -c "
>> from proyecto_inferencia import MotorInferencia      
>> m = MotorInferencia('base_conocimiento.json')
>> ok = m.ejecutar_inferencia(['Fiebre','Tos','Esputo','Dolor_Toracico','Dificultad_Respiratoria','Saturacion_Baja','Cianosis'], 'Alerta_Falla_Respiratoria')
>> print(ok)
>> m.imprimir_traza() >> m.exportar_traza('traza_caso1.txt') >> "
"""


def crear_motor(kb):
    fd, ruta = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(kb, f)
    motor = MotorInferencia(ruta)
    os.remove(ruta)
    return motor


class TestKBEjemplo(unittest.TestCase):
    def setUp(self):
        self.m = crear_motor(KB_EJEMPLO)

    def test_cadena_completa(self):
        ok = self.m.ejecutar_inferencia(
            ["Fiebre", "Tos", "Dificultad_Respiratoria", "Saturacion_Baja"],
            "Alerta_Neumonia_Grave")
        self.assertTrue(ok)
        self.assertEqual([t["id"] for t in self.m.traza_explicacion], ["E1", "E2", "E3"])

    def test_objetivo_intermedio_se_detiene(self):
        ok = self.m.ejecutar_inferencia(
            ["Fiebre", "Tos", "Dificultad_Respiratoria", "Saturacion_Baja"], "Neumonia")
        self.assertTrue(ok)
        self.assertEqual([t["id"] for t in self.m.traza_explicacion], ["E1", "E2"])  # E3 no se dispara

    def test_falta_un_antecedente(self):
        self.assertFalse(self.m.ejecutar_inferencia(["Fiebre", "Tos"], "Neumonia"))
        self.assertEqual([t["id"] for t in self.m.traza_explicacion], ["E1"])

    def test_objetivo_ya_en_hechos(self):
        self.assertTrue(self.m.ejecutar_inferencia(["Fiebre"], "Fiebre"))
        self.assertEqual(self.m.traza_explicacion, [])

    def test_sin_hechos(self):
        self.assertFalse(self.m.ejecutar_inferencia([], "Infeccion"))
        self.assertEqual(self.m.traza_explicacion, [])

    def test_objetivo_inexistente(self):
        self.assertFalse(self.m.ejecutar_inferencia(["Fiebre", "Tos"], "Inexistente"))

    def test_hechos_duplicados(self):
        self.assertTrue(self.m.ejecutar_inferencia(["Fiebre", "Fiebre", "Tos"], "Infeccion"))

    def test_traza_se_reinicia(self):
        self.m.ejecutar_inferencia(["Fiebre", "Tos"], "Infeccion")
        self.m.ejecutar_inferencia(["Fiebre", "Tos"], "Infeccion")
        self.assertEqual(len(self.m.traza_explicacion), 1)

    def test_no_modifica_lista_de_entrada(self):
        hechos = ["Fiebre", "Tos"]
        self.m.ejecutar_inferencia(hechos, "Infeccion")
        self.assertEqual(hechos, ["Fiebre", "Tos"])

    def test_orden_de_reglas_en_kb_no_importa(self):
        kb = {"reglas": list(reversed(KB_EJEMPLO["reglas"]))}
        m = crear_motor(kb)
        ok = m.ejecutar_inferencia(
            ["Fiebre", "Tos", "Dificultad_Respiratoria", "Saturacion_Baja"], "Alerta_Neumonia_Grave")
        self.assertTrue(ok)
        self.assertEqual([t["id"] for t in m.traza_explicacion], ["E1", "E2", "E3"])

    def test_kb_con_ciclo_termina(self):
        kb = {"reglas": [
            {"id": "C1", "antecedentes": ["A"], "consecuente": "B"},
            {"id": "C2", "antecedentes": ["B"], "consecuente": "A"},
        ]}
        m = crear_motor(kb)
        self.assertFalse(m.ejecutar_inferencia(["A"], "Z"))

    def test_exportar_traza(self):
        self.m.ejecutar_inferencia(["Fiebre", "Tos"], "Infeccion")
        with tempfile.TemporaryDirectory() as d:
            txt, js = os.path.join(d, "t.txt"), os.path.join(d, "t.json")
            self.m.exportar_traza(txt)
            self.m.exportar_traza(js)
            with open(txt, encoding="utf-8") as f:
                self.assertIn("E1: Fiebre AND Tos -> Infeccion", f.read())
            with open(js, encoding="utf-8") as f:
                self.assertEqual(json.load(f)[0]["id"], "E1")


class TestKBReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "base_conocimiento.json")
        cls.m = MotorInferencia(ruta)

    def test_kb_cargada(self):
        self.assertGreaterEqual(len(self.m.reglas), 50)

    def test_sindrome_respiratorio_alto(self):
        self.assertTrue(self.m.ejecutar_inferencia(
            ["Fiebre", "Tos", "Dolor_Garganta", "Congestion_Nasal"], "Sindrome_Respiratorio_Alto"))

    def test_caso_negativo(self):
        self.assertFalse(self.m.ejecutar_inferencia(["Fiebre"], "Sindrome_Respiratorio_Alto"))

    def test_alerta_profunda_nivel_5(self):
        hechos = ["Fiebre", "Tos", "Esputo", "Dolor_Toracico",
                  "Dificultad_Respiratoria", "Saturacion_Baja", "Cianosis"]
        self.assertTrue(self.m.ejecutar_inferencia(hechos, "Alerta_Falla_Respiratoria"))
        self.assertGreaterEqual(len(self.m.traza_explicacion), 5)

    def test_alerta_sin_sintoma_critico(self):
        hechos = ["Fiebre", "Tos", "Esputo", "Dolor_Toracico",
                  "Dificultad_Respiratoria", "Saturacion_Baja"]
        self.assertFalse(self.m.ejecutar_inferencia(hechos, "Alerta_Falla_Respiratoria"))
        self.assertIn("Neumonia_Grave", self.m.memoria_trabajo)


if __name__ == "__main__":
    unittest.main()