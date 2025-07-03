from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Optional, Dict, Any, Union
import os
import json
import uuid
from datetime import datetime
import asyncio

from models.test_case import TestCase, TestCaseRequest, TestCaseResponse
from services.ai_service import ai_service
from services.excel_service import excel_service

router = APIRouter(
    prefix="/api/test-cases",
    tags=["test-cases"],
    responses={404: {"description": "Not found"}},
)

# 如果上传目录不存在，则创建
os.makedirs("uploads", exist_ok=True)


#返回流式
@router.post("/generate")
async def generate_test_cases(
    context: str = Form(...),
    requirements: str = Form(...),
    input_type: str = Form(...),
    image: Optional[UploadFile] = File(None),
    prd_text: Optional[str] = Form(None)
):
    """
    从上传的图像或PRD文本、上下文和需求生成测试用例
    参数:
        context: 测试用例生成的上下文信息
        requirements: 测试用例生成的需求
        input_type: 输入类型 ('image' 或 'text')
        image: 上传的流程图、思维导图或UI截图（当input_type为'image'时必需）
        prd_text: PRD文档文本内容（当input_type为'text'时必需）
    返回:
        包含生成的测试用例的流式响应
    """
    image_path = None
    if input_type == 'image':
        if not image:
            raise HTTPException(status_code=400, detail="图片输入模式下必须提供图片文件")
        
        # 保存上传的图像
        image_id = str(uuid.uuid4())
        image_extension = os.path.splitext(image.filename)[1]
        image_path = f"uploads/{image_id}{image_extension}"

        with open(image_path, "wb") as image_file:
            image_file.write(await image.read())
            
    elif input_type == 'text':
        if not prd_text or not prd_text.strip():
            raise HTTPException(status_code=400, detail="PRD文本输入模式下必须提供PRD文档内容")
    else:
        raise HTTPException(status_code=400, detail="输入类型必须是'image'或'text'")
    # 使用流式响应生成测试用例
    return StreamingResponse(
        ai_service.generate_test_cases_stream(
            context=context, 
            requirements=requirements,
            image_path=image_path,
            prd_text=prd_text
        ),
        media_type="text/markdown"
    )





@router.post("/export")
async def export_test_cases(test_cases: List[Union[TestCase, Dict[str, Any]]]):
    """
    将测试用例导出到Excel

    参数:
        test_cases: 要导出的测试用例列表

    返回:
        下载生成的Excel文件的URL
    """
    try:
        # 生成Excel文件
        excel_path = excel_service.generate_excel(test_cases)

        # 返回文件供下载
        return FileResponse(
            path=excel_path,
            filename=os.path.basename(excel_path),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting test cases: {str(e)}")

@router.get("/download/{filename}")
async def download_excel(filename: str):
    """
    下载生成的Excel文件

    参数:
        filename: 要下载的Excel文件名

    返回:
        供下载的Excel文件
    """
    file_path = f"results/{filename}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
