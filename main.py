from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1bab.mp3",
    "https://cdn.pixabay.com/audio/2021/11/13/audio_cb4f5da9a6.mp3",
]

CLIPS = [
    {
        "query": "Suits Harvey Specter you dont send a message scene clip",
        "hook": ["He Didn't Negotiate The Price", "He Negotiated The Power! 💼"]
    },
    {
        "query": "Suits Harvey closer best I can do scene",
        "hook": ["The Best Lawyers Don't Win In Court", "They Win Before It Starts! ⚖️"]
    },
    {
        "query": "Suits Mike Ross genius memory scene",
        "hook": ["He Used His Mind As", "His Only Weapon! 🧠"]
    },
    {
        "query": "Mad Men Don Draper Carousel pitch scene",
        "hook": ["He Didn't Sell A Product", "He Sold A Feeling! 🎯"]
    },
    {
        "query": "Mad Men Don Draper this is not the future pitch",
        "hook": ["They Came To Fire Him", "He Left With The Deal! 🤝"]
    },
    {
        "query": "Wolf of Wall Street sell me this pen scene",
        "hook": ["Create The Need First", "Then Offer The Solution! 💰"]
    },
    {
        "query": "Wolf of Wall Street Jordan Belfort motivational speech",
        "hook": ["He Lost Everything Twice", "And Still Built An Empire! 🔥"]
    },
    {
        "query": "Billions Bobby Axelrod I am the best scene",
        "hook": ["He Never Asked For Permission", "He Asked For Forgiveness After! 📈"]
    },
    {
        "query": "Billions Chuck Rhoades courtroom speech",
        "hook": ["The Room Went Silent", "The Moment He Walked In! 🏛️"]
    },
    {
        "query": "Silicon Valley Richard Hendricks compression algorithm pitch",
        "hook": ["They Laughed At The Idea", "Until It Was Worth Billions! 💻"]
    },
    {
        "query": "Succession Logan Roy business meeting scene",
        "hook": ["He Built An Empire", "By Trusting No One! 👑"]
    },
    {
        "query": "Breaking Bad Walter White I am the danger scene",
        "hook": ["The Moment He Stopped Being", "A Victim And Became The Boss! ⚡"]
    },
    {
        "query": "Breaking Bad Walter I am the one who knocks",
        "hook": ["He Didn't Ask For Respect", "He Demanded It! 😤"]
    },
