import re
from typing import Dict, List, Optional, Any


def extract_email(text: str) -> Optional[str]:
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    pattern = r'1[3-9]\d{9}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_personal_info(text: str) -> Dict[str, str]:
    info = {}

    email = extract_email(text)
    if email:
        info["email"] = email

    phone = extract_phone(text)
    if phone:
        info["phone"] = phone

    name_match = re.search(r'^([\u4e00-\u9fa5]{2,4})(?:\s|,|，|$)', text, re.MULTILINE)
    if name_match:
        info["name"] = name_match.group(1)

    age_match = re.search(r'(?:age|年龄)[:：]?\s*(\d{1,3})', text, re.I)
    if age_match:
        info["age"] = age_match.group(1)

    location_match = re.search(r'([\u4e00-\u9fa5]{2,6})(?:市|区|省)', text)
    if location_match:
        info["location"] = location_match.group(1)

    return info


def extract_education(text: str) -> List[Dict[str, str]]:
    education_list = []

    education_section = re.split(r'(?:教育经历|学历背景|Education)', text, flags=re.I)
    if len(education_section) > 1:
        content = education_section[1]
        next_section = re.split(r'(?:工作经历|项目经历|实习经历|技能特长)', content, flags=re.I)
        content = next_section[0]
    else:
        content = text

    patterns = [
        r'([\u4e00-\u9fa5]{4,20}?大学|[\u4e00-\u9fa5]{4,20}?学院)\s*[-–]?\s*([^\n]{1,30})',
        r'([\u4e00-\u9fa5]{2,10}?大学|[\u4e00-\u9fa5]{2,10}?学院)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            school = match.group(1).strip()
            degree_info = match.group(2).strip() if match.lastindex >= 2 else ""

            entry = {
                "school": school,
                "degree": degree_info or "本科"
            }

            time_match = re.search(r'(20\d{2}|19\d{2})\s*[-~至]\s*(20\d{2}|19\d{2}|至今|现在)', content)
            if time_match:
                entry["duration"] = f"{time_match.group(1)} - {time_match.group(2)}"

            if entry not in education_list:
                education_list.append(entry)

    return education_list


def extract_work_experience(text: str) -> List[Dict[str, str]]:
    experience_list = []

    experience_section = re.split(r'(?:工作经历|职业经历|Employment|Experience)', text, flags=re.I)
    if len(experience_section) > 1:
        content = experience_section[1]
        next_section = re.split(r'(?:项目经历|教育经历|技能特长)', content, flags=re.I)
        content = next_section[0]
    else:
        return experience_list

    company_pattern = r'([\u4e00-\u9fa5a-zA-Z0-9]{2,30}?(?:公司|企业|集团|机构))\s*[-–|]\s*([^ \n]{1,20})'
    matches = re.finditer(company_pattern, content)

    for match in matches:
        company = match.group(1).strip()
        position = match.group(2).strip()

        entry = {
            "company": company,
            "position": position,
            "description": ""
        }

        date_match = re.search(r'(20\d{2}|19\d{2})\s*[-./~至]\s*(20\d{2}|19\d{2}|至今|现在|\d+个月)', content)
        if date_match:
            entry["duration"] = f"{date_match.group(1)} - {date_match.group(2)}"

        experience_list.append(entry)

    return experience_list


def extract_projects(text: str) -> List[Dict[str, Any]]:
    project_list = []

    project_section = re.split(r'(?:项目经历|项目经验|Projects)', text, flags=re.I)
    if len(project_section) > 1:
        content = project_section[1]
        next_section = re.split(r'(?:工作经历|教育经历|技能特长|实习经历)', content, flags=re.I)
        content = next_section[0]
    else:
        return project_list

    project_blocks = re.split(r'(?:^|\n)(?=\d+[.、]|\*\*|[\u4e00-\u9fa5]{2,10}?项目)', content)

    for block in project_blocks:
        if len(block.strip()) < 10:
            continue

        project = {
            "name": "",
            "role": "",
            "tech_stack": [],
            "description": block.strip(),
            "highlights": []
        }

        name_match = re.search(r'([\u4e00-\u9fa5a-zA-Z0-9]{2,30}?项目)', block)
        if name_match:
            project["name"] = name_match.group(1)

        role_patterns = [
            r'(?:担任|负责|角色)[:：]?\s*([^\n,，]{1,20})',
            r'(?:前端|后端|全栈|开发|设计|负责人)\s*[-–]?\s*([^\n,，]{0,15})'
        ]
        for pattern in role_patterns:
            role_match = re.search(pattern, block)
            if role_match:
                project["role"] = role_match.group(1).strip()
                break

        tech_stack = re.findall(r'(?:Python|Java|JavaScript|Go|Rust|C\+\+|React|Vue|Angular|Spring|Django|Flask|Node\.js|MySQL|PostgreSQL|MongoDB|Redis|Kubernetes|Docker|Linux|Git|SVN|Swift|Kotlin|Ruby|PHP|R|C#|TypeScript|HTML|CSS|SASS|LESS|jQuery|Bootstrap|Tailwind|Vue\.js|React\.js|Node\.js|Next\.js|Nuxt\.js|TensorFlow|PyTorch|Scikit-learn|Keras|Pandas|NumPy|OpenCV|OpenGL|Three\.js|ECharts|AntV|D3\.js)', block, re.I)
        if tech_stack:
            project["tech_stack"] = list(set([t.capitalize() for t in tech_stack]))

        highlights = re.findall(r'(?:成果|业绩|亮点|成绩)[:：]?\s*([^。\n]{5,50})', block, re.I)
        project["highlights"] = highlights

        if project["name"] or project["description"]:
            project_list.append(project)

    return project_list


def extract_skills(text: str) -> Dict[str, List[str]]:
    skills = {
        "technical": [],
        "soft": []
    }

    skills_section = re.split(r'(?:技能特长|专业技能|技术栈|Skills)', text, flags=re.I)
    if len(skills_section) > 1:
        content = skills_section[1]
        next_section = re.split(r'(?:项目经历|工作经历|教育经历)', content, flags=re.I)
        content = next_section[0]
    else:
        content = text

    technical_keywords = [
        'Python', 'Java', 'JavaScript', 'Go', 'Rust', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring', 'MySQL', 'PostgreSQL',
        'MongoDB', 'Redis', 'Docker', 'Kubernetes', 'Linux', 'Git', 'TensorFlow', 'PyTorch',
        'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'API', 'REST', 'GraphQL',
        'HTML', 'CSS', 'TypeScript', 'jQuery', 'Bootstrap', 'SASS', 'LESS', 'Webpack', 'Vite'
    ]

    found_technical = set()
    for keyword in technical_keywords:
        if re.search(r'\b' + keyword + r'\b', content, re.I):
            found_technical.add(keyword)

    skills["technical"] = sorted(list(found_technical))

    soft_keywords = ['团队协作', '沟通能力', '问题解决', '学习能力', '抗压能力', '领导力', '创新思维', '项目管理', '时间管理']
    for keyword in soft_keywords:
        if keyword in content:
            skills["soft"].append(keyword)

    return skills


def parse_resume_text(text: str) -> Dict[str, Any]:
    if not text or not isinstance(text, str):
        return {
            "personal_info": {},
            "education": [],
            "experience": [],
            "projects": [],
            "skills": {"technical": [], "soft": []}
        }

    text = text.strip()

    personal_info = extract_personal_info(text)
    education = extract_education(text)
    experience = extract_work_experience(text)
    projects = extract_projects(text)
    skills = extract_skills(text)

    return {
        "personal_info": personal_info,
        "education": education,
        "experience": experience,
        "projects": projects,
        "skills": skills
    }


def resume_to_summary(resume_data: Dict[str, Any]) -> str:
    parts = []

    if resume_data.get("personal_info", {}).get("name"):
        parts.append(f"姓名: {resume_data['personal_info']['name']}")

    if resume_data.get("personal_info", {}).get("email"):
        parts.append(f"邮箱: {resume_data['personal_info']['email']}")

    if resume_data.get("education"):
        edu = resume_data["education"][0]
        parts.append(f"教育: {edu.get('school', '')} {edu.get('degree', '')}")

    if resume_data.get("skills", {}).get("technical"):
        techs = resume_data["skills"]["technical"][:10]
        parts.append(f"技术栈: {', '.join(techs)}")

    if resume_data.get("experience"):
        parts.append(f"工作经历: {len(resume_data['experience'])}段")

    if resume_data.get("projects"):
        parts.append(f"项目经验: {len(resume_data['projects'])}个")

    return "\n".join(parts) if parts else "简历信息提取不完整"