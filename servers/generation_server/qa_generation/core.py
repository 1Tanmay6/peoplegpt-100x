from .blueprints import ResumeQAOutput
from ...connectors import BaseConnector
from ...scoring_server.ats_scoring import JobRequirements
from dataclasses import asdict


class QAGenerator:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.connector_obj = self.connector.create_obj(
            structure=ResumeQAOutput)

    async def generate(self, resume_text: dict, job_descr: JobRequirements) -> ResumeQAOutput:

        qna_prompt = f"""
        You are an AI interview assistant. Based on the resume below, generate 10 personalized interview questions and expected answers. Make sure that you create half technical questions and other half a mix of technical, and experience. Make sure they are relevant and can connect with job description.

        Resume:
        {resume_text}

        Job Description:
        {asdict(job_descr)}

        Go Ahead generate the question answer pairs.
        """

        res = await self.connector.acall(obj=self.connector_obj, prompt=qna_prompt)

        return res


if __name__ == '__main__':
    from ...connectors import OllamaConnector

    qa = QAGenerator(OllamaConnector(thinking='thinking', model="qwen3:8b"))

    import asyncio
    example_job_requirements = JobRequirements(
        required_skills=['Python', 'Machine Learning',
                         'SQL', 'Statistics', 'Data Analysis'],
        preferred_skills=['TensorFlow',
                          'Deep Learning', 'AWS', 'Docker', 'MLOps'],
        min_experience_years=0,
        required_education='Bachleor Degree',
        industry_keywords=['Python', "Data Science", "Data Driven"],
        job_title_keywords=['data scientist',
                            'machine learning', 'analyst', 'AI engineer'],
        extra_information=[]
    )
    print(
        asyncio.run(
            qa.generate(
                resume_text={"personal_information": {"first_name": "Tanmay", "last_name": "Patil", "phone_number": "+91-8080380670", "email_address": "tanmayp162004@gmail.com", "linkedin_url": "https://www.linkedin.com/in/tanmay-patil-181820177", "website_url": "site-cv-sigma.vercel.app", "headline": "Innovative Computer Science Engineering student with a passion for Machine Learning and Web Development, currently working on state-of-the-art recommendation systems and event management tools.", "github_url": ""}, "skill": {"category": "Technical", "skill_values": ["Python", "Java", "Data Analysis", "Machine Learning", "Algorithms", "Matplotlib", "Keras", "Numpy", "LangChain", "Deep Learning", "ReactJS", "NodeJS", "NextJS", "ReduxJS", "Flask-Python", "Flutter", "Dart", "JavaScript", "Typescript", "Firebase", "MongoDB", "MYSQL", "MSSQL", "PostgreSQL", "Hadoop", "Apache Spark", "PIG", "HIVE"]}, "work_experience": [{"company_name": "Oasis Web Solutions", "job_title": "Internship", "city": "", "country": "", "from_date": "Jun 2023", "to_date": "Present", "description": "- Currently advancing towards the implementation phase of a recommendation system aimed at suggesting events to users and justifying them using an LLM. - Successfully completed Literature Survey and Methodology, which reduced development time by 30%. - Focus on building a hybrid recommendation system with feedbacks for increased user-centric approach. - Future plans include upgrading to state-of-the-art NCF to ensure continual advancement and anticipated up to 25% increase in recommendation accuracy."}, {"company_name": "Infobyte Development", "job_title": "Internship", "city": "", "country": "", "from_date": "Jul 2023", "to_date": "Present", "description": "- Initial focus on building a hybrid recommendation system with feedbacks for increased user-centric approach. - Successfully integrated LLM into the project, enhancing text generation capabilities. - Used Cloudflare and py-localtunnel for efficient tunneling."}], "education": [{"institution_name": "NIIT University", "field_of_study": "BTech CSE", "degree": "", "grade": "CGPA Bootcamp", "city": "", "country": "", "from_date": "June, 2019", "to_date": "2025", "description": "- Currently pursuing BTech in Computer Science Engineering with a focus on Machine Learning and Data Analysis. - Completed courses like Python for Data Learning, Programming & Network Essentials, PCAP: Cisco Networking essentials."}, {"institution_name": "Anglo Urdu Boys High School", "field_of_study": "", "degree": "10th", "grade": "89.20%", "city": "", "country": "", "from_date": "Feb 2019", "to_date": "May 2022", "description": "- Attended Anglo Urdu Boys High School, completed up to 12th grade with a high grade of 93.17%. - Participated in various projects and secured several achievements."}, {
                    "institution_name": "Tapti Public School", "field_of_study": "", "degree": "12th", "grade": "93.17%", "city": "", "country": "", "from_date": "May 2016", "to_date": "Jul 2017", "description": "- Attended Tapti Public School, completed up to 12th grade with a high grade of 93.17%. - Participated in various projects and secured several achievements."}], "certifications": [{"certification_name": "Python for Data Learning", "issuer": "Udemy", "certification_date": "Jun 2023", "certification_expiry_date": "Lifetime", "certification_url": "", "description": "- Successfully completed Python course on Udemy, designed for data science and machine learning applications."}, {"certification_name": "PCAP: Cisco Networking Essentials", "issuer": "Cisco", "certification_date": "Jan 2022", "certification_expiry_date": "Lifetime", "certification_url": "", "description": "- Successfully completed PCAP certification for network essentials from Cisco."}], "summary": {"profile": "Innovative Computer Science Engineering student with a passion for Machine Learning and Web Development, currently working on state-of-the-art recommendation systems and event management tools. Skilled in Python, Java, Data Analysis, and various web development frameworks like ReactJS, NodeJS, NextJS."}, "achievements": {"achievements": "- Secured 1st position in SiNusoid 2022 hackathon. - Secured 1st position in tech fair 2022. - Lead Web Developer in Google Developer Student Club at NIIT University. - Technical Manager and Robotics Club Coordinator/Manager in Google Developer Student Club at NIIT University."}, "projects": [{"title": "Recommendation System Implementation", "project_role": "Internship", "city": "", "country": "", "from_date": "Jun 2023 \u2013 Present", "to_date": "", "description": "- Currently advancing towards the implementation phase of a recommendation system aimed at suggesting events to users and justifying them using an LLM. - Successfully completed Literature Survey and Methodology, which reduced development time by 30%. - Focus on building a hybrid recommendation system with feedbacks for increased user-centric approach. - Future plans include upgrading to state-of-the-art NCF to ensure continual advancement and anticipated up to 25% increase in recommendation accuracy."}, {"title": "Ticker: Ticket Booking Application", "project_role": "Internship", "city": "", "country": "", "from_date": "June, 2019 \u2013 Present", "to_date": "", "description": "- Developed a comprehensive plane ticket booking application using Flutter and Dart. - Currently working on the website counterpart to provide a seamless user experience across platforms. - Successfully integrated Firebase as the database backend for efficient data management. - Implemented ticket printing functionality and incorporated Razorpay as a secure payment gateway. - Designed and applied customized animations for fluid and engaging page navigation."}]},
                job_descr=example_job_requirements

            )
        )
    )
