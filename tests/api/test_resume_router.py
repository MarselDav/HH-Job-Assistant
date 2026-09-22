import pytest

from llm.resume_analyzer import ResumeAnalysis, SkillItem, LanguageItem


@pytest.mark.parametrize(
    ["filename", "content", "expected_text"],
    [
        (
            "resume_example.txt",
            "Python-developer with 1 year experience",
            "Python-developer with 1 year experience"
        ),
        (
            "resume_example.txt",
            "Начинающий C++ программист",
            "Начинающий C++ программист"
        ),
        (
            "resume_example.txt",
            "",
            ""
        )
    ]
)
def test_upload_resume_success(test_resume_client,
                               mock_resume_repository,
                               filename,
                               content,
                               expected_text):


    mock_resume_repository.create.return_value = 123

    response = test_resume_client.post(
        "/upload_resume/",
        params={"name" : "ExampleResume"},
        files={
            "file": (
                filename,
                content,
                "text/plain"
            )
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "resume_id" : 123,
        "text" : expected_text
    }

    mock_resume_repository.create.assert_called_once_with(
        "ExampleResume",
        expected_text,
    )

@pytest.mark.parametrize(
    ["filename", "content", "expected_status", "expected_detail"],
    [
        (
            "resume_example.txt",
            b"\xff\xfe\xfa",
            422,
            "Файл должен быть в кодировки utf-8"
        )
    ]
)
def test_upload_resume_failure(test_resume_client,
                               mock_resume_repository,
                               filename,
                               content,
                               expected_status,
                               expected_detail):

    response = test_resume_client.post(
        "/upload_resume/",
        params={"name" : "ExampleResume"},
        files={
            "file": (
                filename,
                content,
                "text/plain"
            )
        }
    )

    assert response.status_code == expected_status
    assert response.json() == {
        "detail" : expected_detail
    }

    mock_resume_repository.create.assert_not_called()


@pytest.mark.parametrize(
    ["resume", "analysis", "expected_resume_id", "expected_resume_name", "expected_resume_analysis"],
    [
        (
            {
                "name" : "Python-developer",
                "raw_text" : "Python-developer with 1 year experience",
                "analysis" : None,
                "created_at" : "22.09.2026"
            },
            ResumeAnalysis(
                skills_sorted_by_level=[
                    SkillItem(skill="c++", level="0.9"),
                    SkillItem(skill="python", level="0.8")
                ],
                profession_name="Python-developer",
                languages_with_level=[LanguageItem(language="english", level="0.8")],
                experience="noExperience",
                brief_description="Опытный программист"
            ),
            123,
            "Python-developer",
            {
                'skills_sorted_by_level': [
                    {'skill': 'c++', 'level': '0.9'},
                    {'skill': 'python', 'level': '0.8'}
                ],
                'profession_name': 'Python-developer',
                'experience': 'noExperience',
                'languages_with_level': [{'language': 'english', 'level': '0.8'}],
                'work_formats': ['ON_SITE', 'REMOTE', 'HYBRID', 'FIELD_WORK'],
                'work_schedule_by_days': ['FIVE_ON_TWO_OFF'],
                'working_hours': ['HOURS_8'],
                'brief_description': 'Опытный программист'
            }
        ),
        (
            {
                "name" : "Python-developer",
                "raw_text" : "Python-developer with 1 year experience",
                "analysis" : {
                    'skills_sorted_by_level': [
                        {'skill': 'c++', 'level': '0.9'},
                        {'skill': 'python', 'level': '0.8'}
                    ],
                    'profession_name': 'Python-developer',
                    'experience': 'noExperience',
                    'languages_with_level': [{'language': 'english', 'level': '0.8'}],
                    'work_formats': ['ON_SITE', 'REMOTE', 'HYBRID', 'FIELD_WORK'],
                    'work_schedule_by_days': ['FIVE_ON_TWO_OFF'],
                    'working_hours': ['HOURS_8'],
                    'brief_description': 'Опытный программист'
                },
                "created_at" : "22.09.2026"
            },
            ResumeAnalysis(
                skills_sorted_by_level=[
                    SkillItem(skill="c#", level="0.9"),
                    SkillItem(skill="c++", level="0.8")
                ],
                profession_name="C++ developer",
                languages_with_level=[LanguageItem(language="english", level="0.8")],
                experience="noExperience",
                brief_description="Опытный программист"
            ),
            123,
            "Python-developer",
            {
                'skills_sorted_by_level': [
                    {'skill': 'c++', 'level': '0.9'},
                    {'skill': 'python', 'level': '0.8'}
                ],
                'profession_name': 'Python-developer',
                'experience': 'noExperience',
                'languages_with_level': [{'language': 'english', 'level': '0.8'}],
                'work_formats': ['ON_SITE', 'REMOTE', 'HYBRID', 'FIELD_WORK'],
                'work_schedule_by_days': ['FIVE_ON_TWO_OFF'],
                'working_hours': ['HOURS_8'],
                'brief_description': 'Опытный программист'
            }
        )
    ]
)
def test_analyze_resume_success(test_resume_client,
                                mock_resume_repository,
                                mock_resume_analyzer,
                                resume,
                                analysis,
                                expected_resume_id,
                                expected_resume_name,
                                expected_resume_analysis):

    mock_resume_repository.get_by_id.return_value = resume
    mock_resume_analyzer.analyze.return_value = analysis

    response = test_resume_client.get(
       f"/analyze_resume/{expected_resume_id}"
    )

    assert response.status_code == 201
    assert response.json() == {
        "resume_id": expected_resume_id,
        "resume_name": expected_resume_name,
        "resume_analysis": expected_resume_analysis,
    }

    if resume["analysis"] is None:
        mock_resume_analyzer.analyze.assert_called_once_with(
            resume["raw_text"]
        )
    else:
        mock_resume_analyzer.analyze.assert_not_called()

    mock_resume_repository.get_by_id.assert_called_once_with(
        expected_resume_id
    )