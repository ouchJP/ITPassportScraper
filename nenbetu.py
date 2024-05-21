import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

def clean_kaisetsu(kaisetsu_html):
    # Parse kaisetsu content
    soup = BeautifulSoup(kaisetsu_html, 'html.parser')
    
    # Remove unnecessary classes
    for tag in soup.find_all(class_=True):
        del tag['class']
        
    # Only keep ul, li, and the required li elements
    for tag in soup.find_all(True):
        if tag.name not in ['ul', 'li', 'lia', 'lii', 'liu', 'lie']:
            tag.unwrap()  # Remove unwanted tags but keep their contents


    for tag in soup.find_all(['lia', 'lii', 'liu', 'lie']):
        if tag.name == 'lia':
            tag.insert(0, 'ア. ')
        elif tag.name == 'lii':
            tag.insert(0, 'イ. ')
        elif tag.name == 'liu':
            tag.insert(0, 'ウ. ')
        elif tag.name == 'lie':
            tag.insert(0, 'エ. ')
    
    
    return str(soup)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py {year_season} \n try: 06_haru 23_aki")
        sys.exit(1)

    # Get the year and season from the command line argument
    year_season = sys.argv[1]

    # Define the base URL and the range of question URLs
    base_url = f"https://www.itpassportsiken.com/kakomon/{year_season}/q"
    question_range = range(1, 101)  # From q1.html to q100.html

    # Lists to store the extracted data
    data = []

    # Loop through each question number
    for q_no in question_range:
        url = f"{base_url}{q_no}.html"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract the required data with checks
            mondai = soup.find(id="mondai")
            select_a = soup.find(id="select_a")
            select_i = soup.find(id="select_i")
            select_u = soup.find(id="select_u")
            select_e = soup.find(id="select_e")
            answer_char = soup.find(id="answerChar")
            kaisetsu = soup.find(id="kaisetsu")

            # Get text or set default value if element is not found
            mondai_text = mondai.get_text(strip=True) if mondai else "N/A"
            select_a_text = select_a.get_text(strip=True) if select_a else "N/A"
            select_i_text = select_i.get_text(strip=True) if select_i else "N/A"
            select_u_text = select_u.get_text(strip=True) if select_u else "N/A"
            select_e_text = select_e.get_text(strip=True) if select_e else "N/A"
            answer_char_text = answer_char.get_text(strip=True) if answer_char else "N/A"
            kaisetsu_text = clean_kaisetsu(str(kaisetsu)) if kaisetsu else "N/A"
            
            # Format the front and back of the card with bold tags
            front = (
                f"{mondai_text}<br>"
                f"<b>A.</b> {select_a_text}<br>"
                f"<b>I.</b> {select_i_text}<br>"
                f"<b>U.</b> {select_u_text}<br>"
                f"<b>E.</b> {select_e_text}"
            )
            back = f"<b>{answer_char_text}</b><br>{kaisetsu_text}"
            
            # Append the data as a row in the list
            data.append([front, back])
        else:
            print(f"Failed to retrieve data for q{q_no}.html")

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    # Display the DataFrame
    print(df)

    # Save the DataFrame to a CSV file with UTF-8 encoding, without headers
    output_filename = f"{year_season}_flashcards.csv"
    df.to_csv(output_filename, index=False, header=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()
