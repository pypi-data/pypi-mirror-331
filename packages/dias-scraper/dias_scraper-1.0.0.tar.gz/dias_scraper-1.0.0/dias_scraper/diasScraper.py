from playwright.sync_api import sync_playwright
import re
from colorama import Fore,Style
import getpass
import os

def account():
    # Reads from .bashrc
    username = os.getenv("MY_USERNAME")
    password = os.getenv("MY_PASSWORD")

    # It username or password don't exist in .bashrc
    if not username:
        username = input("Enter your username:")
    if not password:
        password = getpass.getpass("Enter your password:")

    return username, password

def diasScraper():
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=100)
        page = browser.new_page()


        print("Dias Scraper")
        username, password = account()
        #Starts webscraping
        try:
            page.goto("https://dias.ionio.gr")
            print("Welcome to Ionio Dias portal")

            page.fill('input[name="username"]', username)
            page.fill('input[name="password"]', password)


            page.wait_for_selector("button#loginButton", state="visible")
            sd = page.query_selector("button#loginButton")

            if sd:
                sd.click()
                print("Logged in")
            else:
                print("Failed to find login button")
            

            page.wait_for_selector("em.ic.ic-grades-alt3", state="visible")
            icon_element = page.query_selector("em.ic.ic-grades-alt3")

            if icon_element:
                icon_element.click()
                #print("Clicked on the icon")
            else:
                print("Icon not found.")

            page.wait_for_selector('em.ic-md.ic-grades', state="visible")
            icon_element = page.query_selector('em.ic-md.ic-grades')
            if icon_element:
                icon_element.click()
                #print("Clicked on the icon")
            else:
                print("Icon not found.")

            page.wait_for_timeout(5000)

#-------------------------- GRABBING MO, ECTS AND sum of lesson passed---------------------------------------------


            page.wait_for_selector('div.col-md-12.col-sm-12', state="visible")
            strong_tags = page.query_selector_all('div.col-md-12.col-sm-12 strong')


            '''
            #Debugger to chech the strong_tags for webscraping
            for i, tag in enumerate(strong_tags):
                print(f"Strong tag {i+1} content: {tag.inner_text()}")
            '''

            if len(strong_tags) > 1:
                MO  = strong_tags[1].inner_text()
    
                pattern = r'(\d+\.\d+)'
                match = re.search(pattern, MO)
                    
                if match:
                    MO  = match.group(1)
                    print("=================================")
                    print(f"MO: {MO} ")
                else:
                    print("Number not found")

                Passed_L = None
                if len(strong_tags) > 3:
                    Passed_L = strong_tags[3].inner_text()
                    print(f"Αριθμός περασμένων μαθημάτων: {Passed_L}")

                ECTS = None
                if len(strong_tags) > 4:
                    ECTS = strong_tags[4].inner_text()
                    print(f"ECTS : {ECTS}")

            else:
                print("Not enough strong tags found.")

            

#======================VATHMOI==========================
            
            page.wait_for_selector("tr")
            rows = page.query_selector_all("tr")
            
            #Prints all the lessons
            firstCheck = False
            for row in rows:
                cells = row.query_selector_all("td")
                cell_texts = [cell.inner_text().strip() for cell in cells]
                if len(cell_texts) < 2:
                    continue
                if len(cell_texts) == 2:
                    eksamhno = str(cell_texts[1])
                    print(Fore.BLUE + Style.BRIGHT + eksamhno + Style.RESET_ALL)
                    continue
               
                cell_vathmos = safeInt(cell_texts[2]) 
                is_exempt = str(cell_texts[3]) == 'Απαλλαγή / Κατοχύρωση'

                #Check if first time printing
                if (firstCheck == False):
                    firstCheck = True
                    print(Fore.CYAN + Style.BRIGHT + "ID / ΜΑΘΗΜΑ / ΒΑΘΜΟΣ / ΕΞΕΤΑΣΤΙΚΗ ΠΕΡΙΟΔΟΣ " + Style.RESET_ALL)

                if len(cell_texts) >= 5:
                    if cell_vathmos == None and not is_exempt:
                        print(Fore.YELLOW + Style.BRIGHT + ' '.join(cell_texts[:5]) + Style.RESET_ALL)
                    elif is_exempt:
                        print(Fore.GREEN + Style.BRIGHT + ' '.join(cell_texts[:5]) + Style.RESET_ALL)
                    elif cell_vathmos is not None and cell_vathmos >= 5:
                        print(Fore.GREEN + Style.BRIGHT + ' '.join(cell_texts[:5]) + Style.RESET_ALL)
                    elif cell_vathmos is not None and cell_vathmos < 5:
                        print(Fore.RED + Style.BRIGHT + ' '.join(cell_texts[:5]) + Style.RESET_ALL)

        except Exception as e:
            print(f"An error occurred: {e}")


            browser.close()

#This function makes the grade from str to int
def safeInt(n):
    try:
        return int(n)
    except ValueError:
        return None


