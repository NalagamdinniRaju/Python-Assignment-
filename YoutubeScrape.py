
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import yagmail
import re

# Chrome WebDriver Setup
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def extract_video_details(url):
    try:
        # Navigate to the YouTube video
        driver.get(url)

        # Extract the title
        try:
            title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='title']/h1/yt-formatted-string"))
            ).text
        except Exception:
            title = "Title could not be extracted"

        # Wait for the description element to load
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#description-inline-expander"))
        )

        # Expand the description
        try:
            expand_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "expand"))
            )
            expand_button.click()
        except Exception as e:
            print("Expand button could not be clicked:", e)

        # Extract description text
        description_text = description_element.text

        # Remove unwanted text
        unwanted_phrases = ["RK-P", "Videos", "About", "Show less"]
        for phrase in unwanted_phrases:
            description_text = description_text.replace(phrase, "")

        # Use regex to extract timestamps and their surrounding text
        matches = re.findall(r'(\d{1,2}:\d{2}.*)', description_text)

        return title, description_text.strip(), matches
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None, None, None

def save_to_file(url, title, description, timestamps, filename="timestamps.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"URL: {url}\n\n")
            file.write(f"Title: {title}\n\n")
            file.write("Description:\n")
            file.write(description + "\n\n")
            file.write("Timestamps List:\n")
            file.write("\n".join(timestamps))
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")

def send_email(sender_email, sender_password, recipient_email, subject, body, attachment):
    try:
        yag = yagmail.SMTP(sender_email, sender_password)
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=body,
            attachments=attachment
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    # Specify the YouTube video URL
    video_url = "https://youtu.be/iTmlw3vQPSs"

    # Extract video details
    title, description, timestamps = extract_video_details(video_url)

    if title and description and timestamps:
        # Save the URL, title, description, and timestamps to a file
        filename = "timestamps.txt"
        save_to_file(video_url, title, description, timestamps, filename)

        # Email the file with the video link
        sender_email = "nalagamdinniraju@gmail.com"  # Sender email
        sender_password = "avxo shej bbam ckks"      # Sender app-specific password
        recipient_email = "boyahanumanthu326@gmail.com"    # Recipient email
        subject = "YouTube Video Details with Timestamps"
        body = (
            f"Here is the data extracted from the YouTube video:\n\n"
            f"URL: {video_url}\n\n"
            f"Title: {title}\n\n"
            f"Description:\n{description}\n\n"
            f"Timestamps:\n{'  '.join(timestamps)}"
        )

        send_email(sender_email, sender_password, recipient_email, subject, body, filename)
    else:
        print("Failed to extract data.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()
