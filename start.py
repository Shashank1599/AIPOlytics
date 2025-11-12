import os
import time

# --- Third-party Library Imports ---
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# --- LLM and Web Scraping Imports ---
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


######Langchain usage######
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser



# --- Load Environment Variables ---
load_dotenv() 

# --- Configure Google AI ---
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    print("Google AI SDK configured successfully.")
except Exception as e:
    print(f"Error configuring Google AI SDK: {e}")

# ==============================================================================
# WORKER FUNCTION 1: SCRAPE THE IPO DASHBOARD (The "Librarian")
# ==============================================================================
def scrape_ipo_dashboard():
    """
    Scrapes the main IPO dashboard to get a list of upcoming IPOs and their links.
    ** This function now uses Selenium to bypass anti-scraping measures. **
    """
    print("Step 1: Scraping the IPO Dashboard for upcoming IPOs...")
    url = "https://www.chittorgarh.com/ipo/ipo_dashboard.asp"
    upcoming_ipos = []
    current_ipos = []
    
    # --- Using Selenium for the dashboard ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("Navigating to dashboard with robot browser...")
        driver.get(url)
        
        # Wait for the mainboard IPO table header to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Current IPOs (Mainboard)')]"))
        )
        print("Dashboard loaded successfully.")
        
        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        mainboard_header = soup.find('h2', string=lambda text: 'Current IPOs (Mainboard)' in text)
        if not mainboard_header:
            print("Could not find the 'Current IPOs (Mainboard)' table header.")
            return []
            
        ipo_table = mainboard_header.find_next('table')
        if not ipo_table:
            print("Could not find the table following the header.")
            return []

        rows = ipo_table.find('tbody').find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                status = cells[3].text.strip()
                if status.lower() == 'current':
                    company_name = cells[0].text.strip()
                    link_tag = cells[0].find('a')
                    if link_tag and link_tag.has_attr('href'):
                        relative_url = link_tag['href']
                        full_url = f"https://www.chittorgarh.com{relative_url}"

                        current_ipos.append({
                            "name": company_name,
                            "url": full_url,
                        })
                elif status.lower() == 'upcoming':
                    company_name = cells[0].text.strip()
                    link_tag = cells[0].find('a')
                    if link_tag and link_tag.has_attr('href'):
                        relative_url = link_tag['href']
                        full_url = f"https://www.chittorgarh.com{relative_url}"
                        
                        upcoming_ipos.append({
                            "name": company_name,
                            "url": full_url,
                        })
                else:
                    continue

        
        print(f"Found {len(upcoming_ipos)} upcoming Mainboard IPOs.")
        print("Name of first current ipo:", current_ipos[0]['name'] if current_ipos else "No current IPOs found")
        print(f"Found {len(current_ipos)} current Mainboard IPOs")
        print("Name of fist upcoming ipo:", upcoming_ipos[0]['name'] if upcoming_ipos else "No upcoming IPOs found")
        return current_ipos, upcoming_ipos

    except Exception as e:
        print(f"An error occurred while scraping the dashboard: {e}")
        return []
    finally:
        driver.quit()

# ==============================================================================
# WORKER FUNCTIONS 2, 3, 4 (The Analysis Pipeline - No Changes Needed)
# ==============================================================================
def get_page_source_with_selenium(url):
    """Uses Selenium to get the full HTML of a detailed IPO page."""
    print(f"\nStep 2: Visiting detail page with Robot Browser -> {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(url)
        print("Waiting for main content div (id='main') to load...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "main")))
        print("Page content loaded successfully.")
        return driver.page_source
    except TimeoutException:
        print("\n--- ERROR: Timed out waiting for the element with id='main'. This IPO may not have a detailed report yet.")
        return None
    finally:
        driver.quit()

def parse_and_aggregate_data(html_content):
    """Uses BeautifulSoup to parse the detailed HTML."""
    print("Step 3: Parsing HTML with the Detective...")
    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find('div', id='main')
    if not main_content: return None
    aggregated_text = ""
    for header in main_content.find_all(['h2', 'h3']):
        if "Message Board" in header.get_text(): continue
        aggregated_text += f"\n\n--- Section: {header.get_text(strip=True)} ---\n"
        content = ""
        for sibling in header.find_next_siblings():
            if sibling.name in ['h2', 'h3']: break
            content += sibling.get_text(separator=' ', strip=True) + " "
        aggregated_text += content
    return aggregated_text.strip()

def get_ipo_analysis_with_gemini(ipo_data_text):
    """Sends the data to Gemini for analysis."""
    print("Step 4: Sending data to the AI Analyst (Gemini)...")
    prompt = f"""
    You are an expert IPO analyst with immense stock market knowledge, providing a summary for a retail investor. Based ONLY on the text provided below, generate a comprehensive analysis of the IPO. Structure your response as follows:
    1.  **IPO Snapshot:** Briefly list the Issue Size, Price Band, and Dates.
    2.  **Business Overview:** A one or two-sentence summary of what the company does.
    3.  **Financial Health:** Briefly comment on the company's financial performance (revenue/profit trends) based on the data.
    4.  **Positive Indicators (Reasons to consider applying):** Create a bulleted list of positive points.
    5.  **Negative Indicators (Reasons for caution):** Create a bulleted list of negative points.
    6.  **Final Verdict:** Conclude with a balanced, one-paragraph verdict based *strictly* on the provided information. Start with "Based on the available data...".

    --- IPO DATA START ---
    {ipo_data_text}
    --- IPO DATA END ---
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"An error occurred while communicating with the Google AI API: {e}"
    
def ipo_analysis_langchain():
    llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash", google_api_key = os.getenv("GOOGLE_API_KEY"), temperature=0.4)
    prompt_template = ChatPromptTemplate.from_template
    (
        """
        You are an expert IPO analyst with immense stock market knowledge, providing a summary for a retail investor. 
        Based ONLY on the text provided below, generate a comprehensive analysis of the IPO. 
        Structure your response as follows:
        1.  **IPO Snapshot:** Briefly list the Issue Size, Price Band, and Dates.
        2.  **Business Overview:** A one or two-sentence summary of what the company does.
        3.  **Financial Health:** Briefly comment on the company's financial performance (revenue/profit trends) based on the data.
        4.  **Positive Indicators (Reasons to consider applying):** Create a bulleted list of positive points.
        5.  **Negative Indicators (Reasons for caution):** Create a bulleted list of negative points.
        6.  **Final Verdict:** Conclude with a balanced, one-paragraph verdict based *strictly* on the provided information. Start with "Based on the available data...".

        --- IPO DATA START ---
        {ipo_data_text}
        --- IPO DATA END ---
        """
    )
    output_parser = StrOutputParser() #LLM output into string
    analysis_chain = prompt_template | llm | output_parser #This line creates a chain something called as LangChain expression language 
    return analysis_chain


# ==============================================================================
# THE MAIN ENGINE (The "Conductor")
# ==============================================================================
if __name__ == "__main__":
    current_ipos, upcoming_ipos = scrape_ipo_dashboard()

    if not current_ipos and not upcoming_ipos:
        print("\nNo current or upcoming IPOs found to analyze. Exiting.")
    else:
        # Analyze Current IPOs
        if current_ipos:
            print("\n" + "="*80)
            print(f"Starting analysis for {len(current_ipos)} CURRENT IPO(s).")
            print("="*80)

            for ipo in current_ipos:
                print(f"\n\nANALYZING CURRENT IPO: {ipo['name'].upper()}")
                print("-" * 50)
                
                html_content = get_page_source_with_selenium(ipo['url'])

                if html_content:
                    aggregated_data = parse_and_aggregate_data(html_content)
                    
                    if aggregated_data:
                        ipo_analysis = get_ipo_analysis_with_gemini(aggregated_data)
                        
                        print("\n" + "#"*80)
                        print(f"          GEMINI-GENERATED ANALYSIS FOR CURRENT IPO: {ipo['name'].upper()}")
                        print("#"*80 + "\n")
                        print(ipo_analysis)
                    else:
                        print("Could not parse data from the detail page. It may be a placeholder page.")
                else:
                    print("Could not retrieve the detail page HTML.")
                
                print("\n--- Pausing for 5 seconds before next IPO ---")
                time.sleep(5)
        else:
            print("\nNo current IPOs found to analyze.")

        # Analyze Upcoming IPOs
        if upcoming_ipos:
            print("\n\n" + "="*80)
            print(f"Starting analysis for {len(upcoming_ipos)} UPCOMING IPO(s).")
            print("="*80)

            for ipo in upcoming_ipos:
                print(f"\n\nANALYZING UPCOMING IPO: {ipo['name'].upper()}")
                print("-" * 50)
                
                html_content = get_page_source_with_selenium(ipo['url'])

                if html_content:
                    aggregated_data = parse_and_aggregate_data(html_content)
                    
                    if aggregated_data:
                        ipo_analysis = get_ipo_analysis_with_gemini(aggregated_data)
                        
                        print("\n" + "#"*80)
                        print(f"          GEMINI-GENERATED ANALYSIS FOR UPCOMING IPO: {ipo['name'].upper()}")
                        print("#"*80 + "\n")
                        print(ipo_analysis)
                    else:
                        print("Could not parse data from the detail page. It may be a placeholder page.")
                else:
                    print("Could not retrieve the detail page HTML.")
                
                print("\n--- Pausing for 5 seconds before next IPO ---")
                time.sleep(5)
        else:
            print("\nNo upcoming IPOs found to analyze.")