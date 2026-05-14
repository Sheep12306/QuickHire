import pytest
import sys
sys.path.insert(0, '..')

from resume_parser import (
    parse_resume_text,
    extract_email,
    extract_phone,
    extract_personal_info,
    extract_skills
)
from prompt_builder import (
    build_optimize_prompt,
    build_interview_question_prompt
)
from api_client import validate_api_key, validate_prompt


class TestResumeParser:
    def test_extract_email(self):
        assert extract_email("邮箱: test@example.com") == "test@example.com"
        assert extract_email("联系邮箱: abc@163.com") == "abc@163.com"
        assert extract_email("没有邮箱") is None

    def test_extract_phone(self):
        assert extract_phone("电话: 13800138000") == "13800138000"
        assert extract_phone("手机：15912345678") == "15912345678"
        assert extract_phone("没有电话") is None

    def test_extract_personal_info(self):
        text = """
        张三
        邮箱：zhangsan@example.com
        电话：13800138000
        """
        info = extract_personal_info(text)
        assert info.get("email") == "zhangsan@example.com"
        assert info.get("phone") == "13800138000"

    def test_extract_skills(self):
        text = """
        技能特长：
        - Python, Java, JavaScript
        - Django, Flask
        - MySQL, PostgreSQL
        - Docker, Git
        """
        skills = extract_skills(text)
        assert "Python" in skills["technical"]
        assert "Django" in skills["technical"]
        assert "MySQL" in skills["technical"]

    def test_parse_resume_text(self):
        text = """
        姓名：李四
        邮箱：lisi@example.com
        电话：13800138001

        技能特长：
        Python, Java, MySQL
        """
        result = parse_resume_text(text)
        assert "personal_info" in result
        assert "skills" in result
        assert result["personal_info"]["email"] == "lisi@example.com"


class TestPromptBuilder:
    def test_build_optimize_prompt(self):
        prompt = build_optimize_prompt(
            resume_text="测试简历内容",
            target_position="Python开发",
            optimization_style="简洁专业",
            word_limit=800
        )
        assert "测试简历内容" in prompt
        assert "Python开发" in prompt
        assert "使用专业术语" in prompt
        assert "800" in prompt

    def test_build_interview_question_prompt(self):
        prompt = build_interview_question_prompt(
            resume_summary="测试简历摘要",
            technical_stack=["Python", "Django"],
            project_highlights=["项目1", "项目2"],
            difficulty="中等",
            question_types=["简答题"],
            scope="仅技术面试",
            question_count=5
        )
        assert "测试简历摘要" in prompt
        assert "Python" in prompt
        assert "中等" in prompt
        assert "简答题" in prompt


class TestAPIClient:
    def test_validate_api_key(self):
        assert validate_api_key("") is False
        assert validate_api_key("your_api_key_here") is False
        assert validate_api_key("sk-123456") is True

    def test_validate_prompt(self):
        assert validate_prompt("") is False
        assert validate_prompt("   ") is False
        assert validate_prompt(None) is False
        assert validate_prompt("valid prompt") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])