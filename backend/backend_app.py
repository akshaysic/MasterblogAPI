from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory data store
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    sorted_posts = POSTS.copy()

    if sort_field:
        if sort_field not in ["title", "content"]:
            return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400
        if direction not in ["asc", "desc"]:
            return jsonify({"error": "Invalid sort direction. Must be 'asc' or 'desc'."}), 400

        reverse = (direction == "desc")
        sorted_posts.sort(key=lambda post: post.get(sort_field, "").lower(), reverse=reverse)

    return jsonify(sorted_posts), 200

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Both 'title' and 'content' are required."}), 400

    new_id = max([post["id"] for post in POSTS], default=0) + 1
    new_post = {"id": new_id, "title": title, "content": content}
    POSTS.append(new_post)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)
    if not post_to_delete:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS = [post for post in POSTS if post["id"] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    for post in POSTS:
        if post["id"] == post_id:
            post["title"] = data.get("title", post["title"])
            post["content"] = data.get("content", post["content"])
            return jsonify(post), 200

    return jsonify({"error": f"Post with id {post_id} not found."}), 404

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()

    results = []
    for post in POSTS:
        title_matches = title_query in post["title"].lower() if title_query else False
        content_matches = content_query in post["content"].lower() if content_query else False
        if title_matches or content_matches:
            results.append(post)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
