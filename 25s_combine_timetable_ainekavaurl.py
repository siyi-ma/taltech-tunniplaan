import os
import json

# Set your input and output directories
input_directory = "C:/Users/siyi.ma/Downloads/25sdailytimetables_new"
output_directory = input_directory  # You can set a different output directory if needed

combined = []
seen = set()
ainekavaurl_set = set()

# Loop through all JSON files and combine unique rows
for filename in os.listdir(input_directory):
    if filename.endswith("_daily_timetable.json"):
        file_path = os.path.join(input_directory, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for row in data:
                    # Use a tuple of sorted items as a unique key for each row
                    row_tuple = tuple(sorted(row.items()))
                    if row_tuple not in seen:
                        seen.add(row_tuple)
                        combined.append(row)
                        # Collect unique ainekavaurl if present and non-empty
                        ainekavaurl = row.get("ainekavaurl", "").strip()
                        if ainekavaurl:
                            ainekavaurl_set.add(ainekavaurl)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

# Save the combined unique rows to a new JSON file
output_file = os.path.join(output_directory, "all_daily_timetable.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

# Save all unique ainekavaurl to a separate JSON file
ainekavaurl_file = os.path.join(output_directory, "unique_ainekavaurl.json")
with open(ainekavaurl_file, "w", encoding="utf-8") as f:
    json.dump(sorted(ainekavaurl_set), f, ensure_ascii=False, indent=2)

print(f"Combined {len(combined)} unique rows into {output_file}")
print(f"Extracted {len(ainekavaurl_set)} unique ainekavaurl into {ainekavaurl_file}")