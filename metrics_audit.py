import os
from radon.complexity import cc_visit, cc_rank
from src.lcom import LCOM4

def check_complexity(path):
    print(f"--- McCABE CYCLOMATIC COMPLEXITY ---")
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py") and "migrations" not in root:
                full_path = os.path.join(root, file)
                with open(full_path, "r") as f:
                    code = f.read()

                blocks = cc_visit(code)
                for block in blocks:
                    if block.complexity > 5: # Focus on "Moderate" to "High" risk
                        rank = cc_rank(block.complexity)
                        print(f"[!] {file} -> {block.name}: {block.complexity} ({rank})")

def check_lcom4(path):
    from src.reflection import ModuleReflection

    print(f"\n--- LCOM4 (LACK OF COHESION) ---")
    print("Goal: 1 (Highly Cohesive). Score > 1 means the class should be split.")

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py") and "migrations" not in root:
                full_path = os.path.join(root, file)
                try:
                    # LCOM4 library analysis
                    module_reflection = ModuleReflection.from_file(full_path)
                    lcom4 = LCOM4()

                    for class_reflection in module_reflection.classes():
                        score = lcom4.calculate(class_reflection)
                        class_name = class_reflection.name().split('.')[-1]

                        if score > 1:
                            status = "⚠️  SHOULD BE SPLIT"
                            print(f"{status} | {file} -> {class_name}: LCOM4 = {score}")
                        else:
                            print(f"✅ OK | {file} -> {class_name}: LCOM4 = {score}")
                except Exception as e:
                    print(f"⚠️  Error analyzing {file}: {e}")

if __name__ == "__main__":
    # Point to your backend directory
    project_root = "./backend"
    check_complexity(project_root)
    check_lcom4(project_root)