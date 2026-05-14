import re
from collections import Counter


class ResumeDefectDetector:
    def __init__(self):
        self.weak_patterns = {
            'vague_descriptions': [
                r'(负责相关工作|参与相关项目|完成相关任务)',
                r'(有一定的|相关的)',
                r'(熟悉|了解|掌握)\s*[a-zA-Z\u4e00-\u9fa5]+',
                r'(良好的|较强的)\s*(能力|经验)'
            ],
            'empty_phrases': [
                r'(认真负责|团队合作|沟通能力)',
                r'(学习能力强|工作积极主动)',
                r'(吃苦耐劳|责任心强)',
                r'(有较强的.*能力)'
            ],
            'passive_voice': [
                r'(被.*负责|由.*完成|被.*设计)',
                r'(获得.*奖励|荣获.*称号)'
            ],
            'repetitive_content': [
                r'(\b\w+\b)\s+\1'
            ],
            'missing_keywords': []
        }

        self.professional_verbs = [
            '负责', '主导', '设计', '开发', '优化', '实现',
            '搭建', '架构', '规划', '推动', '解决', '提升',
            '重构', '集成', '测试', '部署', '运维', '管理',
            '分析', '调研', '评估', '制定', '执行', '协调'
        ]

        self.quantification_words = [
            '增加', '减少', '提高', '降低', '优化', '节省',
            '完成', '达成', '实现', '突破', '达到', '超越'
        ]

    def detect_vague_descriptions(self, resume_text):
        defects = []
        for pattern in self.weak_patterns['vague_descriptions']:
            matches = re.findall(pattern, resume_text)
            for match in matches[:3]:
                defects.append({
                    'type': 'vague_description',
                    'severity': 'medium',
                    'description': f'发现模糊描述: "{match}"',
                    'suggestion': '建议使用具体的职责描述和成果量化'
                })
        return defects

    def detect_empty_phrases(self, resume_text):
        defects = []
        for pattern in self.weak_patterns['empty_phrases']:
            matches = re.findall(pattern, resume_text)
            for match in matches[:3]:
                defects.append({
                    'type': 'empty_phrase',
                    'severity': 'low',
                    'description': f'发现空洞描述: "{match}"',
                    'suggestion': '建议使用具体事例或成果代替通用描述'
                })
        return defects

    def detect_passive_voice(self, resume_text):
        defects = []
        for pattern in self.weak_patterns['passive_voice']:
            matches = re.findall(pattern, resume_text)
            for match in matches[:3]:
                defects.append({
                    'type': 'passive_voice',
                    'severity': 'low',
                    'description': f'发现被动语态: "{match}"',
                    'suggestion': '建议使用主动语态，突出个人贡献'
                })
        return defects

    def detect_repetition(self, resume_text):
        defects = []
        words = re.findall(r'[\u4e00-\u9fa5]{2,}', resume_text)
        word_counts = Counter(words)
        repetitive_words = [(word, count) for word, count in word_counts.items() if count >= 5]

        for word, count in repetitive_words[:3]:
            defects.append({
                'type': 'repetition',
                'severity': 'low',
                'description': f'发现重复使用: "{word}" ({count}次)',
                'suggestion': '建议使用同义词替换，增加语言多样性'
            })
        return defects

    def detect_keyword_gaps(self, resume_text, required_keywords):
        defects = []
        text_lower = resume_text.lower()
        missing_keywords = []

        for keyword in required_keywords:
            if keyword.lower() not in text_lower:
                missing_keywords.append(keyword)

        if missing_keywords:
            defects.append({
                'type': 'keyword_gap',
                'severity': 'high',
                'description': f'缺少关键技能关键词: {", ".join(missing_keywords[:5])}',
                'suggestion': f'建议在简历中适当提及以下关键词: {", ".join(missing_keywords[:5])}'
            })

        return defects

    def analyze_action_verbs(self, resume_text):
        defects = []
        verb_count = sum(1 for verb in self.professional_verbs if verb in resume_text)

        if verb_count < 5:
            defects.append({
                'type': 'weak_action_verbs',
                'severity': 'medium',
                'description': f'专业动词使用较少（仅{verb_count}个）',
                'suggestion': f'建议增加专业动词使用，如: {", ".join(self.professional_verbs[:10])}'
            })

        return defects

    def analyze_quantification(self, resume_text):
        defects = []
        quant_patterns = [r'\d+[%％]', r'\d+[万千万亿]', r'\d+\+', r'\d+[\u4e00-\u9fa5]{1,2}']
        quant_count = sum(len(re.findall(pattern, resume_text)) for pattern in quant_patterns)

        if quant_count < 3:
            defects.append({
                'type': 'lack_quantification',
                'severity': 'high',
                'description': f'量化数据较少（仅{quant_count}处）',
                'suggestion': '建议增加量化成果描述，如"提升效率30%"、"处理100+用户请求"'
            })

        return defects

    def detect_all_defects(self, resume_text, required_keywords=None):
        all_defects = []

        all_defects.extend(self.detect_vague_descriptions(resume_text))
        all_defects.extend(self.detect_empty_phrases(resume_text))
        all_defects.extend(self.detect_passive_voice(resume_text))
        all_defects.extend(self.detect_repetition(resume_text))
        all_defects.extend(self.analyze_action_verbs(resume_text))
        all_defects.extend(self.analyze_quantification(resume_text))

        if required_keywords:
            all_defects.extend(self.detect_keyword_gaps(resume_text, required_keywords))

        all_defects.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['severity']])

        return all_defects

    def get_severity_summary(self, defects):
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        for defect in defects:
            severity_counts[defect['severity']] += 1

        return severity_counts

    def generate_optimization_suggestions(self, resume_text, required_keywords=None):
        defects = self.detect_all_defects(resume_text, required_keywords)
        severity_summary = self.get_severity_summary(defects)

        suggestions = []

        if severity_summary['high'] > 0:
            suggestions.append({
                'priority': 'high',
                'title': '优先改进',
                'items': [d['suggestion'] for d in defects if d['severity'] == 'high']
            })

        if severity_summary['medium'] > 0:
            suggestions.append({
                'priority': 'medium',
                'title': '建议改进',
                'items': [d['suggestion'] for d in defects if d['severity'] == 'medium']
            })

        if severity_summary['low'] > 0:
            suggestions.append({
                'priority': 'low',
                'title': '细节优化',
                'items': [d['suggestion'] for d in defects if d['severity'] == 'low']
            })

        return {
            'defects': defects,
            'severity_summary': severity_summary,
            'suggestions': suggestions
        }