import logging
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import random
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Flask app initialization
app = Flask(__name__)

# Logger configuration
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
        sender_email = "getyourproductprice@gmail.com"
        sender_password = "Pricecomparison @123"  # Replace with actual credentials
        subject = f"Price Drop Alert: {product_name}"

        body = f"Good news! The price of {product_name} has dropped.\n\nCheck it out here: {product_link}"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()

        logger.info(f"Price drop notification sent to {email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

# Fetch pages with retries
def fetch_with_retries(url, headers, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if response.status_code == 429:  # Too Many Requests
                wait_time = 2 ** attempt + random.uniform(0, 1)
                logger.warning(f"429 Too Many Requests. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Request failed: {e}")
                raise e
    raise Exception(f"Failed to fetch URL {url} after {max_retries} retries.")

# Normalize product name
def normalize_product_name(name):
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()

# Scrape Amazon
def scrape_amazon(product, pages=2):
    amazon_data = []
    for page in range(1, pages + 1):
        url = f"https://www.amazon.in/s?k={'+'.join(product.split())}&page={page}"
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            response = fetch_with_retries(url, headers)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.find_all("div", {"data-component-type": "s-search-result"})
            for container in product_containers:
                try:
                    name_tag = container.find("h2", class_="a-size-medium")
                    if not name_tag:
                        continue
                    product_name = name_tag.text.strip()
                    product_link = f"https://www.amazon.in{container.find('a', href=True)['href']}"
                    price = container.find("span", class_="a-price-whole").text.strip() if container.find("span", class_="a-price-whole") else "N/A"
                    amazon_data.append({
                        "Product Name": product_name,
                        "Price": price,
                        "Product Link": product_link
                    })
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Error scraping Amazon: {e}")
    return amazon_data

# Scrape Flipkart
def scrape_flipkart(product, pages=2):
    flipkart_data = []
    for page in range(1, pages + 1):
        url = f"https://www.flipkart.com/search?q={'+'.join(product.split())}&page={page}"
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            response = fetch_with_retries(url, headers)
            soup = BeautifulSoup(response.text, "lxml")
            product_containers = soup.find_all("a", class_="IRpwTa")
            for container in product_containers:
                try:
                    product_name = container.text.strip()
                    product_link = f"https://www.flipkart.com{container['href']}"
                    flipkart_data.append({
                        "Product Name": product_name,
                        "Product Link": product_link
                    })
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Error scraping Flipkart: {e}")
    return flipkart_data

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/results', methods=['POST'])
def results():
    logger.info("Processing request at /results")
    product = request.form['product']
    amazon_data = scrape_amazon(product)
    flipkart_data = scrape_flipkart(product)
    logger.info("Request completed at /results")
    return render_template('result.html', amazon_data=amazon_data, flipkart_data=flipkart_data)

@app.route('/notify', methods=['POST'])
def notify_price_drop():
    email = request.form['email']
    product_name = request.form['product_name']
    product_link = request.form['product_link']
    send_price_drop_notification(email, product_name, product_link)
    return render_template('notification_success.html')

if __name__ == '__main__':
    app.run(debug=True)
