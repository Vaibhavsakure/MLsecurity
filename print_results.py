import json
data = json.load(open("test_results2.json"))
for platform, tests in data.items():
    print(platform.upper())
    for t in tests:
        if "error" in t:
            print("  " + t["label"] + ": ERROR - " + t["error"])
        else:
            print("  " + t["label"] + ": prob=" + str(t["probability"]) + " risk=" + t["risk_level"])
    print()
