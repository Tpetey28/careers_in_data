# Careers in Data

### Scraper.py

- Script parses and scrapes information from job postings for Data Analyst, Data Scientist, and Data Engineer positions posted within a 24 hour period.
- It extracts the position title, organization, pay details (if provided), location (if provided), and all skills/qualifications.
- The extracts are stored in a pandas dataframe and are cleaned using the Transform.py script.

### Transform.py

- Script cleans and formats scraped information and returns a clean pandas dataframe with usable data.

### Load.py

- Script takes the clean pandas dataframe and uploads into MySQL database instance.
