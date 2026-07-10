import asyncio
import random
from typing import Callable, Awaitable
from .governance import GovernanceEngine, PolicyDecision
from database.models import SessionLocal, AuditLog
from datetime import datetime
from .agents import (
    PlanningAgent, SecurityAgent, DependencyAgent, 
    BuildAgent, TestingAgent, DeploymentAgent, 
    VerificationAgent, AuditAgent
)

class StateMachine:
    def __init__(self, websocket_emit: Callable[[dict], Awaitable[None]]):
        self.emit = websocket_emit
        self.states = [
            "PLANNING",
            "SECURITY_SCAN",
            "DEPENDENCY_ANALYSIS",
            "BUILD",
            "UNIT_TEST",
            "DEPLOY",
            "VERIFY",
            "AUDIT",
            "COMPLETE"
        ]
        self.current_state_idx = 0
        self.governance = GovernanceEngine()
        self.is_paused = False
        self.pending_approval = None
        self.running = False
        self.logs = []
        
        # Initialize specialized agents
        self.planning_agent = PlanningAgent(self._agent_log)
        self.security_agent = SecurityAgent(self._agent_log, self.governance)
        self.dependency_agent = DependencyAgent(self._agent_log)
        self.build_agent = BuildAgent(self._agent_log)
        self.testing_agent = TestingAgent(self._agent_log)
        self.deployment_agent = DeploymentAgent(self._agent_log, self.governance)
        self.verification_agent = VerificationAgent(self._agent_log)
        self.audit_agent = AuditAgent(self._agent_log)

    async def _log(self, msg: str, level: str = "INFO", agent: str = "Master Agent"):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(), 
            "msg": f"[{agent}] {msg}", 
            "level": level,
            "agent": agent
        }
        self.logs.append(log_entry)
        await self.emit({"type": "log", "data": log_entry})

    async def _agent_log(self, agent: str, msg: str, level: str = "INFO"):
        await self._log(msg, level, agent)

    async def _update_state(self):
        state = self.states[self.current_state_idx]
        await self.emit({"type": "state_update", "data": {"state": state, "progress": int((self.current_state_idx / (len(self.states) - 1)) * 100)}})

    async def _save_audit(self, action: str, decision: str, approval_event: str, retries: int, status: str):
        db = SessionLocal()
        try:
            log = AuditLog(
                goal="Secure and Deploy Customer Portal",
                agent="VaultGuard Autonomous Agent",
                action=action,
                policy_decision=decision,
                approval_event=approval_event,
                retry_count=retries,
                execution_time_ms=random.randint(500, 5000),
                final_status=status
            )
            db.add(log)
            db.commit()
            await self.emit({"type": "audit_update", "data": "Audit log saved"})
        finally:
            db.close()

    async def start(self):
        self.logs = []
        self.current_state_idx = 0
        self.is_paused = False
        self.pending_approval = None
        await self._log("Starting Autonomous Goal Execution: Secure and Deploy Customer Portal")
        await self._update_state()
        if not self.running:
            self.running = True
            asyncio.create_task(self._loop())

    async def _loop(self):
        while self.running and self.current_state_idx < len(self.states):
            if self.is_paused:
                await asyncio.sleep(1)
                continue

            current_state = self.states[self.current_state_idx]
            
            if current_state == "PLANNING":
                await self._log("Delegating task to Planning Agent...")
                await self.planning_agent.execute()
                self.current_state_idx += 1
                await self._update_state()

            elif current_state == "SECURITY_SCAN":
                # We will demonstrate parallel execution here by jumping to the next state logically,
                # but we handle it together in code for simplicity of demonstration.
                await self._log("Initiating Parallel Execution for Security and Dependency Analysis...")
                
                # Execute in parallel
                sec_task = asyncio.create_task(self.security_agent.execute())
                dep_task = asyncio.create_task(self.dependency_agent.execute())
                
                sec_result, dep_result = await asyncio.gather(sec_task, dep_task)
                
                await self._save_audit("npm audit", sec_result["decision"], None, sec_result["retries"], sec_result["status"])
                
                # Skip the DEPENDENCY_ANALYSIS state since we just ran it in parallel
                self.current_state_idx += 2
                await self._update_state()

            elif current_state == "DEPENDENCY_ANALYSIS":
                # Handled in parallel with SECURITY_SCAN
                self.current_state_idx += 1
                await self._update_state()

            elif current_state == "BUILD":
                await self._log("Delegating task to Build Agent...")
                await self.build_agent.execute()
                self.current_state_idx += 1
                await self._update_state()

            elif current_state == "UNIT_TEST":
                await self._log("Delegating task to Testing Agent...")
                await self.testing_agent.execute()
                await self._save_audit("jest", "ALLOW", None, 1, "SUCCESS")
                self.current_state_idx += 1
                await self._update_state()

            elif current_state == "DEPLOY":
                await self._log("Delegating task to Deployment Agent...")
                result = await self.deployment_agent.execute()
                
                if result["status"] == "REQUIRE_APPROVAL":
                    self.is_paused = True
                    self.pending_approval = "npm run deploy"
                    await self.emit({
                        "type": "approval_required",
                        "data": {
                            "action": "npm run deploy",
                            "risk": result["decision"].risk_level.value,
                            "reason": result["decision"].reason
                        }
                    })
                else:
                    self.current_state_idx += 1
                    await self._update_state()

            elif current_state == "VERIFY":
                await self._log("Delegating task to Verification Agent...")
                await self.verification_agent.execute()
                self.current_state_idx += 1
                await self._update_state()

            elif current_state == "AUDIT":
                await self._log("Delegating task to Audit Agent...")
                await self.audit_agent.execute()
                self.current_state_idx += 1
                await self._update_state()

            elif current_state == "COMPLETE":
                await self._log("All agents have completed their tasks. Goal fully executed.")
                self.running = False
                await self.emit({"type": "goal_complete", "data": {}})
                break

    async def approve(self):
        if self.is_paused and self.pending_approval:
            await self._log(f"Approval granted for {self.pending_approval}", agent="Master Agent")
            await self._save_audit(self.pending_approval, "REQUIRE_APPROVAL", "APPROVED", 0, "SUCCESS")
            self.is_paused = False
            self.pending_approval = None
            self.current_state_idx += 1
            await self._update_state()

    async def reject(self):
        if self.is_paused and self.pending_approval:
            await self._log(f"Approval rejected for {self.pending_approval}", level="ERROR", agent="Master Agent")
            await self._save_audit(self.pending_approval, "REQUIRE_APPROVAL", "REJECTED", 0, "FAILED")
            self.is_paused = False
            self.pending_approval = None
            self.running = False
            await self._log("Goal execution cancelled safely.", agent="Master Agent")
            await self.emit({"type": "goal_complete", "data": {}})
