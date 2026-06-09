# 🔍 Reddit Sentiment & Virality Analyzer — r/technology

[![Data Pipeline & Deployment](https://github.com/nishkmistry/Tech-Public-Opinion-Tracker/actions/workflows/data_pipeline.yml/badge.svg)](https://github.com/nishkmistry/Tech-Public-Opinion-Tracker/actions/workflows/data_pipeline.yml)
[![Code Quality & Maintenance](https://github.com/nishkmistry/Tech-Public-Opinion-Tracker/actions/workflows/ci_maintenance.yml/badge.svg)](https://github.com/nishkmistry/Tech-Public-Opinion-Tracker/actions/workflows/ci_maintenance.yml)

An end-to-end NLP and Machine Learning project that scrapes posts from r/technology, analyzes sentiment, discovers hidden topics...
---

## 📌 Project Highlights

- **2091 posts** scraped from r/technology using Reddit's public JSON endpoint
- **62.7%** of r/technology posts carry negative sentiment — tech Reddit is overwhelmingly critical
- **Negative posts go viral at nearly double the rate** of positive posts (27.4% vs 16.8%)
- **Net Neutrality** is the most viral topic despite **General AI Discourse** being the most discussed
- **Logistic Regression** achieved **ROC AUC of 0.7833** predicting post virality from text and metadata alone
- **Best time to post:** 16:00 UTC on weekends for maximum reach

---

## 📁 Project Structure

```
reddit-sentiment-analyzer/
├── data/
│   ├── raw_posts.csv               # scraped Reddit posts
│   ├── clean_posts.csv             # after text cleaning
│   ├── sentiment_posts.csv         # after HuggingFace sentiment labeling
│   ├── nlp_posts.csv               # after TF-IDF, LDA, NER
│   ├── feature_matrix.csv          # final ML-ready feature matrix
│   └── viz_*.png                   # all visualizations
├── notebooks/
│   ├── Cleaning.ipynb              # text cleaning pipeline
│   ├── Sentiment_analysis.ipynb    # HuggingFace sentiment inference
│   ├── nlp_features.ipynb          # TF-IDF, LDA topic modeling, spaCy NER
│   ├── feature_engineering.ipynb   # feature engineering for ML
│   ├── Virality.ipynb              # virality prediction model
│   └── EDA_storytelling.ipynb      # visualizations and insights
├── app/
│   └── app.py                      # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## 🔬 Pipeline Overview

```
Reddit JSON  →  Text Cleaning  →  Sentiment Analysis  →  TF-IDF + LDA + NER
                                                                    ↓
                                        Virality Prediction  ←  Feature Engineering
                                                                    ↓
                                                        EDA + Streamlit Dashboard
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core language |
| Requests | Reddit JSON scraping (no API needed) |
| Pandas / NumPy | Data manipulation |
| HuggingFace Transformers | Pretrained sentiment model (RoBERTa) |
| Scikit-learn | TF-IDF, LDA, ML models |
| spaCy | Named Entity Recognition |
| Matplotlib / Seaborn | Visualizations |
| WordCloud | Sentiment word clouds |
| Streamlit | Interactive dashboard |
| Jupyter Notebook | Development environment |

---

## 📊 Dataset

- **Source:** r/technology via Reddit public JSON endpoint
- **Size:** 2091 unique posts
- **Categories scraped:** hot, top/week, top/month, top/year, top/all
- **Features:** title, body, score, upvote ratio, comment count, flair, author, timestamp, top comments

---

## 🔤 NLP Pipeline

### 1. Text Cleaning (`Cleaning.ipynb`)
- Removed URLs, Reddit mentions (`u/`, `r/`), special characters
- Combined title + body + top comments into unified `full_text` column
- Filtered posts with insufficient text content

### 2. Sentiment Analysis (`Sentiment_analysis.ipynb`)
- Used pretrained `cardiffnlp/twitter-roberta-base-sentiment-latest` from HuggingFace
- No model training — pure inference on 2091 posts
- Output: positive / neutral / negative label + confidence score

### 3. TF-IDF + Topic Modeling (`nlp_features.ipynb`)
- TF-IDF vectorization (1000 features, bigrams, min_df=5)
- LDA topic modeling with 15 discovered topics
- Topics labeled manually based on top words (e.g. "General AI Discourse", "Net Neutrality & FCC Regulations")
- spaCy NER to extract company (ORG) and person (PERSON) mentions

---

## 🤖 Virality Prediction Model

**Target variable:** A post is "viral" if its score is in the top 25% (threshold score: ~X)

**Features used (no data leakage):**
- Sentiment score and confidence
- Title length, word count, punctuation signals
- Hour of day, day of week, weekend flag
- Dominant topic and topic confidence
- Named entity mention counts
- Post flair (one-hot encoded)

> Note: `num_comments`, `upvote_ratio`, and `comment_score_ratio` were explicitly excluded as they are post-virality features and would constitute data leakage.

**Model comparison:**

| Model | CV ROC AUC | Test ROC AUC |
|-------|-----------|--------------|
| Logistic Regression | 0.7755 ± 0.031 | **0.7833** ✅ |
| Random Forest | 0.7650 ± 0.029 | 0.7695 |
| Gradient Boosting | 0.7594 ± 0.027 | 0.7373 |

**Top predictive features:** title length, sentiment confidence, topic confidence, posting hour, flair type

---

## 📈 Key Findings

**Sentiment:**
- 62.7% of r/technology posts are negative
- Only 5.7% are positive — tech Reddit is overwhelmingly critical

**Virality:**
- Negative posts go viral at 27.4% vs 16.8% for positive posts
- Outrage and criticism drive engagement more than positive content
- Net Neutrality posts are the most viral topic despite AI being most discussed
- Best time to post: **16:00 UTC on weekends**

**Companies:**
- Google and Apple appear most in positive posts
- Facebook appears most in negative posts
- Privacy and government-related posts are among the most negatively received

**Word Clouds:**
- Positive posts: "google", "good", "free", "apple", "great"
- Neutral posts: "openai", "data", "billion", "law", "pentagon"
- Negative posts: "company", "work", "facebook", "government", "data"

---

## 🚀 Getting Started

```bash
# clone the repo
git clone https://github.com/nishkmistry/Tech-Public-Opinion-Tracker.git
cd reddit-sentiment-analyzer

# install dependencies
pip install -r requirements.txt

# download spaCy model
python -m spacy download en_core_web_sm

# run the scraper (takes ~70 mins due to rate limiting)
python reddit_scraper.py

# run notebooks in order
# Cleaning → Sentiment_analysis → nlp_features → feature_engineering → Virality → EDA_storytelling

# launch the dashboard
streamlit run app/app.py
```

---

## 📦 Requirements

```
requests
pandas
numpy
transformers
torch
scikit-learn
spacy
matplotlib
seaborn
wordcloud
streamlit
jupyter
```

---

## 📝 License

This project is open-source under the [MIT License](LICENSE).
