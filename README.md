# group-visualiser

Graphing groups on Facebook in a visually intuitive way - inspired by some convo with a friend. Borrows heavily from this [guide](https://medium.com/analytics-vidhya/read-your-network-of-friends-in-facebook-by-scraping-with-python-a012adabb713).

## Requirements

- Firefox

## Usage

- Edit the `.env` file to use your Facebook username and password
- Install the python libraries `webdriver-manager`, `dotenv` and `selenium`
- Run `main.py` with the Facebook group id and any other command-line arguments

For example, `python main.py 2099121503727072` runs a full scrape on the Facebook group 'University of St Andrews Class of 2024' since `2099121503727072` is the group's id.

Use a website like <http://lookup-id.com/> to find your group's id.

## Notes

- You will need an account with access to the group - if it is private - to scrape its group members.
- Members of the group may hide their friends according to their Facebook privacy settings, so you will likely scrape incomplete data.
