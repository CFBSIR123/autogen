import json
from typing import List, Dict, Any, AsyncGenerator

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, MultiModalMessage as AGMultiModalMessage
from autogen_core import Image as AGImage
from PIL import Image as PILImage
from utils.llms import model_client
from models.test_case import TestCase


class AIService:
    def __init__(self):
        # 在这里初始化 AI 模型
        # 在真实实现中，你需要加载模型
        self.image_analysis_model = None
        self.test_case_generator_model = None

    async def generate_test_cases_stream_from_image(
        self,
        image_path: str,
        context: str,
        requirements: str
    ) -> AsyncGenerator[str, None]:
        """
        基于图像分析、上下文和需求生成测试用例

        参数:
            image_path: 图像路径
            context: 用户提供的上下文
            requirements: 用户提供的需求

        产出:
            Markdown 格式的生成的测试用例块
        """
        # 在真实实现中，你需要调用支持流式输出的 LLM API
        pil_image = PILImage.open(image_path)
        img = AGImage(pil_image)

        # 构建提示词，要求先生成 Markdown 格式的测试用例，然后再生成结构化的 JSON 数据
        prompt = f"""请基于上传的图像生成全面的测试用例。

上下文信息: {context}

需求: {requirements}

请先以 Markdown 格式生成测试用例，包含以下内容：
1. 测试用例 ID 和标题（使用二级标题格式，如 ## TC-001: 测试标题）
2. 优先级（加粗显示，如 **优先级:** 高）
3. 描述（加粗显示，如 **描述:** 测试描述）
4. 前置条件（如果有，加粗显示，如 **前置条件:** 条件描述）
5. 测试步骤和预期结果（使用标准 Markdown 表格格式）

对于测试步骤表格，请使用以下格式：

```
### 测试步骤

| # | 步骤描述 | 预期结果 |
| --- | --- | --- |
| 1 | 第一步描述 | 第一步预期结果 |
| 2 | 第二步描述 | 第二步预期结果 |
```

请确保表格格式正确，包含表头和分隔行。

然后，在生成完 Markdown 格式的测试用例后，请生成结构化的测试用例数据，包含相同的内容，但使用 JSON 格式，以便于导出到 Excel。

请确保测试用例覆盖全面，包含正向和负向测试场景。"""

        multi_modal_message = AGMultiModalMessage(content=[prompt, img], source="user")
        agent = AssistantAgent(
            name=f"agent",
            model_client=model_client,
            system_message="你是一个专业的测试用例生成器，擅长基于图像生成全面的测试用例。请以标准 Markdown 格式生成测试用例，包含正确的表格格式。",
            model_client_stream=True,  # 启用流式输出
        )

        # 首先输出标题
        yield "# 正在生成测试用例...\n\n"

        # 初始化测试用例列表
        markdown_buffer = ""

        # 流式输出生成的测试用例
        async for event in agent.run_stream(task=multi_modal_message):
            if isinstance(event, ModelClientStreamingChunkEvent):
                # 返回生成的文本片段
                content = event.content
                markdown_buffer += content
                yield content
            elif isinstance(event, TaskResult):
                # 任务完成，处理最终结果
                pass

        # 在流式输出结束后，尝试从 Markdown 中提取测试用例
        test_cases_json = self._extract_test_cases_from_markdown(markdown_buffer)
        if test_cases_json:
            yield "\n\n<!-- TEST_CASES_JSON: " + json.dumps(test_cases_json) + " -->\n"

    def _test_case_to_dict(self, test_case: TestCase) -> Dict[str, Any]:
        """
        将 TestCase 对象转换为字典
        """
        return {
            'id': test_case.id,
            'title': test_case.title,
            'description': test_case.description,
            'preconditions': test_case.preconditions,
            'priority': test_case.priority,
            'steps': [
                {
                    'step_number': step.step_number,
                    'description': step.description,
                    'expected_result': step.expected_result
                } for step in test_case.steps
            ]
        }

    def _generate_markdown_from_test_cases(self, test_cases: List[TestCase]) -> str:
        """
        从测试用例列表生成 Markdown 格式的文本
        """
        markdown = "# 生成的测试用例\n\n"

        for tc in test_cases:
            markdown += f"## {tc.id}: {tc.title}\n\n"

            if tc.priority:
                markdown += f"**优先级:** {tc.priority}\n\n"

            markdown += f"**描述:** {tc.description}\n\n"

            if tc.preconditions:
                markdown += f"**前置条件:** {tc.preconditions}\n\n"

            # 确保表格格式正确，包含表头和分隔行
            markdown += "### 测试步骤\n\n"
            # 添加表格头
            markdown += "| # | 步骤描述 | 预期结果 |\n"
            # 添加分隔行（这一行很重要）
            markdown += "| --- | --- | --- |\n"

            # 添加每一行数据
            for step in tc.steps:
                markdown += f"| {step.step_number} | {step.description} | {step.expected_result} |\n"

            markdown += "\n\n"

        return markdown

    def _extract_test_cases_from_markdown(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        从 Markdown 文本中提取测试用例信息

        参数:
            markdown_text: Markdown 格式的测试用例文本

        返回:
            测试用例列表
        """
        test_cases = []
        lines = markdown_text.split('\n')

        current_test_case = None
        current_steps = []
        in_table = False
        table_headers = []

        for line in lines:
            # 检测新测试用例的开始
            if line.startswith('## '):
                # 如果有当前测试用例，将其添加到列表中
                if current_test_case is not None and current_steps:
                    current_test_case['steps'] = current_steps
                    test_cases.append(current_test_case)

                # 初始化新的测试用例
                title_parts = line[3:].strip().split(': ', 1)
                if len(title_parts) > 1:
                    test_id = title_parts[0].strip()
                    title = title_parts[1].strip()
                else:
                    test_id = f"TC-{len(test_cases) + 1}"
                    title = line[3:].strip()

                current_test_case = {
                    'id': test_id,
                    'title': title,
                    'description': '',
                    'preconditions': None,
                    'priority': None
                }
                current_steps = []
                in_table = False

            # 提取优先级
            elif line.startswith('**优先级:**') and current_test_case:
                current_test_case['priority'] = line.replace('**优先级:**', '').strip()

            # 提取描述
            elif line.startswith('**描述:**') and current_test_case:
                current_test_case['description'] = line.replace('**描述:**', '').strip()

            # 提取前置条件
            elif line.startswith('**前置条件:**') and current_test_case:
                current_test_case['preconditions'] = line.replace('**前置条件:**', '').strip()

            # 检测表格头
            elif '| --- | --- | --- |' in line:
                in_table = True
                # 获取前一行的表头
                for i, prev_line in enumerate(reversed(lines[:lines.index(line)])):
                    if '|' in prev_line:
                        table_headers = [h.strip() for h in prev_line.split('|')[1:-1]]
                        break

            # 提取测试步骤
            elif in_table and '|' in line and '---' not in line and len(line.split('|')) > 3:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) >= 3:
                    try:
                        step_number = int(cells[0])
                        description = cells[1]
                        expected_result = cells[2]

                        current_steps.append({
                            'step_number': step_number,
                            'description': description,
                            'expected_result': expected_result
                        })
                    except (ValueError, IndexError):
                        pass  # 忽略无法解析的行

        # 添加最后一个测试用例
        if current_test_case is not None and current_steps:
            current_test_case['steps'] = current_steps
            test_cases.append(current_test_case)

        return test_cases

    async def generate_test_cases_stream_from_text(
        self,
        prd_text: str,
        context: str,
        requirements: str
    ) -> AsyncGenerator[str, None]:
        """
        基于PRD文本、上下文和需求生成测试用例

        参数:
            prd_text: PRD文档文本内容
            context: 用户提供的上下文
            requirements: 用户提供的需求

        产出:
            Markdown 格式的生成的测试用例块
        """
        # 构建提示词，要求先生成 Markdown 格式的测试用例，然后再生成结构化的 JSON 数据
        prompt = f"""请基于以下PRD文档内容生成全面的测试用例。

PRD文档内容:
{prd_text}

上下文信息: {context}

需求: {requirements}

请先以 Markdown 格式生成测试用例，包含以下内容：
1. 测试用例 ID 和标题（使用二级标题格式，如 ## TC-001: 测试标题）
2. 优先级（加粗显示，如 **优先级:** 高）
3. 描述（加粗显示，如 **描述:** 测试描述）
4. 前置条件（如果有，加粗显示，如 **前置条件:** 条件描述）
5. 测试步骤和预期结果（使用标准 Markdown 表格格式）

对于测试步骤表格，请使用以下格式：

```
### 测试步骤

| # | 步骤描述 | 预期结果 |
| --- | --- | --- |
| 1 | 第一步描述 | 第一步预期结果 |
| 2 | 第二步描述 | 第二步预期结果 |
```

请确保表格格式正确，包含表头和分隔行。

然后，在生成完 Markdown 格式的测试用例后，请生成结构化的测试用例数据，包含相同的内容，但使用 JSON 格式，以便于导出到 Excel。

请确保测试用例覆盖全面，包含正向和负向测试场景。"""

        # 创建纯文本消息
        from autogen_agentchat.messages import TextMessage
        text_message = TextMessage(content=prompt, source="user")
        
        agent = AssistantAgent(
            name=f"text_agent",
            model_client=model_client,
            system_message="你是一个专业的测试用例生成器，擅长基于PRD文档生成全面的测试用例。请以标准 Markdown 格式生成测试用例，包含正确的表格格式。",
            model_client_stream=True,  # 启用流式输出
        )

        # 首先输出标题
        yield "# 正在基于PRD文档生成测试用例...\n\n"

        # 初始化测试用例列表
        markdown_buffer = ""

        # 流式输出生成的测试用例
        async for event in agent.run_stream(task=text_message):
            if isinstance(event, ModelClientStreamingChunkEvent):
                # 返回生成的文本片段
                content = event.content
                markdown_buffer += content
                yield content
            elif isinstance(event, TaskResult):
                # 任务完成，处理最终结果
                pass

        # 在流式输出结束后，尝试从 Markdown 中提取测试用例
        test_cases_json = self._extract_test_cases_from_markdown(markdown_buffer)
        if test_cases_json:
            yield "\n\n<!-- TEST_CASES_JSON: " + json.dumps(test_cases_json) + " -->\n"

    async def generate_test_cases_stream(
        self,
        context: str,
        requirements: str,
        image_path: str = None,
        prd_text: str = None
    ) -> AsyncGenerator[str, None]:
        """
        统一的测试用例生成入口，根据输入类型调用相应的处理方法
        
        参数:
            context: 用户提供的上下文
            requirements: 用户提供的需求
            image_path: 图像路径（可选）
            prd_text: PRD文档文本（可选）
        
        产出:
            Markdown 格式的生成的测试用例块
        """
        if image_path:
            # 图片输入模式
            async for chunk in self.generate_test_cases_stream_from_image(image_path, context, requirements):
                yield chunk
        elif prd_text:
            # PRD文本输入模式
            async for chunk in self.generate_test_cases_stream_from_text(prd_text, context, requirements):
                yield chunk
        else:
            yield "错误：必须提供图片或PRD文本输入\n"


ai_service = AIService()
