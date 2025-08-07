import pytest
from dlt.sources.helpers.rest_client.paginators import DateRangePaginator
from dlt.common.time import pendulum


def test_date_range_paginator_invalid_init():
    with pytest.raises(TypeError):
        DateRangePaginator()

    with pytest.raises(TypeError):
        DateRangePaginator(
            start_date=pendulum.now(),
        )

    with pytest.raises(TypeError):
        DateRangePaginator(
            start_date=pendulum.now(),
            end_date=pendulum.now(),
        )

    with pytest.raises(ValueError):
        DateRangePaginator(
            start_date=pendulum.now(),
            end_date=pendulum.now(),
            step=pendulum.duration(days=1),
            start_param=None,
            end_param='end',
        )

    with pytest.raises(ValueError):
        DateRangePaginator(
            start_date=pendulum.now(),
            end_date=pendulum.now(),
            step=pendulum.duration(days=1),
            start_param='start',
            end_param=None,
        )


def test_date_range_paginator_one_step():
    paginator = DateRangePaginator(
        start_date=pendulum.date(2024, 1, 1),
        end_date=pendulum.date(2024, 1, 2),
        step=pendulum.duration(days=1),
    )

    assert paginator.start_date == pendulum.date(2024, 1, 1)
    assert paginator.end_date == pendulum.date(2024, 1, 2)
    assert paginator.step == pendulum.duration(days=1)
    assert paginator.current_start_date == pendulum.date(2024, 1, 1)
    assert paginator.has_next_page

    paginator.update_state(None)
    assert paginator.current_start_date == pendulum.date(2024, 1, 2)
    assert not paginator.has_next_page


def test_date_range_paginator_two_steps():
    paginator = DateRangePaginator(
        start_date=pendulum.date(2024, 1, 1),
        end_date=pendulum.date(2024, 1, 3),
        step=pendulum.duration(days=1),
    )

    assert paginator.has_next_page
    paginator.update_state(None)
    assert paginator.current_start_date == pendulum.date(2024, 1, 2)
    assert paginator.has_next_page
    paginator.update_state(None)
    assert paginator.current_start_date == pendulum.date(2024, 1, 3)
    assert not paginator.has_next_page


@pytest.mark.usefixtures("mock_api_server")
def test_client_pagination(rest_client):
    paginator = DateRangePaginator(
        start_date=pendulum.date(2024, 1, 1),
        end_date=pendulum.date(2024, 1, 3),
        step=pendulum.duration(days=1),
    )

    pages = list(rest_client.paginate("/date-range", paginator=paginator))

    assert len(pages) == 2
    assert pages[0][0]["start_date"] == "2024-01-01"
    assert pages[0][0]["end_date"] == "2024-01-02"
    assert pages[1][0]["start_date"] == "2024-01-02"
    assert pages[1][0]["end_date"] == "2024-01-03"
