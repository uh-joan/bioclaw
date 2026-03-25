# Scoring: clinical-trial-protocol-designer
Target: 0.9

1. **Design Appropriateness (0.25)**: Correct trial design for the question = 1.0
2. **Regulatory Alignment (0.20)**: Design meets FDA/EMA expectations for the indication = 1.0
3. **Statistical Plan Quality (0.20)**: Sample size, alpha, endpoints, interim rules specified = 1.0
4. **Protocol Completeness (0.20)**: All required_sections present with appropriate detail = 1.0
5. **Population/Endpoint Selection (0.15)**: Appropriate eligibility and primary endpoint = 1.0

Override: NI trial without margin justification = -0.3. Bispecific T-cell engager without CRS management plan = -0.3. Rare disease given standard RCT design without justifying single-arm = -0.2.
