import tempfile
import azure.cognitiveservices.speech as speechsdk

class AzureTTS:
    def __init__(self, key: str, region: str):
        self.key = key
        self.region = region

    def synthesize(self, text: str, voice: str, style="default", rate="0%", pitch="0%") -> str:
        speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
        speech_config.speech_synthesis_voice_name = voice

        if style != "default":
            ssml = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
                       xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-GB">
                  <voice name="{voice}">
                    <mstts:express-as style="{style}">
                      <prosody rate="{rate}" pitch="{pitch}">{text}</prosody>
                    </mstts:express-as>
                  </voice>
                </speak>
            """
        else:
            ssml = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-GB">
                  <voice name="{voice}">
                    <prosody rate="{rate}" pitch="{pitch}">{text}</prosody>
                  </voice>
                </speak>
            """

        file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir="audio_outputs")
        audio_config = speechsdk.audio.AudioOutputConfig(filename=file.name)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return file.name
        else:
            raise RuntimeError(f"Speech synthesis failed: {result.reason}")
