from typing import List, Dict, Literal
from collections import Counter


def classify_test_cases(
    test_cases: List[Dict],
    strategy: Literal["simple", "rule"] = "simple"
) -> Dict[str, List[Dict]]:
    good_cases = []
    bad_cases = []
    for case in test_cases:
        title = case.get("title", "").lower()
        description = case.get("description", "").lower()
        steps = case.get("steps", [])
        if strategy == "simple":
            bad_keywords = ["异常", "错误", "失败", "无效", "空值", "越权", "非法"]
            good_keywords = ["成功", "正确", "有效", "正常", "通过"]

            if any(k in title or k in description for k in bad_keywords):
                bad_cases.append(case)
            elif any(k in title or k in description for k in good_keywords):
                good_cases.append(case)
            else:
                bad_step = any("失败" in step.get("expected_result", "") or "异常" in step.get("expected_result", "") for step in steps)
                if bad_step:
                    bad_cases.append(case)
                else:
                    good_cases.append(case)
        elif strategy == "rule":
            good_cases.append(case)  # 可扩展为高级逻辑

    return {
        "good_cases": good_cases,
        "bad_cases": bad_cases,
        "good_prompt_templates": extract_good_case_prompts(good_cases),
        "bad_case_patterns": generalize_bad_cases(bad_cases)
    }

def extract_good_case_prompts(good_cases: List[Dict]) -> List[str]:
    """
    将 Good Case 转化为提示词模板，用于喂给模型作为正向学习参考。
    """
    prompts = []
    for case in good_cases:
        steps_str = "\n".join(
            [f"{step['step_number']}. {step['description']} -> {step.get('expected_result', '')}"
             for step in case.get("steps", [])]
        )
        prompt = f"测试用例标题：{case['title']}\n描述：{case['description']}\n步骤与预期：\n{steps_str}"
        prompts.append(prompt)
    return prompts


def generalize_bad_cases(bad_cases: List[Dict]) -> Dict[str, int]:
    """
    泛化 Bad Case 错误类型，用于总结错误模式（可用来训练模型避免再犯）。
    返回错误类型频次统计。
    """
    error_patterns = []
    for case in bad_cases:
        text = case.get("title", "") + case.get("description", "")
        if "密码错误" in text:
            error_patterns.append("认证失败")
        elif "空" in text or "缺失" in text:
            error_patterns.append("参数缺失")
        elif "越权" in text or "权限" in text:
            error_patterns.append("权限问题")
        elif "格式" in text:
            error_patterns.append("格式错误")
        elif "异常" in text:
            error_patterns.append("系统异常")
        else:
            error_patterns.append("其他")

    return dict(Counter(error_patterns))


# 示例调试
if __name__ == "__main__":
    sample_cases = [
        {
            "id": "TC-001",
            "title": "成功登录",
            "description": "用户使用正确账号密码成功登录系统",
            "steps": [
                {"step_number": 1, "description": "输入正确账号密码", "expected_result": "跳转到首页"}
            ]
        },
        {
            "id": "TC-002",
            "title": "登录失败-密码错误",
            "description": "用户输入错误密码后登录失败",
            "steps": [
                {"step_number": 1, "description": "输入错误密码", "expected_result": "提示密码错误"}
            ]
        }
    ]

    result = classify_test_cases(sample_cases)

    print("✅ Good Cases:")
    for prompt in result["good_prompt_templates"]:
        print(prompt, "\n")

    print("❌ Bad Case Error Patterns:")
    print(result["bad_case_patterns"])
