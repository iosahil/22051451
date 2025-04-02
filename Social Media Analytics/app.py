from flask import Flask, jsonify, request
import requests
import json

app = Flask(__name__)

# Server URL
BASE_URL = "http://20.244.56.144/evaluation-service"


def load_access_token():
    try:
        with open('auth_token.json', 'r') as f:
            token_data = json.load(f)
            return token_data.get('access_token')
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading access token: {e}")
        return None


ACCESS_TOKEN = load_access_token()


def get_api_data(endpoint):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None


def get_post_comments(post_id):
    endpoint = f"posts/{post_id}/comments"
    return get_api_data(endpoint)


@app.route('/users', methods=['GET'])
def top_users():
    users_data = get_api_data("users")
    if not users_data:
        return jsonify({"error": "Failed to fetch users"}), 500

    user_post_counts = {}

    for user_id, username in users_data.get("users", {}).items():
        posts_data = get_api_data(f"users/{user_id}/posts")
        if posts_data:
            post_count = len(posts_data.get("posts", []))
            user_post_counts[user_id] = {
                "name": username,
                "posts": post_count
            }

    sorted_users = sorted(user_post_counts.items(), key=lambda x: x[1]["posts"], reverse=True)
    top_five = sorted_users[:5]

    result = [
        {
            "id": user_id,
            "name": info["name"],
            "posts": info["posts"]
        } for user_id, info in top_five
    ]

    return jsonify({"top_users": result})


@app.route('/posts', methods=['GET'])
def get_posts():
    post_type = request.args.get('type', 'latest')

    if post_type not in ['latest', 'popular']:
        return jsonify({"error": "Invalid post type. Use 'latest' or 'popular'"}), 400

    all_posts = []

    users_data = get_api_data("users")
    if not users_data:
        return jsonify({"error": "Failed to fetch users"}), 500

    for user_id, username in users_data.get("users", {}).items():
        posts_data = get_api_data(f"users/{user_id}/posts")
        if posts_data:
            for post in posts_data.get("posts", []):
                post["username"] = username
                all_posts.append(post)

    if post_type == 'popular':
        for post in all_posts:
            comments_data = get_post_comments(post['id'])
            post["comment_count"] = len(comments_data.get("comments", [])) if comments_data else 0

        if all_posts:
            max_comments = max(post["comment_count"] for post in all_posts)
            popular_posts = [post for post in all_posts if post["comment_count"] == max_comments]
            return jsonify({"popular_posts": popular_posts})
        else:
            return jsonify({"popular_posts": []})
    else:
        sorted_posts = sorted(all_posts, key=lambda x: int(x["id"]), reverse=True)
        latest_posts = sorted_posts[:5]
        return jsonify({"latest_posts": latest_posts})


@app.route('/comments/<post_id>', methods=['GET'])
def get_comments(post_id):
    comments_data = get_post_comments(post_id)

    if not comments_data:
        return jsonify({"error": f"Failed to fetch comments for post {post_id}"}), 500

    return jsonify(comments_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
