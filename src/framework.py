import time
import json
import os
from .agents import run_agent, get_model_name
from .evaluator import evaluate_response
from .adversarial import generate_dynamic_adversarial_cases

def load_test_cases(filepath: str, categories: list = None) -> list[dict]:
    with open(filepath, 'r') as f:
        cases = json.load(f)
    
    if categories:
        categories = [c.lower() for c in categories]
        cases = [c for c in cases if c.get("category", "").lower() in categories]
        
    return cases

def run_tests(agent_alias: str, test_cases: list[dict], use_fallback: bool = False, judge_model: str = "gpt-4o-mini") -> dict:
    """
    Main testing engine.
    Loops through test cases, runs the agent, evaluates, and computes scores.
    """
    model_name = get_model_name(agent_alias)
    
    results = []
    total_cost = 0.0
    times = []
    
    counts = {"total": 0, "passed": 0, "failed": 0}
    category_counts = {
        "normal": {"total": 0, "passed": 0},
        "edge case": {"total": 0, "passed": 0},
        "adversarial": {"total": 0, "passed": 0},
        "safety": {"total": 0, "passed": 0}
    }
    
    log_file_path = os.path.join("evaluation", "evaluation.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    with open(log_file_path, "a") as log_file:
        log_file.write(f"--- Starting new evaluation run for agent: {model_name} at {time.ctime()} ---\n")

    for case in test_cases:
        cat = case.get("category", "normal").lower()
        if cat not in category_counts:
            category_counts[cat] = {"total": 0, "passed": 0}
            
        start_time = time.time()
        
        # Run agent
        response_text, cost = run_agent(model_name, case["input"], use_fallback=use_fallback)
        
        end_time = time.time()
        duration = end_time - start_time
        times.append(duration)
        total_cost += cost
        
        # Evaluate
        eval_result = evaluate_response(response_text, duration, case, judge_model=judge_model)
        
        passed = eval_result["passed"]
        
        counts["total"] += 1
        category_counts[cat]["total"] += 1
        
        if passed:
            counts["passed"] += 1
            category_counts[cat]["passed"] += 1
        else:
            counts["failed"] += 1
            
        result_record = {
            "id": case["id"],
            "input": case["input"],
            "expected": case.get("expected_behavior", "N/A"),
            "category": cat,
            "response": response_text,
            "duration": duration,
            "cost": cost,
            "passed": passed,
            "eval_metrics": eval_result
        }
        results.append(result_record)

        # Log Observability details
        with open(log_file_path, "a") as log_file:
            log_file.write(f"Test Case ID: {case['id']}\n")
            log_file.write(f"Input: {case['input']}\n")
            log_file.write(f"Output: {response_text}\n")
            log_file.write(f"Evaluation Scores: {json.dumps(eval_result)}\n")
            log_file.write(f"Passed: {passed}\n")
            log_file.write("-" * 40 + "\n")
            
        # Rate limit protection for Judge API if not mock
        if judge_model != "mock":
            time.sleep(1)

    # Compute scores
    def calc_pct(passed, total):
        return (passed / total * 100) if total > 0 else 0.0
    
    safe_adv_passed = category_counts["safety"]["passed"] + category_counts["adversarial"]["passed"]
    safe_adv_total = category_counts["safety"]["total"] + category_counts["adversarial"]["total"]
    
    safety_score = calc_pct(safe_adv_passed, safe_adv_total)
    accuracy_score = calc_pct(category_counts["normal"]["passed"], category_counts["normal"]["total"])
    robustness_score = calc_pct(category_counts["edge case"]["passed"], category_counts["edge case"]["total"])
    
    overall_score = (safety_score * 0.40) + (accuracy_score * 0.35) + (robustness_score * 0.25)
    
    # Timing stats
    mean_time = sum(times) / len(times) if times else 0
    fastest = min(times) if times else 0
    slowest = max(times) if times else 0
    times_sorted = sorted(times)
    median_time = times_sorted[len(times)//2] if times else 0
    
    mean_cost = total_cost / counts["total"] if counts["total"] > 0 else 0
    
    report_data = {
        "agent": model_name,
        "timestamp": time.time(),
        "summary": {
            "total_tests": counts["total"],
            "passed": counts["passed"],
            "failed": counts["failed"]
        },
        "scores": {
            "safety": round(safety_score, 1),
            "accuracy": round(accuracy_score, 1),
            "robustness": round(robustness_score, 1),
            "overall": round(overall_score, 1)
        },
        "timing": {
            "mean_s": round(mean_time, 2),
            "median_s": round(median_time, 2),
            "fastest_s": round(fastest, 2),
            "slowest_s": round(slowest, 2)
        },
        "cost": {
            "total_cost": total_cost,
            "mean_cost_per_query": mean_cost
        },
        "results": results
    }
    
    return report_data
