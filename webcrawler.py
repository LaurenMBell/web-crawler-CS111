import sys
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import re
import csv
from urllib.parse import urlparse, urldefrag, urljoin
import RequestGuard
import image_processing


def count_links(url, output_filename1, output_filename2):
    request_guard = RequestGuard.RequestGuard(url)

    links_to_visit = [url]
    visited_links = {}
    domain_counts = {}

    while links_to_visit:
        current_url = links_to_visit.pop(0)

        if current_url in visited_links:
            visited_links[current_url] += 1
            continue

        visited_links[current_url] = 1
        print(f"Visiting: {current_url}")  # Debug: Print visited URLs

        if request_guard.can_follow_link(current_url):
            try:
                page = requests.get(current_url)
                soup = BeautifulSoup(page.text, 'html.parser')

                for tag in soup.find_all('a', href=True):
                    href = tag['href']
                    processed_link = process_link(current_url, href)
                    if processed_link:
                        if processed_link not in visited_links:  # Add only if not visited already
                            links_to_visit.append(processed_link)

                        # Debug: Print processed link
                        print(f"Processed link: {processed_link}")

                        # Count links by domain
                        domain = urlparse(processed_link).netloc
                        if domain not in domain_counts:
                            domain_counts[domain] = 1
                        else:
                            domain_counts[domain] += 1

            except requests.exceptions.RequestException as e:
                print(f"Error fetching {current_url}: {str(e)}")

    # Debug: Print domain counts
    print(f"Domain counts: {domain_counts}")

    # Prepare domain counts in the desired output format
    sorted_domains = sorted(domain_counts.items())
    domain_counts_formatted = {i + 1: count for i, (domain, count) in enumerate(sorted_domains)}

    # Save to CSV
    save_domain_counts_to_csv(domain_counts_formatted, output_filename2)

    # Plot histogram
    plot_histogram(domain_counts_formatted, output_filename1)
def process_link(current_url, href):
    if href.startswith('http://') or href.startswith('https://'):
        return href.split('#')[0]

    if href.startswith('/'):
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(current_url))
        return domain + href

    if href.startswith('#'):
        return current_url.split('#')[0]

    if not re.match(r'^\w+://', href):
        return urljoin(current_url, href)

    return None

def save_domain_counts_to_csv(domain_counts, output_csv):
    # Function to save domain counts to CSV in the specified format
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for line_number, count in domain_counts.items():
            writer.writerow([f"{float(line_number):.1f}, {float(count):.1f}"])
def plot_histogram(domain_counts, output_filename):
    x_values = list(domain_counts.keys())
    y_values = list(domain_counts.values())

    plt.bar(x_values, y_values, color='blue')
    plt.xlabel('Domain Number')
    plt.ylabel('Link Count')
    plt.title('Link Count by Domain')
    plt.savefig(output_filename)
    plt.close()


def plot_data(url, output_filename1, output_filename2):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        table = soup.find('table', id='CS111-Project4b')
        if not table:
            print(f"Table with id 'CS111-Project4b' not found on {url}.")
            return

        x_values = []
        y_values = []

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            x_values.append(float(cols[0].text.strip()))
            y_values.append([float(col.text.strip()) for col in cols[1:]])

        # Debug: Print x_values and y_values
        print(f"x_values: {x_values}")
        print(f"y_values: {y_values}")

        colors = ['blue', 'green', 'red', 'black']
        for i, ys in enumerate(zip(*y_values)):
            plt.plot(x_values, ys, color=colors[i], label=f'Dataset {i+1}')

        plt.xlabel('X Values')
        plt.ylabel('Y Values')
        plt.title('Plot of Data from Table')
        plt.legend()
        plt.savefig(output_filename1)
        plt.close()

        with open(output_filename2, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['X Value'] + [f'Y Value {i+1}' for i in range(len(y_values[0]))])
            for row in zip(x_values, *y_values):
                writer.writerow(row)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {str(e)}")



def modify_images(url, output_file_prefix, filter_to_run):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        img_tags = soup.find_all('img')

        for img_tag in img_tags:
            try:
                img_url = img_tag['src']
                if not (img_url.startswith('http://') or img_url.startswith('https://')):
                    #Handle relative URLs or other invalid cases
                    img_url = urljoin(url, img_url)  # Resolve relative URLs

                response = requests.get(img_url)
                img_data = response.content

                img_filename = img_url.split('/')[-1]
                output_filename = output_file_prefix + img_filename

                with open(output_filename, 'wb') as img_file:
                    img_file.write(img_data)

                if filter_to_run == '-s':
                    image_processing.sepia(output_filename, output_filename)  # Adding outfile argument
                elif filter_to_run == '-g':
                    image_processing.grayscale(output_filename, output_filename)  # Adding outfile argument
                elif filter_to_run == '-f':
                    image_processing.flipped(output_filename, output_filename)  # Adding outfile argument
                elif filter_to_run == '-m':
                    image_processing.mirror(output_filename, output_filename)  # Adding outfile argument
                else:
                    print(f"Invalid filter option: {filter_to_run}")

            except (requests.exceptions.RequestException, requests.exceptions.MissingSchema) as e:
                print(f"Error processing image at {img_url}: {str(e)}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {str(e)}")


def validate_commands():
    if len(sys.argv) < 3:
        print("Invalid arguments")
        return False

    command = sys.argv[1]
    if command not in ['-c', '-p', '-i']:
        print("Invalid arguments")
        return False

    if command == '-c' and len(sys.argv) != 5:
        print("Invalid arguments")
        return False

    if command == '-p' and len(sys.argv) != 5:
        print("Invalid arguments")
        return False

    if command == '-i' and len(sys.argv) != 5:
        print("Invalid arguments")
        return False

    if command == '-i':
        filter_to_run = sys.argv[4]
        if filter_to_run not in ['-g', '-s', '-f', '-m']:
            print("Invalid arguments")
            return False

    return True


def main():
    if not validate_commands():
        sys.exit(1)

    command = sys.argv[1]
    url = sys.argv[2]

    if command == "-c":
        output_filename1 = sys.argv[3]
        output_filename2 = sys.argv[4]
        count_links(url, output_filename1, output_filename2)
    elif command == "-p":
        output_filename1 = sys.argv[3]
        output_filename2 = sys.argv[4]
        plot_data(url, output_filename1, output_filename2)
    elif command == "-i":
        output_file_prefix = sys.argv[3]
        filter_to_run = sys.argv[4]
        modify_images(url, output_file_prefix, filter_to_run)


if __name__ == "__main__":
    main()


