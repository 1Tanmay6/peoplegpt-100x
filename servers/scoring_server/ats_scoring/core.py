import re
import json
import difflib
from datetime import datetime
from typing import Dict, List, Any

from .blueprints import JobRequirements, ScoringWeights


class ATSScorer:
    def __init__(self, job_requirements: JobRequirements, weights: ScoringWeights = None):
        self.job_requirements = job_requirements
        self.weights = weights or ScoringWeights()
        self.threshold_score = 60.0

    def calculate_overall_score(self, resume_data: Dict) -> Dict[str, Any]:
        try:
            scores = {
                'skills_score': self._safe_call(self._calculate_skills_score, resume_data),
                'experience_score': self._safe_call(self._calculate_experience_score, resume_data),
                'education_score': self._safe_call(self._calculate_education_score, resume_data),
                'progression_score': self._safe_call(self._calculate_career_progression_score, resume_data),
                'project_score': self._safe_call(self._calculate_project_score, resume_data),
                'recency_score': self._safe_call(self._calculate_recency_score, resume_data),
                'completeness_score': self._safe_call(self._calculate_completeness_score, resume_data)
            }

            overall_score = (
                scores['skills_score'] * self.weights.skills_match +
                scores['experience_score'] * self.weights.experience_relevance +
                scores['education_score'] * self.weights.education_match +
                scores['progression_score'] * self.weights.career_progression +
                scores['project_score'] * self.weights.project_relevance +
                scores['recency_score'] * self.weights.recency +
                scores['completeness_score'] * self.weights.completeness
            )

            return {
                'overall_score': round(overall_score, 2),
                'detailed_scores': scores,
                'pass_threshold': overall_score >= self.threshold_score,
                'candidate_name': f"{resume_data.get('personal_information', {}).get('first_name', '')} {resume_data.get('personal_information', {}).get('last_name', '')}".strip(),
            }
        except Exception as e:
            return {
                'overall_score': 0.0,
                'detailed_scores': {},
                'pass_threshold': False,
                'candidate_name': '',
                'error': str(e)
            }

    def _safe_call(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return 0.0

    def _calculate_skills_score(self, resume_data: Dict) -> float:
        """Calculate skills matching score (0-100)"""
        skill_info = resume_data.get('skill', {})
        if not skill_info:
            return 0.0

        resume_skills = []
        skill_values = skill_info.get('skill_values', [])

        for skill_text in skill_values:
            resume_skills.extend(self._extract_skills_from_text(skill_text))

        resume_skills = [skill.lower().strip() for skill in resume_skills]
        required_skills = [skill.lower().strip()
                           for skill in self.job_requirements.required_skills]
        preferred_skills = [skill.lower().strip()
                            for skill in self.job_requirements.preferred_skills]

        required_matches = self._fuzzy_skill_match(
            resume_skills, required_skills)
        preferred_matches = self._fuzzy_skill_match(
            resume_skills, preferred_skills)

        if not required_skills:
            required_score = 100
        else:
            required_score = (required_matches / len(required_skills)) * 100

        if not preferred_skills:
            preferred_score = 100
        else:
            preferred_score = (preferred_matches / len(preferred_skills)) * 100

        final_score = (required_score * 0.7) + (preferred_score * 0.3)
        return min(100, final_score)

    def _calculate_experience_score(self, resume_data: Dict) -> float:
        """Calculate experience relevance score (0-100)"""
        work_experiences = resume_data.get('work_experience', [])
        if not work_experiences:
            return 0.0

        total_score = 0
        max_score = 0

        for exp in work_experiences:
            exp_score = 0
            max_exp_score = 100

            job_title = exp.get('job_title', '').lower()
            title_relevance = self._calculate_keyword_relevance(
                job_title, self.job_requirements.job_title_keywords
            )
            exp_score += title_relevance * 30

            description = exp.get('description', '').lower()
            desc_relevance = self._calculate_keyword_relevance(
                description, self.job_requirements.industry_keywords
            )
            exp_score += desc_relevance * 40

            duration = self._calculate_experience_duration(exp)

            duration_score = min(20, duration * 4)
            exp_score += duration_score

            company_score = 10 if exp.get('company_name') else 5
            exp_score += company_score

            total_score += exp_score
            max_score += max_exp_score

        if max_score == 0:
            return 0

        return min(100, (total_score / max_score) * 100)

    def _calculate_education_score(self, resume_data: Dict) -> float:
        """Calculate education matching score (0-100)"""
        educations = resume_data.get('education', [])
        if not educations:
            return 30.0

        max_score = 0
        required_education_lower = self.job_requirements.required_education.lower()

        for edu in educations:
            score = 0
            degree = edu.get('degree', '').lower()
            field = edu.get('field_of_study', '').lower()
            grade = edu.get('grade', '')

            if 'bachelor' in required_education_lower and 'bachelor' in degree:
                score += 60
            elif 'master' in required_education_lower and 'master' in degree:
                score += 70
            elif 'phd' in required_education_lower or 'doctorate' in required_education_lower:
                if 'phd' in degree or 'doctorate' in degree:
                    score += 80
            elif degree:
                score += 40

            field_keywords = ['computer', 'data',
                              'engineering', 'science', 'technology']
            for keyword in field_keywords:
                if keyword in field:
                    score += 5
                    break
            if 'data science' in field or 'computer science' in field:
                score += 25

            if grade:
                try:
                    if '/' in grade:
                        grade_num = float(grade.split('/')[0])
                        grade_max = float(grade.split('/')[1])
                        grade_percentage = (grade_num / grade_max) * 100
                    else:
                        grade_percentage = float(grade)

                    if grade_percentage >= 85:
                        score += 15
                    elif grade_percentage >= 75:
                        score += 10
                    elif grade_percentage >= 65:
                        score += 5
                except:
                    score += 5

            max_score = max(max_score, score)

        return min(100, max_score)

    def _calculate_career_progression_score(self, resume_data: Dict) -> float:
        """Calculate career progression score (0-100)"""
        work_experiences = resume_data.get('work_experience', [])
        if len(work_experiences) < 2:
            return 50.0

        sorted_exp = sorted(work_experiences,
                            key=lambda x: self._parse_date(x.get('from_date', '')))

        progression_score = 50

        titles = [exp.get('job_title', '').lower() for exp in sorted_exp]
        progression_keywords = ['intern', 'junior',
                                'senior', 'lead', 'manager', 'director']

        title_levels = []
        for title in titles:
            level = 0
            for i, keyword in enumerate(progression_keywords):
                if keyword in title:
                    level = i
                    break
            title_levels.append(level)

        for i in range(1, len(title_levels)):
            if title_levels[i] > title_levels[i-1]:
                progression_score += 15
            elif title_levels[i] == title_levels[i-1]:
                progression_score += 5

        companies = [exp.get('company_name', '') for exp in sorted_exp]
        if len(set(companies)) > 1:
            progression_score += 10

        return min(100, progression_score)

    def _calculate_project_score(self, resume_data: Dict) -> float:
        """Calculate project relevance score (0-100)"""
        projects = resume_data.get('projects', [])
        if not projects:
            print('NOOOOOO')
            return 0.0

        total_score = 0

        for project in projects:
            project_score = 0
            title = project.get('title', '').lower()
            description = project.get('description', '').lower()

            title_relevance = self._calculate_keyword_relevance(
                title, self.job_requirements.industry_keywords +
                self.job_requirements.required_skills
            )
            project_score += title_relevance * 30

            desc_relevance = self._calculate_keyword_relevance(
                description, self.job_requirements.industry_keywords +
                self.job_requirements.required_skills
            )
            project_score += desc_relevance * 40

            duration = self._calculate_project_duration(project)
            project_score += min(30, duration * 10)

            total_score += project_score

        avg_score = total_score / len(projects) if projects else 0
        return min(100, avg_score)

    def _calculate_recency_score(self, resume_data: Dict) -> float:
        """Calculate recency score based on latest experience (0-100)"""
        work_experiences = resume_data.get('work_experience', [])
        if not work_experiences:
            return 50.0

        latest_end_date = None
        for exp in work_experiences:
            end_date = exp.get('to_date', '')
            if end_date.lower() in ['present', 'current', '']:
                return 100.0

            parsed_date = self._parse_date(end_date)
            if parsed_date and (latest_end_date is None or parsed_date > latest_end_date):
                latest_end_date = parsed_date

        if not latest_end_date:
            return 50.0

        current_date = datetime.now()
        months_since = (current_date.year - latest_end_date.year) * \
            12 + (current_date.month - latest_end_date.month)

        if months_since <= 6:
            return 100.0
        elif months_since <= 12:
            return 80.0
        elif months_since <= 24:
            return 60.0
        elif months_since <= 36:
            return 40.0
        else:
            return 20.0

    def _calculate_completeness_score(self, resume_data: Dict) -> float:
        """Calculate resume completeness score (0-100)"""
        score = 0
        max_score = 100

        personal_info = resume_data.get('personal_information', {})
        if personal_info.get('first_name') and personal_info.get('last_name'):
            score += 5
        if personal_info.get('email_address'):
            score += 5
        if personal_info.get('phone_number'):
            score += 5
        if personal_info.get('linkedin_url') or personal_info.get('website_url') or personal_info.get('github_url'):
            score += 5

        if resume_data.get('work_experience'):
            score += 30

        if resume_data.get('education'):
            score += 20

        if resume_data.get('skill', {}).get('skill_values'):
            score += 20

        if resume_data.get('projects'):
            score += 10

        return score

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract individual skills from skill text"""

        skills = re.split(r'[,;|:]', text)

        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()

            skill = re.sub(r'^[^:]*:\s*', '', skill)
            if skill and len(skill) > 1:
                cleaned_skills.append(skill)

        return cleaned_skills

    def _fuzzy_skill_match(self, resume_skills: List[str], required_skills: List[str]) -> int:
        """Count fuzzy matches between resume and required skills"""
        matches = 0

        for req_skill in required_skills:
            for resume_skill in resume_skills:

                if req_skill in resume_skill or resume_skill in req_skill:
                    matches += 1
                    break

                elif difflib.SequenceMatcher(None, req_skill, resume_skill).ratio() > 0.8:
                    matches += 1
                    break

        return matches

    def _calculate_keyword_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword relevance score (0-1)"""
        if not keywords:
            return 1.0

        text_lower = text.lower()
        matches = sum(
            1 for keyword in keywords if keyword.lower() in text_lower)
        return matches / len(keywords)

    def _calculate_experience_duration(self, experience: Dict) -> float:
        """Calculate experience duration in years"""
        from_date = self._parse_date(experience.get('from_date', ''))
        to_date_str = experience.get('to_date', '')

        if to_date_str.lower() in ['present', 'current', '']:
            to_date = datetime.now()
        else:
            to_date = self._parse_date(to_date_str)

        if not from_date or not to_date:
            return 0.0

        duration = to_date - from_date
        return duration.days / 365.25

    def _calculate_project_duration(self, project: Dict) -> float:
        """Calculate project duration in years"""
        return self._calculate_experience_duration(project)

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        if not date_str:
            return None

        date_str = date_str.strip()

        formats = [
            '%b %Y',
            '%B %Y',
            '%m/%Y',
            '%Y-%m',
            '%Y',
            '%m %Y'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None
