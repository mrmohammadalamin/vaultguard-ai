import asyncio
from typing import Callable, Awaitable
from .governance import GovernanceEngine, PolicyDecision

class BaseAgent:
    def __init__(self, name: str, log_func: Callable[[str, str, str], Awaitable[None]]):
        self.name = name
        self.log_func = log_func

    async def log(self, msg: str, level: str = "INFO"):
        await self.log_func(self.name, msg, level)

class PlanningAgent(BaseAgent):
    def __init__(self, log_func):
        super().__init__("Planning Agent", log_func)

    async def execute(self):
        await self.log("Analyzing project structure...")
        await asyncio.sleep(1)
        await self.log("Plan created successfully: 7 tasks identified.")
        return True

class SecurityAgent(BaseAgent):
    def __init__(self, log_func, governance: GovernanceEngine):
        super().__init__("Security Agent", log_func)
        self.governance = governance

    async def execute(self):
        await self.log("Initiating security scan...")
        await asyncio.sleep(1)
        decision = self.governance.inspect_and_decide("npm audit")
        await self.log(f"Running task npm audit. Governance: {decision.decision}")
        await self.log("Vulnerability detected. Analyzing failure...", "WARN")
        await asyncio.sleep(1)
        await self.log("Generating fix: npm audit fix")
        await self.log("Fix applied successfully. Retrying scan...")
        return {"decision": decision.decision.value, "retries": 1, "status": "SUCCESS"}

class DependencyAgent(BaseAgent):
    def __init__(self, log_func):
        super().__init__("Dependency Agent", log_func)

    async def execute(self):
        await self.log("Analyzing project dependencies...")
        await asyncio.sleep(2)
        await self.log("Dependencies mapped. All clear.")
        return True

class BuildAgent(BaseAgent):
    def __init__(self, log_func):
        super().__init__("Build Agent", log_func)

    async def execute(self):
        await self.log("Starting build process...")
        await asyncio.sleep(2)
        await self.log("Build completed successfully.")
        return True

class TestingAgent(BaseAgent):
    def __init__(self, log_func):
        super().__init__("Testing Agent", log_func)

    async def execute(self):
        await self.log("Running tests: jest")
        await asyncio.sleep(1)
        await self.log("Tests failed! Detected failure in auth.test.ts", "WARN")
        await asyncio.sleep(1)
        await self.log("Analyzing failure...", "WARN")
        await self.log("Generating corrective action...")
        await self.log("Patching auth.test.ts...")
        await self.log("Retrying tests...")
        await asyncio.sleep(1)
        await self.log("Tests passed successfully.")
        return True

class DeploymentAgent(BaseAgent):
    def __init__(self, log_func, governance: GovernanceEngine):
        super().__init__("Deployment Agent", log_func)
        self.governance = governance

    async def execute(self):
        await self.log("Preparing deployment to production...")
        decision = self.governance.inspect_and_decide("npm run deploy")
        if decision.decision == PolicyDecision.REQUIRE_APPROVAL:
            await self.log(f"High risk action intercepted: {decision.reason}", "WARN")
            return {"status": "REQUIRE_APPROVAL", "decision": decision}
        await self.log("Deployment initiated autonomously.")
        return {"status": "SUCCESS", "decision": decision}

class VerificationAgent(BaseAgent):
    def __init__(self, log_func):
        super().__init__("Verification Agent", log_func)

    async def execute(self):
        await self.log("Verifying deployment health...")
        await asyncio.sleep(1)
        await self.log("Deployment verified successfully.")
        return True

class AuditAgent(BaseAgent):
    def __init__(self, log_func):
        super().__init__("Audit Agent", log_func)

    async def execute(self):
        await self.log("Generating final audit report...")
        await asyncio.sleep(1)
        await self.log("Audit complete. Writing to secure storage.")
        return True
