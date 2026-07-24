# 🍷 Seoul & Sip: K-Food & Wine Pairing Web App

Seoul & Sip is an interactive, data-driven web application developed as an internship project at Pair Anything. The application helps wine lovers discover the ideal wine pairing for authentic Korean dishes based on flavor profiles and personal preferences.

The project combines data analysis, visualization, and user-centered design to create an engaging wine recommendation experience.

The app evaluates factors such as body, acidity, spice tolerance, and richness to recommend wines that create either a **congruent pairing** or a **contrasting pairing** with the selected Korean dish.

---

## 🌟 Key Features

* **Interactive Preference Quiz**
  Captures users’ preferences for wine body, acidity, spiciness, and richness.

* **Smart Pairing Algorithm**
  Matches Korean dishes with suitable wines using normalized flavor-profile metrics.

* **Dynamic Radar Chart Visualization**
  Uses Plotly to visually explain the relationship between the dish and recommended wine, including **congruent** and **contrasting** pairing styles.

* **Direct Purchase Integration**
  Provides links that allow users to purchase recommended wines online.

* **Email Result Delivery**
  Sends styled HTML emails containing the pairing result and a dynamic radar chart generated through the QuickChart API.

---

## 🛠️ Tech Stack

* **Programming Language:** Python
* **Web Framework:** Streamlit
* **Data Processing:** Pandas
* **Visualization:** Plotly, QuickChart API
* **Deployment:** Streamlit Community Cloud
* **Version Control:** Git and GitHub

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_ID/PairAnythingKoreanProject.git
cd PairAnythingKoreanProject
```

### 2. Install the required packages

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Replace `app.py` with the name of your main Streamlit file if it is different.

---

## 📁 Project Structure

```text
PairAnythingKoreanProject/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── pairing_data.csv
├── images/
└── pages/
```

The project structure may vary depending on the final version of the application.

---

## 🧠 How the Pairing System Works

1. The user selects a Korean dish.
2. The user completes a preference quiz.
3. The application converts the selected preferences into normalized flavor-profile values.
4. The pairing algorithm compares the user’s preferences and the dish profile with the available wine data.
5. The app recommends a wine and displays the pairing through an interactive radar chart.
6. The user can review the result, purchase the wine, or receive the recommendation by email.

---

## 📊 Pairing Approaches

### Congruent Pairing

A congruent pairing matches similar flavor characteristics between the dish and wine. For example, a rich dish may be paired with a fuller-bodied wine.

### Contrasting Pairing

A contrasting pairing balances opposing characteristics. For example, a high-acidity wine may help refresh the palate when paired with a rich or fatty dish.

---

## ☁️ Deployment

The application can be deployed through **Streamlit Community Cloud** by connecting the GitHub repository and selecting the main application file.

Make sure all required dependencies are included in `requirements.txt`.

---

## 🔮 Future Improvements

* Expand the database of Korean dishes and wines
* Add more detailed dietary and allergy filters
* Improve the recommendation algorithm using user feedback
* Add user accounts and saved pairing histories
* Provide additional online wine retailer options
* Optimize the interface for mobile devices

---

## 👩‍💻 Project Information

Developed by Heejung Lim as part of a software development internship at Pair Anything.

The project focuses on applying data analysis, recommendation algorithms, and interactive web development to improve the Korean food and wine pairing experience.

---

## 📄 License

This project is intended for educational and portfolio purposes.
