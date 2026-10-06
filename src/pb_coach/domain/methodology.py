# Modelo tipado de un perfil de metodología (carga desde YAML, ver
# methodology/profiles/_template.yaml).

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from pb_coach.domain.training import ClaseSesion, ObjetivoMesociclo, TipoSesion


class CategoriaRegla(str, Enum):
    """Clasificación de una RegistroRegla — metadata, no afecta su evaluación."""

    CARGA = "Carga"
    PROGRESION = "Progresión"
    DESCANSO = "Descanso"
    INTENSIDAD = "Intensidad"


class RegistroRegla(BaseModel):
    """Una regla de metodología transcrita de la fuente del autor.

    Las condiciones de aplicabilidad (objetivo_mesociclo, clase_sesion,
    tipo_sesion) son todas opcionales: si quedan en None, la regla se
    interpreta como "aplica siempre, sin condición".
    """

    id: str
    categoria: CategoriaRegla
    descripcion: str

    objetivo_mesociclo: Optional[ObjetivoMesociclo] = None
    clase_sesion: Optional[ClaseSesion] = None
    tipo_sesion: Optional[TipoSesion] = None

    parametros: dict[str, float | int | str] = Field(default_factory=dict)


class RestriccionGlobal(BaseModel):
    """Una regla cuyo alcance es el Plan completo, no una sesión/mesociclo
    puntual (ej. "no más de 3 microciclos de carga seguidos sin descarga").
    """

    id: str
    descripcion: str
    parametros: dict[str, float | int | str] = Field(default_factory=dict)


class RegistroReglaSecuencial(BaseModel):
    """Regla sobre la relación entre una sesión y la sesión inmediatamente
    anterior dentro de un microciclo.

    clases_permitidas_despues es una lista de permitidas (no de prohibidas):
    dice explícitamente qué SÍ puede seguir a clase_sesion_previa, en vez de
    enumerar todo lo que no. Cualquier ClaseSesion ausente de la lista queda
    prohibida después de clase_sesion_previa.
    """

    id: str
    descripcion: str
    clase_sesion_previa: ClaseSesion
    clases_permitidas_despues: list[ClaseSesion] = Field(min_length=1)


class ReglaConteoMicrociclo(BaseModel):
    """Regla sobre cuántas sesiones de una clase dada debe/puede haber
    dentro de un microciclo (ej. "mínimo un día de Descanso por semana").
    """

    id: str
    descripcion: str
    clase_sesion: ClaseSesion
    minimo: Optional[int] = None
    maximo: Optional[int] = None

    @model_validator(mode="after")
    def validar_algun_limite_presente(self) -> "ReglaConteoMicrociclo":
        if self.minimo is None and self.maximo is None:
            raise ValueError(
                "ReglaConteoMicrociclo debe especificar minimo, maximo, o ambos"
            )
        if self.minimo is not None and self.maximo is not None and self.minimo > self.maximo:
            raise ValueError(
                f"minimo ({self.minimo}) no puede ser mayor que maximo ({self.maximo})"
            )
        return self


class PerfilMetodologia(BaseModel):
    """Un perfil de metodología completo — la traducción íntegra de un YAML
    de autor a objetos tipados. Solo un perfil está activo por Plan.
    """

    autor: str
    fuente: str
    version: str
    deportes_soportados: list[str]

    reglas: list[RegistroRegla] = Field(min_length=1)
    restricciones_globales: list[RestriccionGlobal] = Field(default_factory=list)
    reglas_secuenciales: list[RegistroReglaSecuencial] = Field(default_factory=list)
    reglas_conteo_microciclo: list[ReglaConteoMicrociclo] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_ids_unicos(self) -> "PerfilMetodologia":
        todos_los_ids = (
            [r.id for r in self.reglas]
            + [r.id for r in self.restricciones_globales]
            + [r.id for r in self.reglas_secuenciales]
            + [r.id for r in self.reglas_conteo_microciclo]
        )
        vistos: set[str] = set()
        duplicados: set[str] = set()
        for rid in todos_los_ids:
            if rid in vistos:
                duplicados.add(rid)
            vistos.add(rid)

        if duplicados:
            raise ValueError(f"IDs de regla duplicados en el perfil: {sorted(duplicados)}")
        return self


if __name__=="__main__":
    from pb_coach.domain.training import ClaseSesion, ObjetivoMesociclo

    # 1-2 reglas en `reglas` — usa CategoriaRegla y, si quieres,
    # objetivo_mesociclo/clase_sesion como condición de aplicabilidad.
    regla_progresion = RegistroRegla(
        id="LYDIARD-PROGRESION-001",
        categoria=CategoriaRegla.PROGRESION,
        descripcion=" En mesociclos de base aeróbica, el volumen semanal no debe subir más del 10% respecto a la semana anterior.",
        objetivo_mesociclo=ObjetivoMesociclo.BASE_AEROBICA,   # opcional, o quítalo
        parametros={"incremento_maximo_pct": 10},
    )

    # Regla 1 de tu tabla: después de Fondo, solo Recuperación o Descanso.
    regla_secuencial_fondo = RegistroReglaSecuencial(
        id="LYDIARD-SECUENCIA-002",
        descripcion="después de Fondo, solo Recuperación o Descanso",
        clase_sesion_previa=ClaseSesion.FONDO,
        clases_permitidas_despues=[ClaseSesion.RECUPERACION, ClaseSesion.DESCANSO],
    )

    # Regla 2 de tu tabla: no dos Específico seguidos.
    regla_secuencial_especifico = RegistroReglaSecuencial(
        id="LYDIARD-SECUENCIA-003",
        descripcion="no dos Específico seguidos",
        clase_sesion_previa=ClaseSesion.ESPECIFICO,
        clases_permitidas_despues=[    ClaseSesion.FONDO,
    ClaseSesion.RECUPERACION,
    ClaseSesion.DESCANSO,],  # todas MENOS Específico
    )

    # Regla 4 de tu tabla: mínimo 1 Descanso por microciclo.
    regla_conteo_descanso = ReglaConteoMicrociclo(
        id="LYDIARD-CONTEO-001",
        descripcion="mínimo 1 Descanso por microciclo",
        clase_sesion=ClaseSesion.DESCANSO,
        minimo=1,
    )

    perfil = PerfilMetodologia(
        autor="luis lydiard",
        fuente="https://www.runnersworld.com/training/a20803112/lydiard-training-method/",
        version="0.1.0",
        deportes_soportados=["running", "trail running"],
        reglas=[regla_progresion],
        reglas_secuenciales=[regla_secuencial_fondo, regla_secuencial_especifico],
        reglas_conteo_microciclo=[regla_conteo_descanso],
    )
    print("Perfil construido OK:", perfil.autor, "-", len(perfil.reglas_secuenciales), "reglas secuenciales")

    # Caso que DEBE fallar: dos reglas con el mismo id.
    try:
        PerfilMetodologia(
            autor="luis lydiard",
            fuente="https://www.runnersworld.com/training/a20803112/lydiard-training-method/",
            version="0.1.0",
            deportes_soportados=["running"],
            reglas=[
                RegistroRegla(id="DUP-001", categoria=CategoriaRegla.CARGA, descripcion=" la regla "),
            ],
            reglas_conteo_microciclo=[
                ReglaConteoMicrociclo(id="DUP-001", descripcion=" en mesociclos", clase_sesion=ClaseSesion.DESCANSO, minimo=1),
            ],
        )
        print("ERROR: no se rechazó el id duplicado")
    except Exception as e:
        print("Rechazado correctamente (id duplicado)")
