import pytest


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
def test_parse_logo_info(test_hh_vacancy_client, company_info, expected_result):
    assert test_hh_vacancy_client._parse_logo_info(company_info, "small") == expected_result