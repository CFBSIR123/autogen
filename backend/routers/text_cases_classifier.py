import sys
from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any
import json
import logging
from services.testcase_classifier_service import classify_test_cases
from services.testcase_classifier_service import classify_test_cases
from services.vector_store import add_bad_case_to_faiss  # ✅ 导入向量数据库写入方法

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
    result = classify_test_cases(cases)
    logger.info("✅ Good Cases:")
    for case in result.get("good_cases", []):
        logger.info(f"- {case.get('title', '无标题')} | {case.get('description', '无描述')}")
    logger.info("❌ Bad Cases:")
    for case in result.get("bad_cases", []):
        logger.info(f"- {case.get('title', '无标题')} | {case.get('description', '无描述')}")
        # ✅ 将坏用例写入向量数据库
        try:
            add_bad_case_to_faiss(case)
        except Exception as e:
            logger.warning(f"添加坏用例到向量库失败: {e}")

    return {
        "good_cases": [{"title": c.get("title", ""), "description": c.get("description", ""), "testSteps": c.get("testSteps", "")} for c in result.get("good_cases", [])],
        "bad_cases":  [{"title": c.get("title", ""), "description": c.get("description", ""), "testSteps": c.get("testSteps", "")} for c in result.get("bad_cases", [])]
    }
