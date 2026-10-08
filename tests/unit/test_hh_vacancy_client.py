import pytest

from hh.hh_models import SalaryInfo
from hh.hh_vacancy_client import HHVacancyClient


@pytest.mark.parametrize(
    ["company_info", "expected_result"],
    [({'logos': {'logo': [
        {
            '@type': 'ORIGINAL',
            '@url': '/employer-logo-original/1530092.png'
        },
        {
            '@type': 'small',
            '@url': '/employer-logo/12410688.png'},
        {
            '@type': 'vacancyPage',
            '@url': '/employer-logo/12410689.png'},
        {
            '@type': 'medium',
            '@url': '/employer-logo/12410689.png'
        }]}},
        '/employer-logo/12410688.png'
    ),
    ({'logos': {'logo': [
        {
            '@type': 'ORIGINAL',
            '@url': '/employer-logo-original/1530092.png'
        },
        {
            '@type': 'employerPage',
            '@url': '/employer-logo/12410687.png'
        },
        {
            '@type': 'searchResultsPage',
            '@url': '/employer-logo/12410688.png'
        },
        ]}},
        '/employer-logo-original/1530092.png'
    ),
    ({'logos': {'logo': [
        {
            '@type': 'ORIGINAL',
            '@url': '/employer-logo-original/1530092.png'
        },
        {
            '@type': 'small'
        },
        {
            '@type': 'searchResultsPage',
            '@url': '/employer-logo/12410689.png'
        },
        ]}},
        '/employer-logo-original/1530092.png'
    ),
    ({'logos': {'logo': [
        {
            '@type': 'small'
        },
        {
            '@type': 'searchResultsPage',
            '@url': '/employer-logo/12410689.png'
        },
        ]}},
        None
    ),
    ({'logos': {'logo': [
        {
            '@type': 'searchResultsPage',
            '@url': '/employer-logo/12410689.png'
        },
        ]}},
        None
    ),
    ]
)
def test_parse_logo_info(test_hh_vacancy_client : HHVacancyClient,
                         company_info : dict,
                         expected_result : str):
    assert test_hh_vacancy_client._parse_logo_info(company_info, "small") == expected_result


@pytest.mark.parametrize(
    ["salary_info", "expected_result"],
    [
        (
            {
                'currencyCode': 'RUR',
                'from': 200000,
                'gross': True,
                'mode': 'MONTH',
                'perModeFrom': 200000
            },
            SalaryInfo(
                salary_from=200000,
                salary_to=None,
                salary_mode='MONTH',
                currency='RUR'
            )
        ),
        (
            {
                'currencyCode': 'RUR',
                'to': 160000,
                'gross': True,
                'mode': 'MONTH',
                'perModeFrom': 200000
            },
            SalaryInfo(
                salary_from=None,
                salary_to=160000,
                salary_mode='MONTH',
                currency='RUR'
            )
        ),
        (
            {
                'from': 80000,
                'to': 150000,
                'currencyCode': 'RUR',
                'gross': False,
                'perModeFrom': 80000,
                'perModeTo': 150000,
                'mode': 'MONTH',
                'frequency': 'TWICE_PER_MONTH'
            },
            SalaryInfo(
                salary_from=80000,
                salary_to=150000,
                salary_mode='MONTH',
                currency='RUR'
            )
        ),
        (
            {'noCompensation': {}},
            SalaryInfo(
                salary_from=None,
                salary_to=None,
                salary_mode=None,
                currency=None
            )
        ),
    ]
)
def test_parse_salary_info(test_hh_vacancy_client : HHVacancyClient,
                         salary_info : dict,
                         expected_result : SalaryInfo):

    assert test_hh_vacancy_client._parse_salary_info(salary_info) == expected_result