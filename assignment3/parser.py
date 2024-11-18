#-------------------------------------------------------------------------
# AUTHOR: Armin Erika Polanco
# FILENAME: crawler.py
# SPECIFICATION: CPP CompSci Website DB Parser
# FOR: CS 4250 - Assignment #3, Question 6
# TIME SPENT: 3 hours
#-----------------------------------------------------------*/

from pymongo import MongoClient
from bs4 import BeautifulSoup
import sys

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["crawlerDB"]                # Database
page_collection = db["pages"]         # Collection for pages
prof_collection = db["professors"]    # Collection for professors

# Function to get permanent faculty information
def getFacultyHTML():
    url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
    page = page_collection.find_one({"url": url})
    if page:
        return page['html']
    else:
        raise ValueError("Permanent Faculty page not found in database. Please add it manually.")
    
# Function to parse faculty data
def parseFacultyData(html):
    soup = BeautifulSoup(html, 'html.parser')
    faculty_data = []

    # Select all divs with the "clearfix" class
    faculty_rows = soup.select('div.clearfix')

    for row in faculty_rows:
        try:
            # Extract all names (h2) and corresponding detail sections (p)
            names = row.find_all('h2')
            details_list = row.find_all('p')

            # Pair each name with its corresponding details
            for name_tag, details_tag in zip(names, details_list):
                name = name_tag.get_text(strip=True) if name_tag else "Unknown Name"

                # Parse details
                details = details_tag.get_text(strip=True) if details_tag else ""
                title = None
                office = None
                phone = None
                email = None
                website = None

                if "Title:" in details:
                    title = details.split("Title:")[1].split("Office:")[0].strip()
                if "Office:" in details:
                    office = details.split("Office:")[1].split("Phone:")[0].strip()
                if "Phone:" in details:
                    phone = details.split("Phone:")[1].split("Email:")[0].strip()
                if "Email:" in details:
                    email_tag = details_tag.select_one('a[href^="mailto:"]')
                    email = email_tag.get_text(strip=True) if email_tag else None
                if "Web:" in details:
                    web_tag = details_tag.select_one('a[href^="http"]')
                    website = web_tag.get('href') if web_tag else None

                # Append parsed data to the list
                faculty_data.append({
                    "name": name,
                    "title": title,
                    "office": office,
                    "phone": phone,
                    "email": email,
                    "website": website,
                })
        except Exception as e:
            print(f"Error parsing row: {e}")


    print(f"Parsed faculty data: {faculty_data}")  # Debugging line
    return faculty_data

# Function to store parsed faculty data into prof_collection
def storeFacultyData(faculty_data):
    for professor in faculty_data:
        try:
            print(f"Inserting into MongoDB: {professor}")
            result = prof_collection.insert_one(professor)
            print(f"Stored professor: {professor['name']} with ID {result.inserted_id}")
        except Exception as e:
            print(f"Failed to store professor {professor['name']}: {e}")

if __name__ == "__main__":
    try:
        # Retrieve the Permanent Faculty HTML
        html = getFacultyHTML()

        # Parse the faculty data
        faculty_data = parseFacultyData(html)
        print(f"Parsed faculty data: {faculty_data}")

        if not faculty_data:
            print("No faculty data found. Exiting.")
            sys.exit(1)
            
        # Store parsed data in MongoDB
        storeFacultyData(faculty_data)
        print("Faculty data parsing and storage completed.")
        
    except Exception as e:
        print(f"Error: {e}")