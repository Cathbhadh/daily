import requests
import streamlit as st
import pandas as pd
import concurrent.futures

@st.cache_data(ttl=7200)
def fetch_and_concat_data(offsets):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data_for_offset, offset) for offset in offsets]
        all_data = pd.concat([future.result() for future in concurrent.futures.as_completed(futures)], ignore_index=True)
    return all_data

def fetch_data_for_offset(offset):
    url = f"https://api.yodayo.com/v1/posts?limit=500&offset={offset}&width=600&include_nsfw=true"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data)

def count_stats(data):
    total_likes = data['likes'].sum()
    total_posts = len(data)
    nsfw_posts = data['nsfw'].sum()
    nsfw_percentage = (nsfw_posts / total_posts) * 100 if total_posts > 0 else 0

    date_counts = data['created_at'].str.split('T', expand=True)[0].value_counts().sort_index(ascending=False)

    return total_likes, total_posts, nsfw_posts, nsfw_percentage, date_counts

def main():
    st.title("Post Analytics")
    max_posts = 500
    offsets = range(0, max_posts, 500)

    all_data = fetch_and_concat_data(offsets)

    total_likes, total_posts, nsfw_posts, nsfw_percentage, date_counts = count_stats(all_data)

    st.write(f"Total Likes: {total_likes}")
    st.write(f"Total Posts: {total_posts}")
    st.write(f"NSFW Posts: {nsfw_posts} ({nsfw_percentage:.2f}%)")

    st.subheader("Posts per Day")
    for date, count in date_counts.items():
        st.write(f"{date}: {count}")

if __name__ == "__main__":
    main()
