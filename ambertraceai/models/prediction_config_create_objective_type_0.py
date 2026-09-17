from enum import Enum


class PredictionConfigCreateObjectiveType0(str, Enum):
    DIRECTIONAL_PNL = "directional_pnl"
    HIT_RATE = "hit_rate"
    SHARPE_RATIO = "sharpe_ratio"
    SKILL_VS_PERSISTENCE = "skill_vs_persistence"

    def __str__(self) -> str:
        return str(self.value)
