# Instagram Comments Scraper

A simple tool to scrape Instagram comments using cookie authentication.

## Prerequisites

- Python 3.10 or higher
- Instagram account with valid login cookies

## Installation

1. **Clone the repository** and navigate to the project folder:
   ```bash
   git clone https://github.com/billycemerson/IG-Scraping/
   cd IG-Scraping
   ```

2. **Install dependencies**:
   
   **Option A: Using conda (recommended)**:
   ```bash
   conda create -n igscrape python=3.10
   conda activate igscrape
   pip install -r requirements.txt
   ```
   
   **Option B: Using pip**:
   ```bash
   pip install -r requirements.txt
   ```

## Cookie Setup

Instagram requires authentication cookies to access post data. Follow these steps:

1. Navigate to the source folder:
   ```bash
   cd src
   ```

2. Copy the example cookie file:
   ```bash
   cp cookies_example.py cookies.py
   ```

3. **Extract cookies from your browser**:
   - Open Instagram in your web browser and log in
   - Open Developer Tools (F12 or right-click → Inspect)
   - Go to **Application** tab → **Storage** → **Cookies** → `https://www.instagram.com`
   - Find and copy the following cookie values:
     - `sessionid`
     - `ds_user_id` 
     - `csrftoken`
     - `mid`

4. **Update the cookie file**:
   - Open `cookies.py` in your text editor
   - Replace the placeholder values with your actual cookie values
   - Save the file

   Example format:
   ```python
   cookies = {
       'sessionid': 'your_session_id_here',
       'ds_user_id': 'your_user_id_here', 
       'csrftoken': 'your_csrf_token_here',
       'mid': 'your_mid_here'
   }
   ```

## Usage

1. **Navigate to the source folder**:
   ```bash
   cd src
   ```

2. **Run the scraper**:
   ```bash
   python scrape_comment.py
   ```

3. **Enter Instagram post URL**:
   - A prompt will appear asking for the Instagram post link
   - Paste the full URL of any Instagram post (photo, reel, or carousel)
   - Example: `https://www.instagram.com/p/ABC123xyz/`
   - Press **Enter** to start scraping

4. **Output**:
   - Comments will be scraped and saved to `data/comments.csv`
   - The output file will be automatically created in the `data` folder

## File Structure

```
IG-Scraping/
├── src/
│   ├── scrape_comment.py      # Main scraper script
│   ├── cookies_example.py     # Example cookie configuration
│   └── cookies.py            # Your actual cookies (create this)
├── data/
│   └── comments.csv          # Output file (generated after scraping)
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Troubleshooting

- **Authentication Error**: Ensure your cookies are fresh and valid. Instagram cookies expire periodically.
- **Rate Limiting**: If you encounter rate limits, wait a few minutes before trying again.
- **Private Posts**: This tool can only scrape comments from public posts or posts you have access to.
- **Missing Dependencies**: Make sure all packages in `requirements.txt` are installed.

## Legal Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with Instagram's Terms of Service and applicable laws regarding data scraping and privacy.