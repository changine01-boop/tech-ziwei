from datetime import datetime

from pydantic import BaseModel

from tech_ziwei.models.reading import ReadingStatus, ReadingType


class ReadingResponse(BaseModel):
    id: str
    chart_id: str
    reading_type: ReadingType
    status: ReadingStatus
    content: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
