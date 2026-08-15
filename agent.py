"""
Requirement-driven test-case generation agent.

The agent is deterministic by design: it parses acceptance criteria and business-rule
language, generates categorized cases, critiques coverage, and repairs concrete gaps.
No LLM/API key is required, so the workflow is reproducible for CI and review.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CATEGORIES = ("positive", "negative", "boundary", "edge")
PRIORITIES = ("P0", "P1", "P2", "P3")

@dataclass
class TestCase:
    id: str
    feature: str
    category: str
    priority: str
    acceptance_criteria: str
    rule_trace: str
    title: str
    preconditions: str
    steps: str
    expected_result: str
    risk: str
    source: str = "generated"

def tc(feature, category, priority, ac, rule, title, preconditions, steps, expected, risk, source="generated"):
    return TestCase("", feature, category, priority, ac, rule, title, preconditions, steps, expected, risk, source)

class TestCaseAgent:
    def __init__(self, max_iterations=4):
        self.max_iterations=max(1,max_iterations); self.iterations=[]
    @staticmethod
    def _ac(spec, ac_id): return next(x for x in spec["acceptance_criteria"] if x["id"]==ac_id)
    @staticmethod
    def _business_rules(spec):
        rules=[{"id":f"RULE{i}","text":r} for i,r in enumerate(spec.get("promo_rules",[]),1)]
        if spec.get("notes"): rules.append({"id":"NOTE1","text":spec["notes"]})
        return rules
    def _base_cases(self,spec):
        cases=[]
        for ac in spec["acceptance_criteria"]:
            aid,text=ac["id"],ac["text"]
            cases.append(tc(spec["name"],"positive","P0",aid,aid,f"{aid}: verify the required behavior","Required feature state and valid test data are available.",f"Execute the exact condition described in {aid}: {text}",f"The system satisfies {aid} exactly, including the stated outcome and message/state.","High business impact","initial-generation"))
            cases.append(self._targeted_case(spec,aid,"negative"))
        return cases
    def _targeted_case(self,spec,ac_id,category):
        ac=self._ac(spec,ac_id); text=ac["text"]; feature=spec["name"]
        A={
        "AC1":{"boundary":("Password length rule","Use a valid account and try password lengths 7, 8, 64, and 65.","8 and 64 character passwords are accepted; 7 and 65 character passwords are rejected according to the password constraint.","Authentication + validation"),"edge":("Session starts after successful login","Log in successfully and inspect authenticated state/session.","A session is established and the user is authenticated on the dashboard.","Authentication/session")},
        "AC2":{"negative":("Wrong password stays on login","Enter correct email and wrong password; click Log In.","Exactly 'Invalid email or password' is shown and the user remains on the login page.","Authentication failure"),"edge":("Failed login contributes to lockout","Submit consecutive wrong passwords and count failures.","Each failed authentication is rejected and the failures contribute to the AC6 lockout threshold.","Account security")},
        "AC3":{"negative":("Unknown email cannot be enumerated","Enter an unregistered email with a password and submit.","The exact generic 'Invalid email or password' message is shown; no indication reveals whether the email exists.","Security/account enumeration"),"boundary":("Unknown email with password length boundaries","Submit the unknown email with passwords of 8 and 64 characters.","The same generic authentication error is returned without account enumeration.","Security/validation"),"edge":("Registered-wrong-password and unknown-email responses match","Compare registered+wrong-password with unregistered+any-password.","Both paths expose the same generic authentication error and do not reveal account existence.","Security/account enumeration")},
        "AC4":{"negative":("Blank required fields are validated inline","Leave email blank, password blank, then each field blank separately; click Log In.","Inline required-field prompts identify the missing field(s), and no authentication request is sent.","Validation/request suppression"),"boundary":("One blank field at a time","Test blank email with valid password, then valid email with blank password.","Only the missing field is prompted and no authentication request is sent in either case.","Validation"),"edge":("Whitespace-only required fields","Enter whitespace-only values in email/password and click Log In.","The UI treats whitespace-only required values as empty/invalid and does not send authentication.","Input validation")},
        "AC5":{"negative":("Malformed email formats","Submit user, user@, @example.com, user@@example.com and user name@example.com.","Each malformed email shows inline 'Enter a valid email address'.","Input validation"),"boundary":("Email format near valid boundary","Compare user@example.com with user@example and user@example.com.","Only the valid email format proceeds past email-format validation; invalid formats show the exact inline message.","Input validation"),"edge":("Email normalization does not bypass format validation","Try leading/trailing spaces and mixed-case valid email addresses.","Valid formatted email remains valid after permitted normalization; malformed input still receives format validation.","Input normalization")},
        "AC6":{"negative":("Five failures lock the account","Submit 5 consecutive wrong-password attempts within 15 minutes, then submit correct credentials.","After the fifth failure the account is locked for 30 minutes and correct credentials still show 'Your account is locked. Try again later.'.","Account security"),"boundary":("Lockout thresholds and time window","Compare 4 failures vs 5 failures; place failures inside and outside the 15-minute window.","Four failures do not lock the account; five qualifying consecutive failures within 15 minutes do; failures outside the window do not incorrectly satisfy the threshold.","Account security"),"edge":("Lock expires after 30 minutes","Attempt correct credentials immediately, just before 30 minutes, and at/after 30 minutes.","Correct credentials are rejected during the lock period and accepted after the 30-minute lock expires, subject to other account rules.","Account security/time")},
        "AC7":{"negative":("Password casing is significant","Use the correct email but alter password casing.","Authentication fails because the password is case-sensitive.","Authentication security"),"boundary":("Email casing permutations","Try User@x.com, user@x.com, USER@X.COM and mixed-case variants with the same password.","All email-case variants authenticate as the same account.","Authentication identity"),"edge":("Password case permutations","Try Password, password, PASSWORD and mixed-case variants.","Only the exact registered password casing succeeds.","Authentication security")},
        "AC8":{"negative":("Expired session cannot access dashboard","Refresh or navigate to the dashboard after expiry.","The user is no longer authenticated and must log in again.","Session security"),"boundary":("Session expiry boundary","Refresh at 23:59:59 and then at 24:00:00 after login.","The session remains valid before 24 hours and expires at the defined 24-hour boundary.","Session security"),"edge":("Refresh, logout and direct navigation session behavior","Refresh the dashboard, log out, refresh again, then navigate directly to the dashboard URL.","Refresh preserves the active session; after logout, the session is invalid and protected navigation requires authentication.","Session security")},
        "AC9":{"negative":("Inactive account is not authenticated","Enter the inactive user's correct email and password.","The exact 'This account is inactive. Contact support.' message is shown and no authenticated session is created.","Account access control"),"boundary":("Inactive status blocks even correct credentials","Deactivate the account, then attempt login with previously valid credentials.","The account is rejected after deactivation; valid credentials do not bypass inactive status.","Account lifecycle"),"edge":("Inactive account cannot establish session","Attempt login and inspect session/dashboard access.","No authenticated session exists and protected pages remain inaccessible.","Access control")}}
        B={
        "AC1":{"negative":("Invalid percentage input does not apply discount","Alter the code or use an invalid percentage code and apply it.","Invalid/ineligible code is rejected and the order total is unchanged.","Pricing integrity"),"boundary":("Percentage discount calculation","Apply SAVE10 to subtotals ₹1, ₹1000 and ₹1500.","Discount equals exactly 10% of item subtotal and the resulting subtotal/total uses the calculated discounted amount.","Pricing calculation"),"edge":("Percentage discount uses discounted subtotal for downstream calculations","Apply SAVE10 and inspect subtotal, shipping and tax calculations.","Discount applies to item subtotal only; shipping and tax are calculated from the discounted subtotal.","Pricing integrity")},
        "AC2":{"negative":("Fixed code rejected when not eligible","Apply FLAT200 below its eligibility threshold.","The code is rejected and the total remains unchanged.","Pricing eligibility"),"boundary":("Fixed-code minimum threshold","Apply FLAT200 at ₹999, ₹1000 and ₹1001.","₹999 is rejected; ₹1000 and ₹1001 are eligible and receive ₹200 off.","Pricing eligibility"),"edge":("Fixed discount affects only subtotal","Apply FLAT200 at ₹1500 and inspect order breakdown.","Exactly ₹200 is removed from item subtotal and shipping/tax use the discounted subtotal.","Pricing integrity")},
        "AC3":{"negative":("Fixed code below minimum shows exact message","Apply FLAT200 at ₹800.","The exact 'This code requires a minimum order of ₹1000.' message is shown and the total is unchanged.","Pricing eligibility"),"boundary":("Minimum subtotal boundary","Apply FLAT200 at ₹999, ₹1000 and ₹1001.","Only ₹1000 and above meet the minimum requirement.","Pricing eligibility"),"edge":("Minimum threshold after cart change","Apply FLAT200 to an eligible cart, then remove items until subtotal is below ₹1000.","The discount is revalidated and removed once the cart becomes ineligible.","Cart/pricing state")},
        "AC4":{"negative":("Expired code is rejected","Apply the expired code.","The exact 'This code has expired.' message is shown and total is unchanged.","Promo lifecycle"),"boundary":("Expiry timing boundary","Apply immediately before expiry, at expiry, and after expiry.","The code is accepted only while within its validity window and rejected once expired.","Promo lifecycle"),"edge":("Expired code does not overwrite existing valid discount","Attempt to replace a valid code with an expired code.","The expired code is rejected and the existing valid discount remains unchanged.","Pricing integrity")},
        "AC5":{"negative":("Non-existent promo code","Enter a code that does not exist and click Apply.","The exact 'Invalid promo code.' message is shown and the total is unchanged.","Input/error handling"),"boundary":("Invalid code around valid identifier","Compare SAVE10 with a one-character mutation and an unknown code.","Only the exact valid code is accepted; invalid variants are rejected without changing the total.","Promo validation"),"edge":("Invalid code cannot replace valid code","Attempt to apply a non-existent second code when a valid promo is already applied.","The invalid code is rejected and the existing discount remains intact.","Pricing integrity")},
        "AC6":{"negative":("Case-insensitive promo identity","Apply SAVE10, save10 and SaVe10 on equivalent orders.","All case variants resolve to the same code and discount.","Promo identity"),"boundary":("Mixed-case promo variants","Apply save10, SAVE10 and SaVe10 separately.","Each variant produces the same discount and order total.","Promo identity"),"edge":("Case normalization with whitespace","Apply '  save10  '.","Whitespace is trimmed and case is normalized so the valid code is applied once.","Input normalization")},
        "AC7":{"negative":("Same customer cannot reuse single-use code","Customer A has already redeemed a single-use code; apply it again.","The exact 'This code has already been used.' message is shown and no second discount is applied.","Promo abuse prevention"),"boundary":("First redemption versus second redemption","Redeem once, then immediately attempt a second redemption as the same customer.","First redemption succeeds; second redemption is rejected.","Promo usage control"),"edge":("Single-use limit is per customer","Customer A redeemed the code; Customer B has not. Apply the code as Customer B.","Customer B can use the code if otherwise valid; Customer A cannot reuse it.","Promo usage control")},
        "AC8":{"negative":("Fixed discount never creates negative subtotal","Apply FLAT200 to subtotal ₹150.","Discounted subtotal is exactly ₹0 and never becomes negative.","Pricing integrity"),"boundary":("Fixed discount cap boundaries","Apply FLAT200 to subtotals ₹150, ₹200 and ₹201.","Results are ₹0, ₹0 and ₹1 respectively; the discounted subtotal never goes below ₹0.","Pricing calculation"),"edge":("Capped discount preserves downstream calculations","Apply FLAT200 at subtotal ₹150 and inspect order breakdown.","Discounted subtotal is ₹0 and downstream calculations use the defined discounted subtotal without negative values.","Pricing integrity")},
        "AC9":{"negative":("Canceling replacement keeps first code","Apply a second code, then cancel the replacement prompt.","First code and its discount remain active; second code is not applied.","Checkout state"),"boundary":("Confirm replacement removes old discount","Apply second code and confirm replacement.","Only the new discount is present; the old discount is fully removed and total is recalculated once.","Checkout state/pricing"),"edge":("Second code cannot stack with first","Apply a second code and inspect order summary before and after confirmation.","No stacked discounts exist; confirmation is required and only one code remains applied.","Pricing integrity")},
        "AC10":{"negative":("Empty promo input","Leave Promo code blank and click Apply.","The exact 'Enter a promo code.' message is shown and the order total is unchanged.","Input validation"),"boundary":("Whitespace-only promo input","Enter spaces/tabs only and click Apply.","The input is treated as empty and the required-code message is shown.","Input validation"),"edge":("Empty apply does not replace existing promo","Clear the input and click Apply while a valid promo is already applied.","The existing applied code and discount remain unchanged; empty input does not clear the active promotion.","Checkout state")},
        "AC11":{"negative":("Whitespace is normalized before validation","Apply ' SAVE10 ', 'SAVE10 ', and ' SAVE10'.","Each value is trimmed and resolves to SAVE10.","Input normalization"),"boundary":("Whitespace variants","Test leading-only, trailing-only, and leading+trailing spaces.","All permitted leading/trailing whitespace is trimmed before validation.","Input normalization"),"edge":("Internal whitespace is not silently removed","Apply 'SA VE10' and compare with ' SAVE10 '.","Only leading/trailing spaces are trimmed; internal whitespace does not become a valid code unless explicitly supported.","Input validation")},
        "AC12":{"negative":("Promo is removed after cart becomes ineligible","Apply FLAT200 at ₹1500, then remove items until subtotal is ₹800.","The discount is revalidated, removed, and the order total is recalculated without FLAT200.","Cart/pricing integrity"),"boundary":("Cart-change minimum threshold","Change subtotal to ₹1001, ₹1000 and ₹999 after applying FLAT200.","The promo remains valid at ₹1000/above and is removed below ₹1000.","Cart/pricing integrity"),"edge":("Cart increase and decrease recalculate discount","Increase subtotal, decrease it while eligible, then decrease it below eligibility.","Discount and total are recalculated after each cart change and eligibility is enforced.","Cart/pricing integrity")}}
        library=A if spec["id"]=="A" else B
        if ac_id in library and category in library[ac_id]:
            title,steps,expected,risk=library[ac_id][category]
            return tc(feature,category,"P0" if category in ("negative","boundary") else "P1",ac_id,ac_id,title,"Feature is available with required test data.",steps,expected,risk,"targeted-rule")
        if category=="positive": return tc(feature,category,"P1",ac_id,ac_id,"Verify acceptance criterion with valid data","Feature is available.",f"Execute the stated condition: {text}",f"The stated outcome of {ac_id} is achieved: {text}","Business behavior","targeted-fallback")
        if category=="negative": return tc(feature,category,"P1",ac_id,ac_id,"Reject a prohibited or invalid condition","Feature is available.",f"Exercise {ac_id} with an invalid, missing, unauthorized, expired, or prohibited condition relevant to the criterion.","The system rejects the invalid condition and preserves the required state/error behavior.","Error handling","targeted-fallback")
        if category=="boundary": return tc(feature,category,"P1",ac_id,ac_id,"Verify the nearest requirement boundary","Boundary values are available.",f"Test values immediately below, at, and immediately above the threshold or limit stated/implied by {ac_id}.","Behavior changes only at the defined boundary and remains compliant with the requirement.","Boundary behavior","targeted-fallback")
        return tc(feature,category,"P1",ac_id,ac_id,"Verify an edge sequence for the criterion","Feature is available.",f"Exercise a meaningful edge sequence or state transition around {ac_id}.","The system handles the edge condition without violating the acceptance criterion.","Resilience/state behavior","targeted-fallback")
    def _coverage(self,spec,cases):
        ac_ids=[x["id"] for x in spec["acceptance_criteria"]]; by={a:[] for a in ac_ids}
        for c in cases:
            for a in c.acceptance_criteria.split(","):
                if a.strip() in by: by[a.strip()].append(c)
        ac_report=[]; gaps=[]
        for a in ac_ids:
            present={c.category for c in by[a]}; missing=sorted(set(CATEGORIES)-present)
            ac_report.append({"ac":a,"categories_present":sorted(present),"required_categories":list(CATEGORIES),"missing_categories":missing})
            if missing: gaps.append({"type":"acceptance_criterion","id":a,"reason":"Missing required category coverage","missing":missing})
        rule_report=[]
        for rule in self._business_rules(spec):
            keywords=[w.lower() for w in re.findall(r"[A-Za-z]{4,}",rule["text"])[:6]]
            matched=[c.id for c in cases if any(k in (c.title+" "+c.steps+" "+c.expected_result).lower() for k in keywords)]
            covered=bool(matched); rule_report.append({"rule":rule["id"],"text":rule["text"],"covered":covered,"example_test_cases":matched[:5]})
            if not covered: gaps.append({"type":"business_rule","id":rule["id"],"reason":"No test case covers this explicit rule","missing":[rule["text"]]})
        messages=[]
        for ac in spec["acceptance_criteria"]:
            for msg in re.findall(r'"([^"]+)"',ac["text"]):
                matched=[c.id for c in by[ac["id"]] if msg in c.expected_result or msg in c.steps]
                messages.append({"ac":ac["id"],"message":msg,"covered":bool(matched),"example_test_cases":matched[:3]})
                if not matched: gaps.append({"type":"required_message","id":ac["id"],"reason":"Required message is not explicitly asserted","missing":[msg]})
        return {"case_count":len(cases),"acceptance_criteria":ac_report,"business_rules":rule_report,"required_messages":messages,"gaps":gaps,"covered_acceptance_criteria":[x["ac"] for x in ac_report if not x["missing_categories"]],"uncovered_acceptance_criteria":[x["ac"] for x in ac_report if x["missing_categories"]]}
    def critique(self,spec,cases): return self._coverage(spec,cases)
    def repair_from_gaps(self,spec,cases,critique):
        existing={(c.acceptance_criteria,c.category,c.title) for c in cases}; additions=[]
        for gap in critique["gaps"]:
            if gap["type"]=="acceptance_criterion":
                for cat in gap["missing"]:
                    c=self._targeted_case(spec,gap["id"],cat); key=(c.acceptance_criteria,c.category,c.title)
                    if key not in existing: additions.append(c)
            elif gap["type"]=="business_rule":
                rule=gap["missing"][0]; candidates=spec["acceptance_criteria"]
                words=set(re.findall(r"[a-z]{5,}",rule.lower())); best=max(candidates,key=lambda a:len(words & set(re.findall(r"[a-z]{5,}",a["text"].lower()))))
                c=self._targeted_case(spec,best["id"],"edge"); c.rule_trace=gap["id"]; c.title=f"{gap['id']}: explicit rule coverage - {rule}"; c.source="rule-repair"; additions.append(c)
            else:
                msg=gap["missing"][0]; c=tc(spec["name"],"negative","P0",gap["id"],gap["id"],f"{gap['id']}: assert required message","Feature is available.",f"Trigger {gap['id']} and observe the response.",f'The exact required message "{msg}" is shown.',"Error-message correctness","message-repair"); additions.append(c)
        return cases+additions
    def run(self,spec):
        self.iterations=[]; cases=self._base_cases(spec)
        for i in range(1,self.max_iterations+1):
            critique=self.critique(spec,cases); self.iterations.append({"iteration":i,"case_count":len(cases),"critique":critique})
            if not critique["gaps"]: break
            repaired=self.repair_from_gaps(spec,cases,critique)
            if len(repaired)==len(cases): break
            cases=repaired
        for n,c in enumerate(cases,1): c.id=f"{spec['id']}-TC-{n:03d}"
        return {"spec":spec,"cases":cases,"critique":self.critique(spec,cases),"iterations":self.iterations}
    @staticmethod
    def _gherkin(cases,feature):
        lines=[f"Feature: {feature}",""]
        for c in cases: lines += [f"  # {c.id} | {c.category} | {c.priority} | {c.acceptance_criteria} | {c.rule_trace}",f"  Scenario: {c.title}",f"    Given {c.preconditions}",f"    When {c.steps}",f"    Then {c.expected_result}",""]
        return "\n".join(lines)
    def write_outputs(self,result,outdir):
        outdir.mkdir(parents=True,exist_ok=True); fields=[f.name for f in TestCase.__dataclass_fields__.values()]
        with (outdir/f"test_cases_{result['spec']['id']}.csv").open("w",newline="",encoding="utf-8-sig") as h:
            w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(asdict(c) for c in result["cases"])
        (outdir/f"test_suite_{result['spec']['id']}.feature").write_text(self._gherkin(result["cases"],result["spec"]["name"]),encoding="utf-8")
        report={"feature":result["spec"]["name"],"acceptance_criteria_count":len(result["spec"]["acceptance_criteria"]),"generated_case_count":len(result["cases"]),"coverage":result["critique"],"iterations":result["iterations"]}
        (outdir/f"coverage_report_{result['spec']['id']}.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")

def generate_all(spec_dir,outdir,iterations=4):
    all_cases=[]; summary=[]; agent=TestCaseAgent(iterations)
    for path in sorted(Path(spec_dir).glob("feature_*.json")):
        spec=json.loads(path.read_text(encoding="utf-8")); result=agent.run(spec); agent.write_outputs(result,Path(outdir)); all_cases.extend(result["cases"])
        summary.append({"feature_id":spec["id"],"feature":spec["name"],"generated_cases":len(result["cases"]),"final_gaps":result["critique"]["gaps"],"iterations":len(result["iterations"])})
    fields=[f.name for f in TestCase.__dataclass_fields__.values()]
    with (Path(outdir)/"all_test_cases.csv").open("w",newline="",encoding="utf-8-sig") as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(asdict(c) for c in all_cases)
    (Path(outdir)/"coverage_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
    return {"features":summary,"total_cases":len(all_cases)}

def main():
    p=argparse.ArgumentParser(description="Generate categorized, traceable test suites with self-critique and repair."); p.add_argument("--spec-dir",default="specs"); p.add_argument("--out-dir",default="outputs"); p.add_argument("--iterations",type=int,default=4); a=p.parse_args(); print(json.dumps(generate_all(a.spec_dir,a.out_dir,a.iterations),indent=2,ensure_ascii=False))

if __name__=="__main__": main()
