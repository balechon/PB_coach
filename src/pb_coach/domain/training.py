# Entidades de dominio: Sesión, Microciclo, Mesociclo, Plan.
#
# Placeholder — se implementará cuando definamos el modelo de datos real
# a partir del primer perfil de metodología transcrito.


from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date,  timedelta

class Terreno(str, Enum):
    """Terreno de entrenamiento"""
    ASFALTO = "Asfalto"
    PISTA = "Pista"
    CAMINO_NO_TECNICO = "Camino no técnico"
    SENDERO_TECNICO = "Sendero técnico"
    ALTA_MONTANA = "Alta montaña"

class TipoSesion(str, Enum):
    """Tipo de sesión de entrenamiento running/trailrunning"""
    SERIES = "Series"
    TEMPO = "Tempo"
    UMBRAL = "Umbral"
    BASE = "Base"
    FONDO = "Fondo"
    FUERZA = "Fuerza"
    RECUPERACION = "Recuperación"

class ClaseSesion(str, Enum):
    """Clase de sesión de entrenamiento running/trailrunning"""
    FONDO = "Fondo"            # F — Z1,Z2 — Base, Fondo
    ESPECIFICO = "Específico"  # E — Z3-Z5 — Series, Tempo, Umbral
    RECUPERACION = "Recuperación"  # R — Z1 — Recuperación
    DESCANSO = "Descanso"      # D — NA — ninguno
class ZonasFC(str, Enum):
    """Zonas de frecuencia cardíaca"""
    Z1 = "Z1"
    Z2 = "Z2"
    Z3 = "Z3"
    Z4 = "Z4"
    Z5 = "Z5"

# que tipo de sesiones esta permitido en cada clase de sesión
TIPOS_PERMITIDOS: dict[ClaseSesion, set[TipoSesion]] = {
    ClaseSesion.FONDO: {TipoSesion.BASE, TipoSesion.FONDO, TipoSesion.RECUPERACION},
    ClaseSesion.ESPECIFICO: {TipoSesion.SERIES, TipoSesion.TEMPO, TipoSesion.UMBRAL, TipoSesion.FUERZA},
    ClaseSesion.RECUPERACION: {TipoSesion.RECUPERACION},
    ClaseSesion.DESCANSO: set(),
}

class Sesion(BaseModel):
    fecha: date
    duracion: timedelta
    distancia_km: float
    terreno: Terreno
    clase_sesion: ClaseSesion
    tipo_sesion: Optional[TipoSesion] = None

    desnivel_positivo_m: Optional[float] = None
    desnivel_negativo_m: Optional[float] = None
    fc_media: Optional[int] = None
    fc_zona: Optional[ZonasFC] = None
    ritmo_medio_min_km: Optional[float] = None
    rpe: Optional[int] = None
    sensaciones: Optional[str] = None

    @model_validator(mode="after")
    def validar_coherencia(self) -> "Sesion":
        # Validar que el tipo de sesión es coherente con la clase de sesión
        permitidos = TIPOS_PERMITIDOS[self.clase_sesion]
        if self.clase_sesion == ClaseSesion.DESCANSO:
            #validar el descanso 
            if self.tipo_sesion is not None:
                raise ValueError(
                f"Descanso pasivo no debe tener tipo_sesion, recibido: {self.tipo_sesion!r}"
                )
            if self.duracion != timedelta(0):
                raise ValueError("Descanso pasivo debe tener duración 0")
            if self.distancia_km != 0:
                raise ValueError("Descanso pasivo debe tener distancia_km 0")
            if self.fc_zona is not None:
                raise ValueError("Descanso pasivo no debe tener fc_zona")
        elif self.tipo_sesion not in permitidos:
            raise ValueError(
                f"Tipo de sesión {self.tipo_sesion!r} no permitido para clase de sesión {self.clase_sesion}\n"
                f"validos: {permitidos}"
            )
        return self
    
class TipoMicrociclo(str, Enum):
    CARGA = "Carga"
    DESCARGA = "Descarga"
class Microciclo(BaseModel):
    sesiones: List[Sesion]
    fecha_inicio: date
    fecha_fin: date
    tipo_microciclo: TipoMicrociclo

    @model_validator(mode="after")
    def validar_coherencia(self) -> "Microciclo":
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior (o igual) a fecha_inicio")

        for s in self.sesiones:
            if not (self.fecha_inicio <= s.fecha <= self.fecha_fin):
                raise ValueError(
                    f"Sesión {s.fecha} fuera del rango del microciclo {self.fecha_inicio} - {self.fecha_fin}"
                )
        return self

class ObjetivoMesociclo(str, Enum):
    """Objetivo del mesociclo"""
    BASE_AEROBICA = "Base aeróbica"
    ACONDICIONAMIENTO_ESTRUCTURAL = "Acondicionamiento estructural"
    FUERZA_Y_ECONOMIA = "Fuerza y economía"
    ACONDICIONAMIENTO_EXCENTRICO = "Acondicionamiento excéntrico"
    UMBRAL = "Umbral"
    POTENCIA_AEROBICA = "Potencia aeróbica"
    VELOCIDAD_Y_POTENCIA = "Velocidad y potencia"
    ESPECIFICO_COMPETENCIA = "Específico competencia"
    PUESTA_A_PUNTO = "Puesta a punto"
    TRANSICION = "Transición"

class Mesociclo(BaseModel):
    microciclos: List[Microciclo]
    objetivo: ObjetivoMesociclo
    fecha_inicio: date
    fecha_fin: date

    @model_validator(mode="after")
    def validar_coherencia(self) -> "Mesociclo":
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior (o igual) a fecha_inicio")

        for m in self.microciclos:
            if not (self.fecha_inicio <= m.fecha_inicio <= m.fecha_fin <= self.fecha_fin):
                raise ValueError(
                    f"Microciclo {m.fecha_inicio} - {m.fecha_fin} fuera del rango del mesociclo {self.fecha_inicio} - {self.fecha_fin}"
                )
        return self


class Plan(BaseModel):
    mesociclos: List[Mesociclo] = Field(min_length=1)
    fecha_inicio: date
    fecha_objetivo: date
    nombre_evento: Optional[str] = None
    distancia_evento_km: Optional[float] = None
    desnivel_positivo_evento_m: Optional[float] = None

    @model_validator(mode="after")
    def validar_coherencia(self) -> "Plan":
        if self.fecha_objetivo < self.fecha_inicio:
            raise ValueError("fecha_objetivo debe ser posterior (o igual) a fecha_inicio")

        for m in self.mesociclos:
            if not (self.fecha_inicio <= m.fecha_inicio <= m.fecha_fin <= self.fecha_objetivo):
                raise ValueError(
                    f"Mesociclo {m.fecha_inicio} - {m.fecha_fin} fuera del rango del plan {self.fecha_inicio} - {self.fecha_objetivo}"
                )
        return self


