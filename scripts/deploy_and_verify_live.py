import os, sys, time, json, urllib.request, urllib.error
import subprocess
from huggingface_hub import HfApi

TOKEN = os.environ.get("HF_TOKEN", "")
REPO_ID = "sheik11111/Doculens"
SPACE_URL = "https://sheik11111-doculens.hf.space"

def main():
    print("1. Committing to GitHub...")
    subprocess.run(["git", "add", "src/generation/open_weight_generator.py", "scripts/test_15_questions.py"], check=False)
    subprocess.run(["git", "commit", "-m", "fix: precise entity synthesis for candidate name and inquiries"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=False)
    print("GitHub push completed.")

    print("\n2. Uploading updated open_weight_generator.py to Hugging Face Space...")
    api = HfApi(token=TOKEN)
    api.upload_file(
        path_or_fileobj="src/generation/open_weight_generator.py",
        path_in_repo="src/generation/open_weight_generator.py",
        repo_id=REPO_ID,
        repo_type="space"
    )
    print("File uploaded successfully to Hugging Face Space.")

    print("\n3. Waiting for Space to rebuild and reach RUNNING state...")
    for i in range(30):
        time.sleep(4)
        try:
            runtime = api.get_space_runtime(REPO_ID)
            stage = runtime.stage
            print(f"[{i*4}s] Current Space stage: {stage}")
            if stage == "RUNNING":
                print("Space is RUNNING!")
                break
        except Exception as e:
            print(f"Error checking runtime: {e}")

    # Give an extra 3 seconds for server to be ready to accept requests
    time.sleep(3)

    print("\n4. Running 15 Verification Queries on LIVE Hugging Face Space Cloud Endpoint...")
    print("Endpoint:", f"{SPACE_URL}/api/query")

    test_queries = [
        {"q": "name of the candidate", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Sheik Mohammed"},
        {"q": "who is the candidate?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Sheik Mohammed"},
        {"q": "what are the project he has done ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "EduCrazepolis"},
        {"q": "tell me about educrazepolis project", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Django"},
        {"q": "tell me about handplay hub project", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Hand Cricket"},
        {"q": "what is his technical skills ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Java"},
        {"q": "what are the programming languages he knows ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Java"},
        {"q": "where is he currently working ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Zlendo"},
        {"q": "what is his work experience and internship ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Zlendo"},
        {"q": "tell me about his education and college", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Sethu Institute of Technology"},
        {"q": "what is his CGPA ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "8.8"},
        {"q": "what languages can he speak and what is his fluency ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Tamil"},
        {"q": "how can i contact him? email and phone", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "sheikmohammed480@gmail.com"},
        {"q": "audit discrepancies in INV-099", "doc": "INV_2024_099_Disputed.pdf", "expect": "210"},
        {"q": "what is the limitation of liability cap under the agreement?", "doc": "MSA_Acme_Cyberdyne_2024.pdf", "expect": "12"}
    ]

    results = []
    for idx, t in enumerate(test_queries, 1):
        payload = json.dumps({
            "query": t["q"],
            "target_document": t["doc"],
            "user_token": "admin_master_token"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{SPACE_URL}/api/query",
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data.get("answer", "")
                passed = t["expect"].lower() in ans.lower()
                status = "PASS" if passed else "FAIL"
                results.append({
                    "id": idx,
                    "query": t["q"],
                    "status": status,
                    "expected": t["expect"],
                    "answer_preview": ans.replace("\n", " ")[:150]
                })
                print(f"[{status}] Q{idx:02d}: {t['q']} -> Match: {passed}")
        except Exception as e:
            print(f"[ERROR] Q{idx:02d}: {t['q']} -> {e}")
            results.append({"id": idx, "query": t["q"], "status": "ERROR", "expected": t["expect"], "answer_preview": str(e)})

    with open("scripts/live_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    passed_count = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n==========================================")
    print(f"LIVE CLOUD TEST SUMMARY: {passed_count}/{len(test_queries)} Passed")
    print(f"==========================================")

if __name__ == "__main__":
    main()
