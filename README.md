# 🤖 Sonia: Your Personal AI Soft Skills Coach

<table>
  <tr>
    <td width="50%" valign="top">
       <div align="center">
      <img src="assets/sonia.gif" alt="Sonia in Action" width="80%">
       </div>
    </td>
    <td width="60%" valign="top">
      <p>
        Meet <strong>Sonia</strong>, a conversational AI assistant designed to help you master the art of communication. Built with Python, Sonia listens to you speak, provides real-time feedback on your grammar and tone, and helps you practice your soft skills in a dynamic and interactive way.
      </p>
  </tr>
</table>
---

## ✨ Core Features

*   **🗣️ Real-Time Voice Conversations:** Engage in natural, spoken conversations directly from your terminal.
*   **🎓 Expert Feedback:** Sonia acts as a strict but fair teacher, providing detailed suggestions to improve your grammar, vocabulary, and communication style.
*   **🧠 Context-Aware:** Maintains the context of the conversation, allowing for deep and meaningful practice sessions.
*   **⚡ Blazing Fast:** Powered by the high-speed Groq API for near-instant transcription and responses.
*   **🔊 Low-Latency TTS:** Utilizes `RealtimeTTS` with the local Edge TTS engine for smooth, responsive audio output.
*   **🔧 Fully Customizable:** Easily modify Sonia's personality, goals, and teaching style by changing a single text prompt in the code.

---

## 🛠️ How It Works & Tech Stack

Sonia operates in a seamless loop of listening, thinking, and speaking. The architecture is designed to be both powerful and flexible.

1.  **🎤 Audio Recording (`PyAudio`):** The system continuously listens for your voice and records it when you're ready to speak.
2.  **✍️ Speech-to-Text (`Groq`):** Your recorded audio is sent to the Groq API, which uses the `whisper-large-v3-turbo` model to transcribe your speech into text with incredible speed and accuracy.
    *   *Note: While services like Google Speech-to-Text are great, Groq was chosen for its exceptional performance, which is crucial for a real-time conversational feel.*
3.  **🧠 The Brain (`Groq` LLM):** The transcribed text is then sent to a Large Language Model (like Llama 3.2) running on Groq. The model, guided by a system prompt, formulates a response based on its persona as "Sonia."
    *   *Flexibility is key! You can easily swap out the Groq LLM for other providers like **OpenAI (GPT-4), Anthropic (Claude), or Google (Gemini)** by simply modifying the API call section in the code.*
4.  **📢 Text-to-Speech (`RealtimeTTS`):** Sonia's response is converted back into audible speech using the `RealtimeTTS` library. This project uses the `EdgeEngine`, which leverages Microsoft Edge's built-in TTS capabilities for high-quality, low-latency voice output directly from your machine.

---

## 🚀 Getting Started

Follow these steps to get Sonia running on your local machine.

### 1. Prerequisites
*   Python 3.8+
*   A **Groq API Key**. You can get one for free from the [Groq Console](https://console.groq.com/keys).
*   (On Windows) Microsoft Edge installed for the TTS engine.

### 2. Installation
First, clone the repository to your local machine:
```bash
git clone https://github.com/your-username/sonia-assistant.git
cd sonia-assistant
```

Next, install the required Python libraries. It's recommended to do this in a virtual environment.
```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```
*(You'll need a `requirements.txt` file with the following content):*
```txt
groq
RealtimeTTS
keyboard
pyaudio
```

### 3. Configuration
Open the Python script (`main.py` or `sonia.py`) and replace the placeholder API key with your actual Groq key:
```python
# In the main() function
api_key = "YOUR_GROQ_API_KEY"  # <--- PASTE YOUR KEY HERE
```

---

## ▶️ How to Use Sonia

Using Sonia is simple and intuitive.

1.  **Run the script** from your terminal:
    ```bash
    python main.py
    ```
2.  The script will immediately say **"Recording..."**. Start speaking your sentence.
3.  When you are finished speaking, **press the `Spacebar`** to stop the recording.
4.  Wait a moment while your audio is transcribed and Sonia formulates a response.
5.  Listen to Sonia's spoken feedback.

### Playback Controls
*   **`Spacebar`:** Press during playback to **Pause/Resume** Sonia's speech.
*   **`q`:** Press during playback to **Stop** the current audio output.

### Ending the Session
*   After Sonia finishes speaking, press **`Enter`** to start a new recording session.
*   Type **`exit`** and press Enter to quit the program.

---

## 🔧 Customize Your Assistant's Behavior

The most powerful feature of this project is the ability to completely change Sonia's personality and purpose. You can transform her from a soft skills coach into a compassionate friend, a historical expert, or anything you can imagine!

To do this, simply edit the **`system`** role content within the `fetch_groq_response` function in the code.

#### Default Personality (Soft Skills Teacher):
```python
"role": "system",
"content": (
    "You are a soft skills teacher name 'Sonia'. Your role is to help improve the user's "
    "grammar, language, and communication. Provide concise but detailed feedback. "
    "Suggest better word choices and explain improvements where necessary. "
    "Ignore Punctuations in sentences as audio is transcribed to text. "
    "Be Strict and maintain the context of the ongoing conversation."
)
```

#### Example of a Different Personality (Kind and Compassionate Mental health Assistant):
You could change the content to the commented-out prompt in the code to create a completely different experience.
```python
"role": "system",
"content": (
    "You are 'Sonia', a compassionate and non-judgmental mental health assistant trained in basic psychotherapy principles. "
    "Your goal is to help users explore their thoughts, feelings, and behaviors through reflective conversation. "
    "Listen carefully, ask open-ended questions, and encourage self-awareness. "
    "Avoid giving medical advice or diagnoses. Do not focus on grammar or punctuation. "
    "Maintain a calm, empathetic tone and ensure the user feels heard and safe throughout the session."
)
```
**Experiment with this prompt to create the perfect AI assistant for your needs!**
