from recommendation_engine.ab_testing import ABExperimentManager


def test_ab_assignment_determinism():
    manager = ABExperimentManager()

    # Same user should deterministically receive the same variant
    v1 = manager.assign_variant("user_123", "exp_homepage_algo")
    v2 = manager.assign_variant("user_123", "exp_homepage_algo")
    assert v1 == v2
    assert v1 in ["control", "variant_a", "variant_b"]


def test_ab_event_recording():
    manager = ABExperimentManager()
    summary_before = manager.get_experiment_summary("exp_homepage_algo")
    imp_before = summary_before["variants"][0]["impressions"]

    manager.record_event("exp_homepage_algo", "control", "impression")
    summary_after = manager.get_experiment_summary("exp_homepage_algo")
    imp_after = summary_after["variants"][0]["impressions"]

    assert imp_after == imp_before + 1
