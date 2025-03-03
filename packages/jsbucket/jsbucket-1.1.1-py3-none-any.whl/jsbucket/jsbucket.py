import argparse
import requests
from urllib.parse import urljoin
import re
import json
import threading
from tqdm import tqdm
from rich.console import Console
from rich.style import Style
import os

# force ANSI support on Windows
os.system("")

console = Console(force_terminal=True)

# styles for terminal output
json_key_style = Style(color="green", bold=True)  
subdomain_value_style = Style(color="blue")  
bucket_name_value_style = Style(color="cyan") 
bucket_url_value_style = Style(color="blue") 
success_style = Style(color="green", bold=True) 
error_style = Style(color="red", bold=True) 
progress_style = Style(color="magenta", bold=True) 

# fetch HTML content
def get_html_content(url):
    try:
        response = requests.get(url, timeout=20, verify=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException:
        return None

# extract JavaScript URLs
def extract_js_urls(html_content, base_url):
    try:
        js_urls = re.findall(r"(?<=src=['\"])[a-zA-Z0-9_\.\-\:\/]+\.js", html_content.decode('utf-8', 'ignore'))
        return [urljoin(base_url, js_url) for js_url in js_urls]
    except Exception as e:
        console.print(f"Error extracting JavaScript URLs: {e}", style=error_style)
        return []

# extract S3 buckets
def extract_s3_buckets(content):
    try:
        if content is None:
            return []

        # extract S3 bucket names
        decoded_content = content.decode('utf-8', 'ignore')
        regs3 = r"([\w\-\.]+)\.s3\.?(?:[\w\-\.]+)?\.amazonaws\.com|(?<!\.)s3\.?(?:[\w\-\.]+)?\.amazonaws\.com\\?\/([\w\-\.]+)"
        matches = re.findall(regs3, decoded_content)
        # filtering empty
        s3_buckets = [match[0] or match[1] for match in matches if match[0] or match[1]]
        # deduplicate
        return list(set(s3_buckets))
    except Exception as e:
        console.print(f"Error extracting S3 Buckets: {e}", style=error_style)
        return []

# format JSON output
def format_json_with_colors(data):
    formatted_output = []
    for key, value in data.items():
        if key == "subdomain":
            formatted_output.append(
                f"{console.render_str(key, style=json_key_style)}: {console.render_str(value if value.startswith(('http://', 'https://')) else 'https://' + value, style=subdomain_value_style)}"
            )
        elif key == "s3_buckets": 
            formatted_buckets = "[\n"
            for bucket in value:
                bucket_formatted = ",\n".join(
                    f"    {console.render_str(k, style=json_key_style)}: "
                    f"{console.render_str(v, style=bucket_name_value_style if k == 'bucket_name' else bucket_url_value_style)}"
                    for k, v in bucket.items()
                )
                formatted_buckets += f"  {{\n{bucket_formatted}\n  }},\n"
            formatted_buckets = formatted_buckets.rstrip(",\n") + "\n]"
            formatted_output.append(f"{console.render_str(key, style=json_key_style)}: {formatted_buckets}")
        else: 
            formatted_output.append(
                f"{console.render_str(key, style=json_key_style)}: {console.render_str(value, style=subdomain_value_style)}"
            )
    return "{\n" + ",\n".join(formatted_output) + "\n}"

# analyze a single subdomain
def analyze_subdomain(subdomain, base_domain, results, lock, progress_bar, args):  # Add `args` as a parameter
    result_entry = {"subdomain": subdomain, "s3_buckets": []}

    protocols = ["https://", "http://"]
    successful_protocol = None
    html_content = None

    if any(subdomain.startswith(protocol) for protocol in protocols):
        full_url = subdomain
        try:
            response = requests.get(full_url, timeout=args.timeout, verify=True)  # Use `args.timeout`
            response.raise_for_status()
            html_content = response.content
            successful_protocol = full_url.split("://")[0] + "://"
        except requests.exceptions.RequestException as e:
            pass
    else:
        for protocol in protocols:
            full_url = f"{protocol}{subdomain}"
            try:
                response = requests.get(full_url, timeout=args.timeout, verify=True)  # Use `args.timeout`
                response.raise_for_status()
                html_content = response.content
                successful_protocol = protocol
                break
            except requests.exceptions.RequestException:
                continue
        if not successful_protocol:
            if progress_bar:
                progress_bar.update(1)
            return

    subdomain_with_protocol = f"{successful_protocol}{subdomain}" if not subdomain.startswith(('http://', 'https://')) else subdomain

    try:
        s3_buckets = extract_s3_buckets(html_content)
        unique_buckets = []
        seen_buckets = set()

        for bucket_name in s3_buckets:
            if bucket_name not in seen_buckets:
                seen_buckets.add(bucket_name)
                bucket_url = f"https://{bucket_name}.s3.amazonaws.com"
                unique_buckets.append({
                    "bucket_name": bucket_name,
                    "bucket_url": bucket_url
                })

        result_entry["s3_buckets"] = unique_buckets

        if unique_buckets and not args.silent:
            alert_message = f"\nAlert: S3 Bucket(s) found on subdomain {subdomain_with_protocol}!"
            console.print(alert_message, style=success_style)
            formatted_json = format_json_with_colors(result_entry)
            console.print(formatted_json)

    except Exception as e:
        pass

    # update progress bar
    if progress_bar:
        progress_bar.update(1)

    # Thread-safe update of results
    with lock:
        results.append(result_entry)

# main function
def main():
    parser = argparse.ArgumentParser(description="Analyze Javascript files from given subdomain(s) for S3 buckets.")
    parser.add_argument("-u", "--subdomain", help="single subdomain")
    parser.add_argument("-d", "--domain", required=True, help="base/root domain")
    parser.add_argument("-l", "--list", help="file containing a list of subdomains")
    parser.add_argument("-t", "--threads", type=int, default=10, help="number of threads (default: 10)")
    parser.add_argument("-timeout", type=int, default=10, help="timeout for HTTP requests (default: 10s)")
    parser.add_argument("-o", "--output", help="output file in JSON format")
    parser.add_argument("-silent", action="store_true", help="suppress all output except raw JSON")

    args = parser.parse_args()

    if not args.subdomain and not args.list:
        parser.error("Either -u/--subdomain or -l/--list and -d must be provided.")

    subdomains = []
    if args.subdomain:
        subdomains.append(args.subdomain)
    if args.list:
        try:
            with open(args.list, "r") as f:
                subdomains.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            if not args.silent:
                console.print(f"Error: File '{args.list}' not found.", style=error_style)
            exit(1)

    # progress bar is disabled in silent mode
    progress_bar = tqdm(total=len(subdomains), desc="Analyzing subdomains", unit="subdomain", dynamic_ncols=True) if not args.silent else None

    # analyze subdomains using threads
    results = []
    lock = threading.Lock()
    threads = []

    try:
        for subdomain in subdomains:
            thread = threading.Thread(target=analyze_subdomain, args=(subdomain, args.domain, results, lock, progress_bar, args))  # Pass `args`
            threads.append(thread)
            thread.start()

            # number of concurrent threads
            if len(threads) >= args.threads:
                for t in threads:
                    t.join()
                threads = []

        for t in threads:
            t.join()

        if progress_bar:
            progress_bar.close()

        filtered_results = [result for result in results if result["s3_buckets"]]

        if args.output:
            with open(args.output, "w") as f:
                json.dump(filtered_results, f, indent=4)
            if not args.silent:
                console.print(f"\n📝 Results written to {args.output}", style=progress_style)

        # raw JSON output in silent mode
        if args.silent:
            print(json.dumps(filtered_results, indent=4))
        else:
            console.print("\n✅ Analysis complete!", style=progress_style)

    except KeyboardInterrupt:
        if not args.silent:
            console.print("\n❌ Process interrupted by user. Exiting gracefully...", style=error_style)
        if progress_bar:
            progress_bar.close()
        exit(1)

if __name__ == "__main__":
    main()