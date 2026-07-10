# VaultGuard AI: Demo Script

**Speaker:** "Welcome to our Google Agentic Architect Sprint demonstration. Today, we're showcasing VaultGuard AI, an Enterprise Agent Governance & Safety Control Platform."

**Action:** Open `http://localhost:3000` in the browser. Toggle between Dark and Light mode to show off the Enterprise SaaS UI.

**Speaker:** "Our focus today is demonstrating **Fully Autonomous Goal Execution**. Specifically, what happens when an agent is given a complex `/goal` command, and how enterprise governance policies can autonomously intercept and correct unsafe behaviors."

**Action:** Click the `/goal Secure and Deploy` button.

**Speaker:** "We've triggered the master execution. Behind the scenes, a `MasterAgent` is coordinating a fleet of specialized sub-agents: Planning, Security, Testing, Build, Deployment, Verification, and Audit."

**Action:** Point to the Animated Timeline as it moves from `PLANNING` to `SECURITY_SCAN`.

**Speaker:** "Notice how the system operates in parallel. The Security Agent and Dependency Agent are running concurrently. Here, the Security Agent encountered a simulated vulnerability during `npm audit`."

**Action:** Highlight the Activity Feed where the text turns yellow/red. 

**Speaker:** "Instead of failing and giving up, the agent enters a self-correcting closed loop. It analyzes the failure, generates a fix (`npm audit fix`), and automatically retries the scan until it passes. This demonstrates highly reliable closed-loop engineering."

**Action:** Wait for the timeline to reach the `DEPLOY` phase. The Approval Modal will pop up.

**Speaker:** "This is the **Human Approval Gate**. We have declarative safety rules in place. The Governance Engine caught the command `npm run deploy`. Because this is a high-risk operation, the agent halts execution entirely and demands human authorization."

**Action:** Click the **Approve** button on the modal.

**Speaker:** "Once approved, the deployment proceeds autonomously. Verification occurs, and finally, the Audit Agent generates a secure report."

**Action:** Click the **JSON Download** button in the Audit Table. 

**Speaker:** "Every action, policy decision, retry attempt, and approval event is immutably logged for compliance. This is how organizations can achieve enterprise-scale autonomous software engineering without compromising security."
