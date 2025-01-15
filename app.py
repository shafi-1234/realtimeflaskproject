from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# List of User-Agent strings to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36',
]

# Function to send price drop notification email
def send_price_drop_notification(email, product_name, product_link):
    try:
        # Email setup
        sender_email = "getyourproductprice@gmail.com"  # Replace with your sender email
        sender_password = "Pricecomparison @123"  # Replace with your email password
        subject = f"Price Drop Alert: {product_name}"

        body = f"Good news! The price of the product {product_name} has dropped.\n\nCheck it out here: {product_link}"

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Sending the email via Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        server.quit()
        print(f"Price drop notification sent to {email}")

    except Exception as e:
        print(f"Error sending email: {e}")

# Function to fetch pages with retries
def fetch_with_retries(url, headers, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if response.status_code == 429:  # Too Many Requests
                wait_time = 2 ** attempt + random.uniform(0, 1)  # Exponential backoff with jitter
                print(f"429 Too Many Requests. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception(f"Failed to fetch URL {url} after {max_retries} retries.")

# Normalize product name
def normalize_product_name(name):
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)  # Remove non-alphanumeric characters
    name = re.sub(r'\s+', ' ', name)  # Replace multiple spaces with one
    name = name.strip().lower()  # Remove leading/trailing spaces and convert to lowercase
    return name

# Scraping Amazon
def scrape_amazon(product, pages=2):
    amazon_data = []

    for page in range(1, pages + 1):
        url = f"https://www.amazon.in/s?k={'+'.join(product.split())}&page={page}"
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'en-US, en;q=0.5'
        }
        try:
            response = fetch_with_retries(url, headers)
            soup = BeautifulSoup(response.text, "lxml")

            product_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
            if not product_containers:
                continue

            for container in product_containers:
                try:
                    name_tag = container.find("h2", class_="a-size-medium a-spacing-none a-color-base a-text-normal")
                    if not name_tag:
                        continue

                    product_name = name_tag.text.strip()
                    normalized_name = normalize_product_name(product_name)

                    link_tag = name_tag.find_parent("a", href=True)
                    product_link = f"https://www.amazon.in{link_tag['href']}" if link_tag else "No link available"
                    price_tag = container.find("span", class_="a-price-whole")
                    price = price_tag.text.replace(",", "") if price_tag else "No price available"
                    desc_tag = container.find("div", class_="a-row a-size-base a-color-secondary")
                    description = desc_tag.text if desc_tag else "No description available"
                    review_tag = container.find("span", class_="a-icon-alt")
                    review = review_tag.text if review_tag else "No reviews available"
                    img_tag = container.find("img", class_="s-image")
                    product_image = img_tag["src"] if img_tag else "https://via.placeholder.com/100"

                    # Handle relative URLs for images
                    if not product_image.startswith('http'):
                        product_image = 'https://www.amazon.in' + product_image

                    amazon_data.append({
                        "Product Name": product_name,
                        "Normalized Name": normalized_name,
                        "Price": price,
                        "Description": description,
                        "Reviews": review,
                        "Product Link": product_link,
                        "Product Image": product_image
                    })

                except Exception as e:
                    continue

            time.sleep(random.uniform(2, 5))  # Random delay between requests
        except requests.exceptions.RequestException as e:
            continue

    return amazon_data

# Scraping Flipkart
def scrape_flipkart(product, pages=2):
    flipkart_data = []

    for page in range(1, pages + 1):
        url = f"https://www.flipkart.com/search?q={'+'.join(product.split())}&page={page}"
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept-Language': 'en-US, en;q=0.5'
        }
        try:
            response = fetch_with_retries(url, headers)
            soup = BeautifulSoup(response.text, "lxml")

            product_containers = soup.find_all("div", class_="cPHDOP col-12-12")
            if not product_containers:
                continue

            for container in product_containers:
                try:
                    name_tag = container.find("div", class_="KzDlHZ")
                    if not name_tag:
                        continue

                    product_name = name_tag.text.strip()
                    normalized_name = normalize_product_name(product_name)

                    link_tag = container.find("a", href=True)
                    product_link = f"https://www.flipkart.com{link_tag['href']}" if link_tag else "No link available"
                    price_tag = container.find("div", class_="Nx9bqj _4b5DiR")
                    price = price_tag.text.replace("\u20b9", "").replace(",", "") if price_tag else "No price available"
                    desc_tag = container.find("li", class_="J+igdf")
                    description = desc_tag.text if desc_tag else "No description available"
                    review_tag = container.find("div", class_="XQDdHH")
                    review = review_tag.text if review_tag else "No reviews available"
                    img_tag = container.find("img", class_="DByuf4")
                    product_image = img_tag["src"] if img_tag else "https://via.placeholder.com/100"

                    # Handle relative URLs for images
                    if not product_image.startswith('http'):
                        product_image = 'https://www.flipkart.com' + product_image

                    flipkart_data.append({
                        "Product Name": product_name,
                        "Normalized Name": normalized_name,
                        "Price": price,
                        "Description": description,
                        "Reviews": review,
                        "Product Link": product_link,
                        "Product Image": product_image
                    })

                except Exception as e:
                    continue

            time.sleep(random.uniform(2, 5))  # Random delay between requests
        except requests.exceptions.RequestException as e:
            continue

    return flipkart_data

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/results', methods=['POST'])
def results():
    try:
        if request.method == 'POST':
            product = request.form['product']
            amazon_data = scrape_amazon(product)
            flipkart_data = scrape_flipkart(product)

            if not amazon_data and not flipkart_data:
                return render_template('no_results.html')

            return render_template('result.html', amazon_data=amazon_data, flipkart_data=flipkart_data)
        else:
            return "Method Not Allowed", 405
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred. Please try again later."



@app.route('/notify', methods=['POST'])
def notify_price_drop():
    email = request.form['email']
    product_name = request.form['product_name']
    product_link = request.form['product_link']

    # You can implement your logic here to check if the price dropped
    # For now, we'll send the email regardless
    send_price_drop_notification(email, product_name, product_link)

    return render_template('notification_success.html')  # Redirect to a success page

if __name__ == '__main__':
    app.run(debug=True)
