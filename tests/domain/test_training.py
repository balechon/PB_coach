from datetime import date, timedelta

import pytest

from pb_coach.domain.training import (
    ClaseSesion,
    Mesociclo,
    Microciclo,
    ObjetivoMesociclo,
    Plan,
    Sesion,
    Terreno,
    TipoMicrociclo,
    TipoSesion,
)


# ---------- Sesion ----------

def test_sesion_valida_especifico_con_series():
    sesion = Sesion(
        fecha=date(2026, 1, 5),
        duracion=timedelta(minutes=45),
        distancia_km=8,
        terreno=Terreno.ASFALTO,
        clase_sesion=ClaseSesion.ESPECIFICO,
        tipo_sesion=TipoSesion.SERIES,
    )
    assert sesion.tipo_sesion == TipoSesion.SERIES


def test_sesion_rechaza_descanso_con_tipo_sesion():
    with pytest.raises(ValueError):
        Sesion(
            fecha=date(2026, 1, 5),
            duracion=timedelta(minutes=45),
            distancia_km=8,
            terreno=Terreno.ASFALTO,
            clase_sesion=ClaseSesion.DESCANSO,
            tipo_sesion=TipoSesion.SERIES,
        )


def test_sesion_rechaza_especifico_con_tipo_no_permitido():
    # TODO: construir una Sesion con clase_sesion=ESPECIFICO y un tipo_sesion
    # que NO esté en TIPOS_PERMITIDOS[ESPECIFICO] (ej. TipoSesion.BASE).
    # Debe lanzar ValueError — usa pytest.raises como en el test de arriba.
    with pytest.raises(ValueError):
        Sesion(
            fecha=date(2026, 1, 5),
            duracion=timedelta(minutes=45),
            distancia_km=8,
            terreno=Terreno.ASFALTO,
            clase_sesion=ClaseSesion.ESPECIFICO,
            tipo_sesion=TipoSesion.BASE,
        )
    


def test_sesion_descanso_valido_sin_tipo_sesion():
    # TODO: construir una Sesion de clase_sesion=DESCANSO válida
    # (duracion=timedelta(0), distancia_km=0, sin tipo_sesion, sin fc_zona).
    # No debe lanzar error — assert sobre algún campo del resultado.
    sesion = Sesion(
        fecha=date(2026, 1, 5),
        duracion=timedelta(0),
        distancia_km=0,
        terreno=Terreno.ASFALTO,
        clase_sesion=ClaseSesion.DESCANSO,
    )
    assert sesion.duracion == timedelta(0)




# ---------- Microciclo ----------

def test_microciclo_rechaza_sesion_fuera_de_rango():
    # TODO: crea una Sesion con fecha FUERA del rango [fecha_inicio, fecha_fin]
    # que le vayas a dar al Microciclo, y confirma que se lanza ValueError.
    sesion_fuera = Sesion(
        fecha=date(2026, 1, 10),  # fuera del rango
        duracion=timedelta(minutes=30),
        distancia_km=5,
        terreno=Terreno.ASFALTO,
        clase_sesion=ClaseSesion.FONDO,
        tipo_sesion=TipoSesion.BASE,
    )
    with pytest.raises(ValueError):
        Microciclo(
            sesiones=[sesion_fuera],
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 1, 5),
            tipo_microciclo=TipoMicrociclo.CARGA,
        )




def test_microciclo_rechaza_fecha_fin_antes_de_fecha_inicio():
    # TODO: fecha_fin < fecha_inicio debe fallar, incluso con sesiones=[].
    with pytest.raises(ValueError):
        Microciclo(
            sesiones=[],
            fecha_inicio=date(2026, 1, 5),
            fecha_fin=date(2026, 1, 1),
            tipo_microciclo=TipoMicrociclo.CARGA,
        )


# ---------- Mesociclo ----------

def test_mesociclo_rechaza_microciclo_fuera_de_rango():
    # TODO: análogo al de Microciclo, pero un nivel arriba.
    microciclo_fuera = Microciclo(
        sesiones=[],
        fecha_inicio=date(2026, 1, 10),  # fuera del rango
        fecha_fin=date(2026, 1, 15),
        tipo_microciclo=TipoMicrociclo.CARGA,
    )
    with pytest.raises(ValueError):
        Mesociclo(
            microciclos=[microciclo_fuera],
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 1, 5),
            objetivo=ObjetivoMesociclo.BASE_AEROBICA,
        )



# ---------- Plan ----------

def test_plan_rechaza_mesociclos_vacio():
    # TODO: Plan(mesociclos=[], ...) debe fallar por el Field(min_length=1).
    with pytest.raises(ValueError):
        Plan(
            mesociclos=[],
            fecha_objetivo=date(2026, 1, 31),
            nombre_evento="Maratón de Prueba",
            distancia_evento_km=42.195,
            desnivel_evento_m=500,
        )



def test_plan_sin_carrera_objetivo_es_valido():
    # TODO: un Plan con nombre_evento/distancia_evento_km/desnivel en None
    # (bloque de base genérica) debe construirse sin error.
    plan = Plan(
        mesociclos=[
            Mesociclo(
                microciclos=[],
                fecha_inicio=date(2026, 1, 1),
                fecha_fin=date(2026, 1, 31),
                objetivo=ObjetivoMesociclo.BASE_AEROBICA,
            )
        ],
        fecha_inicio=date(2026, 1, 1),
        fecha_objetivo=date(2026, 1, 31),
        nombre_evento=None,
        distancia_evento_km=None,
        desnivel_positivo_evento_m=None,
    )
    assert plan.nombre_evento is None


def test_plan_rechaza_mesociclo_fuera_de_rango():
    # TODO: un Plan cuya fecha_objetivo termina ANTES de que termine
    # alguno de sus mesociclos debe lanzar ValueError.
    mesociclo_fuera = Mesociclo(
        microciclos=[],
        fecha_inicio=date(2026, 1, 1),
        fecha_fin=date(2026, 2, 15),  # fuera del rango
        objetivo=ObjetivoMesociclo.BASE_AEROBICA,
    )
    with pytest.raises(ValueError):
        Plan(
            mesociclos=[mesociclo_fuera],
            fecha_inicio=date(2026, 1, 1),
            fecha_objetivo=date(2026, 1, 31),
            nombre_evento="Maratón de Prueba",
            distancia_evento_km=42.195,
            desnivel_positivo_evento_m=500,
        )
