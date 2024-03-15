import requests
import json
import streamlit as st
import pandas as pd
import concurrent.futures

def fetch_and_concat_data(offsets):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data_for_offset, offset) for offset in offsets]
        all_data = pd.concat([future.result() for future in concurrent.futures.as_completed(futures)], ignore_index=True)
    return all_data

def fetch_data_for_offset(offset):
    url = f"https://api.yodayo.com/v1/posts?limit=500&offset={offset}&width=600&include_nsfw=true"
    response = requests.get(url)
    try:
        data = response.json()  # If the response is a list of dictionaries
    except ValueError:
        data = json.loads(response.content)  # If the response is a single string

    if isinstance(data, list):
        all_keys = [key for d in data for key in d.keys()]
        data_dict = {key: [d.get(key) for d in data] for key in set(all_keys)}
    else:
        data_dict = {"response": [data]}

    return pd.DataFrame(data_dict)

def count_stats(data):
    data['nsfw'] = data['nsfw'].astype(bool)

    total_likes = data['likes'].sum()
    total_posts = len(data)
    nsfw_posts = data['nsfw'].sum()
    nsfw_percentage = (nsfw_posts / total_posts) * 100 if total_posts > 0 else 0
    date_counts = data['created_at'].str.split('T', expand=True)[0].value_counts().sort_index(ascending=False)
    nsfw_likes = data[data['nsfw']]['likes'].sum()
    non_nsfw_likes = data[~data['nsfw']]['likes'].sum()
    hour_counts = data['created_at'].str.split('T', expand=True)[1].str[:2].value_counts().sort_index()

    return total_likes, total_posts, nsfw_posts, nsfw_percentage, date_counts, nsfw_likes, non_nsfw_likes, hour_counts


def main():
    st.title("Post Analytics")
    max_posts = 1000
    offsets = range(0, max_posts, 500)
    all_data = fetch_and_concat_data(offsets)

    total_likes, total_posts, nsfw_posts, nsfw_percentage, date_counts, nsfw_likes, non_nsfw_likes, hour_counts = count_stats(all_data)

    st.write(f"Total Likes: {total_likes}")
    st.write(f"Total Posts: {total_posts}")
    st.write(f"NSFW Posts: {nsfw_posts} ({nsfw_percentage:.2f}%)")
    st.write(f"NSFW Likes: {nsfw_likes}")
    st.write(f"Non-NSFW Likes: {non_nsfw_likes}")

    st.subheader("Posts per Day")
    for date, count in date_counts.items():
        st.write(f"{date}: {count}")

    st.subheader("Posts per Hour")
    st.bar_chart(hour_counts)

if __name__ == "__main__":
    main()
