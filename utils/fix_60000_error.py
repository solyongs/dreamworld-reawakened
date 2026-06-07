import json
from pathlib import Path

MASK = 2147483647  # 0x7FFFFFFF


def calculate_pid(friend_code: str) -> int:
    friend_code = friend_code.replace("-", "").replace(" ", "")

    if not friend_code.isdigit():
        raise ValueError("Friend Code must contain only digits.")

    return int(friend_code) & MASK


def main():
    print("Error 60000 Fix\n")

    friend_code = input("Enter your in-game Friend Code from your Pal Pad (with or without dashes): ")

    pid = calculate_pid(friend_code)

    print(f"\nCalculated PID: {pid}")

    root_dir = Path(__file__).resolve().parent.parent
    save_dir = root_dir / "save_data"

    files = sorted(save_dir.glob("WFC-*.json"))

    if not files:
        print(f"No WFC profiles found in {save_dir}")
        return

    print(f"Found {len(files)} save file(s).\n")

    for file_path in files:
        with open(file_path, encoding="UTF-8") as f:
            data = json.load(f)

        profiles = data.get("profiles", {})
        updated = 0

        for profile_name, profile in profiles.items():
            old_pid = profile.get("id")
            profile["id"] = pid

            print(
                f"{file_path.name}: "
                f"{profile_name} "
                f"({old_pid} -> {pid})"
            )

            updated += 1

        if updated:
            with open(file_path, "w", encoding="UTF-8") as f:
                json.dump(data, f, indent=2)

    print("\nDone.")
    print("Restart the game sync server and try connecting again.")


if __name__ == "__main__":
    main()
