import os
import threading
import time
import keyboard
import pyaudio
import wave
import sys
from datetime import datetime
from groq import Groq
from RealtimeTTS import TextToAudioStream, EdgeEngine

class SpeechInteractionSystem:
    def __init__(self, groq_api_key):
        # Create recordings directory if it doesn't exist
        self.recordings_dir = "recordings"
        os.makedirs(self.recordings_dir, exist_ok=True)

        # Initialize Groq Client
        self.client = Groq(api_key=groq_api_key)

        # Initialize Text-to-Speech Player
        self.tts_player = self.create_tts_player()

        # Initialize conversation history
        self.conversation_history = []
        self.MAX_HISTORY_LENGTH = 1000  # Limit history to prevent context overflow

        # Initialize output list to save terminal output
        self.output = []

    def create_tts_player(self, rate=0, pitch=0, volume=0):
        """Create a Text-to-Speech Player with specified parameters."""
        engine = EdgeEngine(rate=rate, pitch=pitch, volume=volume)
        engine.set_voice("sonia")
        stream = TextToAudioStream(engine)
        return TTSPlayer(stream)

    def record_audio(self, duration=1000):
        """
        Record audio from microphone and save to a file.
        
        Args:
            duration (int): Maximum recording duration in seconds
        
        Returns:
            str: Path to the recorded audio file
        """
        filename = os.path.join(self.recordings_dir, f"audio_{int(time.time())}.wav")
        
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        frames = []
        print("Recording... Press 'space' to stop recording.")
        
        start_time = time.time()
        stop_recording = False
        
        def listen_for_stop():
            nonlocal stop_recording
            while not stop_recording:
                if keyboard.is_pressed('space'):
                    stop_recording = True
                    print("Space pressed. Stopping recording...")
                    break
                time.sleep(0.1)

        # Start the thread to listen for the 'space' key press
        stop_thread = threading.Thread(target=listen_for_stop, daemon=True)
        stop_thread.start()
        
        # Record audio while not stopped and within duration
        while not stop_recording and (time.time() - start_time) < duration:
            data = stream.read(CHUNK)
            frames.append(data)

        # Clean up audio stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the recorded audio to file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        
        print(f"Saved audio to {filename}")
        self.output.append(f"Saved audio to {filename}")
        return filename

    def transcribe_audio(self, audio_file):
        """
        Transcribe audio file using Groq Whisper.
        
        Args:
            audio_file (str): Path to the audio file
        
        Returns:
            str: Transcribed text or None if transcription fails
        """
        try:
            with open(audio_file, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file, file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    # timestamp_granularities="segment"
                )
            return transcription.text
        except Exception as e:
            print(f"Transcription error: {e}")
            self.output.append(f"Transcription error: {e}")
            return None

    def fetch_groq_response(self, prompt):
        """
        Fetch a response from Groq LLM with a soft skills teaching role.
        
        Args:
            prompt (str): User's input text
        
        Returns:
            str: AI's response
        """
        print("Fetching response from Groq...")
        self.output.append("Fetching response from Groq...")
        
        # Prepare messages with conversation history
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a soft skills teacher name 'Sonia'. Your role is to help improve the user's "
                    "grammar, language, and communication. Provide concise but detailed feedback. "
                    "Suggest better word choices and explain improvements where necessary. "
                    "Ignore Punctuations in sentences as audio is transcribed to text. "
                    "Be Strict and maintain the context of the ongoing conversation."
                )
            }
        ]
        
        # Add conversation history
        for historical_message in self.conversation_history:
            messages.append(historical_message)
        
        # Add current user input
        messages.append({"role": "user", "content": prompt})
        
        # Generate response
        response = self.client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            #model="llama-3.3-70b-specdec",
            messages=messages,
            temperature=0.8,
            max_tokens=1000,
            top_p=1,
            stream=False,
        )
        
        # Extract response text
        response_text = response.choices[0].message.content
        
        # Update conversation history
        self.update_conversation_history(prompt, response_text)
        
        return response_text

    def update_conversation_history(self, user_input, ai_response):
        """
        Update the conversation history.
        
        Args:
            user_input (str): User's input text
            ai_response (str): AI's response text
        """
        # Add user input to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Add AI response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Limit history length
        if len(self.conversation_history) > self.MAX_HISTORY_LENGTH * 2:
            # Remove oldest messages while keeping the most recent ones
            self.conversation_history = self.conversation_history[-(self.MAX_HISTORY_LENGTH * 2):]

    def interactive_session(self):
        """
        Main interactive session for speech interaction.
        Handles recording, transcription, response generation, and playback.
        """
        try:
            while True:
                # Record audio
                audio_file = self.record_audio()
                
                # Transcribe recorded audio
                user_input = self.transcribe_audio(audio_file)
                
                if not user_input:
                    print("No valid input detected. Please try again.")
                    self.output.append("No valid input detected. Please try again.")
                    continue
                
                print(f"Your input: {user_input}")
                self.output.append(f"Your input: {user_input}")
                
                # Get Groq response
                response = self.fetch_groq_response(user_input)
                print(f"Groq Response: {response}")
                self.output.append(f"Groq Response: {response}")
                
                # Play response using TTS
                self.tts_player.play(response)
                
                # Playback control
                def playback_control():
                    while self.tts_player.playing:
                        if keyboard.is_pressed('q'):
                            print("Quitting playback...")
                            self.tts_player.stop()
                            break
                        if keyboard.is_pressed('space'):
                            self.tts_player.toggle_pause()
                            state = "Paused" if self.tts_player.paused else "Resumed"
                            print(state)
                            time.sleep(0.5)  # Debounce delay

                # Start playback controls in a separate thread
                control_thread = threading.Thread(target=playback_control, daemon=True)
                control_thread.start()

                # Wait until playback finishes
                while self.tts_player.playing:
                    time.sleep(0.1)

                # Ask if user wants to continue
                if input("Press Enter to continue or type 'exit' to quit: ").lower() == 'exit':
                    break

        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            self.output.append("\nProgram terminated by user.")
        finally:
            self.tts_player.stop()

            # Save terminal output to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join("outputs", f"terminal_output_{timestamp}.txt")
            os.makedirs("outputs", exist_ok=True)
            with open(output_filename, 'w', encoding='utf-8') as f:  # Specify the encoding as 'utf-8'
                for line in self.output:
                    f.write(line + "\n")
            print(f"Terminal output saved to {output_filename}")



class TTSPlayer:
    def __init__(self, stream):
        """
        Initialize TTS Player with a given audio stream.
        
        Args:
            stream (TextToAudioStream): Audio stream for playback
        """
        self.stream = stream
        self.playing = False
        self.paused = False
        self.stop_signal = threading.Event()

    def play(self, text):
        """
        Play text as audio.
        
        Args:
            text (str): Text to be converted to speech and played
        """
        self.playing = True
        self.stop_signal.clear()
        self.paused = False

        def synthesize_and_play():
            try:
                self.stream.feed([text]).play_async(log_synthesized_text=True)
                while not self.stop_signal.is_set() and self.stream.is_playing():
                    if self.paused:
                        self.stream.pause()
                        time.sleep(0.1)
                    else:
                        self.stream.resume()
                        time.sleep(0.1)
                self.stream.stop()
            except Exception as e:
                print(f"Playback error: {e}")
            finally:
                self.playing = False

        playback_thread = threading.Thread(target=synthesize_and_play, daemon=True)
        playback_thread.start()

    def stop(self):
        """Stop audio playback."""
        self.stop_signal.set()

    def toggle_pause(self):
        """Toggle between pause and resume."""
        self.paused = not self.paused

def main(): 
    # Replace with your actual Groq API key
    api_key = "YOUR_GROQ_API_KEY"
    
    # Initialize and start the speech interaction system
    speech_system = SpeechInteractionSystem(api_key)
    speech_system.interactive_session()

if __name__ == "__main__":
    main()
