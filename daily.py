import requests
import streamlit as st
from datetime import datetime, timedelta

def fetch_data(offset):
    url = f"https://api.yodayo.com/v1/posts?limit=500&offset={offset}&width=600&include_nsfw=true"
    response = requests.get(url)
    return response.json()

def count_stats(data):
    total_likes = sum(post.get('likes', 0) for post in data)
    total_posts = len(data)
    date_counts = {}

    for post in data:
        created_at = post.get('created_at')
        if created_at:
            date = created_at.split('T')[0]
            date_counts[date] = date_counts.get(date, 0) + 1

    return total_likes, total_posts, date_counts

def main():
    st.title("Post Analytics")

    offset = 0
    all_data = []

    while True:
        data = fetch_data(offset)
        if not data:
            break

        all_data.extend(data)
        offset += 500

    total_likes, total_posts, date_counts = count_stats(all_data)

    st.write(f"Total Likes: {total_likes}")
    st.write(f"Total Posts: {total_posts}")

    st.subheader("Posts per Day")
    for date, count in sorted(date_counts.items(), reverse=True):
        st.write(f"{date}: {count}")

if __name__ == "__main__":
    main()
