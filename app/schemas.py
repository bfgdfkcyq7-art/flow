"""
Pydantic 请求/响应模型，用于 API 参数校验。
"""

from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class RecordBase(BaseModel):
    date: str = Field(..., description="记录日期 YYYY-MM-DD")
    weight: Optional[float] = Field(
        None, gt=0, le=999999, description="可选数值：体重、步数、心率等，由你定义"
    )
    mood: Optional[int] = Field(None, ge=1, le=5)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="睡眠 0–24 小时")
    exercise_minutes: Optional[int] = Field(None, ge=0, le=1440, description="运动 ≥ 0 分钟")
    keywords: list[str] = Field(default_factory=list)
    diary: str = Field(default="", max_length=200)
    life_areas: list[str] = Field(default_factory=list)

    @field_validator("weight", "sleep_hours", "exercise_minutes", "mood", mode="before")
    @classmethod
    def empty_to_none(cls, v: Union[str, int, float, None]) -> Union[str, int, float, None]:
        """空字符串视为未填写，避免前端传 '' 导致校验异常。"""
        if v == "" or v is None:
            return None
        return v

    @field_validator("diary", mode="before")
    @classmethod
    def diary_to_str(cls, v) -> str:
        if v is None:
            return ""
        return str(v).strip()

    @field_validator("keywords", mode="before")
    @classmethod
    def keywords_to_list(cls, v) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    @field_validator("keywords")
    @classmethod
    def clean_keywords(cls, v: list[str]) -> list[str]:
        return [k.strip() for k in v if k and k.strip()]

    @field_validator("life_areas")
    @classmethod
    def validate_life_areas(cls, v: list[str]) -> list[str]:
        allowed = {"学业", "健身", "感情", "旅行", "摄影", "生活"}
        return [x for x in v if x in allowed]


class RecordCreate(RecordBase):
    pass


class RecordUpdate(RecordBase):
    pass
