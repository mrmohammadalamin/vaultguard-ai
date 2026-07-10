from engine.governance import GovernanceEngine, PolicyDecision

def test_governance_deny():
    engine = GovernanceEngine()
    decision = engine.inspect_and_decide("rm -rf /")
    assert decision.decision == PolicyDecision.DENY

def test_governance_approval():
    engine = GovernanceEngine()
    decision = engine.inspect_and_decide("npm run deploy")
    assert decision.decision == PolicyDecision.REQUIRE_APPROVAL

def test_governance_allow():
    engine = GovernanceEngine()
    decision = engine.inspect_and_decide("npm audit")
    assert decision.decision == PolicyDecision.ALLOW
