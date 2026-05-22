import io

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tech_ziwei.database import get_db
from tech_ziwei.models.reading import ReadingType
from tech_ziwei.models.user import User
from tech_ziwei.schemas.chart import ChartRequest, ChartResponse
from tech_ziwei.schemas.reading import ReadingResponse
from tech_ziwei.services.chart import create_chart, delete_chart, get_chart, list_charts
from tech_ziwei.services.pdf import generate_chart_pdf
from tech_ziwei.services.reading import get_complete_readings, get_or_create_reading, get_reading_by_type
from tech_ziwei.workers.report_worker import generate_reading_task
from .deps import get_current_user

router = APIRouter(prefix="/charts", tags=["charts"])


@router.post("", response_model=ChartResponse, status_code=status.HTTP_201_CREATED)
async def create(
    req: ChartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChartResponse:
    chart = await create_chart(db, current_user.id, req)
    return ChartResponse.model_validate(chart)


@router.get("", response_model=list[ChartResponse])
async def list_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChartResponse]:
    charts = await list_charts(db, current_user.id)
    return [ChartResponse.model_validate(c) for c in charts]


@router.get("/{chart_id}", response_model=ChartResponse)
async def get_one(
    chart_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChartResponse:
    chart = await get_chart(db, chart_id, current_user.id)
    if chart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
    return ChartResponse.model_validate(chart)


@router.get("/{chart_id}/pdf")
async def download_pdf(
    chart_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    if current_user.subscription_tier == "free":
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="payment_required")

    chart = await get_chart(db, chart_id, current_user.id)
    if chart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")

    readings = await get_complete_readings(db, chart_id)
    pdf_bytes = generate_chart_pdf(chart, readings, current_user.email)

    filename = f"ziwei-{chart_id[:8]}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    chart_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    deleted = await delete_chart(db, chart_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")


@router.get("/{chart_id}/readings/{reading_type}", response_model=ReadingResponse)
async def get_reading_status(
    chart_id: str,
    reading_type: ReadingType,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadingResponse:
    chart = await get_chart(db, chart_id, current_user.id)
    if chart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
    reading = await get_reading_by_type(db, chart_id, reading_type)
    if reading is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")
    return ReadingResponse.model_validate(reading)


@router.post("/{chart_id}/report", response_model=ReadingResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_report(
    chart_id: str,
    reading_type: ReadingType = Query(default=ReadingType.CORE),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadingResponse:
    if current_user.subscription_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="payment_required",
        )

    chart = await get_chart(db, chart_id, current_user.id)
    if chart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")

    reading, created = await get_or_create_reading(db, chart_id, reading_type)
    if created:
        generate_reading_task.delay(reading.id)
    return ReadingResponse.model_validate(reading)
