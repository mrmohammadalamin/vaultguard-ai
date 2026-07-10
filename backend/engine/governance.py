from enum import Enum
from pydantic import BaseModel

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"

class GovernanceDecision(BaseModel):
    action: str
    decision: PolicyDecision
    risk_level: RiskLevel
    reason: str

class GovernanceEngine:
    def __init__(self):
        self.deny_rules = [
            "rm -rf /",
            "rm -rf /*",
            "cat /etc/shadow",
            "cat .env"
        ]
        self.approval_rules = [
            "deploy",
            "docker push",
            "kubectl apply",
            "migrate"
        ]

    def inspect_and_decide(self, command: str) -> GovernanceDecision:
        command_lower = command.lower()

        # Check deny rules
        for deny in self.deny_rules:
            if deny in command_lower:
                return GovernanceDecision(
                    action=command,
                    decision=PolicyDecision.DENY,
                    risk_level=RiskLevel.CRITICAL,
                    reason=f"Command violates security policy: unrestricted or sensitive access ({deny})"
                )

        # Check approval rules
        for app in self.approval_rules:
            if app in command_lower:
                return GovernanceDecision(
                    action=command,
                    decision=PolicyDecision.REQUIRE_APPROVAL,
                    risk_level=RiskLevel.HIGH,
                    reason=f"High-risk operation requires human approval: {app}"
                )

        return GovernanceDecision(
            action=command,
            decision=PolicyDecision.ALLOW,
            risk_level=RiskLevel.LOW,
            reason="Command complies with governance policies"
        )
