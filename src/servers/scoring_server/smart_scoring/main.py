import asyncio
import json
from typing import Dict, Any, Tuple

from .education_score import calculate_education_score
from .language_score import calculate_language_score
from .project_score import calculate_project_score
from .experience_adequate import calculate_experience_adequacy
from .work_exp_score import calculate_work_experience_score
from .relevance_score import calculate_relevance_score


async def process_candidate(candidate_tuple: Tuple) -> Dict[str, Any]:
    """
    Process a candidate's data and return comprehensive scoring analysis
    """
    _, name, email, phone, _, data = candidate_tuple

    if isinstance(data, str):
        data = json.loads(data)

    scoring_tasks = [
        calculate_education_score(data['education']),
        calculate_language_score(data['skill']),
        calculate_project_score(data['projects']),
        calculate_experience_adequacy(data),
        calculate_work_experience_score(data['work_experience']),
        calculate_relevance_score(data)
    ]

    # Wait for all scoring tasks to complete
    scores = await asyncio.gather(*scoring_tasks)

    # Compile results
    result = {
        'candidate': {
            'name': name,
            'email': email,
            'phone': phone
        },
        'scores': {
            'education': scores[0],
            'technical_skills': scores[1],
            'projects': scores[2],
            'experience_adequacy': scores[3],
            'work_experience': scores[4],
            'overall_relevance': scores[5]
        }
    }

    # Calculate final aggregate score
    total_score = (
        scores[0]['score'] * 0.2 +  # Education
        scores[1]['score'] * 0.25 +  # Technical Skills
        scores[2]['score'] * 0.15 +  # Projects
        scores[4]['score'] * 0.25 +  # Work Experience
        scores[5]['score'] * 0.15   # Overall Relevance
    )

    result['final_score'] = round(total_score, 2)
    result['is_adequate'] = scores[3]['is_adequate']
    result['recommended_level'] = scores[3]['recommended_level']

    return result


async def main():
    example_candidate = ('9bafafd2-4e16-4c89-97bb-0f18c631ebfc',
                         'Tanmay Patil',
                         'tanmayp162004@gmail.com',
                         '+91-8080380670',
                         '3f496a1c-3e16-11f0-81c1-e1be77211e00',
                         '{"personal_information": {"first_name": "Tanmay", "last_name": "Patil", "phone_number": "+91-8080380670", "email_address": "tanmayp162004@gmail.com", "linkedin_url": "https://www.linkedin.com/in/tanmay-patil-181820177", "website_url": "site-cv-sigma.vercel.app", "headline": "Innovative Computer Science Engineering student with a passion for Machine Learning and Web Development, currently working on state-of-the-art recommendation systems and event management tools.", "github_url": ""}, "skill": {"category": "Technical", "skill_values": ["Python", "Java", "Data Analysis", "Machine Learning", "Algorithms", "Matplotlib", "Keras", "Numpy", "LangChain", "Deep Learning", "ReactJS", "NodeJS", "NextJS", "ReduxJS", "Flask-Python", "Flutter", "Dart", "JavaScript", "Typescript", "Firebase", "MongoDB", "MYSQL", "MSSQL", "PostgreSQL", "Hadoop", "Apache Spark", "PIG", "HIVE"]}, "work_experience": [{"company_name": "Oasis Web Solutions", "job_title": "Internship", "city": "", "country": "", "from_date": "Jun 2023", "to_date": "Present", "description": "- Currently advancing towards the implementation phase of a recommendation system aimed at suggesting events to users and justifying them using an LLM. - Successfully completed Literature Survey and Methodology, which reduced development time by 30%. - Focus on building a hybrid recommendation system with feedbacks for increased user-centric approach. - Future plans include upgrading to state-of-the-art NCF to ensure continual advancement and anticipated up to 25% increase in recommendation accuracy."}, {"company_name": "Infobyte Development", "job_title": "Internship", "city": "", "country": "", "from_date": "Jul 2023", "to_date": "Present", "description": "- Initial focus on building a hybrid recommendation system with feedbacks for increased user-centric approach. - Successfully integrated LLM into the project, enhancing text generation capabilities. - Used Cloudflare and py-localtunnel for efficient tunneling."}], "education": [{"institution_name": "NIIT University", "field_of_study": "BTech CSE", "degree": "", "grade": "CGPA Bootcamp", "city": "", "country": "", "from_date": "June, 2019", "to_date": "2025", "description": "- Currently pursuing BTech in Computer Science Engineering with a focus on Machine Learning and Data Analysis. - Completed courses like Python for Data Learning, Programming & Network Essentials, PCAP: Cisco Networking essentials."}, {"institution_name": "Anglo Urdu Boys High School", "field_of_study": "", "degree": "10th", "grade": "89.20%", "city": "", "country": "", "from_date": "Feb 2019", "to_date": "May 2022", "description": "- Attended Anglo Urdu Boys High School, completed up to 12th grade with a high grade of 93.17%. - Participated in various projects and secured several achievements."}, {"institution_name": "Tapti Public School", "field_of_study": "", "degree": "12th", "grade": "93.17%", "city": "", "country": "", "from_date": "May 2016", "to_date": "Jul 2017", "description": "- Attended Tapti Public School, completed up to 12th grade with a high grade of 93.17%. - Participated in various projects and secured several achievements."}], "certifications": [{"certification_name": "Python for Data Learning", "issuer": "Udemy", "certification_date": "Jun 2023", "certification_expiry_date": "Lifetime", "certification_url": "", "description": "- Successfully completed Python course on Udemy, designed for data science and machine learning applications."}, {"certification_name": "PCAP: Cisco Networking Essentials", "issuer": "Cisco", "certification_date": "Jan 2022", "certification_expiry_date": "Lifetime", "certification_url": "", "description": "- Successfully completed PCAP certification for network essentials from Cisco."}], "summary": {"profile": "Innovative Computer Science Engineering student with a passion for Machine Learning and Web Development, currently working on state-of-the-art recommendation systems and event management tools. Skilled in Python, Java, Data Analysis, and various web development frameworks like ReactJS, NodeJS, NextJS."}, "achievements": {"achievements": "- Secured 1st position in SiNusoid 2022 hackathon. - Secured 1st position in tech fair 2022. - Lead Web Developer in Google Developer Student Club at NIIT University. - Technical Manager and Robotics Club Coordinator/Manager in Google Developer Student Club at NIIT University."}, "projects": [{"title": "Recommendation System Implementation", "project_role": "Internship", "city": "", "country": "", "from_date": "Jun 2023", "to_date": "Present", "description": "- Currently advancing towards the implementation phase of a recommendation system aimed at suggesting events to users and justifying them using an LLM. - Successfully completed Literature Survey and Methodology, which reduced development time by 30%. - Focus on building a hybrid recommendation system with feedbacks for increased user-centric approach. - Future plans include upgrading to state-of-the-art NCF to ensure continual advancement and anticipated up to 25% increase in recommendation accuracy."}, {"title": "Ticker: Ticket Booking Application", "project_role": "Internship", "city": "", "country": "", "from_date": "June, 2019", "to_date": "Present", "description": "- Developed a comprehensive plane ticket booking application using Flutter and Dart. - Currently working on the website counterpart to provide a seamless user experience across platforms. - Successfully integrated Firebase as the database backend for efficient data management. - Implemented ticket printing functionality and incorporated Razorpay as a secure payment gateway. - Designed and applied customized animations for fluid and engaging page navigation."}]}')

    try:
        result = await process_candidate(example_candidate)
        print("\nCandidate Evaluation Results:")
        print("=" * 50)
        print(f"Name: {result['candidate']['name']}")
        print(f"Email: {result['candidate']['email']}")
        print("\nScores:")
        print("-" * 50)
        for category, score_data in result['scores'].items():
            print(
                f"{category.replace('_', ' ').title()}: {score_data['score']}")
        print("-" * 50)
        print(f"Final Score: {result['final_score']}")
        print(f"Experience Level: {result['recommended_level']}")
        print(f"Is Adequate: {result['is_adequate']}")

    except Exception as e:
        print(f"Error processing candidate: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
