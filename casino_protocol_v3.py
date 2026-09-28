class CasinoProtocolEngine:
    def __init__(self, r_contract: float, r_ip: float, epsilon: float = 1e-9):
        self.r_contract = r_contract
        self.r_ip = r_ip
        self.r_audit = 1.0
        self.state = "OPERATIONAL"
        self.anomaly_reason = None
        self.epsilon = epsilon

    @property
    def r_protected(self) -> float:
        """権利保護残高 (R_protected = R_contract + R_IP + R_audit)"""
        return self.r_contract + self.r_ip + self.r_audit

    def _normalize_value(self, val: float) -> float:
        """入力値の境界チェック（[0.0, 1.0] 閉区間に正規化）"""
        return max(0.0, min(1.0, float(val)))

    def calculate_3c3(self, c1: float, c2: float, c3: float) -> float:
        """
        調和平均によるシステム信頼度 T の算出
        c_i <= epsilon の場合、完全欠損 (T = 0.0) として安全側に遷移
        """
        c1_norm = self._normalize_value(c1)
        c2_norm = self._normalize_value(c2)
        c3_norm = self._normalize_value(c3)

        if c1_norm <= self.epsilon or c2_norm <= self.epsilon or c3_norm <= self.epsilon:
            return 0.0

        return 3.0 / ((1.0 / c1_norm) + (1.0 / c2_norm) + (1.0 / c3_norm))

    def audit_and_remediate(self, c1: float, c2: float, c3: float, gv: float):
        c1_norm = self._normalize_value(c1)
        c2_norm = self._normalize_value(c2)
        c3_norm = self._normalize_value(c3)
        gv_norm = self._normalize_value(gv)

        T = self.calculate_3c3(c1_norm, c2_norm, c3_norm)
        C = 1.0 - T

        print(f"\n--- Audit Telemetry ---")
        print(f"c1={c1_norm:.2f}, c2={c2_norm:.2f}, c3={c3_norm:.2f}, GV={gv_norm:.2f}")
        print(f"Systemic Verification Confidence (T): {T:.4f}")
        print(f"Verification Uncertainty (C): {C:.4f}")

        if self.state == "ISOLATED_HOLD":
            print("🛑 [STATE LOCK] System is in ISOLATED_HOLD. Independent verification (release_hold) required.")
            return

        if c2_norm <= self.epsilon:
            self.anomaly_reason = "C2_MISSING_EMPIRICAL_CORRESPONDENCE_ANOMALY"
            self.execute_casino_protocol(gv_norm, C)
        elif T <= self.epsilon:
            self.anomaly_reason = "SYSTEMIC_CONFIDENCE_COLLAPSE"
            self.execute_casino_protocol(gv_norm, C)
        else:
            self.state = "OPERATIONAL"
            self.anomaly_reason = None
            self.r_audit = 1.0
            print(f"[STATUS] System Operational. R_protected = {self.r_protected:.2f}")

    def execute_casino_protocol(self, gv: float, C: float):
        self.state = "ISOLATED_HOLD"
        self.r_audit = 1.0
        print("🚨 [ANOMALY DETECTED] Trigger Reason:", self.anomaly_reason)
        print("🛡️ [CASINO PROTOCOL ACTIVATED]")
        print(f"  1. Telemetry Scan: Analyzed Spatial Distortion Index GV={gv:.2f}, Uncertainty C={C:.2f}")
        print("  2. Circuit Hold: Payment/Transaction circuit automatically suspended.")
        print("  3. Vault Isolation: Assets and access rights locked in Vault state.")
        print(f"  4. Rights Preserved: R_protected maintained at {self.r_protected:.2f}")

    def release_hold(self, auditor_credentials: str, c1: float, c2: float, c3: float, gv: float) -> bool:
        print(f"\n--- Independent Re-verification Attempt by [{auditor_credentials}] ---")
        c1_norm = self._normalize_value(c1)
        c2_norm = self._normalize_value(c2)
        c3_norm = self._normalize_value(c3)
        gv_norm = self._normalize_value(gv)

        T = self.calculate_3c3(c1_norm, c2_norm, c3_norm)

        if c2_norm > self.epsilon and T > self.epsilon:
            self.state = "OPERATIONAL"
            self.anomaly_reason = None
            print("🔄 [HOLD RELEASED] Independent verification passed. System restored to OPERATIONAL.")
            print(f"[STATUS] System Operational. R_protected = {self.r_protected:.2f}")
            return True
        else:
            print("🚫 [RELEASE FAILED] Re-verification failed. System remains in ISOLATED_HOLD.")
            return False


if __name__ == "__main__":
    engine = CasinoProtocolEngine(r_contract=100.0, r_ip=200.0)

    print("=== CASE 1: Normal Operation ===")
    engine.audit_and_remediate(c1=0.95, c2=0.90, c3=0.88, gv=0.05)

    print("\n=== CASE 2: Empirical Correspondence Anomaly (c2 = 0) ===")
    engine.audit_and_remediate(c1=0.95, c2=0.00, c3=0.88, gv=0.85)

    print("\n=== CASE 3: Attempting Audit While Locked ===")
    engine.audit_and_remediate(c1=0.95, c2=0.90, c3=0.88, gv=0.05)

    print("\n=== CASE 4: Independent Release & Restoration ===")
    engine.release_hold(auditor_credentials="AUTHORIZED_AUDITOR_KEY", c1=0.95, c2=0.90, c3=0.88, gv=0.05)
