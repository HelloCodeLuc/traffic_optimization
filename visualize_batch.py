
def count_non_blank_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        non_blank_lines = [line for line in file if line.strip()]  # Filter out blank lines
    return len(non_blank_lines)



file_path = "out/2025_03_23_20_35_49/TRAIN_BLUETOOTH/output_data.txt"
non_blank_count = count_non_blank_lines(file_path)
print(f"Number of non-blank lines: {non_blank_count}")