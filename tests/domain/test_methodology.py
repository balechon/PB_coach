import pytest

from pb_coach.domain.methodology import (
    CategoriaRegla,
    PerfilMetodologia,
    ReglaConteoMicrociclo,
    RegistroRegla,
    RegistroReglaSecuencial,
    RestriccionGlobal,
)
from pb_coach.domain.training import ClaseSesion, ObjetivoMesociclo


def _regla_progresion() -> RegistroRegla:
    return RegistroRegla(
        id="LYDIARD-PROGRESION-001",
        categoria=CategoriaRegla.PROGRESION,
        descripcion="El volumen semanal no debe subir más del 10% respecto a la semana anterior.",
        objetivo_mesociclo=ObjetivoMesociclo.BASE_AEROBICA,
        parametros={"incremento_maximo_pct": 10},
    )


def _regla_secuencial_fondo() -> RegistroReglaSecuencial:
    return RegistroReglaSecuencial(
        id="LYDIARD-SECUENCIA-001",
        descripcion="Después de Fondo, solo Recuperación o Descanso.",
        clase_sesion_previa=ClaseSesion.FONDO,
        clases_permitidas_despues=[ClaseSesion.RECUPERACION, ClaseSesion.DESCANSO],
    )


def _regla_conteo_descanso() -> ReglaConteoMicrociclo:
    return ReglaConteoMicrociclo(
        id="LYDIARD-CONTEO-001",
        descripcion="Mínimo 1 Descanso por microciclo.",
        clase_sesion=ClaseSesion.DESCANSO,
        minimo=1,
    )


def _perfil_base(**overrides) -> PerfilMetodologia:
    campos = dict(
        autor="Lydiard",
        fuente="https://example.com/lydiard",
        version="0.1.0",
        deportes_soportados=["running", "trail running"],
        reglas=[_regla_progresion()],
        reglas_secuenciales=[_regla_secuencial_fondo()],
        reglas_conteo_microciclo=[_regla_conteo_descanso()],
    )
    campos.update(overrides)
    return PerfilMetodologia(**campos)


# ---------- PerfilMetodologia ----------

def test_perfil_valido_se_construye():
    perfil = _perfil_base()
    assert perfil.autor == "Lydiard"
    assert len(perfil.reglas) == 1
    assert len(perfil.reglas_secuenciales) == 1
    assert len(perfil.reglas_conteo_microciclo) == 1


def test_perfil_rechaza_reglas_vacio():
    with pytest.raises(ValueError):
        _perfil_base(reglas=[])


def test_perfil_rechaza_id_duplicado_entre_listas_distintas():
    # Mismo id en `reglas` y en `reglas_conteo_microciclo` — validar_ids_unicos
    # debe detectarlo aunque estén en listas de tipos distintos.
    regla_dup = RegistroRegla(
        id="DUP-001", categoria=CategoriaRegla.CARGA, descripcion="Regla de carga."
    )
    conteo_dup = ReglaConteoMicrociclo(
        id="DUP-001",
        descripcion="Conteo duplicado.",
        clase_sesion=ClaseSesion.DESCANSO,
        minimo=1,
    )
    with pytest.raises(ValueError):
        _perfil_base(reglas=[regla_dup], reglas_conteo_microciclo=[conteo_dup])


# ---------- RegistroReglaSecuencial ----------

def test_regla_secuencial_permite_lo_declarado():
    regla = _regla_secuencial_fondo()
    assert ClaseSesion.RECUPERACION in regla.clases_permitidas_despues
    assert ClaseSesion.ESPECIFICO not in regla.clases_permitidas_despues


def test_regla_secuencial_rechaza_lista_vacia():
    with pytest.raises(ValueError):
        RegistroReglaSecuencial(
            id="X-001",
            descripcion="Lista vacía no tiene sentido.",
            clase_sesion_previa=ClaseSesion.FONDO,
            clases_permitidas_despues=[],
        )


# ---------- ReglaConteoMicrociclo ----------

def test_conteo_rechaza_sin_minimo_ni_maximo():
    with pytest.raises(ValueError):
        ReglaConteoMicrociclo(
            id="X-002",
            descripcion="Sin límite no dice nada.",
            clase_sesion=ClaseSesion.DESCANSO,
        )


def test_conteo_rechaza_minimo_mayor_que_maximo():
    with pytest.raises(ValueError):
        ReglaConteoMicrociclo(
            id="X-003",
            descripcion="Rango invertido.",
            clase_sesion=ClaseSesion.ESPECIFICO,
            minimo=5,
            maximo=2,
        )


def test_conteo_valido_con_solo_minimo():
    regla = ReglaConteoMicrociclo(
        id="X-004",
        descripcion="Al menos 1 Descanso.",
        clase_sesion=ClaseSesion.DESCANSO,
        minimo=1,
    )
    assert regla.minimo == 1
    assert regla.maximo is None


# ---------- RestriccionGlobal ----------

def test_restriccion_global_valida_con_parametros():
    restriccion = RestriccionGlobal(
        id="LYDIARD-GLOBAL-001",
        descripcion="No más de 3 microciclos de carga seguidos sin descarga.",
        parametros={"microciclos_carga_max": 3},
    )
    assert restriccion.parametros["microciclos_carga_max"] == 3
