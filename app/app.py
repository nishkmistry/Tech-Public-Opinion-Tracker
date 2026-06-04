import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tech Public Opinion Tracker",
    page_icon="🔍",
    layout="wide"
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/nlp_posts.csv")
    df = df.rename(columns={
        "Dominant_topics" : "dominant_topic",
        "topic_confidance": "topic_confidence",
        "Topic_labels"    : "topic_label"
    })
    threshold   = df["score"].quantile(0.75)
    df["viral"] = (df["score"] > threshold).astype(int)
    df["created_utc"] = pd.to_datetime(df["created_utc"])
    df["hour"]        = df["created_utc"].dt.hour
    df["day_of_week"] = df["created_utc"].dt.dayofweek
    df["day_name"]    = df["created_utc"].dt.day_name()
    df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)
    return df

df = load_data()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
st.sidebar.markdown("Use filters to explore the dataset")

selected_sentiment = st.sidebar.multiselect(
    "Filter by Sentiment",
    options=df["sentiment"].unique().tolist(),
    default=df["sentiment"].unique().tolist()
)

selected_topics = st.sidebar.multiselect(
    "Filter by Topic",
    options=df["topic_label"].unique().tolist(),
    default=df["topic_label"].unique().tolist()
)

# apply filters
filtered_df = df[
    (df["sentiment"].isin(selected_sentiment)) &
    (df["topic_label"].isin(selected_topics))
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Posts shown:** {len(filtered_df)} / {len(df)}")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("🔍 Tech Public Opinion Tracker")
st.markdown("### How does Reddit's tech community feel about technology?")
st.markdown("An NLP analysis of **2091 posts** from r/technology — sentiment, topics, virality, and named entities.")
st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 1 — KEY METRICS
# ─────────────────────────────────────────────
st.subheader("📌 Key Findings")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Total Posts Analyzed",
    value="2,091"
)
col2.metric(
    label="Negative Sentiment",
    value="62.7%",
    delta="overwhelmingly critical",
    delta_color="inverse"
)
col3.metric(
    label="Best Model ROC AUC",
    value="0.7833",
    delta="Logistic Regression"
)
col4.metric(
    label="Negative Posts Viral Rate",
    value="27.4%",
    delta="vs 16.8% positive",
    delta_color="inverse"
)

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 2 — SENTIMENT DISTRIBUTION
# ─────────────────────────────────────────────
st.subheader("📊 Sentiment Distribution")

col1, col2 = st.columns(2)

with col1:
    sentiment_counts = filtered_df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ["sentiment", "count"]

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=sentiment_counts, x="sentiment", y="count",
        palette=["#e74c3c", "#95a5a6", "#2ecc71"], ax=ax
    )
    ax.set_title("Sentiment Distribution")
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Number of Posts")
    st.pyplot(fig)
    plt.close()

with col2:
    viral_sentiment = filtered_df.groupby("sentiment")["viral"].mean().reset_index()
    viral_sentiment["viral_pct"] = (viral_sentiment["viral"] * 100).round(1)

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=viral_sentiment, x="sentiment", y="viral_pct",
        palette=["#e74c3c", "#95a5a6", "#2ecc71"], ax=ax
    )
    ax.axhline(25, color="black", linestyle="--", label="average (25%)")
    ax.set_title("Viral Rate by Sentiment")
    ax.set_ylabel("Viral Rate (%)")
    ax.set_xlabel("Sentiment")
    ax.legend()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 3 — TOPIC ANALYSIS
# ─────────────────────────────────────────────
st.subheader("🗂️ Topic Analysis")

col1, col2 = st.columns(2)

with col1:
    topic_counts = filtered_df["topic_label"].value_counts().reset_index()
    topic_counts.columns = ["topic", "count"]

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(
        data=topic_counts, y="topic", x="count",
        palette="Set2", ax=ax
    )
    ax.set_title("Topic Distribution")
    ax.set_xlabel("Number of Posts")
    ax.set_ylabel("")
    st.pyplot(fig)
    plt.close()

with col2:
    viral_topic = filtered_df.groupby("topic_label")["viral"].mean().reset_index()
    viral_topic["viral_pct"] = (viral_topic["viral"] * 100).round(1)
    viral_topic = viral_topic.sort_values("viral_pct")

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(
        data=viral_topic, y="topic_label", x="viral_pct",
        palette="Blues_d", ax=ax
    )
    ax.axvline(25, color="red", linestyle="--", label="average (25%)")
    ax.set_title("Viral Rate by Topic")
    ax.set_xlabel("Viral Rate (%)")
    ax.set_ylabel("")
    ax.legend()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 4 — TIMING ANALYSIS
# ─────────────────────────────────────────────
st.subheader("⏰ When Do Posts Go Viral?")

col1, col2 = st.columns(2)

with col1:
    viral_hour = filtered_df.groupby("hour")["viral"].mean().reset_index()
    viral_hour["viral_pct"] = (viral_hour["viral"] * 100).round(1)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.lineplot(
        data=viral_hour, x="hour", y="viral_pct",
        color="red", linewidth=2, marker="o", ax=ax
    )
    ax.axhline(25, color="black", linestyle="--", label="average (25%)")
    ax.set_title("Viral Rate by Hour of Day (UTC)")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Viral Rate (%)")
    ax.legend()
    st.pyplot(fig)
    plt.close()

with col2:
    day_order = ["Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = filtered_df.groupby(["day_name", "hour"]).size().unstack(fill_value=0)
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])

    # only show heatmap if pivot is not empty
    if pivot.empty or pivot.shape[0] == 0:
        st.info("Not enough data to show heatmap with current filters.")
    else:
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.heatmap(
            pivot, cmap="YlOrRd",
            linewidths=0.3, linecolor="white", ax=ax
        )
        ax.set_title("Post Activity - Day vs Hour (UTC)")
        ax.set_xlabel("Hour")
        ax.set_ylabel("")
        st.pyplot(fig)
        plt.close()

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 5 — WORD CLOUDS
# ─────────────────────────────────────────────
st.subheader("☁️ Word Clouds by Sentiment")

custom_stopwords = STOPWORDS.union({
    "will", "also", "one", "new", "say", "said",
    "use", "just", "like", "get", "got", "go",
    "make", "way", "time", "year", "day", "now",
    "that", "this", "they", "them", "their",
    "have", "has", "had", "would", "could", "should",
    "people", "us", "we", "our", "your", "my",
    "don", "it", "re", "ve", "ll", "doesn", "isn",
    "s", "u", "t", "i", "m", "b"
})

sentiment_colors = {
    "positive": "Greens",
    "neutral":  "Greys",
    "negative": "Reds"
}

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for col, sentiment in zip(cols, ["positive", "neutral", "negative"]):
    subset = filtered_df[filtered_df["sentiment"] == sentiment]["clean_text"].dropna()
    if len(subset) > 0:
        text = " ".join(subset.values)
        wc = WordCloud(
            width=400, height=300,
            background_color="white",
            colormap=sentiment_colors[sentiment],
            max_words=60,
            stopwords=custom_stopwords
        ).generate(text)

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        ax.set_title(f"{sentiment.capitalize()} Posts")
        col.pyplot(fig)
        plt.close()

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 6 — TOP COMPANIES
# ─────────────────────────────────────────────
st.subheader("🏢 Top Companies by Sentiment")

all_orgs = []
for _, row in filtered_df.iterrows():
    if isinstance(row["orgs"], str) and row["orgs"].strip():
        for org in row["orgs"].split(" | "):
            org = org.strip()
            if len(org) > 2:
                all_orgs.append({
                    "org":       org,
                    "sentiment": row["sentiment"]
                })

if all_orgs:
    orgs_df = pd.DataFrame(all_orgs)
    top_orgs = orgs_df["org"].value_counts().head(10).index.tolist()
    orgs_filtered = orgs_df[orgs_df["org"].isin(top_orgs)]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.countplot(
        data=orgs_filtered, y="org", hue="sentiment",
        palette=["#e74c3c", "#95a5a6", "#2ecc71"],
        order=top_orgs, ax=ax
    )
    ax.set_title("Top 10 Companies — Sentiment Breakdown")
    ax.set_xlabel("Number of Mentions")
    ax.set_ylabel("")
    ax.legend(title="Sentiment")
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 7 — EXPLORE RAW DATA
# ─────────────────────────────────────────────
st.subheader("📋 Explore Posts")

col1, col2 = st.columns(2)
with col1:
    sentiment_filter = st.selectbox(
        "Filter by sentiment",
        ["all"] + df["sentiment"].unique().tolist()
    )
with col2:
    viral_filter = st.selectbox(
        "Filter by virality",
        ["all", "viral only", "not viral only"]
    )

# use df not filtered_df — independent of sidebar filters
explore_df = df.copy()

if sentiment_filter != "all":
    explore_df = explore_df[explore_df["sentiment"] == sentiment_filter]
if viral_filter == "viral only":
    explore_df = explore_df[explore_df["viral"] == 1]
elif viral_filter == "not viral only":
    explore_df = explore_df[explore_df["viral"] == 0]

st.dataframe(
    explore_df[["title", "sentiment", "confidence",
                "topic_label", "score", "viral"]]
    .sort_values("score", ascending=False)
    .head(50)
    .reset_index(drop=True),
    use_container_width=True
)
st.markdown("---")
st.markdown("Built by Vansh Agarwal and Nishk Mistry · VIT Chennai · 2025")

st.markdown("---")

# ─────────────────────────────────────────────
# SECTION 8 — VIRALITY PREDICTOR
# ─────────────────────────────────────────────
st.subheader("🚀 Will Your Post Go Viral?")
st.markdown("Enter a post title and see how it compares to viral posts on r/technology.")

user_title = st.text_input(
    "Enter your post title:",
    placeholder="e.g. Google announces new AI model that replaces developers"
)

post_hour = st.slider("What hour will you post? (UTC)", 0, 23, 16)
post_day  = st.selectbox(
    "What day will you post?",
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)
post_flair = st.selectbox(
    "Select a flair:",
    sorted(df["topic_label"].unique().tolist())
)

if st.button("Predict Virality 🔮"):
    if user_title.strip() == "":
        st.warning("Please enter a post title first.")
    else:
        # simple rule-based scoring
        score = 0
        reasons = []

        # title length — longer titles do better
        title_len = len(user_title)
        if title_len > 80:
            score += 2
            reasons.append("✅ Long title — performs well on r/technology")
        elif title_len > 50:
            score += 1
            reasons.append("⚠️ Medium length title — could be longer")
        else:
            reasons.append("❌ Short title — viral posts tend to be more descriptive")

        # question mark — questions engage
        if "?" in user_title:
            score += 1
            reasons.append("✅ Question format — drives engagement")

        # numbers — specificity helps
        if any(char.isdigit() for char in user_title):
            score += 1
            reasons.append("✅ Contains numbers — specific claims perform better")

        # peak hour
        if 14 <= post_hour <= 20:
            score += 2
            reasons.append("✅ Posting during peak hours (14:00-20:00 UTC)")
        else:
            reasons.append("⚠️ Off-peak hour — consider posting between 14:00-20:00 UTC")

        # weekend
        if post_day in ["Saturday", "Sunday"]:
            score += 1
            reasons.append("✅ Weekend post — slightly higher viral rate (27.3%)")
        else:
            reasons.append("⚠️ Weekday post — viral rate slightly lower (24.4%)")

        # keywords that appear in viral posts
        viral_keywords = [
            "google", "apple", "ai", "privacy", "government",
            "ban", "data", "billion", "facebook", "net neutrality",
            "security", "hack", "leak", "fcc", "law"
        ]
        matched = [kw for kw in viral_keywords if kw.lower() in user_title.lower()]
        if matched:
            score += 2
            reasons.append(f"✅ Contains viral keywords: {', '.join(matched)}")
        else:
            reasons.append("⚠️ No strong viral keywords detected")

        # max score is 9
        max_score = 9
        pct = round((score / max_score) * 100)

        st.markdown("---")

        # result
        if pct >= 70:
            st.success(f"🔥 High viral potential — {pct}% score")
        elif pct >= 45:
            st.warning(f"⚡ Moderate viral potential — {pct}% score")
        else:
            st.error(f"📉 Low viral potential — {pct}% score")

        st.markdown("**What's working and what's not:**")
        for reason in reasons:
            st.markdown(reason)

        st.markdown("---")
        st.caption("Based on patterns from 2091 r/technology posts. "
                   "Model ROC AUC: 0.7833 — predictions are probabilistic not guaranteed.")