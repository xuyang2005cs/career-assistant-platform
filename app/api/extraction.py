"""Job-description extraction preview endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.schemas.error import ErrorResponse
from app.schemas.extraction import JobExtractRequest, JobExtractionPreview
from app.services.extraction import ExtractionService, get_extraction_service

router = APIRouter(
    prefix="/api/v1",
    tags=["职位信息提取"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "请求参数校验失败",
        }
    },
)
ExtractionServiceDependency = Annotated[
    ExtractionService,
    Depends(get_extraction_service),
]


@router.post(
    "/job-extract",
    response_model=JobExtractionPreview,
    summary="提取职位信息",
    description="从职位描述文本中提取结构化岗位信息，仅返回预览，不写入数据库。",
)
async def extract_job(
    request: JobExtractRequest,
    service: ExtractionServiceDependency,
) -> JobExtractionPreview:
    """Extract a non-persistent Job preview from pasted description text."""

    return await service.extract(request.text)
