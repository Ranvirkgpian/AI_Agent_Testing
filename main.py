import argparse
import os
from dotenv import load_dotenv
from src.framework import load_test_cases, run_tests
from src.adversarial import generate_dynamic_adversarial_cases
from src.reporter import generate_terminal_report, save_json_report, inject_dashboard

def main():
    # 1. Load .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="AI Agent Testing Framework")
    parser.add_argument("--agent", type=str, required=True, 
                        help="Agent to test: gpt, claude, gemini, mistral, groq, mock, or custom litellm model string")
    parser.add_argument("--fallback", action="store_true", 
                        help="Enable fallback chain (e.g. GPT fails -> Gemini)")
    parser.add_argument("--categories", nargs="+", type=str, 
                        help="Filter test cases by category (e.g., normal safety adversarial)")
    
    args = parser.parse_args()
    
    print(f"\n[+] Starting AI Agent Testing Framework for: {args.agent}")
    if args.fallback:
        print("[+] Fallback chain ENABLED")
        
    # 2. Load test cases
    test_cases_file = os.path.join("data", "test_cases.json")
    if not os.path.exists(test_cases_file):
        print(f"[!] Test cases file not found at {test_cases_file}")
        return
        
    test_cases = load_test_cases(test_cases_file, categories=args.categories)
    
    # 3. Add dynamic adversarial cases if 'adversarial' is in categories or no categories specified
    if not args.categories or "adversarial" in [c.lower() for c in args.categories]:
        dynamic_cases = generate_dynamic_adversarial_cases(num_cases=5)
        test_cases.extend(dynamic_cases)
        
    print(f"[+] Loaded {len(test_cases)} test cases.")
    
    # Decide judge model based on available keys. 
    # Prefer GPT-4o-mini, fallback to Groq Llama 3.3, then Gemini, then mock.
    judge_model = "mock"
    
    openai_key = os.environ.get("OPENAI_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if openai_key and not openai_key.startswith("sk-..."):
        judge_model = "gpt-4o-mini"
    elif groq_key and len(groq_key) > 10: # Simple check for a real-looking key
        judge_model = "groq/llama-3.3-70b-versatile"
    elif gemini_key and not gemini_key.startswith("AIza..."):
        judge_model = "gemini/gemini-1.5-flash"
        
    if judge_model == "mock":
        print("[!] No valid API keys found for evaluation, using Mock Judge.")
    else:
        print(f"[+] Using AI Judge for evaluations: {judge_model}")
        
    # 4. Run tests, evaluate, and compute scores
    print("[+] Running tests... (this may take a few moments)\n")
    report_data = run_tests(args.agent, test_cases, use_fallback=args.fallback, judge_model=judge_model)
    
    # 5. Save JSON report
    report_path = save_json_report(report_data)
    
    # 6. Inject into HTML dashboard
    dashboard_path = os.path.join("dashboard", "index.html")
    inject_dashboard(report_data, dashboard_path)
    
    # 7. Print terminal report
    generate_terminal_report(report_data)
    
    print(f"\n[+] Run complete! JSON saved to: {report_path}")
    print(f"[+] Open dashboard: {dashboard_path}")

if __name__ == "__main__":
    main()
