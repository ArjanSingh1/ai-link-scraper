import json
import os
import threading
from typing import Dict

class VotingSystem:
    def __init__(self, votes_file: str = "votes.json"):
        self.votes_file = votes_file
        self.lock = threading.Lock()
        self._ensure_votes_file()

    def _ensure_votes_file(self):
        if not os.path.exists(self.votes_file):
            with open(self.votes_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_votes(self) -> Dict:
        with self.lock:
            with open(self.votes_file, "r", encoding="utf-8") as f:
                return json.load(f)

    def _save_votes(self, votes: Dict):
        with self.lock:
            with open(self.votes_file, "w", encoding="utf-8") as f:
                json.dump(votes, f, indent=2)

    def vote(self, article_url: str, vote_type: str, user_id: str) -> Dict:
        if vote_type not in ("upvote", "downvote"):
            return {"success": False, "error": "Invalid vote type"}
        votes = self._load_votes()
        if article_url not in votes:
            votes[article_url] = {"upvotes": 0, "downvotes": 0, "voters": {}}
        article = votes[article_url]
        action = "added"
        if user_id in article["voters"]:
            prev = article["voters"][user_id]
            if prev == vote_type:
                # Remove vote
                article[prev + "s"] -= 1
                del article["voters"][user_id]
                action = "removed"
            else:
                # Change vote
                article[prev + "s"] -= 1
                article[vote_type + "s"] += 1
                article["voters"][user_id] = vote_type
                action = "changed"
        else:
            article[vote_type + "s"] += 1
            article["voters"][user_id] = vote_type
        self._save_votes(votes)
        return {
            "success": True,
            "action": action,
            "upvotes": article["upvotes"],
            "downvotes": article["downvotes"],
            "score": article["upvotes"] - article["downvotes"]
        }

    def get_votes(self, article_url: str) -> Dict:
        votes = self._load_votes()
        article = votes.get(article_url, {"upvotes": 0, "downvotes": 0, "voters": {}})
        return {
            "upvotes": article["upvotes"],
            "downvotes": article["downvotes"],
            "score": article["upvotes"] - article["downvotes"],
            "total_votes": article["upvotes"] + article["downvotes"]
        }

    def get_all_votes(self) -> Dict:
        votes = self._load_votes()
        result = {}
        for url, article in votes.items():
            result[url] = {
                "upvotes": article["upvotes"],
                "downvotes": article["downvotes"],
                "score": article["upvotes"] - article["downvotes"],
                "total_votes": article["upvotes"] + article["downvotes"]
            }
        return result
