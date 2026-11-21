import os, sys, time, json, urllib.request, urllib.error

SPACE_URL = "https://sheik11111-doculens.hf.space"

def main():
    print("1. Authenticating as Admin with live cloud backend...")
    login_payload = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
    login_req = urllib.request.Request(
        f"{SPACE_URL}/api/auth/login",
        data=login_payload,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(login_req, timeout=15) as resp:
            login_data = json.loads(resp.read().decode("utf-8"))
            token = login_data.get("token")
            user = login_data.get("user", {})
            print(f"Logged in successfully as {user.get('username')} ({user.get('role')})")
            print(f"Token obtained: {token[:20]}...")
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        return

    print("\n2. Executing 15 Comprehensive Evaluation Questions on LIVE Hugging Face Space...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    test_queries = [
        {"id": 1, "q": "name of the candidate", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Sheik Mohammed"},
        {"id": 2, "q": "who is the candidate?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Sheik Mohammed"},
        {"id": 3, "q": "what are the project he has done ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "EduCrazepolis"},
        {"id": 4, "q": "tell me about educrazepolis project", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Django"},
        {"id": 5, "q": "tell me about handplay hub project", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Hand Cricket"},
        {"id": 6, "q": "what is his technical skills ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Java"},
        {"id": 7, "q": "what are the programming languages he knows ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Java"},
        {"id": 8, "q": "where is he currently working ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Zlendo"},
        {"id": 9, "q": "what is his work experience and internship ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Zlendo"},
        {"id": 10, "q": "tell me about his education and college", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Sethu Institute of Technology"},
        {"id": 11, "q": "what is his CGPA ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "8.8"},
        {"id": 12, "q": "what languages can he speak and what is his fluency ?", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "Tamil"},
        {"id": 13, "q": "how can i contact him? email and phone", "doc": "Sheik_Mohammed_Resume.pdf", "expect": "sheikmohammed480@gmail.com"},
        {"id": 14, "q": "audit discrepancies in INV-099", "doc": "INV_2024_099_Disputed.pdf", "expect": "210"},
        {"id": 15, "q": "what is the limitation of liability cap under the agreement?", "doc": "MSA_Acme_Cyberdyne_2024.pdf", "expect": "12"}
    ]

    results = []
    passed_count = 0

    print("=" * 80)
    for t in test_queries:
        payload = json.dumps({
            "query": t["q"],
            "target_document": t["doc"]
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{SPACE_URL}/api/query",
            data=payload,
            headers=headers
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data.get("answer", "")
                passed = t["expect"].lower() in ans.lower()
                status = "PASS" if passed else "FAIL"
                if passed:
                    passed_count += 1
                results.append({
                    "id": t["id"],
                    "query": t["q"],
                    "status": status,
                    "expected": t["expect"],
                    "full_answer": ans
                })
                print(f"[{status}] Q{t['id']:02d}: {t['q']}")
                print(f"       Expected keyword: {t['expect']}")
                print(f"       Answer preview: {ans.replace(chr(10), ' ')[:130]}...")
                print("-" * 80)
        except Exception as e:
            print(f"[ERROR] Q{t['id']:02d}: {t['q']} -> {e}")
            results.append({"id": t["id"], "query": t["q"], "status": "ERROR", "expected": t["expect"], "full_answer": str(e)})

    with open("scripts/live_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nFINAL VERIFICATION SUMMARY: {passed_count}/{len(test_queries)} Questions Passed on Live Cloud Hugging Face Space!")
    print(f"Live Space URL: {SPACE_URL}/static/index.html")

if __name__ == "__main__":
    main()
