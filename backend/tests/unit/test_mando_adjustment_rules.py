from app.services.analysis_service import _should_apply_mando_adjustment


def test_should_apply_mando_adjustment_none_none() -> None:
    assert _should_apply_mando_adjustment(None, None) is True


def test_should_apply_mando_adjustment_any_filter_disables() -> None:
    assert _should_apply_mando_adjustment("casa", None) is False
    assert _should_apply_mando_adjustment(None, "fora") is False
    assert _should_apply_mando_adjustment("casa", "fora") is False
    assert _should_apply_mando_adjustment("fora", "fora") is False

