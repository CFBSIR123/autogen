import sys
from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any
import json
import logging
from services.testcase_classifier_service import classify_test_cases
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
router = APIRouter(
    prefix="/api/test-cases",
    tags=["test-cases"],
    responses={404: {"description": "Not found"}},
)


@router.post("/classify")
async def classify_cases(cases: List[Dict[str, Any]] = Body(...)):
    # cases 就是自动解析好的列表
    result = classify_test_cases(cases)
    # 记录日志（替代 print）
    logger.info("✅ Good Cases:")
    for case in result.get("good_cases", []):
        logger.info(f"- {case.get('title', '无标题')} | {case.get('description', '无描述')}")
    logger.info("❌ Bad Cases:")
    for case in result.get("bad_cases", []):
        logger.info(f"- {case.get('title', '无标题')} | {case.get('description', '无描述')}")
    # 返回简化结果
    return {
        "good_cases": [{"title": c.get("title", ""), "description": c.get("description", ""),"testSteps":c.get("testSteps","")} for c in result.get("good_cases", [])],
        "bad_cases":  [{"title": c.get("title", ""), "description": c.get("description", ""),"testSteps":c.get("testSteps","")} for c in result.get("bad_cases", [])]
    }

