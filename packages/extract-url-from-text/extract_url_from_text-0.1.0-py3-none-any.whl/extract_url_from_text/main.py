import argparse
import datetime
import re


def extract_urls(text):
    text = re.sub(r"\s*\.\s*", ".", text)
    regex = re.compile(r"(https?:\/\/)?" r"([a-zA-Z0-9-]+\.)?" r"([a-zA-Z0-9-]{2,63})" r"(\.[a-zA-Z]{2,63})" r"(:\d{1,5})?" r"(\/[^\s]*)?")
    matches = [match.group(0) for match in re.finditer(regex, text)]
    return matches


def main():
    start_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    parser = argparse.ArgumentParser(description="Extract URLs from a text file")
    parser.add_argument("-i", "--input", required=True, help="Input file to extract")
    args = parser.parse_args()
    target_file = args.input

    try:
        keywords = [".go.th", ".com", ".cc", ".org", ".net", ".vip", ".top"]
        exclude_keyword = ["thaipoliceonline.go.th"]

        with open(target_file, "r", encoding="utf-8") as source_file:
            lines = source_file.readlines()
            lines = [line for line in lines if line.strip() != ""]
            lines = [line for line in lines if any(tld in line for tld in keywords) and not any(excl in line for excl in exclude_keyword)]
        file_name = f"exported_urls_{start_time}.txt"
        with open(file_name, "w", encoding="utf-8") as output_file:
            urls = []
            for line in lines:
                urls.extend(extract_urls(line))
            output_file.write("\n".join(urls))

        print(f"INFO: Exported {len(urls)} url(s) to {file_name}")

    except FileNotFoundError:
        print(f"ERROR: File not found => {target_file}")


if __name__ == "__main__":
    main()
