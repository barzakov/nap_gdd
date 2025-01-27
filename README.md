### NAP GDD Automation Scripts

This repository contains three Python scripts designed to make the process of filling out your **NAP GDD** or **BNB SPB-8** forms simpler and more efficient.

**Please do your best**:  
Before using the output from these scripts in your forms, **check every single line and calculation carefully**. Everything is created according to my understanding and personal view. If there are any rounding differences, they are intentionally made in a way that might lead to paying slightly more taxes, but it is to avoid any potential tax issues. Always verify the results to ensure accuracy for your specific situation.

#### Scripts Overview

###### 1. **`bnb_currency_get.py`**
- **Purpose**: Fetches the exchange rate for a specific currency for specific year from the BNB website. For example, you can retrieve the USD rate for 2024.
- **Why It Matters**: Instead of manually checking currency rates through a browser (which creates multiple requests and consumes unnecessary server resources), this script optimizes the process by making only 4 requests.  
  Please consider the environment and help reduce power consumption by using this efficient solution.

###### 2. **`get_statement_data.py`**
- **Purpose**: Processes your **CSV statement** from a specific broker.  
  - If you want to use all the script's features, ensure you generate a **custom statement** with all available information from the broker's platform.
- **Why It Matters**: This script will help you see the whole picture and ensure you don't miss any important information from your statement.

###### 3. **`interest_flexible_account.py`**
- **Purpose**: Works with another specific broker's **CSV statement** to extract all required information for the forms.
- **Why It Matters**: This script will help you gather all the necessary data from your flexible account statement, ensuring that no key information is missed and making the process easier for you.

---

####  Future Plans
The future plan is to combine these scripts and provide easy copy-paste solutions for the forms.

---

#### Contributions

- **Pull Requests**: Contributions are not required and may be ignored.
- **Recommendations/Issues**: Suggestions and issues will be reviewed periodically, but there are no guarantees for immediate responses.

---

#### Donations
Financial contributions are always appreciated, though your support may or may not directly contribute to the maintenance and improvement of these tools.

---

#### Notes
- Ensure you have Python 3 installed on your system to run these scripts.
- All scripts include the `-h` option to guide you through their usage.
- These scripts are designed to save time.

---

#### License

This software is provided **free of charge** for anyone to use for any purpose. You are free to modify, distribute, and use it as you see fit.  
However, I am not responsible for any consequences or decisions made based on using these scripts. Please use your mind and imagination, proceed with caution and use at your own risk!

---

Thank you for using these tools! Feedback and support are not welcome.

