from typing import Dict, Any, Optional, List


# ---- Power verb library (from resume-optimizer skill) ----
POWER_VERBS = {
    "leadership": ["主导", "带领", "统筹", "搭建", "重塑"],
    "execution": ["推进", "落地", "交付", "完成", "达成"],
    "innovation": ["创新", "首创", "优化", "重构", "升级"],
    "analysis": ["分析", "洞察", "诊断", "评估", "验证"],
    "influence": ["推动", "促成", "影响", "赋能", "孵化"],
}

QUANTIFICATION_EXAMPLES = [
    "提升效率30%，节省团队每周8小时",
    "年销售额从800万提升至1500万，同比增长87.5%",
    "带领5人团队，提前2周完成交付",
    "累计签约客户100+家，3次获得季度冠军",
    "首屏加载时间从4.2s降至1.1s",
]


def _star_method_guide() -> str:
    return """
## STAR法则写作指南
对每段工作经历，按以下结构重写：
- **S**ituation（背景）：项目/任务的背景和挑战是什么
- **T**ask（任务）：你的具体任务和目标
- **A**ction（行动）：你采取了什么行动（使用高能动词开头：主导/推进/创新/分析/推动）
- **R**esult（结果）：量化成果（时间/金额/人数/比例），必须用数据说话

无数据时的替代方案：描述规模("负责3条产品线")、描述频次("日均处理200+工单")、描述排名("部门Top 3")"""


def _data_quantification_guide() -> str:
    return """
## 数据化技巧
- **时间维度**：提前X周完成、缩短X%工期、连续X季度
- **金额维度**：节约X万成本、创造X万营收、预算X万
- **人数维度**：管理X人团队、服务X万用户、协调X个部门
- **比例维度**：提升X%、降低X%、转化率X%、满意度X%
- 禁止使用模糊描述，如"取得了很好的效果"、"完成了相关工作"
"""

def _industry_keywords(industry_hint: str = "") -> str:
    base = """
## 行业关键词增强
根据岗位类型自动匹配关键词：
- **技术岗**：架构设计、性能优化、敏捷开发、CI/CD、微服务、并发量、QPS
- **销售岗**：拓客、转化率、客户关系管理、KPI达成率、市占率、复购率
- **产品岗**：DAU/MAU、用户增长、转化率、留存率、产品迭代、数据驱动、A/B测试
- **财务岗**：预算编制、财务分析、成本控制、审计、合规、资金管理"""
    if industry_hint:
        base += f"\n- 目标行业提示：{industry_hint}，请在优化时重点关注该行业的关键词匹配"
    return base


def _hr_3second_rule() -> str:
    return """
## HR 3秒法则（前1/3决定生死）
HR平均花3-6秒浏览一份简历，视线轨迹：
1. 基本信息区（1秒）：学校、学历、工作年限
2. 个人优势/摘要（1秒）：是否有亮点关键词
3. 最近一段工作（1-2秒）：公司知名度 + 职位 + 成果
4. 技能区（1秒）：是否匹配岗位要求
因此：**优化后简历必须把最亮的信息放在最前面1/3区域**"""


def build_optimize_prompt(
    resume_text: str,
    target_position: str = "",
    optimization_style: str = "简洁专业",
    word_limit: int = 800
) -> str:
    style_instructions = {
        "简洁专业": "使用专业术语，表达清晰有条理，适合正式求职场景。重点突出核心能力和关键成果。",
        "突出业绩": "重点强调工作成果和业绩，用STAR法则重写每段经历，每个成果必须有数据支撑。",
        "技术导向": "突出技术栈深度和项目架构能力，使用精确的技术关键词（版本号、框架名、性能指标），适合技术岗位申请。",
        "创新风格": "表达新颖有创意，展现个人特色和独特价值，适合互联网/创意类岗位。同时保持专业性。",
    }

    style_instruction = style_instructions.get(optimization_style, style_instructions["简洁专业"])

    prompt = f"""你是一位资深HR和简历优化专家，拥有10年招聘经验。请对以下简历进行专业优化。

{_star_method_guide()}

{_data_quantification_guide()}

{_industry_keywords(target_position)}

{_hr_3second_rule()}

## 优化原则
- 用数据说话，每个工作成果必须量化
- 动词开头，使用高能动词（{", ".join(POWER_VERBS["leadership"][:3])}等）
- 删除无关信息和空洞形容词（"认真负责"、"团队合作"这类词必须用具体事例替换）
- 控制篇幅，信息密度要高
- 核心优势放在最显眼位置（前1/3区域）

## 原始简历内容
{resume_text}

## 优化目标
- 目标岗位：{target_position if target_position else '未指定（根据简历内容推断最匹配的岗位方向）'}
- 优化风格：{style_instruction}

## 输出格式要求（重要）
请按以下结构输出，**优化后简历必须使用纯文本格式，不得使用任何 Markdown 语法**（不要用 **、##、- 等符号）：

【简历诊断】
当前问题：[列出3-5个具体问题]
缺少的关键词：[列出目标岗位需要但简历中缺失的关键词]

【优化后简历】
[输出完整优化后的纯文本简历，直接用空格和换行排版，禁止使用任何 Markdown 标记。个人信息、教育经历、工作经历、项目经验、技能特长各部分之间用空行分隔，各部分标题直接用中文括号或冒号标注]

【优化对比】
主要改进：[列举3-5项核心改进点]
数据增强：[说明新增/强化的量化数据]

【HR视角点评】
竞争力评估：[该简历在目标岗位的竞争力评价]
投递建议：[适合投递的公司类型/岗位级别]
面试准备：[针对该简历，面试官可能会深挖的3个问题]

优化后简历字数控制在{word_limit}字以内。
严格禁止在优化后简历部分使用 ** 加粗、## 标题、- 列表等 Markdown 格式。
"""
    return prompt


def build_resume_diagnosis_prompt(
    resume_text: str,
    target_position: str = ""
) -> str:
    """Generate a standalone resume diagnosis report (no rewriting, just analysis)."""
    prompt = f"""你是一位资深HR，请对以下简历进行快速诊断（不重写，只分析问题）。

## 简历内容
{resume_text}

## 目标岗位
{target_position if target_position else "未指定"}

## 诊断维度
请从以下6个维度逐一打分（每项0-100分）并给出具体问题：

1. **信息完整度**：是否有姓名、联系方式、教育背景、工作经历、技能？
2. **关键词匹配度**：和目标岗位的JD关键词匹配程度如何？缺少哪些关键词？
3. **数据量化度**：工作成果是否有数据支撑？量化数据的质量和数量？
4. **结构清晰度**：信息层次是否分明？HR能否在3秒内找到核心信息？
5. **语言专业度**：是否使用了专业术语和高能动词？语言是否精炼？
6. **竞争力表现**：前1/3是否足够亮眼？能否在竞争中脱颖而出？

## 输出格式（纯JSON）
{{
    "diagnosis": {{
        "completeness": {{"score": 数字, "issues": ["问题1", "问题2"]}},
        "keyword_match": {{"score": 数字, "matched": ["已匹配关键词"], "missing": ["缺失关键词"]}},
        "quantification": {{"score": 数字, "current_count": 现有量化数据数量, "suggestions": ["建议1"]}},
        "structure": {{"score": 数字, "issues": ["结构问题"]}},
        "language": {{"score": 数字, "weak_phrases": ["需替换的空洞表述"], "suggested_verbs": ["推荐高能动词"]}},
        "competitiveness": {{"score": 数字, "first_impression": "HR3秒印象评价"}}
    }},
    "overall_score": 综合评分(0-100),
    "top_3_fixes": ["最紧急的3个修改建议"],
    "industry_fit": "该简历最适合的行业/岗位方向"
}}

输出必须是纯JSON，不要有其他内容。
"""
    return prompt


def build_structured_prompt(
    resume_text: str,
    optimization_focus: Optional[List[str]] = None
) -> str:
    focus_areas = optimization_focus or [
        "个人信息完善",
        "教育经历描述优化",
        "工作经历成果量化",
        "项目经验亮点突出",
        "技能特长精准表述"
    ]

    focus_instruction = "\n".join([f"- {area}" for area in focus_areas])

    prompt = f"""你是一位专业的简历优化顾问，请对以下简历进行结构化优化。

## 原始简历
{resume_text}

## 优化重点
{focus_instruction}

## 输出要求
请以结构化格式输出优化后的简历，使用清晰的章节划分：
1. 个人信息
2. 教育经历
3. 工作经历
4. 项目经验
5. 技能特长

每个部分都要突出重点，语言精炼专业。
"""
    return prompt


def build_interview_question_prompt(
    resume_summary: str,
    technical_stack: List[str],
    project_highlights: List[str],
    difficulty: str,
    question_types: List[str],
    scope: str,
    question_count: int = 5
) -> str:
    type_instructions = {
        "选择题": "生成4个选项的单选题，涵盖技术原理、概念理解等知识点",
        "简答题": "生成简答题，要求清晰简洁地回答核心要点",
        "项目手撕题": "生成需要在纸上或白板上编写的代码题或算法题，与候选人项目经历紧密相关",
        "场景面试题": "生成情景题，考察解决实际问题的能力，场景与候选人真实项目背景相关",
        "压力面试题": "生成考验心理素质和应变能力的问题，针对简历中的薄弱点深度追问",
    }

    scope_instruction = {
        "仅技术面试": "只生成技术相关问题，包括编程语言底层原理、框架设计思想、算法与数据结构、系统设计等",
        "仅HR面试": "只生成HR行为面试问题，包括职业规划、团队协作冲突、职业素养、离职原因、薪资期望等",
        "全题型混合": "混合生成技术面试题和行为面试题，比例约6:4",
    }

    types_instruction = "\n".join([type_instructions.get(t, t) for t in question_types])
    scope_text = scope_instruction.get(scope, scope_instruction["全题型混合"])

    tech_stack_str = ", ".join(technical_stack) if technical_stack else "未识别到特定技术栈"
    highlights_str = "\n".join([f"- {h}" for h in project_highlights]) if project_highlights else "无具体项目亮点"

    prompt = f"""你是一位资深技术面试官和HR面试专家。根据候选人的简历内容，生成高度个性化的面试题目。

## 出题原则
- 针对简历中的每一个技术栈，深挖底层原理和实战经验
- 针对简历中的项目经历，追问技术难点、架构决策和个人贡献
- 针对简历中的模糊描述（如"参与了"、"负责了"），设计追问题目
- 面试题难度与候选人实际水平匹配，避免无效刷题

## 候选人简历摘要
{resume_summary}

## 技术栈
{tech_stack_str}

## 项目经历要点
{highlights_str}

## 出题配置
- 面试难度：{difficulty}
- 题目类型要求：
{types_instruction}
- 出题范围：{scope_text}
- 题目数量：{question_count}道

## 难度说明
- 入门：基础概念和简单应用，适合应届生初面
- 基础：基本原理和常规使用，适合1-3年经验
- 中等：综合应用和原理深度，适合3-5年经验
- 面试高频：真实面试中高频出现的典型题目（大厂必问）
- 深度深挖：深入原理的高级问题，考验技术深度和思考能力

## 答案标准
- 每道题必须附带「标准答案」+「答题思路」+「高分回答示例」
- 答案要通俗易懂，不要说正确的废话
- 高分回答示例要展示面试官想听到的完整逻辑链

## 输出格式
请按以下JSON格式输出所有面试题：
{{
    "questions": [
        {{
            "type": "题目类型",
            "difficulty": "难度等级",
            "question": "面试题目内容",
            "answer": "标准答案（清晰完整，覆盖关键知识点）",
            "answer_guide": "答题思路要点（列出回答的结构化框架）",
            "answer_script": "面试话术/高分回答示例（模拟真实的优秀面试回答）",
            "related_skills": ["相关技能1", "相关技能2"]
        }}
    ]
}}

请确保输出的JSON格式正确，可以被标准JSON解析器解析。
"""
    return prompt


def build_weakness_analysis_prompt(resume_text: str, target_position: str = "") -> str:
    prompt = f"""你是一位资深HR和职业顾问，请分析以下简历的薄弱点，并给出改进建议。

## 简历内容
{resume_text}

## 目标岗位
{target_position if target_position else "未指定"}

## 分析要求
1. 识别简历中描述模糊、不具体的地方（如"负责相关工作"、"有一定的经验"）
2. 找出缺少的关键内容（如：量化成果、具体技术细节、项目难点、团队规模）
3. 分析与目标岗位的匹配度差距
4. 指出需要补充或强化的地方
5. 识别空洞词汇（如"认真负责"、"团队合作"）并用具体事例替代建议

## 输出格式
请按以下JSON格式输出分析结果：
{{
    "weaknesses": [
        {{
            "area": "薄弱点所属领域",
            "description": "具体薄弱点描述",
            "suggestion": "改进建议（给出具体的改写示例）"
        }}
    ],
    "overall_score": "总体评分（1-10分）",
    "matching_analysis": "与目标岗位的匹配度分析",
    "top_priority_fix": "最需要优先修改的一项"
}}
"""
    return prompt


def build_interview_coach_prompt(
    resume_summary: str,
    technical_stack: list,
    weak_areas: list,
    interview_type: str,
    difficulty: str,
    question_count: int = 5,
) -> str:
    type_instruction = {
        "技术面": "只出技术面试题，深挖技术原理、架构设计、算法等",
        "HR面": "只出HR行为面试题，考察职业素养、团队协作等",
        "综合面": "混合技术题和HR行为题，比例约6:4",
    }
    weak_instruction = ""
    if weak_areas:
        weak_instruction = "\n## 重点考察弱项\n候选人以下方面较薄弱，请针对这些领域出题：\n" + "\n".join(
            f"- {w}" for w in weak_areas
        )

    prompt = f"""你是一位资深技术面试官，正在进行一场模拟面试。根据候选人简历量身出题。

## 候选人背景
{resume_summary}

技术栈：{", ".join(technical_stack) if technical_stack else "未识别"}

## 面试配置
- 面试类型：{interview_type}
- 难度：{difficulty}
- 题目数量：{question_count}道
{weak_instruction}

## 面试官角色
请模拟一位经验丰富的面试官，提问风格：
- 技术面：大厂高级工程师，追问底层原理和最佳实践
- HR面：资深HRBP，关注职业规划和软技能
- 综合面：技术总监，兼顾技术深度和综合素质

## 输出格式
以JSON格式输出：
{{
    "interview_session": {{
        "type": "{interview_type}",
        "difficulty": "{difficulty}",
        "total_questions": {question_count}
    }},
    "questions": [
        {{
            "question_number": 1,
            "type": "技术/HR/场景/压力",
            "question": "面试官提问内容",
            "expected_answer_points": ["关键点1", "关键点2", "关键点3"],
            "follow_up_question": "如果候选人回答不完整，追问的问题",
            "difficulty": "难度级别"
        }}
    ]
}}

请确保JSON格式正确。
"""
    return prompt


def build_answer_scoring_prompt(
    question_text: str,
    expected_answer_points: str,
    user_answer: str,
    question_type: str,
) -> str:
    prompt = f"""你是一位资深面试官，请对候选人的回答进行评分和反馈。

## 面试题目
{question_text}

## 期望答案要点
{expected_answer_points}

## 候选人实际回答
{user_answer}

## 题目类型
{question_type}

## 评分维度（每项0-100分）
1. **准确性**：回答是否切中问题核心，关键知识点是否正确
2. **深度**：是否展现深层理解和独立思考，而非表面回答
3. **结构**：逻辑是否清晰，STAR法则运用，层次分明
4. **表达**：语言是否简洁专业，自信且有条理
5. **亮点**：是否有量化成果、独特见解、或超出预期的内容

## 输出格式（纯JSON）
{{
    "overall_score": 85,
    "dimensions": {{
        "accuracy": {{"score": 90, "comment": "核心概念回答正确，抓住了问题重点"}},
        "depth": {{"score": 75, "comment": "能回答基本原理但缺乏深入思考和实战经验"}},
        "structure": {{"score": 80, "comment": "逻辑清晰但可以更好地组织"}},
        "expression": {{"score": 85, "comment": "表达专业简洁"}},
        "highlights": {{"score": 70, "comment": "缺少量化数据和具体成果"}}
    }},
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "improved_answer": "一个更好的回答示例（模拟优秀候选人的完整回答）",
    "key_missing_points": ["遗漏的关键点1", "遗漏的关键点2"],
    "encouragement": "对候选人的一句鼓励和具体建议"
}}

输出必须是纯JSON。
"""
    return prompt


def build_weakness_reinforcement_prompt(
    weak_areas: list,
    low_score_dimensions: list,
    resume_summary: str,
    question_count: int = 3,
) -> str:
    dim_str = ", ".join(low_score_dimensions) if low_score_dimensions else "综合"
    areas_str = "\n".join(f"- {a}" for a in weak_areas) if weak_areas else "根据答题记录中的薄弱维度"

    prompt = f"""你是一位资深面试教练，需要为候选人设计针对性强化训练题。

## 候选人背景
{resume_summary}

## 薄弱领域
{areas_str}

## 评分较低的维度
{dim_str}

## 训练目标
生成{question_count}道针对性强化题，帮助候选人弥补短板。

## 输出格式（纯JSON）
{{
    "training_focus": "本次强化训练的核心目标",
    "questions": [
        {{
            "question": "强化题内容",
            "type": "题目类型",
            "target_weakness": "针对的薄弱点",
            "answer_guide": "答题思路指引",
            "key_concepts": ["需要掌握的关键概念1", "概念2"]
        }}
    ],
    "study_tips": ["学习建议1", "学习建议2"]
}}

输出必须是纯JSON。
"""
    return prompt


def build_interview_summary_prompt(session_data: list) -> str:
    qa_text = ""
    total_score = 0
    count = 0
    for item in session_data:
        score = item.get("score", 0)
        total_score += score
        count += 1
        qa_text += f"""
Q{item.get('number', '?')}: {item.get('question', '')}
A: {item.get('answer', '')}
Score: {score}
===="""

    avg = round(total_score / count, 1) if count > 0 else 0

    prompt = f"""你是一位资深面试教练，请根据以下模拟面试记录生成总结报告。

## 面试记录
{qa_text}

## 平均分：{avg}

## 输出格式（纯JSON）
{{
    "overall_assessment": {{
        "average_score": {avg},
        "grade": "S/A/B/C/D (根据分数)",
        "summary": "整体表现评价（100字以内）"
    }},
    "top_3_strengths": ["最强项1", "最强项2", "最强项3"],
    "top_3_improvements": ["最需改进1", "最需改进2", "最需改进3"],
    "dimension_analysis": {{
        "accuracy": "准确性评价",
        "depth": "深度评价",
        "structure": "结构评价",
        "expression": "表达评价",
        "highlights": "亮点评价"
    }},
    "study_plan": [
        "接下来1周应该重点练习的内容",
        "建议阅读/学习的资源方向",
        "下次模拟面试前的准备清单"
    ],
    "next_interview_tip": "下次面试最关键的1条建议"
}}

输出必须是纯JSON。
"""
    return prompt


def build_monthly_report_prompt(
    user_name: str,
    resume_progress: str,
    interview_stats: str,
    weak_area_progress: str,
    application_funnel: str,
) -> str:
    prompt = f"""你是一位专业的职业发展顾问，请为以下用户生成本月求职进展综合报告。

## 用户姓名
{user_name}

## 简历优化历程
{resume_progress}

## 面试练习统计
{interview_stats}

## 薄弱环节进展
{weak_area_progress}

## 求职投递进度
{application_funnel}

## 报告要求
请生成一份温暖而专业的月度报告，包含：
1. 本月概览（简要总结各方面进展）
2. 简历优化成果（评分变化、关键词匹配提升等）
3. 面试能力分析（分数趋势、强项弱项）
4. 薄弱环节进展（哪些在进步，哪些还需加强）
5. 求职进度总结（投递数、面试转化率等）
6. 下月建议（具体可行的行动建议）

语言风格：温暖鼓励 + 数据驱动 + 具体可操作。
"""
    return prompt
