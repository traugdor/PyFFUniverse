# PyFFUniverse

PyFFUniverse is a comprehensive market data analysis tool for Final Fantasy XIV Online. It allows players to track market prices across different worlds and data centers, set price alerts, identify hot items, and find arbitrage opportunities.

## Features

### Market Data Analysis
- View current market listings for any marketable item
- Filter listings by world or data center
- Sort listings by price, quantity, or other attributes
- Track historical price trends

### Alert System
- Set price alerts for specific items
- Configure minimum and maximum price thresholds
- Receive desktop notifications when prices cross your thresholds
- View and manage all active alerts in one place

### Hot Items & Arbitrage
- Identify items with high sale velocity (hot items)
- Find price differences between worlds in the same data center
- Discover profitable trading opportunities

### Multi-language Support
- Switch between English, German, Japanese, and French interfaces
- All UI elements automatically update when language is changed

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/PyFFUniverse.git
   cd PyFFUniverse
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Searching for Items
1. Use the search bar at the top of the application to find items
2. Select an item from the results to view its market data

### Setting Alerts
1. Select an item from the search results
2. Navigate to the "Alerts" tab
3. Set your desired minimum and/or maximum price thresholds
4. Choose a world or data center to monitor
5. Click "Set Alert"

### Managing Alerts
1. Select an item from the search results
2. Select an alert and click "Delete" to remove an alert for that item

OR

1. Go to the "All Alerts" tab to view all your active alerts
2. Select an alert and click "Delete" to remove it

### Finding Arbitrage Opportunities
1. Select an item from the search results
2. Click "Check All Servers" to see price differences between worlds
3. Review the results to identify profitable arbitrage opportunities
4. Use the results to make informed trading decisions between markets

### Exploring Market Trends and Making Predictions
1. Select an item from the search results
2. Navigate to the "Price History" tab
3. See historical price data and potential price trends
4. Use this information to make informed decisions about fair market prices
5. Navigate to the "Sale History" tab to see how often items are sold
6. Use this information to make informed decisions about when to buy or sell

## Configuration

You can find the last saved application settings in the `settings.json` file:
- `language`: Set your preferred language ("English", "Deutsch", "Français", or "日本語")
- `lang_code`: Set your preferred language code ("en", "de", "fr", or "ja")
- `data_center`: Set your default data center
- `world`: Set your default world
- `discord_webhook_url`: Set your Discord webhook URL for notifications

The settings are automatically saved when you use the application, but if you want to configure it manually, you can edit the `settings.json` file yourself, before running the application for the first time.

## Roadmap / TODO

### Short-term Goals
- [X] Improve notification system compatibility across different operating systems
- [X] Add support for more languages
- [ ] Implement batch alert creation for multiple items
- [ ] Add ability to export/import alerts
- [ ] Improve Universalis API integration efficiency

### Medium-term Goals
- [X] Create a dashboard view with summary of all alerts and opportunities
- [ ] Implement historical price charts and trend analysis **(WIP)**
- [ ] Develop a recommendation system for potentially profitable items

### Long-term Goals
- [ ] Create a companion mobile app for alerts on the go?
- [ ] Develop a web interface for cross-platform access?

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Universalis API](https://universalis.app/) for providing market data
- [XIVAPI](https://xivapi.com/) for item information
- The FFXIV community for inspiration and support
- [Plyer](https://plyer.readthedocs.io/en/latest/) for macOS notifications
- [Win10toast](https://github.com/jithurjacob/Windows-10-Toast-Notifications) for Windows 10 notifications
- [Win11toast](https://github.com/GitHub30/win11toast) for Windows 11 notifications
- [Windsurf IDE by Codeium](https://codeium.com/windsurf) for code analysis and development support